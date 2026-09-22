import SwiftUI
import WebKit
import StoreKit

struct ContentView: View {
    var body: some View {
        GameWebView()
            .ignoresSafeArea()
            .background(Color(red: 0.03, green: 0.18, blue: 0.29))
    }
}

struct GameWebView: UIViewRepresentable {
    static let gameURL = URL(string: "arsapp://local/index.html?app=ios&offline=1")!

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        configuration.defaultWebpagePreferences.preferredContentMode = .mobile
        configuration.setURLSchemeHandler(context.coordinator.appSchemeHandler, forURLScheme: "arsapp")

        let controller = WKUserContentController()
        controller.addUserScript(WKUserScript(
            source: """
            window.AR_IOS_OFFLINE_SHELL=true;
            window.ArcticResearchIAP={
              _callbacks:{},
              purchase:function(productId){
                return new Promise((resolve)=>{
                  const requestId='iap-'+Date.now()+'-'+Math.random().toString(36).slice(2);
                  this._callbacks[requestId]=resolve;
                  try{
                    window.webkit.messageHandlers.iapPurchase.postMessage({requestId:requestId,productId:String(productId||'')});
                  }catch(error){
                    delete this._callbacks[requestId];
                    resolve({success:false,message:error&&error.message?error.message:'App Store purchase service is unavailable'});
                  }
                });
              },
              _complete:function(requestId,result){
                const callback=this._callbacks[requestId];
                if(!callback)return;
                delete this._callbacks[requestId];
                callback(result||{success:false,message:'Purchase was not completed'});
              }
            };
            if(document.documentElement){document.documentElement.classList.add('ios-native-shell');}
            """,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: true
        ))
        controller.add(context.coordinator, name: "iapPurchase")
        configuration.userContentController = controller

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = true
        webView.backgroundColor = UIColor(red: 0.03, green: 0.18, blue: 0.29, alpha: 1)
        webView.scrollView.backgroundColor = webView.backgroundColor
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.scrollView.bounces = false
        webView.allowsBackForwardNavigationGestures = false
        #if DEBUG
        if #available(iOS 16.4, *) { webView.isInspectable = true }
        #endif

        context.coordinator.webView = webView
        webView.load(URLRequest(url: Self.gameURL, cachePolicy: .useProtocolCachePolicy, timeoutInterval: 30))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
        let appSchemeHandler = OfflineAppSchemeHandler()
        weak var webView: WKWebView?
        private let allowedProductIDs: Set<String> = [
            "ars.private_funding.1m",
            "ars.private_funding.10m",
            "ars.private_funding.50m"
        ]

        func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
            guard message.name == "iapPurchase",
                  let body = message.body as? [String: Any],
                  let requestId = body["requestId"] as? String,
                  let productId = body["productId"] as? String else { return }

            Task { [weak self] in
                guard let self else { return }
                let result = await self.purchase(productId: productId)
                await self.completePurchaseRequest(requestId: requestId, result: result)
            }
        }

        private func purchase(productId: String) async -> [String: Any] {
            guard allowedProductIDs.contains(productId) else {
                return ["success": false, "message": "Unknown App Store product"]
            }

            do {
                let products = try await Product.products(for: [productId])
                guard let product = products.first else {
                    return ["success": false, "message": "This purchase is not available yet"]
                }
                guard product.type == .consumable else {
                    return ["success": false, "message": "App Store product is misconfigured"]
                }

                let purchaseResult = try await product.purchase()
                switch purchaseResult {
                case .success(let verification):
                    switch verification {
                    case .verified(let transaction):
                        await transaction.finish()
                        return [
                            "success": true,
                            "transactionId": String(transaction.id),
                            "productId": transaction.productID
                        ]
                    case .unverified(_, let error):
                        return ["success": false, "message": "The App Store could not verify this purchase: \(error.localizedDescription)"]
                    }
                case .pending:
                    return ["success": false, "message": "Purchase is pending approval"]
                case .userCancelled:
                    return ["success": false, "message": "Purchase cancelled"]
                @unknown default:
                    return ["success": false, "message": "Purchase was not completed"]
                }
            } catch {
                return ["success": false, "message": error.localizedDescription]
            }
        }

        @MainActor
        private func completePurchaseRequest(requestId: String, result: [String: Any]) {
            guard let webView,
                  let requestData = try? JSONSerialization.data(withJSONObject: requestId),
                  let requestJSON = String(data: requestData, encoding: .utf8),
                  let resultData = try? JSONSerialization.data(withJSONObject: result),
                  let resultJSON = String(data: resultData, encoding: .utf8) else { return }

            let script = "window.ArcticResearchIAP && window.ArcticResearchIAP._complete(\(requestJSON), \(resultJSON));"
            webView.evaluateJavaScript(script, completionHandler: nil)
        }

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.cancel)
                return
            }
            if url.scheme == "arsapp" {
                decisionHandler(.allow)
                return
            }
            if navigationAction.navigationType == .linkActivated, UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }
    }
}

