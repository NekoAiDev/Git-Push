; GitPush 安装包脚本
; 由 Inno Setup 6 (ISCC.exe) 构建
; 说明：只打包运行所需文件（exe + 图标），排除所有工作文件（.git/.workbuddy/.wrangler/version.json/worker.js 等）
;       安装过程中自动把自签名证书 GitPush.cer 装入“受信任的根证书颁发机构”，
;       这样本工具以“NekoAiDev GitPush”发布者身份运行，消除 Windows 的未知发布者/安全警告。
; 注：本脚本全部使用绝对路径，避免相对路径/常量展开问题。
; 注：语言文件位于 Inno 的 Languages 子目录，必须写成 compiler:Languages\English.isl

[Setup]
AppName=GitPush
AppVersion=1.2.0
AppVerName=GitPush 1.2.0
AppPublisher=NekoAiDev
DefaultDirName={autopf}\GitPush
DefaultGroupName=GitPush
OutputDir=D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24
OutputBaseFilename=GitPush_Setup
SetupIconFile=D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\appicon.ico
UninstallDisplayIcon={app}\GitPush.exe
Compression=lzma2
SolidCompression=yes
; 安装证书到 LocalMachine\Root 需要管理员权限
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableProgramGroupPage=no

[Languages]
Name: "English"; MessagesFile: "compiler:Languages\English.isl"

[Files]
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\dist\GitPush.exe"; DestDir: "{app}"; Flags: ignoreversion
; 证书（仅安装时用，装完删除）
Source: "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24\GitPush.cer"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Run]
; 安装时把证书装入受信任根（静默执行），从而让本工具以可信发布者身份运行
Filename: "certutil.exe"; Parameters: "addstore -f ""Root"" ""{tmp}\GitPush.cer"""; StatusMsg: "正在安装受信任证书（用于消除发布者安全警告）..."; Flags: runhidden
; 安装完成后可选启动
Filename: "{app}\GitPush.exe"; Description: "启动 GitPush"; Flags: nowait postinstall runasoriginaluser

[Icons]
Name: "{group}\GitPush"; Filename: "{app}\GitPush.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\GitPush"; Filename: "{app}\GitPush.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项:"
