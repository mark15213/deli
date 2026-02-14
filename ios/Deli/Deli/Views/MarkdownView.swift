import SwiftUI
import WebKit

#if canImport(UIKit)
typealias PlatformViewRepresentable = UIViewRepresentable
#elseif canImport(AppKit)
typealias PlatformViewRepresentable = NSViewRepresentable
#endif

struct MarkdownView: PlatformViewRepresentable {
    let markdown: String
    let fontSize: CGFloat

    init(_ markdown: String, fontSize: CGFloat = 16) {
        self.markdown = markdown
        self.fontSize = fontSize
    }

    #if canImport(UIKit)
    func makeUIView(context: Context) -> WKWebView {
        makeWebView(context: context)
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        loadContent(in: webView)
    }
    #elseif canImport(AppKit)
    func makeNSView(context: Context) -> WKWebView {
        makeWebView(context: context)
    }

    func updateNSView(_ webView: WKWebView, context: Context) {
        loadContent(in: webView)
    }
    #endif

    private func makeWebView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        let webView = WKWebView(frame: .zero, configuration: config)
        #if canImport(UIKit)
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.scrollView.isScrollEnabled = true
        webView.scrollView.bounces = false
        #endif
        webView.navigationDelegate = context.coordinator
        return webView
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    private func loadContent(in webView: WKWebView) {
        let escaped = markdown
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "`", with: "\\`")
            .replacingOccurrences(of: "$", with: "\\$")
        let html = Self.htmlTemplate(content: escaped, fontSize: fontSize)
        webView.loadHTMLString(html, baseURL: nil)
    }

    class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction) async -> WKNavigationActionPolicy {
            if navigationAction.navigationType == .linkActivated,
               let url = navigationAction.request.url {
                #if canImport(UIKit)
                await UIApplication.shared.open(url)
                #elseif canImport(AppKit)
                NSWorkspace.shared.open(url)
                #endif
                return .cancel
            }
            return .allow
        }
    }

    // MARK: - HTML Template

    static func htmlTemplate(content: String, fontSize: CGFloat) -> String {
        """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
        <script src="https://cdn.jsdelivr.net/npm/marked@14.0.0/marked.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: \(Int(fontSize))px;
            line-height: 1.6;
            color: #1a1a1a;
            padding: 0;
            background: transparent;
            -webkit-text-size-adjust: none;
          }
          @media (prefers-color-scheme: dark) {
            body { color: #e5e5e5; }
            code { background: #2a2a2a; }
            pre { background: #1e1e1e; border-color: #333; }
            blockquote { border-color: #555; color: #aaa; }
          }
          h1, h2, h3 { margin: 0.6em 0 0.3em; font-weight: 700; }
          h1 { font-size: 1.4em; }
          h2 { font-size: 1.2em; }
          h3 { font-size: 1.05em; }
          p { margin: 0.4em 0; }
          ul, ol { padding-left: 1.4em; margin: 0.4em 0; }
          li { margin: 0.2em 0; }
          code {
            font-family: 'SF Mono', Menlo, monospace;
            font-size: 0.88em;
            background: #f0f0f0;
            padding: 0.15em 0.35em;
            border-radius: 4px;
          }
          pre {
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
            overflow-x: auto;
            margin: 0.5em 0;
          }
          pre code { background: none; padding: 0; font-size: 0.85em; }
          blockquote {
            border-left: 3px solid #ccc;
            padding-left: 12px;
            color: #666;
            margin: 0.5em 0;
          }
          strong { font-weight: 700; }
          a { color: #007AFF; text-decoration: none; }
          img { max-width: 100%; border-radius: 8px; }
          .katex-display { margin: 0.5em 0; overflow-x: auto; }
          .katex { font-size: 1.05em; }
          table { border-collapse: collapse; width: 100%; margin: 0.5em 0; }
          th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
          th { background: #f5f5f5; font-weight: 600; }
        </style>
        </head>
        <body>
        <div id="content"></div>
        <script>
        (function() {
          const raw = `\(content)`;

          // Replace LaTeX delimiters before markdown parsing
          // Block math: $$ ... $$ or \\[ ... \\]
          let text = raw.replace(/\\$\\$([\\s\\S]*?)\\$\\$/g, (_, m) =>
            '<div class="katex-display">' + katex.renderToString(m.trim(), {displayMode: true, throwOnError: false}) + '</div>'
          );
          text = text.replace(/\\\\\\[([\\s\\S]*?)\\\\\\]/g, (_, m) =>
            '<div class="katex-display">' + katex.renderToString(m.trim(), {displayMode: true, throwOnError: false}) + '</div>'
          );

          // Inline math: $ ... $ or \\( ... \\)
          text = text.replace(/\\$([^$\\n]+?)\\$/g, (_, m) =>
            katex.renderToString(m.trim(), {displayMode: false, throwOnError: false})
          );
          text = text.replace(/\\\\\\(([\\s\\S]*?)\\\\\\)/g, (_, m) =>
            katex.renderToString(m.trim(), {displayMode: false, throwOnError: false})
          );

          // Parse remaining markdown
          marked.setOptions({ breaks: true, gfm: true });
          document.getElementById('content').innerHTML = marked.parse(text);
        })();
        </script>
        </body>
        </html>
        """
    }
}
