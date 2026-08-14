; GitPush 安装包脚本
; 由 Inno Setup 6 (ISCC.exe) 构建
; 说明：整文件夹递归打包，保留目录结构（主程序在 {app}\dist\GitPush.exe）。
;       排除工作文件（.git/.workbuddy/.wrangler/.gitignore/worker.js/wrangler.toml）、
;       构建垃圾（build/__pycache__）与安装包自身，避免套娃与泄露私钥。
;       安装过程中自动把自签名证书 GitPush.cer 装入“受信任的根证书颁发机构”，
;       从而让本工具以“NekoAiDev GitPush”发布者身份运行，消除 Windows 的未知发布者/安全警告。
; 注：本脚本全部使用绝对路径，避免相对路径/常量展开问题。
; 注：语言文件位于 Inno 的 Languages 子目录，必须写成 compiler:Languages\English.isl

[Setup]
AppName=Git Push
AppVersion=1.4.1
AppVerName=Git Push 1.4.1
AppPublisher=NekoAiDev
DefaultDirName=C:\Program Files\Git Push
; 强制显示“选择目标位置”页面，允许用户自定义安装到 D 盘或其他任意目录（默认仍是 C:\Program Files）
DisableDirPage=no
; 不使用上一次安装的目录记忆，确保默认路径始终为 C:\Program Files\Git Push
UsePreviousAppDir=no
DefaultGroupName=Git Push
; ⚠️ 下面 OutputDir 只是“本机编译时把生成的安装包文件(GitPush_Setup.exe)写到哪”，与用户安装位置无关！
;    用户电脑上的【默认安装目录】由上面的 DefaultDirName 决定（C:\Program Files\Git Push），可在安装向导里改到任意盘。
OutputDir=D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24
OutputBaseFilename=GitPush_Setup
SetupIconFile=D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\appicon.ico
Compression=lzma2
SolidCompression=yes
; 安装证书到 LocalMachine\Root 需要管理员权限
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableProgramGroupPage=no
; 安装时展示用户协议与隐私政策（需勾选同意方可继续安装）
LicenseFile=D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\用户服务协议.txt
InfoBeforeFile=D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\隐私政策.txt

[Languages]
Name: "ChineseSimplified"; MessagesFile: "ChineseSimplified.isl"

[Files]
; 根目录项目文件逐个列出（已排除 .git/.workbuddy/.wrangler/.gitignore/worker.js/wrangler.toml 等工作文件，
; 以及安装包自身 GitPush_Setup.exe/.iss、构建垃圾 build/__pycache__、临时文件 cert_thumbprint.txt）
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\appicon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\gen_icon.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\git_push_tool.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\GitPush.cer"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\GitPush.spec"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\launch_gitpush.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\make_cert.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\rebuild_update.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\refresh_icon_cache.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\version.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\用户服务协议.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\隐私政策.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\build_installer.ps1"; DestDir: "{app}"; Flags: ignoreversion
; dist 目录（运行时必需，递归打包）
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\dist\*"; DestDir: "{app}\dist"; Flags: ignoreversion recursesubdirs createallsubdirs

[Run]
; 安装时把证书装入受信任根（静默执行），从而让本工具以可信发布者身份运行
Filename: "certutil.exe"; Parameters: "addstore -f ""Root"" ""{app}\GitPush.cer"""; StatusMsg: "正在安装受信任证书（用于消除发布者安全警告）..."; Flags: runhidden
; 安装完成后可选启动（注意程序在 dist 子目录）
Filename: "{app}\dist\GitPush.exe"; Description: "启动 GitPush"; Flags: nowait postinstall runasoriginaluser

[Icons]
Name: "{group}\GitPush"; Filename: "{app}\dist\GitPush.exe"; WorkingDir: "{app}\dist"
Name: "{commondesktop}\GitPush"; Filename: "{app}\dist\GitPush.exe"; Tasks: desktopicon; WorkingDir: "{app}\dist"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项:"
