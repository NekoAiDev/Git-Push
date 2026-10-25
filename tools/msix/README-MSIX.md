# GitPush 免费版 — MSIX 封装与上架提交指南 / MSIX Packaging & Store Submission Guide

> 适用：Microsoft Store 上架（Windows 桌面应用）
> 前置：PR #7 已合并，代码已含 `STORE_BUILD` 开关（程序目录存在 `STORE_BUILD.flag` 即视为 Store 版）

---

## 0. 先纠正一个误解：exe 你早就有了

仓库 `dist/GitPush.exe`（约 12 MB）就是 PyInstaller 打好的主程序。Microsoft Store **不接受 `.exe` 直接上传**，它只收打包格式 **`.msix`**。所以"找不到 exe"的真实含义是「找不到 Store 能收的格式」——解决方式是**把 exe 封进 MSIX**，再传 MSIX。

> 注意：仓库里的 `GitPush_Setup.exe` 是 Inno Setup 做的**安装器**（自托管分发用），也不能传 Store。Store 要的是**主程序 `GitPush.exe` 封成的 MSIX**。

---

## 1. 两条封装路径（任选其一）

### 路径 A · MSIX Packaging Tool（图形化，★ 强烈推荐，最不容易出错）

1. 在微软商店搜 **"MSIX Packaging Tool"** 免费安装。
2. 打开 → 选 **"Application"（应用程序）** 模式（不是"安装程序包"，因为 GitPush 是单文件 exe，无需安装）。
3. **选择包内的应用**：指向你本地的 `dist\GitPush.exe`。
4. 进入"包内容"编辑：
   - 确认 `GitPush.exe`、`appicon.ico` 在内。
   - **手动新增一个空文件 `STORE_BUILD.flag`**（右键/添加文件 → 新建空文本文件，命名为 `STORE_BUILD.flag`，内容留空）。**这一条必须做，否则 Store 版仍会从 install.nekoaidev.top 自下载 exe，审核必拒。**
5. **标识信息（Identity）**：从 Partner Center → 你的应用 → **"应用标识 / App identity"** 页面，把 **"程序包名称 / Package name"**（形如 `12345NekoAiDev.GitPush`）和 **"发布者 / Publisher"**（形如 `CN=...`）**原样复制**填进来。版本填 `1.4.4.0`。
6. **徽标 / assets**：工具会提示缺 png 徽标（44×44、150×150、310×150、StoreLogo）。用 `appicon.ico` 转成这几张 png 放进去即可（在线转图工具或任意图标软件都能做）。
7. **签名**：选"使用现有证书"→ 选你 `make_cert.ps1` 生成的 `NekoAiDev GitPush` 证书（或暂时用测试证书，商店发布时会重签）。
8. 点"创建" → 生成 `GitPush.msix`。

### 路径 B · build_msix.ps1 一键脚本（进阶，需 Windows 10/11 SDK）

仓库已加 `tools/msix/build_msix.ps1`。前置：已构建出 `dist\GitPush.exe`，并已安装 **Windows 10/11 SDK**（提供 `makeappx.exe` / `signtool.exe`）。

```powershell
# 在仓库根目录打开 PowerShell
.\tools\msix\build_msix.ps1 `
  -IdentityName "12345NekoAiDev.GitPush" `   # 从 Partner Center 应用标识复制
  -Publisher "CN=..." `                        # 从 Partner Center 应用标识复制
  -Version "1.4.4.0"
```

脚本会自动：准备打包目录 → 复制 `GitPush.exe` + `appicon.ico` → **写入 `STORE_BUILD.flag`** → 复制 `assets/*.png` → 生成 `AppxManifest.xml`（含 `runFullTrust`）→ `makeappx` 打包 → 用现有证书签名 → 产出 `GitPush.msix`。

> `assets/` 下的 4 张 png 需你自备（用 `appicon.ico` 转换）。脚本检测到缺失会明确报错提示。

---

## 2. ⚠️ 三个必须做对的开关（漏一个都会被打回）

| 项目 | 怎么做 | 漏掉的后果 |
|---|---|---|
| **STORE_BUILD.flag** | 封包时把程序目录放一个空文件 `STORE_BUILD.flag` | Store 版仍会从 `install.nekoaidev.top` 自下载 exe，违反 Store 政策 10.2.2，**审核拒** |
| **STORE_PRODUCT_ID** | 代码 `git_push_tool.py` 第 58 行 `STORE_PRODUCT_ID = ""` 填上真实 Product ID（Partner Center "应用标识"里的 12 位，形如 `9NXXXXXXXXX`）；留空也能编译，只是"前往商店更新"会回退到商店主页让用户自己搜 | 仅影响更新跳转体验，不阻塞上架 |
| **runFullTrust 能力** | 桌面桥（Desktop Bridge）应用默认被授予 `runFullTrust`，manifest 已含 `<rescap:Capability Name="runFullTrust" />`；用 MSIX Packaging Tool 封装时会自动处理 | 没有它，Win32 程序无法在 MSIX 沙箱里运行 |

---

## 3. 在 Partner Center 上传（Packages 步骤）

1. 进入提交 → 左侧 **Packages（包）**。
2. 点 **"选择包文件"** → 上传 `GitPush.msix`。（上传框默认只收 `.msix;.appx`，**不要切到"所有文件"去选 exe**。）
3. **设备系列**：只勾 **Desktop（桌面）**，取消 Phone / Xbox。
4. 等自动校验通过（校验会比对包内架构 x64 与"系统要求"里填的是否一致）。
5. 若之前误传了 exe：在 Packages 步骤删掉 exe 卡片，再传 msix（没提交前随时可删；已提交则先"停止提交"撤成草稿再改）。

---

## 4. 关于签名与证书

- 上传的 MSIX **需经有效证书签名**，`makeappx` 才允许产出；本地用你 `make_cert.ps1` 生成的 `NekoAiDev GitPush` 自签证书即可。
- **发布时 Microsoft Store 会用它自己的证书重新签名**，所以你本地的自签证书不影响最终用户——用户下载到的是商店签名版，不会有 SmartScreen 拦截。

---

## 5. 提交前最终检查清单

- [ ] `dist\GitPush.exe` 已构建（来自 `GitPush.spec`）
- [ ] 封装进 MSIX 时包含 **`STORE_BUILD.flag`**（空文件）
- [ ] `git_push_tool.py` 第 58 行已填 **`STORE_PRODUCT_ID`**（或接受回退到商店主页）
- [ ] 徽标 png 齐全（44/150/310×150/StoreLogo）
- [ ] MSIX 已用证书签名
- [ ] Partner Center：Packages 只传了 `.msix`，设备系列仅 Desktop
- [ ] 隐私政策 URL、Notes for certification、年龄分级（IARC 全选"无"→ 3+）均已填（见 `GitPush-Store-描述文案.md`）

---

Organization / 归属组织: NekoAiDev 组织（Neko Ai 团队）；Operator / 运营者: 小红蛋
