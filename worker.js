// Cloudflare Worker：install.nekoaidev.top 分发 GitPush + 轻量匿名设备统计后台
// 内容源跟随 GitHub main 分支，自动最新，零文件维护。
// 部署：wrangler deploy（本目录 wrangler.toml 已绑定自定义域 install.nekoaidev.top）
//
// 说明：
// - 根路径 /           → 显示下载落地页（内嵌 HTML，含 Cloudflare Web Analytics 匿名访问统计）
// - /gitpush.exe       → 流式代理上游 exe（cacheTtl=300，5 分钟边缘缓存）
// - /GitPush_Setup.exe → 流式代理上游安装包（cacheTtl=300）
// - /version.json /update.zip → 更新系统用（cacheTtl=0，不缓存，确保永远最新）
// - /api/report        → 工具端匿名统计上报（只含版本、地区、设备名等，不含密码/文件/仓库）
// - /admin             → 公开只读在线设备列表（无密码，因主人厌恶输密码；展示匿名 UUID/IP/地区/版本）
// - IP 地区解析走 ipinfo.io（Worker 内调用第三方 API），实时查询不再缓存（避免 IPv6 等定位漂移被旧结果锁定）

const GITHUB_OWNER = "NekoAiDev";
const GITHUB_REPO = "Git-Push";
const UPSTREAM = "https://raw.githubusercontent.com/NekoAiDev/Git-Push/main/dist/GitPush.exe";
const INSTALLER_UPSTREAM = "https://raw.githubusercontent.com/NekoAiDev/Git-Push/main/GitPush_Setup.exe";

// Cloudflare Web Analytics 站点 token（匿名访问统计，无 Cookie、不收集个人数据）
const WEB_ANALYTICS_TOKEN = "7bfb6ed22436465681c9d445e6775d77";

// ipinfo.io token（可选）。主人可在 ipinfo.io 注册免费账号获取；留空则走免费无 token 接口，限流 1 req/sec/IP
const IPINFO_TOKEN = "";

// 中文省份映射（ipinfo.io 对国内 IP 返回英文 region，需要转中文）
const REGION_EN_TO_CN = {
  "Beijing": "北京", "Tianjin": "天津", "Hebei": "河北", "Shanxi": "山西",
  "Inner Mongolia": "内蒙古", "Liaoning": "辽宁", "Jilin": "吉林",
  "Heilongjiang": "黑龙江", "Shanghai": "上海", "Jiangsu": "江苏",
  "Zhejiang": "浙江", "Anhui": "安徽", "Fujian": "福建", "Jiangxi": "江西",
  "Shandong": "山东", "Henan": "河南", "Hubei": "湖北", "Hunan": "湖南",
  "Guangdong": "广东", "Guangxi": "广西", "Hainan": "海南", "Chongqing": "重庆",
  "Sichuan": "四川", "Guizhou": "贵州", "Yunnan": "云南", "Tibet": "西藏",
  "Shaanxi": "陕西", "Gansu": "甘肃", "Qinghai": "青海", "Ningxia": "宁夏",
  "Xinjiang": "新疆", "Hong Kong": "香港", "Macao": "澳门", "Taiwan": "台湾",
  "Macau": "澳门"
};

function webAnalyticsScript() {
  if (!WEB_ANALYTICS_TOKEN) return "";
  return `<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token":"${WEB_ANALYTICS_TOKEN}"}'></script>`;
}

// 取客户端真实 IP
function getClientIP(request) {
  return (
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim() ||
    "unknown"
  );
}

// 调用 ipinfo.io 解析 IP 地区（Worker 内调用第三方 API，实时查询不缓存）
async function getIpInfo(ip, env) {
  if (!ip || ip === "unknown") return null;
  const url = IPINFO_TOKEN
    ? `https://ipinfo.io/${ip}/json?token=${IPINFO_TOKEN}`
    : `https://ipinfo.io/${ip}/json`;

  try {
    const resp = await fetch(url, {
      headers: { "Accept": "application/json" },
      cf: { cacheTtl: 0 }
    });
    if (!resp.ok) return null;
    return await resp.json();
  } catch (e) {
    return null;
  }
}

// 归一化地区：英文 region 转中文，未命中则保留原文
function normalizeRegion(region) {
  if (!region) return "";
  const trimmed = region.trim();
  return REGION_EN_TO_CN[trimmed] || trimmed;
}

