/* Research Atlas site navigation. Include with <script src="<root>/assets/nav.js" data-root="<root>" defer>.
   Content pages (body[data-nav=bar]) get a sticky top bar; full-screen tools get a small floating menu. */
(function () {
  const me = document.currentScript, root = (me && me.dataset.root) || ".";
  const R = p => (root.replace(/\/$/, "") + "/" + p).replace(/^\.\//, "./");
  const NAV = [
    ["00", "首页", ""],
    ["01", "多伦多大学", "uoft/"],
    ["02", "斯坦福大学", "stanford/"],
    ["03", "北美量化地图", "na-quantum-chem-map/"],
    ["04", "北美 Top 20", "top20/"],
    ["05", "中国量化地图", "cn-quantum-chem-map/"],
    ["06", "中美对比", "compare/"],
    ["07", "北美企业", "na-companies/"],
  ];
  const here = location.pathname.replace(/index\.html$/, "");
  const isCur = p => { const a = document.createElement("a"); a.href = R(p || "./"); const ap = a.pathname.replace(/index\.html$/, ""); return p ? here.startsWith(ap) : here === ap; };
  const css = `
  .ra-bar{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--paper,#f7f6f1) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line,#dedbd2);font-family:var(--body,system-ui)}
  .ra-bar .in{max-width:1160px;margin:0 auto;padding:0 20px;display:flex;align-items:center;gap:18px;height:52px}
  .ra-brand{font:900 16px var(--display,serif);color:var(--ink,#1d262c)!important;white-space:nowrap;letter-spacing:.02em}
  .ra-brand span{color:var(--accent,#1f5f8b)}
  .ra-links{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;flex:1}
  .ra-links::-webkit-scrollbar{display:none}
  .ra-links a{white-space:nowrap;font-size:13px;color:var(--ink-2,#48545c);padding:6px 10px;border-radius:6px;text-decoration:none}
  .ra-links a i{font:500 10.5px var(--mono,monospace);font-style:normal;color:var(--muted,#6b767d);margin-right:5px}
  .ra-links a:hover{background:var(--line-2,#ebe8df);text-decoration:none}
  .ra-links a[aria-current]{color:var(--accent,#1f5f8b);background:var(--accent-soft,#e4edf3)}
  .ra-theme{font:500 12px var(--body,system-ui);border:1px solid var(--line,#dedbd2);background:transparent;color:var(--ink,#1d262c);border-radius:6px;width:32px;height:30px;cursor:pointer;flex:none}
  .ra-fab{position:fixed;z-index:60;left:50%;transform:translateX(-50%);top:calc(10px + env(safe-area-inset-top,0px));font-family:var(--body,system-ui)}
  .ra-fab>button{font:500 12.5px var(--body,system-ui);border:1px solid var(--line,#d5dadd);background:var(--panel,rgba(250,250,247,.94));color:var(--ink,#1d262c);border-radius:99px;padding:5px 13px;cursor:pointer;backdrop-filter:blur(6px);box-shadow:0 2px 10px rgba(0,0,0,.08)}
  .ra-fab .menu{position:absolute;top:36px;left:50%;transform:translateX(-50%);background:var(--panel,#fbfaf6);border:1px solid var(--line,#d5dadd);border-radius:10px;padding:6px;min-width:200px;box-shadow:0 10px 30px rgba(0,0,0,.15);backdrop-filter:blur(8px)}
  .ra-fab .menu a{display:block;padding:7px 10px;border-radius:6px;font-size:13px;color:var(--ink,#1d262c);text-decoration:none}
  .ra-fab .menu a i{font:500 10.5px var(--mono,monospace);font-style:normal;color:var(--muted,#6b767d);margin-right:8px}
  .ra-fab .menu a:hover{background:rgba(127,127,127,.12)}
  .ra-fab .menu a[aria-current]{color:var(--accent,#1f5f8b)}
  .ra-fab.inline{position:relative;left:auto;top:auto;transform:none;z-index:60}.ra-fab.inline .menu{left:0;transform:none}
  @media (max-width:760px){.ra-fab:not(.inline){left:auto;right:auto;left:10px;transform:none}.ra-fab .menu{left:0;transform:none}}`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  const links = NAV.map(([no, nm, p]) => `<a href="${R(p || "./")}"${isCur(p) ? ' aria-current="page"' : ""}><i>${no}</i>${nm}</a>`).join("");
  function themeBtn() {
    const b = document.createElement("button"); b.className = "ra-theme"; b.setAttribute("aria-label", "切换深浅色");
    const cur = () => document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const paint = () => b.textContent = cur() === "dark" ? "浅" : "深";
    b.onclick = () => { const t = cur() === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = t; try { localStorage.setItem("ra-theme", t); } catch (e) {} paint(); };
    paint(); return b;
  }
  try { const t = localStorage.getItem("ra-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
  function mount() {
    if (document.body.dataset.nav === "bar") {
      const bar = document.createElement("nav"); bar.className = "ra-bar"; bar.setAttribute("aria-label", "站点导航");
      bar.innerHTML = `<div class="in"><a class="ra-brand" href="${R("./")}">中美<span>·</span>研究图谱</a><div class="ra-links">${links}</div></div>`;
      bar.querySelector(".in").appendChild(themeBtn());
      document.body.prepend(bar);
    } else {
      const f = document.createElement("div"); f.className = "ra-fab";
      f.innerHTML = `<button aria-expanded="false" aria-haspopup="true">☰ 研究图谱 · 导航</button><div class="menu" hidden>${links}</div>`;
      const b = f.querySelector("button"), m = f.querySelector(".menu");
      b.onclick = e => { e.stopPropagation(); m.hidden = !m.hidden; b.setAttribute("aria-expanded", !m.hidden); };
      document.addEventListener("click", () => { m.hidden = true; b.setAttribute("aria-expanded", "false"); });
      const hd = document.body.dataset.nav === "inline" && document.querySelector("header");
      if (hd) { f.classList.add("inline"); b.textContent = "☰ 研究图谱"; hd.prepend(f); } else document.body.appendChild(f);
    }
  }
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", mount) : mount();
})();
