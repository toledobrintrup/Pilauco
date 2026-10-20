// Revisión de textos en los dibujos SVG de una página (estudio.html, etc.): devuelve, por cada <svg>, los <text> que quedan fuera de su figura (CORTADO) o encima de otro texto (TRASLAPE), medidos en la página real.
// Uso: python3 -m http.server 8799 --bind 127.0.0.1 &  y luego  webshot "http://127.0.0.1:8799/estudio.html" salida.png 1000 700 7 "$(cat fuente/estudio/lint_textos_svg.js)"  (webshot: fuente/webshot.swift). Sin líneas CORTADO/TRASLAPE = limpio (Gabriel, 20-10-2026: "palabras que se traslapan, revisa todo").
(function(){
  const out=[]; document.querySelectorAll("nav,header").forEach(n=>n.style.display="none");
  document.querySelectorAll('svg').forEach((svg,fi)=>{
    const R=svg.getBoundingClientRect(); if(R.width<50||R.height<30) return; const id=svg.id||(svg.closest('section')||{}).id||('svg'+fi);
    const texts=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim()&&t.getClientRects().length).map(t=>{const b=t.getBoundingClientRect(); return {t:t.textContent.trim().slice(0,34), x0:b.left,y0:b.top,x1:b.right,y1:b.bottom};});
    let nclip=0, nover=0;
    texts.forEach(a=>{ if(a.x0<R.left-0.5||a.x1>R.right+0.5||a.y0<R.top-0.5||a.y1>R.bottom+0.5){ nclip++; if(nclip<=6) out.push(`${id} CORTADO "${a.t}"`); } });
    for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){const a=texts[i],b=texts[j]; const ox=Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0), oy=Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0); if(ox>1&&oy>1){ nover++; if(nover<=8) out.push(`${id} TRASLAPE "${a.t}" × "${b.t}" (${ox.toFixed(0)}x${oy.toFixed(0)}px)`);} }
    out.push(`${id}: ${texts.length} textos, ${nclip} cortados, ${nover} traslapes (${Math.round(R.width)}x${Math.round(R.height)})`);
  });
  return out.join('\n');
})()
