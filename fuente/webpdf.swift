// webpdf: carga una URL en un WKWebView (motor de Safari) y guarda lo que se ve como PDF vectorial de una página.
// Sirve para sacar las láminas del estudio a su tamaño de papel: lamina.html?n=01&pdf=1 dibuja la hoja A1 a 2384 × 1684 px (1 px = 1 pt).
// uso: webpdf <url> <salida.pdf> [ancho_pt] [alto_pt] [segundos]
//   swiftc -O -o webpdf fuente/webpdf.swift
//   ./webpdf "http://127.0.0.1:8801/lamina.html?n=01&pdf=1" "lamina 01.pdf" 2384 1684 4
// Los PDF no van al repo (regla del proyecto): se dejan fuera, por ejemplo en ~/Downloads.
import Cocoa
import WebKit
let a = CommandLine.arguments
let url = URL(string: a[1])!, out = a[2]
let w = CGFloat(Double(a.count > 3 ? a[3] : "2384") ?? 2384), h = CGFloat(Double(a.count > 4 ? a[4] : "1684") ?? 1684)
let wait = Double(a.count > 5 ? a[5] : "4") ?? 4
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let cfg = WKWebViewConfiguration()
let hook = WKUserScript(source: "window.__errs=[];window.addEventListener('error',e=>__errs.push('ERR '+e.message+' @'+(e.filename||'').split('/').pop()+':'+e.lineno));const __oe=console.error;console.error=(...x)=>{__errs.push('console.error '+x.map(String).join(' '));__oe.apply(console,x)};", injectionTime: .atDocumentStart, forMainFrameOnly: false)
cfg.userContentController.addUserScript(hook)
let web = WKWebView(frame: NSRect(x: 0, y: 0, width: w, height: h), configuration: cfg)
let win = NSWindow(contentRect: NSRect(x: -30000, y: -30000, width: w, height: h), styleMask: [.borderless], backing: .buffered, defer: false)
win.contentView = web
win.alphaValue = 0.0
win.orderFrontRegardless()
class D: NSObject, WKNavigationDelegate {
  func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + wait) {
      webView.evaluateJavaScript("JSON.stringify({errs: window.__errs, ver: (window.PILAUCO_VERSION||{}).n})") { r, e in
        print("js:", r ?? "nil", e.map { "\($0)" } ?? "")
        let pc = WKPDFConfiguration(); pc.rect = CGRect(x: 0, y: 0, width: w, height: h)
        webView.createPDF(configuration: pc) { res in
          switch res {
          case .success(let data): do { try data.write(to: URL(fileURLWithPath: out)); print("pdf:", out, data.count, "bytes") } catch { print("error al escribir:", error); exit(1) }
          case .failure(let err): print("error pdf:", err); exit(1)
          }
          exit(0)
        }
      }
    }
  }
  func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { print("fallo:", error); exit(1) }
  func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { print("fallo:", error); exit(1) }
}
let d = D(); web.navigationDelegate = d
web.load(URLRequest(url: url))
DispatchQueue.main.asyncAfter(deadline: .now() + wait + 40) { print("tiempo agotado"); exit(2) }
app.run()
