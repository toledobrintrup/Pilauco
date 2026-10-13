// Harness para probar nav3d.js sin navegador (JavaScriptCore): THREE real + OrbitControls r128 + nav3d con un lienzo de mentira.
// Simula pasos de rueda hacia el muro de una sala y mide cuántos toma llegar, atravesar, cruzar la sala y volver a salir.
// Uso (desde una carpeta que tenga three/three.min.js y three/OrbitControls.js de r128, bajados del CDN):
//   /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc fuente/navtest_nav3d.js
// Ajusta las rutas de load() de abajo si los pones en otro lado.
var window = globalThis, self = globalThis; var t0 = 0; var _now = 0;
var performance = { now: function(){ return _now; } };
function El(){ this.ls = {}; this.style = {}; this.children = []; this.attrs = {}; this.classList = { add(){}, remove(){}, toggle(){} }; this.clientWidth = 1200; this.clientHeight = 800; this.ownerDocument = null; }
El.prototype.addEventListener = function(t, f){ (this.ls[t] = this.ls[t] || []).push(f); };
El.prototype.removeEventListener = function(t, f){ if (this.ls[t]) this.ls[t] = this.ls[t].filter(g => g !== f); };
El.prototype.dispatchEvent = function(e){ (this.ls[e.type] || []).forEach(f => f(e)); return true; };
El.prototype.getBoundingClientRect = function(){ return { left: 0, top: 0, width: this.clientWidth, height: this.clientHeight, right: this.clientWidth, bottom: this.clientHeight }; };
El.prototype.hasAttribute = function(a){ return a in this.attrs; }; El.prototype.setAttribute = function(a, v){ this.attrs[a] = v; }; El.prototype.getAttribute = function(a){ return this.attrs[a]; };
El.prototype.appendChild = function(c){ this.children.push(c); return c; }; El.prototype.append = function(){ for (var i = 0; i < arguments.length; i++) this.children.push(arguments[i]); };
El.prototype.focus = function(){}; El.prototype.contains = function(){ return false; }; El.prototype.getContext = function(){ return null; };
var document = { head: new El(), body: new El(), activeElement: null, createElement: function(){ return new El(); }, getElementById: function(){ return null; }, addEventListener(){}, removeEventListener(){} };
window.addEventListener = function(){}; window.removeEventListener = function(){}; window.matchMedia = function(){ return { matches: false, addEventListener(){}, addListener(){} }; };
function CustomEvent(type, o){ this.type = type; this.detail = o && o.detail; } window.CustomEvent = CustomEvent;
var HTMLElement = undefined;
load('three/three.min.js'); load('three/OrbitControls.js'); load('/Users/toledobrintrup/Coding/Pilauco/nav3d.js');
var T = THREE;
var scene = new T.Scene();
// una "sala": caja de 6 x 3 x 10 m con muros de 25 cm, abierta por arriba? No: cerrada, como el búnker. Centro en (0,1.5,0)
function caja(w, h, d, x, y, z){ var m = new T.Mesh(new T.BoxGeometry(w, h, d), new T.MeshBasicMaterial()); m.position.set(x, y, z); m.updateMatrixWorld(); return m; }
var muroS = caja(10, 3, 0.25, 0, 1.5, 3.125), muroN = caja(10, 3, 0.25, 0, 1.5, -3.125), losa = caja(10, 0.2, 6.5, 0, 3.1, 0), piso = caja(10, 0.2, 6.5, 0, -0.1, 0), muroE = caja(0.25, 3, 6, 5.125, 1.5, 0), muroO = caja(0.25, 3, 6, -5.125, 1.5, 0);
[muroS, muroN, losa, piso, muroE, muroO].forEach(m => scene.add(m)); scene.updateMatrixWorld(true);
var camera = new T.PerspectiveCamera(42, 1.5, 0.05, 500); camera.position.set(0, 1.5, 20); camera.updateMatrixWorld();
var dom = new El();
var controls = new T.OrbitControls(camera, dom); controls.target.set(0, 1.5, 3); controls.update();
var nav = Nav3D.conectar({ camera, controls, dom, objetivos: () => [scene], planoY: 0, distMin: 0.05, distMax: 320, avanceMin: 0.4, pedir: function(){} });
function rueda(dy){ dom.dispatchEvent({ type: 'wheel', deltaY: dy, deltaMode: 0, clientX: 600, clientY: 400, ctrlKey: false, preventDefault(){} }); for (var i = 0; i < 40; i++){ _now += 16; nav.actualizar(_now); controls.update(); } }
var log = [];
for (var n = 1; n <= 90; n++){ rueda(-100); var d = camera.position.distanceTo(controls.target); log.push(n + ': cam z=' + camera.position.z.toFixed(2) + ' tgt z=' + controls.target.z.toFixed(2) + ' d=' + d.toFixed(2)); }
print(log.filter((l, i) => i % 3 === 0 || i > 40).join('\n'));
print('dentro de la sala (z entre -3 y 3):', camera.position.z < 3.0 && camera.position.z > -3.0);
// ahora: entrar a la sala (22 pasos), quedar pegado al muro del fondo, y alejarse: ¿retrocede de a pasos razonables?
camera.position.set(0, 1.5, 20); controls.target.set(0, 1.5, 3); controls.update();
for (var n = 1; n <= 31; n++) rueda(-100);
print('pegado al fondo: cam z=' + camera.position.z.toFixed(2) + ' d=' + camera.position.distanceTo(controls.target).toFixed(2));
var out = [];
for (var n = 1; n <= 12; n++){ rueda(100); out.push(n + ': cam z=' + camera.position.z.toFixed(2) + ' tgt z=' + controls.target.z.toFixed(2) + ' d=' + camera.position.distanceTo(controls.target).toFixed(2)); }
print(out.join('\n'));