final class OfflineAppSchemeHandler: NSObject, WKURLSchemeHandler {
    private let fileManager = FileManager.default
    private let cacheLimitBytes: Int64 = 150 * 1024 * 1024
    private let cacheDirectory: URL
    private let stateLock = NSLock()
    private var networkTasks: [ObjectIdentifier: URLSessionDataTask] = [:]
    private var stoppedTasks = Set<ObjectIdentifier>()

    override init() {
        let caches = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first!
        cacheDirectory = caches.appendingPathComponent("ArcticTerrainCache", isDirectory: true)
        super.init()
        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url else {
            fail(urlSchemeTask, code: NSURLErrorBadURL, message: "Missing app resource URL")
            return
        }
        let identifier = taskIdentifier(urlSchemeTask)
        stateLock.lock()
        stoppedTasks.remove(identifier)
        stateLock.unlock()

        if url.path.hasPrefix("/_terrain/") {
            serveTerrain(url: url, schemeTask: urlSchemeTask)
        } else {
            serveBundledResource(url: url, schemeTask: urlSchemeTask)
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {
        let identifier = taskIdentifier(urlSchemeTask)
        stateLock.lock()
        stoppedTasks.insert(identifier)
        let task = networkTasks.removeValue(forKey: identifier)
        stateLock.unlock()
        task?.cancel()
    }

    private func serveBundledResource(url: URL, schemeTask: WKURLSchemeTask) {
        guard let resourceRoot = Bundle.main.resourceURL?.appendingPathComponent("WebApp", isDirectory: true) else {
            fail(schemeTask, code: NSFileNoSuchFileError, message: "Bundled WebApp directory is missing")
            return
        }
        let relative = url.path == "/" || url.path.isEmpty ? "index.html" : String(url.path.dropFirst())
        guard !relative.contains("..") else {
            fail(schemeTask, code: NSURLErrorNoPermissionsToReadFile, message: "Invalid resource path")
            return
        }
        let fileURL = resourceRoot.appendingPathComponent(relative).standardizedFileURL
        let rootPath = resourceRoot.standardizedFileURL.path + "/"
        guard fileURL.path.hasPrefix(rootPath), fileManager.fileExists(atPath: fileURL.path) else {
            fail(schemeTask, code: NSFileNoSuchFileError, message: "Bundled resource not found: \(relative)")
            return
        }
        do {
            let data = try Data(contentsOf: fileURL, options: .mappedIfSafe)
            respond(schemeTask, url: url, data: data, mimeType: mimeType(for: fileURL.pathExtension))
        } catch {
            fail(schemeTask, error: error)
        }
    }

    private func serveTerrain(url: URL, schemeTask: WKURLSchemeTask) {
        let parts = url.path.split(separator: "/")
        guard parts.count == 4,
              parts[0] == "_terrain",
              let year = Int(parts[1]),
              let ix = Int(parts[2]),
              let iy = Int(parts[3].split(separator: ".").first ?? "") else {
            fail(schemeTask, code: NSURLErrorBadURL, message: "Invalid terrain tile URL")
            return
        }

        let filename = "terrain-\(year)-\(ix)-\(iy).png"
        if let bundledRoot = Bundle.main.resourceURL?.appendingPathComponent("WebApp/assets/map/svalbard", isDirectory: true) {
            let bundled = bundledRoot.appendingPathComponent(filename)
            if fileManager.fileExists(atPath: bundled.path), let data = try? Data(contentsOf: bundled, options: .mappedIfSafe) {
                respond(schemeTask, url: url, data: data, mimeType: "image/png")
                return
            }
        }

        let cached = cacheDirectory.appendingPathComponent(filename)
        if fileManager.fileExists(atPath: cached.path), let data = try? Data(contentsOf: cached, options: .mappedIfSafe) {
            try? fileManager.setAttributes([.modificationDate: Date()], ofItemAtPath: cached.path)
            respond(schemeTask, url: url, data: data, mimeType: "image/png")
            return
        }

        guard let remote = terrainWMSURL(year: year, ix: ix, iy: iy) else {
            fail(schemeTask, code: NSURLErrorBadURL, message: "Could not construct terrain URL")
            return
        }
        var request = URLRequest(url: remote, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
        request.setValue("ArcticResearchSimulator/0.1 iOS", forHTTPHeaderField: "User-Agent")
        let identifier = taskIdentifier(schemeTask)
        let dataTask = URLSession.shared.dataTask(with: request) { [weak self, weak schemeTask] data, response, error in
            guard let self, let schemeTask else { return }
            self.stateLock.lock()
            self.networkTasks.removeValue(forKey: identifier)
            let stopped = self.stoppedTasks.contains(identifier)
            self.stateLock.unlock()
            guard !stopped else { return }

            if let error {
                self.fail(schemeTask, error: error)
                return
            }
            guard let http = response as? HTTPURLResponse,
                  (200..<300).contains(http.statusCode),
                  let data,
                  data.count > 1024 else {
                self.fail(schemeTask, code: NSURLErrorCannotDecodeContentData, message: "Terrain server did not return a usable image")
                return
            }
            do {
                try data.write(to: cached, options: .atomic)
                try? self.fileManager.setAttributes([.modificationDate: Date()], ofItemAtPath: cached.path)
                self.pruneTerrainCache()
            } catch {
                // A cache-write failure should not prevent the already downloaded map from displaying.
            }
            self.respond(schemeTask, url: url, data: data, mimeType: "image/png")
        }
        stateLock.lock()
        networkTasks[identifier] = dataTask
        stateLock.unlock()
        dataTask.resume()
    }

    private func terrainWMSURL(year: Int, ix: Int, iy: Int) -> URL? {
        guard year == 2024 || year == 2022 else { return nil }
        let tileKM = 128
        let minX = ix * tileKM
        let minY = iy * tileKM
        let maxX = minX + tileKM
        let maxY = minY + tileKM
        let minE = minX * 1000
        let maxE = maxX * 1000
        let minN = -maxY * 1000
        let maxN = -minY * 1000
        var components = URLComponents(string: "https://wms.gebco.net/\(year)/north-polar/mapserv")
        components?.queryItems = [
            URLQueryItem(name: "BBOX", value: "\(minE),\(minN),\(maxE),\(maxN)"),
            URLQueryItem(name: "crs", value: "EPSG:3996"),
            URLQueryItem(name: "format", value: "image/png"),
            URLQueryItem(name: "height", value: "1024"),
            URLQueryItem(name: "layers", value: "GEBCO_NORTH_POLAR_VIEW_bed_\(year)"),
            URLQueryItem(name: "request", value: "getmap"),
            URLQueryItem(name: "service", value: "wms"),
            URLQueryItem(name: "version", value: "1.3.0"),
            URLQueryItem(name: "width", value: "1024")
        ]
        return components?.url
    }

    private func pruneTerrainCache() {
        guard let files = try? fileManager.contentsOfDirectory(
            at: cacheDirectory,
            includingPropertiesForKeys: [.fileSizeKey, .contentModificationDateKey, .isRegularFileKey],
            options: [.skipsHiddenFiles]
        ) else { return }
        var entries: [(url: URL, size: Int64, date: Date)] = []
        var total: Int64 = 0
        for url in files {
            guard let values = try? url.resourceValues(forKeys: [.fileSizeKey, .contentModificationDateKey, .isRegularFileKey]),
                  values.isRegularFile == true else { continue }
            let size = Int64(values.fileSize ?? 0)
            total += size
            entries.append((url, size, values.contentModificationDate ?? .distantPast))
        }
        guard total > cacheLimitBytes else { return }
        for entry in entries.sorted(by: { $0.date < $1.date }) {
            try? fileManager.removeItem(at: entry.url)
            total -= entry.size
            if total <= cacheLimitBytes { break }
        }
    }

    private func taskIdentifier(_ task: WKURLSchemeTask) -> ObjectIdentifier {
        ObjectIdentifier(task as AnyObject)
    }

    private func isStopped(_ task: WKURLSchemeTask) -> Bool {
        let identifier = taskIdentifier(task)
        stateLock.lock()
        let result = stoppedTasks.contains(identifier)
        stateLock.unlock()
        return result
    }

    private func respond(_ task: WKURLSchemeTask, url: URL, data: Data, mimeType: String) {
        DispatchQueue.main.async { [weak self, weak task] in
            guard let self, let task, !self.isStopped(task) else { return }
            let encoding = mimeType.hasPrefix("text/") || mimeType.contains("javascript") || mimeType.contains("json") ? "utf-8" : nil
            let response = URLResponse(url: url, mimeType: mimeType, expectedContentLength: data.count, textEncodingName: encoding)
            task.didReceive(response)
            task.didReceive(data)
            task.didFinish()
        }
    }

    private func fail(_ task: WKURLSchemeTask, code: Int, message: String) {
        fail(task, error: NSError(domain: NSURLErrorDomain, code: code, userInfo: [NSLocalizedDescriptionKey: message]))
    }

    private func fail(_ task: WKURLSchemeTask, error: Error) {
        DispatchQueue.main.async { [weak self, weak task] in
            guard let self, let task, !self.isStopped(task) else { return }
            task.didFailWithError(error)
        }
    }

    private func mimeType(for ext: String) -> String {
        switch ext.lowercased() {
        case "html": return "text/html"
        case "css": return "text/css"
        case "js": return "text/javascript"
        case "json": return "application/json"
        case "webmanifest": return "application/manifest+json"
        case "svg": return "image/svg+xml"
        case "png": return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "webp": return "image/webp"
        case "gif": return "image/gif"
        case "mp3": return "audio/mpeg"
        case "wav": return "audio/wav"
        case "ogg": return "audio/ogg"
        default: return "application/octet-stream"
        }
    }
}
