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
    static let gameURL = URL(string: "https://ivansav99.github.io/Arctic-Research-Simulator/?app=ios")!

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
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

        let request = URLRequest(url: Self.gameURL, cachePolicy: .reloadRevalidatingCacheData, timeoutInterval: 30)
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
