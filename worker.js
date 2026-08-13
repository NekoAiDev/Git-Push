// Cloudflare Worker：install.nekoaidev.top 分发 GitPush
// 内容源跟随 GitHub main 分支，自动最新，零文件维护。
// 部署：Cloudflare 后台「Workers」→ 创建 Worker → 粘贴本文件 → 部署 → 绑自定义域 install.nekoaidev.top
//
// 说明：
// - 根路径 /           → 显示下载落地页（内嵌 HTML）
// - /gitpush.exe       → 流式代理上游 exe（cacheTtl=300，5 分钟边缘缓存，兼顾速度与新版本生效）
// - /GitPush_Setup.exe → 流式代理上游安装包（cacheTtl=300）
// - /version.json /update.zip → 更新系统用（cacheTtl=0，不缓存，确保永远拿到最新版）
// - 上游使用 GitHub raw（raw.githubusercontent.com），内容跟随 main 分支自动更新
//   注：jsDelivr 对 .exe 二进制文件返回 403，因此不采用 jsDelivr 作为 exe 分发源
// - 若将来 exe 体积变得很大（>50MB）触发 Worker 响应限制，可把代理分支改成 302 重定向到 UPSTREAM

const GITHUB_OWNER = "NekoAiDev";
const GITHUB_REPO = "Git-Push";
const UPSTREAM = "https://raw.githubusercontent.com/NekoAiDev/Git-Push/main/dist/GitPush.exe";
// 安装包（25MB+）经 Worker 流式代理：用流式响应绕过 Worker 大响应体缓冲上限，走 Cloudflare 网络比直连 raw.githubusercontent.com 更快
const INSTALLER_UPSTREAM = "https://raw.githubusercontent.com/NekoAiDev/Git-Push/main/GitPush_Setup.exe";

// 后台鉴权
const ADMIN_PWD = "mw41KUHH65WCIEcqsPoy";
const SESSION_SECRET = "ec419e1cd1970dc5cf2fb55fbfd7a5a06c1053aa4ae16334c13a2696bc3ee9fb"; // 仅用于 HMAC 签名登录会话 Cookie，非密码
const SESSION_COOKIE = "gp_sid";

