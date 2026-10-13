// webshot: carga una URL en un WKWebView (motor de Safari, con WebGL) y guarda una captura PNG tras N segundos.
// uso: webshot <url> <salida.png> [ancho] [alto] [segundos] [js_final]
import Cocoa
import WebKit
let a = CommandLine.arguments
let url = URL(string: a[1])!, out = a[2]
let w = CGFloat(Double(a.count > 3 ? a[3] : "1200") ?? 1200), h = CGFloat(Double(a.count > 4 ? a[4] : "800") ?? 800)
let wait = Double(a.count > 5 ? a[5] : "4") ?? 4
let jsFinal = a.count > 6 && !a[6].isEmpty ? a[6] : "JSON.stringify({errs: window.__errs, ver: (window.PILAUCO_VERSION||{}).n})"
let jsPre = a.count > 7 ? a[7] : ""   // se ejecuta 1,5 s antes de la captura (para apretar botones, mover la cámara, etc.)
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let cfg = WKWebViewConfiguration()
let hook = WKUserScript(source: "window.__errs=[];window.addEventListener('error',e=>__errs.push('ERR '+e.message+' @'+(e.filename||'').split('/').pop()+':'+e.lineno));const __oe=console.error;console.error=(...x)=>{__errs.push('console.error '+x.map(String).join(' '));__oe.apply(console,x)};", injectionTime: .atDocumentStart, forMainFrameOnly: false)
cfg.userContentController.addUserScript(hook)
let web = WKWebView(frame: NSRect(x: 0, y: 0, width: w, height: h), configuration: cfg)
let win = NSWindow(contentRect: NSRect(x: -20000, y: -20000, width: w, height: h), styleMask: [.borderless], backing: .buffered, defer: false)
win.contentView = web
win.alphaValue = 0.0
win.orderFrontRegardless()
class D: NSObject, WKNavigationDelegate {
  func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + max(0.5, wait - 1.5)) {
      if !jsPre.isEmpty { webView.evaluateJavaScript(jsPre) { r, e in print("pre:", r ?? "nil", e.map { "\($0)" } ?? "") } }
    }
    DispatchQueue.main.asyncAfter(deadline: .now() + wait) {
      webView.evaluateJavaScript(jsFinal) { r, e in
        print("js:", r ?? "nil", e.map { "\($0)" } ?? "")
        let sc = WKSnapshotConfiguration(); sc.rect = NSRect(x: 0, y: 0, width: w, height: h)
        webView.takeSnapshot(with: sc) { img, err in
          if let img = img, let t = img.tiffRepresentation, let rep = NSBitmapImageRep(data: t), let png = rep.representation(using: .png, properties: [:]) {
            try? png.write(to: URL(fileURLWithPath: out)); print("captura:", out, Int(img.size.width), "x", Int(img.size.height))
          } else { print("error captura:", err.map { "\($0)" } ?? "?") }
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
DispatchQueue.main.asyncAfter(deadline: .now() + wait + 25) { print("tiempo agotado"); exit(2) }
app.run()
