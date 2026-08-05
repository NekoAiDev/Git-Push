// Cloudflare Worker：install.nekoaidev.top 分发 GitPush
// 内容源跟随 GitHub main 分支，自动最新，零文件维护。
// 部署：Cloudflare 后台「Workers」→ 创建 Worker → 粘贴本文件 → 部署 → 绑自定义域 install.nekoaidev.top
//
// 说明：
// - 根路径 /           → 显示下载落地页（内嵌 HTML）
// - /gitpush.exe       → 流式代理上游 exe（cacheTtl=300，5 分钟边缘缓存，兼顾速度与新版本生效）
// - /GitPush_Setup.exe → 流式代理上游安装包（cacheTtl=300）
// - /version.json /update.zip → 更新系统用（cacheTtl=300）
// - 上游使用 GitHub raw（raw.githubusercontent.com），内容跟随 main 分支自动更新
//   注：jsDelivr 对 .exe 二进制文件返回 403，因此不采用 jsDelivr 作为 exe 分发源
// - 若将来 exe 体积变得很大（>50MB）触发 Worker 响应限制，可把代理分支改成 302 重定向到 UPSTREAM

const GITHUB_OWNER = "NekoAiDev";
const GITHUB_REPO = "Git-Push";
const UPSTREAM = "https://raw.githubusercontent.com/NekoAiDev/Git-Push/main/dist/GitPush.exe";
// 安装包（25MB+）经 Worker 流式代理：用流式响应绕过 Worker 大响应体缓冲上限，走 Cloudflare 网络比直连 raw.githubusercontent.com 更快
const INSTALLER_UPSTREAM = "https://raw.githubusercontent.com/NekoAiDev/Git-Push/main/GitPush_Setup.exe";

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
  async fetch(request) {
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

    // 2.5) /version.json 与 /update.zip → 代理 GitHub raw（更新系统用）
    if (p === "/version.json" || p === "/update.zip") {
      const rawFile = p === "/version.json" ? "version.json" : "dist/update.zip";
      const rawUrl = `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/main/${rawFile}`;
      const upstreamResp = await fetch(
        new Request(rawUrl, { headers: { "User-Agent": "Mozilla/5.0", "Accept": "*/*" } }),
        { cf: { cacheTtl: 300 } }
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

    // 3) 其他 → 404
    return new Response("Not Found", { status: 404 });
  },
};