// 综合拿地区信息：优先用户手动 region_user，否则 ipinfo.io 估算
async function getClientLocation(ip, regionUser, env) {
  if (regionUser && regionUser.trim()) {
    return { ip, country: "CN", region: regionUser.trim(), city: "", location: `${regionUser.trim()}（手动）` };
  }
  const info = await getIpInfo(ip, env);
  if (!info) {
    return { ip, country: "", region: "", city: "", location: "未知" };
  }
  const country = info.country || "";
  const region = normalizeRegion(info.region);
  const city = info.city || "";
  let location = region;
  if (city && city !== region) location += ` ${city}`;
  if (!location) location = country || "未知";
  location += "（ipinfo.io）";
  return { ip, country, region, city, location };
}

// 读取所有设备记录
async function listDevices(env) {
  const devices = [];
  try {
    const list = await env.GP_STATS?.list({ prefix: "u:" });
    if (!list || !list.keys) return devices;
    for (const k of list.keys) {
      try {
        const val = await env.GP_STATS?.get(k.name);
        if (val) devices.push(JSON.parse(val));
      } catch (e) {
        // ignore
      }
    }
  } catch (e) {
    // ignore
  }
  return devices;
}

// 后台 HTML（公开只读，无密码）
function adminPanelHtml(devices) {
  const now = Math.floor(Date.now() / 1000);
  const online = devices.filter(d => d.last_seen && now - d.last_seen < 300).length;
  const rows = devices
    .sort((a, b) => (b.last_seen || 0) - (a.last_seen || 0))
    .map(d => {
      const isOnline = d.last_seen && now - d.last_seen < 300;
      const status = isOnline ? '<span style="color:#22c55e;font-weight:600">在线</span>' : '<span style="color:#9ca3af">离线</span>';
      const lastSeen = d.last_seen ? new Date(d.last_seen * 1000).toLocaleString("zh-CN") : "-";
      const locRaw = d.location || "未知";
      const isManual = locRaw.includes("（手动）");
      const loc = isManual
        ? `${locRaw.replace("（手动）", "")}<span class="tag-manual">手动</span>`
        : locRaw;
      return `<tr>
        <td>${d.uuid?.slice(0, 8) || "-"}</td>
        <td>${d.hostname || "-"}</td>
        <td>${d.os_version || "-"}</td>
        <td>${d.version || "-"}</td>
        <td>${d.ip || "-"}</td>
        <td>${loc}</td>
        <td>${d.push_count || 0}</td>
        <td>${d.update_count || 0}</td>
        <td>${status}</td>
        <td>${lastSeen}</td>
      </tr>`;
    }).join("");

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Git-Push 在线设备</title>
<style>
  body{font-family:"Segoe UI","Microsoft YaHei UI",sans-serif;background:#f6f7f9;color:#1f2937;padding:24px;}
  .wrap{max-width:1400px;margin:0 auto;background:#fff;border-radius:16px;padding:28px;box-shadow:0 8px 30px rgba(0,0,0,.06);}
  h1{margin:0 0 8px;font-size:22px;}
  .stats{display:flex;gap:18px;margin:18px 0;}
  .stat{background:#f3f4f6;border-radius:10px;padding:14px 18px;min-width:120px;}
  .stat b{font-size:20px;display:block;color:#ea4c36;}
  .stat span{font-size:12px;color:#6b7280;}
  table{width:100%;border-collapse:collapse;margin-top:12px;font-size:13px;}
  th{background:#f9fafb;padding:10px;text-align:left;border-bottom:2px solid #e5e7eb;}
  td{padding:10px;border-bottom:1px solid #f0f0f0;}
  tr:hover{background:#fafafa;}
  .small{color:#9ca3af;font-size:12px;margin-top:8px;}
  .notice{background:#fff7ed;border:1px solid #fdba74;color:#9a3412;border-radius:10px;padding:12px 16px;font-size:13px;line-height:1.6;margin:14px 0 4px;}
  .notice b{color:#c2410c;}
  .tag-manual{display:inline-block;background:#dcfce7;color:#166534;border-radius:6px;padding:1px 6px;font-size:11px;margin-left:4px;}
</style>
</head>
<body>
<div class="wrap">
  <h1>Git-Push 在线设备面板</h1>
  <div class="notice">
    ⚠️ <b>IP 定位仅供参考</b>：地区由 ipinfo.io 按 IP 估算，可能不准确（尤其 IPv6 地址）。
    以工具内 <b>设置 → 隐私与统计 → 所在地区</b> 手动选择为准；手动选择会优先显示并标注「手动」。
  </div>
  <div class="stats">
    <div class="stat"><b>${devices.length}</b><span>总设备</span></div>
    <div class="stat"><b>${online}</b><span>当前在线（5 分钟内）</span></div>
  </div>
  <table>
    <thead>
      <tr>
        <th>UUID</th>
        <th>计算机名</th>
        <th>系统</th>
        <th>版本</th>
        <th>IP</th>
        <th>地区</th>
        <th>推送</th>
        <th>更新</th>
        <th>状态</th>
        <th>最近上报</th>
      </tr>
    </thead>
    <tbody>
      ${rows || '<tr><td colspan="10" style="text-align:center;color:#9ca3af;padding:24px">暂无数据</td></tr>'}
    </tbody>
  </table>
  <p class="small">IP 地区由 ipinfo.io 实时解析（仅供参考，可能不准）；工具内手动选择的地区优先显示并标注「手动」。本面板公开只读，不记录密码。</p>
</div>
</body>
</html>`;
}

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
  ${webAnalyticsScript()}
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

    // 2) /api/report → 匿名统计上报
    if (p === "/api/report") {
      if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
      }
      try {
        const payload = await request.json();
        const ip = getClientIP(request);
        const regionUser = (payload.region_user || "").trim();
        const loc = await getClientLocation(ip, regionUser, env);

        const uuid = payload.uuid || "anon";
        const key = `u:${uuid}`;
        let record = {};
        try {
          const existing = await env.GP_STATS?.get(key);
          if (existing) record = JSON.parse(existing);
        } catch (e) {
          // ignore
        }

        record.uuid = uuid;
        record.version = payload.version || record.version || "";
        record.hostname = payload.hostname || record.hostname || "";
        record.os_version = payload.os_version || record.os_version || "";
        record.username = payload.username || record.username || "";
        record.region_user = regionUser || record.region_user || "";
        record.ip = loc.ip;
        record.country = loc.country;
        record.region = loc.region;
        record.city = loc.city;
        record.location = loc.location;

        const event = payload.event;
        if (event === "push") {
          record.push_count = (record.push_count || 0) + 1;
        } else if (event === "update") {
          record.update_count = (record.update_count || 0) + 1;
        }
        record.last_seen = Math.floor(Date.now() / 1000);

        await env.GP_STATS?.put(key, JSON.stringify(record));
        return new Response(JSON.stringify({ ok: true, location: loc.location }), {
          headers: { "Content-Type": "application/json; charset=utf-8" },
        });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: e.message }), {
          status: 500,
          headers: { "Content-Type": "application/json" },
        });
      }
    }

    // 3) /admin → 公开只读在线设备面板（无密码）
    if (p === "/admin") {
      const devices = await listDevices(env);
      return new Response(adminPanelHtml(devices), {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }

    // 4) /gitpush.exe → 流式代理上游 exe
    if (p === "/gitpush.exe" || p === "/gitpush.exe/") {
      const upstreamReq = new Request(UPSTREAM, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0",
          "Accept": "application/octet-stream,*/*",
        },
      });
      const upstreamResp = await fetch(upstreamReq, { cf: { cacheTtl: 300 } });
      if (!upstreamResp.ok) {
        return Response.redirect(UPSTREAM, 302);
      }
      const headers = new Headers(upstreamResp.headers);
      headers.set("Content-Disposition", 'attachment; filename="GitPush.exe"');
      headers.set("Content-Type", "application/octet-stream");
      headers.set("Cache-Control", "public, max-age=300");
      headers.delete("content-encoding");
      headers.delete("content-length");
      return new Response(upstreamResp.body, { status: 200, headers });
    }

    // 5) /GitPush_Setup.exe → 流式代理安装包
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

    // 6) /version.json 与 /update.zip → 代理 GitHub raw（不缓存）
    if (p === "/version.json" || p === "/update.zip") {
      const rawFile = p === "/version.json" ? "version.json" : "dist/update.zip";
      // 追加时间戳强制绕过 GitHub raw (fastly) 的边缘缓存，确保每次拿到最新文件
      const rawUrl = `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/main/${rawFile}?t=${Date.now()}`;
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

    // 7) 其他 → 404
    return new Response("Not Found", { status: 404 });
  },
};
