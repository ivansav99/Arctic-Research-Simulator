import SwiftUI
import WebKit

struct ContentView: View {
    var body: some View {
        GameWebView()
            .ignoresSafeArea()
            .background(Color(red: 0.03, green: 0.18, blue: 0.29))
    }
}

struct GameWebView: UIViewRepresentable {
    // The native shell intentionally loads the same GitHub Pages build as the
    // website. Keeping one web codebase prevents the iOS test app from drifting
    // away from the browser version while the simulator is still evolving.
    static let gameURL = URL(string: "https://ivansav99.github.io/Arctic-Research-Simulator/?app=ios")!

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        // Keep the persistent store so browser saves survive app launches.
        configuration.websiteDataStore = .default()
        configuration.defaultWebpagePreferences.preferredContentMode = .mobile

        let controller = WKUserContentController()
        controller.addUserScript(WKUserScript(
            source: "document.documentElement.classList.add('ios-native-shell');",
            injectionTime: .atDocumentStart,
            forMainFrameOnly: true
        ))
        configuration.userContentController = controller

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = true
        webView.backgroundColor = UIColor(red: 0.03, green: 0.18, blue: 0.29, alpha: 1)
        webView.scrollView.backgroundColor = webView.backgroundColor
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.scrollView.bounces = false
        webView.allowsBackForwardNavigationGestures = false
        if #available(iOS 16.4, *) { webView.isInspectable = true }

        // Always revalidate the live page on launch instead of allowing a stale
        // WKWebView document cache to make the app appear one release behind.
        var request = URLRequest(url: Self.gameURL, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
        request.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
        request.setValue("no-cache", forHTTPHeaderField: "Pragma")
        webView.load(request)
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }
            if let host = url.host, host != GameWebView.gameURL.host, navigationAction.navigationType == .linkActivated {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }
    }
}