const LANDING = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Git-Push 下载</title>
<style>
  :root{ --git-orange:#FF6B3D; --git-orange-dark:#D73219; }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{
    font-family:"Segoe UI","Microsoft YaHei UI",sans-serif;
    background:linear-gradient(135deg,#FFF3ED 0%,#FFE6DA 100%);
    color:#2b2b2b;min-height:100vh;
    display:flex;align-items:center;justify-content:center;padding:24px;
  }
  .card{
    background:#fff;border-radius:18px;
    box-shadow:0 18px 50px rgba(215,50,25,.18);
    padding:48px 44px;max-width:520px;width:100%;text-align:center;
  }
  .badge{
    display:inline-flex;align-items:center;gap:10px;
    background:linear-gradient(135deg,var(--git-orange),var(--git-orange-dark));
    color:#fff;border-radius:14px;padding:16px 18px;margin-bottom:26px;
    box-shadow:0 8px 20px rgba(215,50,25,.35);
  }
  .badge svg{width:34px;height:34px;flex:none;}
  .badge .t{text-align:left;line-height:1.25;}
  .badge .t b{font-size:18px;display:block;}
  .badge .t span{font-size:12px;opacity:.9;}
  h1{font-size:24px;margin-bottom:10px;}
  p.desc{color:#666;font-size:14px;line-height:1.7;margin-bottom:28px;}
  .btn{
    display:inline-block;text-decoration:none;
    background:linear-gradient(135deg,var(--git-orange),var(--git-orange-dark));
    color:#fff;font-size:17px;font-weight:600;
    padding:15px 38px;border-radius:12px;
    box-shadow:0 10px 24px rgba(215,50,25,.35);
    transition:transform .12s ease,box-shadow .12s ease;
  }
  .btn:hover{transform:translateY(-2px);box-shadow:0 14px 30px rgba(215,50,25,.42);}
  .btn:active{transform:translateY(0);}
  .meta{margin-top:26px;font-size:12.5px;color:#999;line-height:1.8;border-top:1px solid #f0f0f0;padding-top:18px;}
  .meta code{background:#f6f6f6;padding:2px 7px;border-radius:6px;color:var(--git-orange-dark);font-size:12px;word-break:break-all;}
  .alt{margin-top:14px;font-size:12.5px;color:#888;}
  .alt a{color:#1a73e8;text-decoration:none;}
  .alt a:hover{text-decoration:underline;}
</style>
</head>
<body>
  <div class="card">
    <div class="badge">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="6" cy="6" r="2.4" fill="#fff"/>
        <circle cx="6" cy="18" r="2.4" fill="#fff"/>
        <circle cx="18" cy="9" r="2.4" fill="#fff"/>
        <path d="M6 8.4V15.6" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M6 6 L16 8.2" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M14 4 L18 8 L14 12" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="t"><b>Git-Push</b><span>图形化 Git 推送工具 · Windows</span></div>
    </div>
    <h1>下载 Git-Push 安装包</h1>
    <p class="desc">
      推荐：一键安装，自动配置证书、创建开始菜单与桌面快捷方式。<br>
      本页面经 Cloudflare Worker 提供，<br>
      始终分发 <strong>GitHub main 分支最新版</strong>。
    </p>
    <a class="btn" href="/GitPush_Setup.exe" download="GitPush_Setup.exe">⬇ 下载安装包（推荐）</a>
    <div class="meta">
      安装包直接链接（可放进网站 / 文档）：<br>
      <code>install.nekoaidev.top/GitPush_Setup.exe</code><br>
      免安装单文件版直接链接：<br>
      <code>install.nekoaidev.top/gitpush.exe</code>
    </div>
    <div class="alt">
      不想安装？<a href="/gitpush.exe" download="GitPush.exe">下载免安装单文件版 GitPush.exe</a>
    </div>
  </div>
</body>
</html>`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const p = url.pathname.toLowerCase();

    // 1) 根路径 / 或 /index.html → 内嵌下载落地页
    if (p === "/" || p === "/index.html") {
      return new Response(LANDING, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "public, max-age=300",
        },
      });
    }

    // 2) /gitpush.exe → 流式代理上游 exe（始终最新）
    if (p === "/gitpush.exe" || p === "/gitpush.exe/") {
      // 带上常见浏览器 UA，避免 GitHub raw 把 Worker 请求当机器人拦截
      const upstreamReq = new Request(UPSTREAM, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0",
          "Accept": "application/octet-stream,*/*",
        },
      });
      const upstreamResp = await fetch(upstreamReq, { cf: { cacheTtl: 300 } });

      // 上游异常时，让浏览器直接跳去 GitHub raw（通常不会被浏览器拦截）
      if (!upstreamResp.ok) {
        return Response.redirect(UPSTREAM, 302);
      }

      const headers = new Headers(upstreamResp.headers);
      headers.set("Content-Disposition", 'attachment; filename="GitPush.exe"');
      headers.set("Content-Type", "application/octet-stream");
      headers.set("Cache-Control", "public, max-age=300");
      // 去掉上游可能带来的、会干扰下载的编码头
      headers.delete("content-encoding");
      headers.delete("content-length");
      return new Response(upstreamResp.body, { status: 200, headers });
    }

    // 2.2) /GitPush_Setup.exe → 流式代理安装包（25MB+，用流式响应绕过 Worker 大响应体缓冲上限，走 Cloudflare 网络更快）
    if (p === "/gitpush_setup.exe" || p === "/gitpush_setup.exe/") {
      const upstreamReq = new Request(INSTALLER_UPSTREAM, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0",
          "Accept": "application/octet-stream,*/*",
        },
      });
      const upstreamResp = await fetch(upstreamReq, { cf: { cacheTtl: 300 } });
      if (!upstreamResp.ok) {
        return Response.redirect(INSTALLER_UPSTREAM, 302);
      }
      const headers = new Headers(upstreamResp.headers);
      headers.set("Content-Disposition", 'attachment; filename="GitPush_Setup.exe"');
      headers.set("Content-Type", "application/octet-stream");
      headers.set("Cache-Control", "public, max-age=300");
      headers.delete("content-encoding");
      headers.delete("content-length");
      return new Response(upstreamResp.body, { status: 200, headers });
    }

    // 2.5) /version.json 与 /update.zip → 代理 GitHub raw（更新系统用，不缓存）
    if (p === "/version.json" || p === "/update.zip") {
      const rawFile = p === "/version.json" ? "version.json" : "dist/update.zip";
      const rawUrl = `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/main/${rawFile}`;
      const upstreamResp = await fetch(
        new Request(rawUrl, { headers: { "User-Agent": "Mozilla/5.0", "Accept": "*/*" } }),
        { cf: { cacheTtl: 0 } }
      );
      if (!upstreamResp.ok) {
        return Response.redirect(rawUrl, 302);
      }
      const headers = new Headers(upstreamResp.headers);
      headers.set("Content-Type", p === "/version.json" ? "application/json" : "application/octet-stream");
      headers.set("Cache-Control", "public, max-age=60");
      headers.delete("content-encoding");
      headers.delete("content-length");
      return new Response(upstreamResp.body, { status: 200, headers });
    }

    // 2.6) POST /api/report → 接收匿名统计并写入 KV（仅收集合法匿名数据）
    if (p === "/api/report" && request.method === "POST") {
      try {
        const raw = await request.text();
        let d;
        try { d = JSON.parse(raw); } catch (e) { return new Response("bad json", { status: 400 }); }
        const uuid = String(d.uuid || "").slice(0, 64);
        if (!uuid) return new Response("bad uuid", { status: 400 });
        const event = String(d.event || "");
        if (!["push", "update", "session_end"].includes(event)) return new Response("bad event", { status: 400 });
        const version = String(d.version || "").slice(0, 32);
        const push_count = Math.max(0, parseInt(d.push_count) || 0);
        const update_count = Math.max(0, parseInt(d.update_count) || 0);
        const session_ms = Math.max(0, parseInt(d.session_ms) || 0);
        const ts = parseInt(d.ts) || Date.now();
        const hostname = String(d.hostname || "").slice(0, 64);
        const os_version = String(d.os_version || "").slice(0, 64);
        const username = String(d.username || "").slice(0, 64);

        // 每个匿名设备一条记录
        const ukey = "u:" + uuid;
        let u = {};
        try { u = await env.GP_STATS.get(ukey, { type: "json" }) || {}; } catch (e) {}
        u.push_count = Math.max(u.push_count || 0, push_count);
        u.update_count = Math.max(u.update_count || 0, update_count);
        if (event === "session_end") u.sessions = (u.sessions || 0) + 1;
        u.version = version || u.version || "未知";
        u.last_seen = ts;
        if (!u.first_seen) u.first_seen = ts;
        if (hostname) u.hostname = hostname;
        if (os_version) u.os_version = os_version;
        if (username) u.username = username;
        await env.GP_STATS.put(ukey, JSON.stringify(u));

        // 全局汇总（累加增量，低频统计竞态可忽略）
        let g = {};
        try { g = await env.GP_STATS.get("g", { type: "json" }) || {}; } catch (e) {}
        g.total_push = (g.total_push || 0) + (event === "push" ? 1 : 0);
        g.total_update = (g.total_update || 0) + (event === "update" ? 1 : 0);
        g.total_sessions = (g.total_sessions || 0) + (event === "session_end" ? 1 : 0);
        g.last_report = ts;
        await env.GP_STATS.put("g", JSON.stringify(g));

        return new Response(JSON.stringify({ ok: true }), {
          headers: { "Content-Type": "application/json" },
        });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: String(e) }), {
          status: 500, headers: { "Content-Type": "application/json" },
        });
      }
    }

    // 2.7) 后台：密码登录 + 签名会话 Cookie（刷新/重开浏览器在有效期内免输密码）
    // 2.7.1) 退出登录
    if (p === "/admin/logout") {
      const headers = new Headers({ "Location": "/admin" });
      headers.append("Set-Cookie",
        `${SESSION_COOKIE}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`);
      return new Response(null, { status: 302, headers });
    }

    // 2.7.2) POST /admin/login → 校验密码并下发会话 Cookie
    if (p === "/admin/login" && request.method === "POST") {
      let fail = {};
      try { fail = JSON.parse(await env.GP_STATS.get("admin_fail") || "{}"); } catch (e) {}
      if ((fail.count || 0) >= 5 && (Date.now() - (fail.ts || 0)) < 15 * 60 * 1000) {
        return new Response(adminLoginHtml("尝试次数过多，请 15 分钟后再试", true), {
          headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
        });
      }
      let pwd = "", remember = false;
      try {
        const form = await request.formData();
        pwd = String(form.get("pwd") || "");
        remember = form.get("remember") === "1" || form.get("remember") === "on";
      } catch (e) {}
      if (pwd !== ADMIN_PWD) {
        fail.count = (fail.count || 0) + 1;
        fail.ts = Date.now();
        try { await env.GP_STATS.put("admin_fail", JSON.stringify(fail)); } catch (e) {}
        const left = Math.max(0, 5 - fail.count);
        return new Response(adminLoginHtml(left > 0 ? `密码错误，还可尝试 ${left} 次` : "密码错误", true), {
          headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" }, status: 401,
        });
      }
      try { await env.GP_STATS.put("admin_fail", JSON.stringify({ count: 0, ts: 0 })); } catch (e) {}
      const maxAge = remember ? 30 * 24 * 3600 : 7 * 24 * 3600;
      const token = await makeSessionToken(Date.now() + maxAge * 1000);
      const headers = new Headers({ "Location": "/admin" });
      headers.append("Set-Cookie",
        `${SESSION_COOKIE}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`);
      return new Response(null, { status: 302, headers });
    }

    // 2.7.3) GET /admin → 面板（校验会话 Cookie；兼容旧书签 ?pwd=）
    if (p === "/admin") {
      const cookieHeader = request.headers.get("Cookie") || "";
      const token = parseCookie(cookieHeader, SESSION_COOKIE);
      const authed = token ? await verifySessionToken(token) : false;

      // 兼容旧书签：?pwd= 也能登录，并顺带下发会话 Cookie
      let authedByPwd = false;
      const pwd = url.searchParams.get("pwd") || "";
      if (!authed && pwd && pwd === ADMIN_PWD) authedByPwd = true;

      if (!authed && !authedByPwd) {
        let fail = {};
        try { fail = JSON.parse(await env.GP_STATS.get("admin_fail") || "{}"); } catch (e) {}
        if ((fail.count || 0) >= 5 && (Date.now() - (fail.ts || 0)) < 15 * 60 * 1000) {
          return new Response("尝试次数过多，请 15 分钟后再试", {
            headers: { "Content-Type": "text/plain; charset=utf-8" }, status: 429,
          });
        }
        return new Response(adminLoginHtml("", false), {
          headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" }, status: 200,
        });
      }

      // 通过认证：重置失败计数
      try { await env.GP_STATS.put("admin_fail", JSON.stringify({ count: 0, ts: 0 })); } catch (e) {}

      const panelResp = await buildAdminPanel(env);
      panelResp.headers.set("Cache-Control", "no-store");
      // 若是用旧 ?pwd= 进来的，补发会话 Cookie，之后刷新不再要密码
      if (authedByPwd && !authed) {
        const maxAge = 7 * 24 * 3600;
        const newToken = await makeSessionToken(Date.now() + maxAge * 1000);
        panelResp.headers.append("Set-Cookie",
          `${SESSION_COOKIE}=${newToken}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`);
      }
      return panelResp;
    }

    // 3) 其他 → 404
    return new Response("Not Found", { status: 404 });
  },
};

// ---- 会话签名辅助 ----
function parseCookie(header, name) {
  if (!header) return "";
  for (const part of header.split(";")) {
    const idx = part.indexOf("=");
    if (idx < 0) continue;
    const k = part.slice(0, idx).trim();
    const v = part.slice(idx + 1).trim();
    if (k === name) return decodeURIComponent(v);
  }
  return "";
}
function b64urlEncode(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlDecode(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = atob(s);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}
async function hmacHex(message, secret) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return Array.from(new Uint8Array(sig)).map((b) => b.toString(16).padStart(2, "0")).join("");
}
async function makeSessionToken(expiryMs) {
  const body = b64urlEncode(JSON.stringify({ e: expiryMs }));
  const sig = await hmacHex(body, SESSION_SECRET);
  return body + "." + sig;
}
async function verifySessionToken(token) {
  if (!token || typeof token !== "string" || !token.includes(".")) return false;
  const idx = token.lastIndexOf(".");
  const body = token.slice(0, idx);
  const sig = token.slice(idx + 1);
  const expected = await hmacHex(body, SESSION_SECRET);
  if (sig !== expected) return false;
  try {
    const payload = JSON.parse(b64urlDecode(body));
    return (payload.e || 0) > Date.now();
  } catch (e) {
    return false;
  }
}

// ---- 后台面板辅助函数 ----
function adminLoginHtml(msg, isError) {
  const tip = msg ? `<p style="color:#c0392b;margin:0 0 14px;font-size:14px">${msg}</p>` : "";
  return `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>GitPush 后台</title>
  <style>body{font-family:"Microsoft YaHei",sans-serif;background:#f4f6f9;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
  .box{background:#fff;padding:32px 40px;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.08);text-align:center;width:300px}
  input[type=password]{padding:10px 14px;font-size:15px;border:1px solid #ccc;border-radius:8px;width:100%;box-sizing:border-box}
  label{display:flex;align-items:center;gap:6px;margin-top:14px;font-size:13px;color:#666;justify-content:center}
  button{margin-top:18px;padding:10px 26px;font-size:15px;border:none;border-radius:8px;background:#FF6B3D;color:#fff;cursor:pointer;width:100%}
  h2{margin:0 0 18px;color:#333}</style></head>
  <body><div class="box"><h2>GitPush 数据后台</h2>
  ${tip}
  <form method="post" action="/admin/login"><input type="password" name="pwd" placeholder="请输入后台密码" autofocus>
  <label><input type="checkbox" name="remember" value="1"> 记住我（30 天内免登录）</label>
  <button type="submit">进入</button></form></div></body></html>`;
}

async function buildAdminPanel(env) {
  let g = {};
  try { g = await env.GP_STATS.get("g", { type: "json" }) || {}; } catch (e) {}
  let users = [];
  try {
    const list = await env.GP_STATS.list({ prefix: "u:" });
    for (const k of list.keys) {
      try {
        const u = await env.GP_STATS.get(k.name, { type: "json" });
        if (u) users.push(u);
      } catch (e) {}
    }
  } catch (e) {}
  const now = Date.now();
  const day = 86400000;
  const ONLINE_MS = 5 * 60 * 1000; // 5 分钟内视为在线
  const onlineUsers = users.filter((u) => ((u.last_seen || 0) * 1000) > now - ONLINE_MS);
  const activeToday = users.filter((u) => ((u.last_seen || 0) * 1000) > now - day).length;
  const active7 = users.filter((u) => ((u.last_seen || 0) * 1000) > now - 7 * day).length;
  const verMap = {};
  for (const u of onlineUsers) { const v = u.version || "未知"; verMap[v] = (verMap[v] || 0) + 1; }
  const verDist = Object.entries(verMap).map(([v, c]) => `${v}: ${c}`).join("，") || "暂无";
  return new Response(adminPanelHtml(g, onlineUsers, activeToday, active7, verDist), {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

function adminPanelHtml(g, onlineUsers, activeToday, active7, verDist) {
  const num = (n) => (n || 0).toLocaleString("zh-CN");
  const last = g.last_report ? new Date(g.last_report * 1000).toLocaleString("zh-CN") : "暂无";
  const rows = onlineUsers.map((u, i) => {
    const seen = u.last_seen ? new Date(u.last_seen * 1000).toLocaleString("zh-CN") : "-";
    const name = u.hostname || `设备 ${i + 1}`;
    const os = u.os_version || "-";
    const usr = u.username || "-";
    const ver = u.version || "未知";
    const push = num(u.push_count);
    const upd = num(u.update_count);
    return `<tr><td>${name}</td><td>${os}</td><td>${usr}</td><td>${ver}</td><td>${seen}</td><td>${push}</td><td>${upd}</td></tr>`;
  }).join("");
  const table = rows ? `<table class="dev-table"><thead><tr><th>计算机名</th><th>系统版本</th><th>用户名</th><th>工具版本</th><th>最近上报</th><th>推送</th><th>更新</th></tr></thead><tbody>${rows}</tbody></table>` : `<p class="empty">当前没有在线设备</p>`;
  return `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>GitPush 数据后台</title>
  <style>body{font-family:"Microsoft YaHei",sans-serif;background:#f4f6f9;margin:0;padding:32px;color:#222}
  h1{font-size:22px;margin:0 0 20px;display:flex;align-items:center;justify-content:space-between}
  .logout{font-size:13px;background:#fff;border:1px solid #ddd;color:#666;padding:8px 14px;border-radius:8px;text-decoration:none}
  .logout:hover{background:#f0f0f0}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}
  .card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 6px 20px rgba(0,0,0,.06)}
  .card .k{font-size:13px;color:#888}.card .v{font-size:28px;font-weight:700;margin-top:6px;color:#FF6B3D}
  .section{margin-top:32px;background:#fff;border-radius:12px;padding:20px;box-shadow:0 6px 20px rgba(0,0,0,.06)}
  .section h2{font-size:18px;margin:0 0 16px}
  .dev-table{width:100%;border-collapse:collapse;font-size:14px}
  .dev-table th,.dev-table td{padding:12px 10px;text-align:left;border-bottom:1px solid #eee}
  .dev-table th{color:#888;font-weight:600;background:#fafafa}
  .dev-table tr:hover{background:#f9f9f9}
  .status{display:inline-block;width:8px;height:8px;border-radius:50%;background:#2ecc71;margin-right:6px}
  .empty{color:#999;padding:20px 0}
  .meta{margin-top:24px;font-size:13px;color:#666;line-height:1.8}
  a{color:#1a73e8;text-decoration:none}</style></head>
  <body><h1>GitPush 匿名数据统计后台<a class="logout" href="/admin/logout">退出登录</a></h1>
  <div class="grid">
    <div class="card"><div class="k">累计推送次数</div><div class="v">${num(g.total_push)}</div></div>
    <div class="card"><div class="k">累计更新次数</div><div class="v">${num(g.total_update)}</div></div>
    <div class="card"><div class="k">累计会话数</div><div class="v">${num(g.total_sessions)}</div></div>
    <div class="card"><div class="k">当前在线设备</div><div class="v">${num(onlineUsers.length)}</div></div>
    <div class="card"><div class="k">今日活跃</div><div class="v">${num(activeToday)}</div></div>
    <div class="card"><div class="k">近7日活跃</div><div class="v">${num(active7)}</div></div>
  </div>
  <div class="section">
    <h2><span class="status"></span>在线设备列表</h2>
    ${table}
  </div>
  <div class="meta">版本分布（在线）：${verDist}<br>最近一次上报：${last}<br>
  在线判定：最近 5 分钟内有上报的设备，超时未上报自动下线不显示。<br>
  安全说明：登录后通过 HMAC 签名的会话 Cookie 保持登录（默认 7 天，勾选"记住我"为 30 天），刷新或重开浏览器在有效期内均无需重新输入密码；后台绝不记录密码（admin_fail 仅记录登录失败次数用于防爆破）。<br>
  <a href="/admin">刷新</a></div></body></html>`;
}
