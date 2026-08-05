; *** Inno Setup version 6.4.0+ Chinese (Simplified) messages ***
; 由繁体中文 ChineseTraditional.isl 转写（简体中文）
;
; Note: When translating this text, do not add periods (.) to the end of
; messages that didn't have them already, because on those messages Inno
; Setup adds the periods automatically (appending a period would result in
; two periods being displayed).

[LangOptions]
LanguageName=<7b80><4f53><4e2d><6587>
LanguageID=$0804
LanguageCodepage=936

[Messages]

; *** Application titles
SetupAppTitle=安装程序
SetupWindowTitle=%1 安装程序
UninstallAppTitle=卸载
UninstallAppFullTitle=卸载 %1

; *** Misc. common
InformationTitle=信息
ConfirmTitle=确认
ErrorTitle=错误

; *** SetupLdr messages
SetupLdrStartupMessage=这将安装 %1。您想要继续吗？
LdrCannotCreateTemp=无法创建临时文件。安装程序将会结束。
LdrCannotExecTemp=无法执行临时文件。安装程序将会结束。
HelpTextNote=

; *** Startup error messages
LastErrorMessage=%1%n%n错误 %2: %3
SetupFileMissing=安装文件夹中丢失文件 %1。请修正此问题或重新获取此软件。
SetupFileCorrupt=安装文件已经损坏。请重新获取此软件。
SetupFileCorruptOrWrongVer=安装文件已经损坏，或与安装程序的版本不符。请重新获取此软件。
InvalidParameter=某个无效的变量已被传递到命令行:%n%n%1
SetupAlreadyRunning=安装程序已经在运行。
WindowsVersionNotSupported=本安装程序并不支持目前在电脑所运行的 Windows 版本。
WindowsServicePackRequired=本安装程序需要 %1 Service Pack %2 或更新。
NotOnThisPlatform=这个程序无法在 %1 运行。
OnlyOnThisPlatform=这个程序必须在 %1 运行。
OnlyOnTheseArchitectures=这个程序只能在专门为以下处理器架构而设计的 Windows 上安装:%n%n%1
WinVersionTooLowError=这个程序必须在 %1 版本 %2 或以上的系统运行。
WinVersionTooHighError=这个程序无法安装在 %1 版本 %2 或以上的系统。
AdminPrivilegesRequired=您必须登录为系统管理员以安装这个程序。
PowerUserPrivilegesRequired=您必须登录为具有系统管理员或 Power User 权限的用户以安装这个程序。
SetupAppRunningError=安装程序检测到 %1 正在运行。%n%n请关闭该程序后按 “确定” 继续，或按 “取消” 离开。
UninstallAppRunningError=卸载程序检测到 %1 正在运行。%n%n请关闭该程序后按 “确定” 继续，或按 “取消” 离开。

; *** Startup questions
PrivilegesRequiredOverrideTitle=选择安装程序安装模式
PrivilegesRequiredOverrideInstruction=选择安装模式
PrivilegesRequiredOverrideText1=可以为所有用户安装 %1 (需要管理员权限)，或是仅为您安装。
PrivilegesRequiredOverrideText2=可以仅为您安装 %1，或是为所有用户安装 (需要管理员权限)。
PrivilegesRequiredOverrideAllUsers=为所有用户安装 (&A)
PrivilegesRequiredOverrideAllUsersRecommended=为所有用户安装 (建议选项) (&A)
PrivilegesRequiredOverrideCurrentUser=仅为我安装 (&M)
PrivilegesRequiredOverrideCurrentUserRecommended=仅为我安装 (建议选项) (&M)

; *** Misc. errors
ErrorCreatingDir=安装程序无法创建文件夹“%1”。
ErrorTooManyFilesInDir=无法在文件夹“%1”内创建文件，因为文件夹内有太多的文件。

; *** Setup common messages
ExitSetupTitle=结束安装程序
ExitSetupMessage=安装尚未完成。如果您现在结束安装程序，这个程序将不会被安装。%n%n您可以稍后再运行安装程序以完成安装程序。您现在要结束安装程序吗?
AboutSetupMenuItem=关于安装程序 (&A)...
AboutSetupTitle=关于安装程序
AboutSetupMessage=%1 版本 %2%n%3%n%n%1 网址:%n%4
AboutSetupNote=
TranslatorNote=

; *** Buttons
ButtonBack=< 上一步(&B)
ButtonInstall=安装(&I)
ButtonNext=下一步(&N)  >
ButtonOK=确定
ButtonCancel=取消
ButtonYes=是(&Y)
ButtonYesToAll=全部皆是 (&A)
ButtonNo=否(&N)
ButtonNoToAll=全部皆否 (&O)
ButtonFinish=完成 (&F)
ButtonBrowse=浏览 (&B)...
ButtonWizardBrowse=浏览 (&R)...
ButtonNewFolder=创建新文件夹 (&M)

; *** "Select Language" dialog messages
SelectLanguageTitle=选择安装语言
SelectLanguageLabel=选择在安装过程中使用的语言:

; *** Common wizard text
ClickNext=按 “下一步” 继续安装，或按 “取消” 结束安装程序。
BeveledLabel=
BrowseDialogTitle=浏览文件夹
BrowseDialogLabel=在下面的文件夹列表中选择一个文件夹，然后按 “确定”。
NewFolderName=新文件夹

; *** "Welcome" wizard page
WelcomeLabel1=欢迎使用 [name] 安装程序
WelcomeLabel2=这个安装程序将会安装 [name/ver] 到您的电脑。%n%n我们强烈建议您在安装过程中关闭其它的应用程序，以避免与安装程序发生冲突。

; *** "Password" wizard page
WizardPassword=密码
PasswordLabel1=这个安装程序具有密码保护。
PasswordLabel3=请输入密码，然后按 “下一步” 继续。密码是区分大小写的。
PasswordEditLabel=密码 (&P):
IncorrectPassword=您输入的密码不正确，请重新输入。

; *** "License Agreement" wizard page
WizardLicense=授权协议
LicenseLabel=请阅读以下授权协议。
LicenseLabel3=请阅读以下授权协议，您必须接受协议的各项条款才能继续安装。
LicenseAccepted=我同意 (&A)
LicenseNotAccepted=我不同意 (&D)

; *** "Information" wizard pages
WizardInfoBefore=信息
InfoBeforeLabel=在继续安装之前请阅读以下重要信息。
InfoBeforeClickLabel=当您准备好继续安装，请按 “下一步”。
WizardInfoAfter=信息
InfoAfterLabel=在继续安装之前请阅读以下重要信息。
InfoAfterClickLabel=当您准备好继续安装，请按 “下一步”。

; *** "User Information" wizard page
WizardUserInfo=用户信息
UserInfoDesc=请输入您的资料。
UserInfoName=用户名称(&U):
UserInfoOrg=组织(&O):
UserInfoSerial=序列号(&S):
UserInfoNameRequired=您必须输入您的名称。

; *** "Select Destination Location" wizard page
WizardSelectDir=选择目标文件夹
SelectDirDesc=选择安装程序安装 [name] 的位置。
SelectDirLabel3=安装程序将会把 [name] 安装到下面的文件夹。
SelectDirBrowseLabel=按 “下一步” 继续，如果您想选择另一个文件夹，请按 “浏览”。
DiskSpaceGBLabel=最少需要 [gb] GB 磁盘空间。
DiskSpaceMBLabel=最少需要 [mb] MB 磁盘空间。
CannotInstallToNetworkDrive=安装程序无法安装于网络磁盘驱动器。
CannotInstallToUNCPath=安装程序无法安装于 UNC 路径。
InvalidPath=您必须输入完整的路径名称及磁盘驱动器代号。%n%n例如 C:\App 或 UNC 路径格式 \\服务器\共享文件夹。
InvalidDrive=您选取的磁盘驱动器或 UNC 名称不存在或无法存取，请选择其他的目的地。
DiskSpaceWarningTitle=磁盘空间不足
DiskSpaceWarning=安装程序需要至少 %1 KB 的磁盘空间，您所选取的磁盘只有 %2 KB 可用空间。%n%n您要继续安装吗？
DirNameTooLong=文件夹名称或路径太长。
InvalidDirName=文件夹名称不正确。
BadDirName32=文件夹名称不得包含以下特殊字符:%n%n%1
DirExistsTitle=文件夹已经存在
DirExists=文件夹：%n%n%1%n%n 已经存在。仍要安装到该文件夹吗？
DirDoesntExistTitle=文件夹不存在
DirDoesntExist=文件夹：%n%n%1%n%n 不存在。要创建该文件夹吗？

; *** "Select Components" wizard page
WizardSelectComponents=选择组件
SelectComponentsDesc=选择将会被安装的组件。
SelectComponentsLabel2=选择您想要安装的组件；清除您不想安装的组件。然后按 “下一步” 继续安装。
FullInstallation=完整安装
CompactInstallation=最小安装
CustomInstallation=自定义安装
NoUninstallWarningTitle=组件已存在
NoUninstallWarning=安装程序检测到以下组件已经安装在您的电脑上:%n%n%1%n%n取消选择这些组件将不会移除它们。%n%n您仍然要继续吗？
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=目前的选择需要至少 [gb] GB 磁盘空间。
ComponentsDiskSpaceMBLabel=目前的选择需要至少 [mb] MB 磁盘空间。

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=选择附加的任务
SelectTasksDesc=选择要执行的附加任务。
SelectTasksLabel2=选择安装程序在安装 [name] 时要执行的附加任务，然后按 “下一步”。

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=选择“开始”菜单的文件夹
SelectStartMenuFolderDesc=选择安装程序创建程序快捷方式的位置。
SelectStartMenuFolderLabel3=安装程序将会把程序的快捷方式建立在下面的“开始”菜单文件夹。
SelectStartMenuFolderBrowseLabel=按 “下一步” 继续，如果您想选择另一个文件夹，请按 “浏览”。
MustEnterGroupName=您必须输入一个文件夹的名称。
GroupNameTooLong=文件夹名称或路径太长。
InvalidGroupName=文件夹名称不正确。
BadGroupName=文件夹名称不得包含下列字符:%n%n%1
NoProgramGroupCheck2=不要在“开始”菜单中创建文件夹 (&D)

; *** "Ready to Install" wizard page
WizardReady=准备安装
ReadyLabel1=安装程序将开始安装 [name] 到您的电脑中。
ReadyLabel2a=按下 “安装” 继续安装，或按 “上一步” 重新查看或设置各选项的内容。
ReadyLabel2b=按下 “安装” 继续安装。
ReadyMemoUserInfo=用户信息
ReadyMemoDir=目标文件夹:
ReadyMemoType=安装类型:
ReadyMemoComponents=选择的组件:
ReadyMemoGroup=“开始”菜单文件夹:
ReadyMemoTasks=附加任务:

; *** TDownloadWizardPage wizard page and DownloadTemporaryFile
DownloadingLabel=正在下载额外文件...
ButtonStopDownload=停止下载 (&S)
StopDownload=您确定要停止下载吗？
ErrorDownloadAborted=已停止下载
ErrorDownloadFailed=下载失败: %1 %2
ErrorDownloadSizeFailed=获取文件大小失败: %1 %2
ErrorFileHash1=文件哈希失败: %1
ErrorFileHash2=文件哈希无效: 必须为 %1，收到 %2
ErrorProgress=进度无效: %1 之 %2
ErrorFileSize=文件大小无效: 必须为 %1，收到 %2

; *** TExtractionWizardPage wizard page and Extract7ZipArchive
ExtractionLabel=正在提取附加文件...
ButtonStopExtraction=停止提取(&S)
StopExtraction=你确定要停止提取吗？
ErrorExtractionAborted=提取终止
ErrorExtractionFailed=提取失败：%1

; *** "Preparing to Install" wizard page
WizardPreparing=准备安装程序
PreparingDesc=安装程序准备将 [name] 安装到您的电脑上。
PreviousInstallNotCompleted=先前的安装/卸载尚未完成，您必须重新启动电脑以完成该安装。%n%n在重新启动电脑之后，请再运行这个程序来安装 [name]。
CannotContinue=安装程序无法继续。请按 “取消” 离开。
ApplicationsFound=下面的应用程序正在使用安装程序所需要更新的文件。建议您允许安装程序自动关闭这些应用程序。
ApplicationsFound2=下面的应用程序正在使用安装程序所需要更新的文件。建议您允许安装程序自动关闭这些应用程序。当安装过程结束后，本安装程序将会尝试重新打开该应用程序。
CloseApplications=关闭应用程序 (&A)
DontCloseApplications=不要关闭应用程序 (&D)
ErrorCloseApplications=安装程序无法自动关闭所有应用程序。建议您在继续前先关闭所有应用程序使用的文件。
PrepareToInstallNeedsRestart=安装程序必须重新启动您的电脑。重新启动后，请再次运行安装程序以完成 [name] 的安装。%n%n您想要现在重新启动电脑吗？

; *** "Installing" wizard page
WizardInstalling=正在安装
InstallingLabel=请稍候，安装程序正在将 [name] 安装到您的电脑上

; *** "Setup Completed" wizard page
FinishedHeadingLabel=安装完成
FinishedLabelNoIcons=安装程序已经将 [name] 安装到您的电脑上。
FinishedLabel=安装程序已经将 [name] 安装到您的电脑中，您可以选择程序的图标来运行该应用程序。
ClickFinish=按 “完成” 以结束安装程序。
FinishedRestartLabel=要完成 [name] 的安装，安装程序必须重新启动您的电脑。您想要现在重新启动电脑吗？
FinishedRestartMessage=要完成 [name] 的安装，安装程序必须重新启动您的电脑。%n%n您想要现在重新启动电脑吗？
ShowReadmeCheck=是，我要阅读自述文件。
YesRadio=是，立即重新启动电脑(&Y)
NoRadio=否，我稍后重新启动电脑(&N)
RunEntryExec=运行 %1
RunEntryShellExec=查看 %1

; *** "Setup Needs the Next Disk"
ChangeDiskTitle=安装程序需要下一张磁盘
SelectDiskLabel2=请插入磁盘 %1，然后按 “确定”。%n%n如果文件不在以下所显示的文件夹之中，请输入正确的文件夹名称或按 [浏览] 选取。
PathLabel=路径(&P):
FileNotInDir2=文件“%1”无法在“%2”找到。请插入正确的磁盘或选择其它的文件夹。
SelectDirectoryLabel=请指定下一张磁盘的位置。

; *** Installation phase messages
SetupAborted=安装没有完成。%n%n请更正问题后重新安装一次。
AbortRetryIgnoreSelectAction=选取动作
AbortRetryIgnoreRetry=请再试一次 (&T)
AbortRetryIgnoreIgnore=略过错误并继续 (&I)
AbortRetryIgnoreCancel=取消安装

; *** Installation status messages
StatusClosingApplications=正在关闭应用程序...
StatusCreateDirs=正在创建文件夹...
StatusExtractFiles=正在解压缩文件...
StatusCreateIcons=正在创建程序集图标...
StatusCreateIniEntries=写入 INI 文件的项...
StatusCreateRegistryEntries=正在更新系统登录...
StatusRegisterFiles=正在注册文件...
StatusSavingUninstall=保存卸载信息...
StatusRunProgram=正在完成安装...
StatusRestartingApplications=正在重新打开应用程序...
StatusRollback=正在复原变更...

; *** Misc. errors
ErrorInternal2=内部错误: %1
ErrorFunctionFailedNoCode=%1 失败
ErrorFunctionFailed=%1 失败；代码 %2
ErrorFunctionFailedWithMessage=%1 失败；代码 %2.%n%3
ErrorExecutingProgram=无法执行文件:%n%1

; *** Registry errors
ErrorRegOpenKey=无法打开登录键:%n%1\%2
ErrorRegCreateKey=无法创建登录项:%n%1\%2
ErrorRegWriteKey=无法变更登录项:%n%1\%2

; *** INI errors
ErrorIniEntry=在文件“%1”创建 INI 项错误。

; *** File copying errors
FileAbortRetryIgnoreSkipNotRecommended=略过这个文件 (不建议) (&S)
FileAbortRetryIgnoreIgnoreNotRecommended=略过错误并继续 (不建议) (&I)
SourceDoesntExist=来源文件“%1”不存在。
SourceIsCorrupted=来源文件已经损坏。
ExistingFileReadOnly2=无法取代现有文件，因为文件已标示为只读。
ExistingFileReadOnlyRetry=移除只读属性并重试 (&R)
ExistingFileReadOnlyKeepExisting=保留现有文件 (&K)
ErrorReadingExistingDest=读取一个已存在的文件时发生错误:
FileExistsSelectAction=选择操作
FileExists2=文件已存在。
FileExistsOverwriteExisting=覆盖现有文件
FileExistsKeepExisting=保留现有文件 (&O)
FileExistsOverwriteOrKeepAll=对下次冲突执行相同操作 (&D)
ExistingFileNewerSelectAction=选择操作
ExistingFileNewer2=现有文件比安装程序尝试安装的文件还新。
ExistingFileNewerOverwriteExisting=覆盖现有文件 (&O)
ExistingFileNewerKeepExisting=保留现有文件 (&K) (建议选项)
ExistingFileNewerOverwriteOrKeepAll=对下次冲突执行相同操作 (&D)
ErrorChangingAttr=在变更文件属性时发生错误:
ErrorCreatingTemp=在目标文件夹中创建文件时发生错误:
ErrorReadingSource=读取原始文件时发生错误:
ErrorCopying=复制文件时发生错误:
ErrorReplacingExistingFile=替换文件时发生错误:
ErrorRestartReplace=重新启动电脑后替换文件失败:
ErrorRenamingTemp=在目标文件夹变更文件名称时发生错误:
ErrorRegisterServer=无法注册 DLL/OCX 文件: %1。
ErrorRegSvr32Failed=RegSvr32 失败；退出代码 %1
ErrorRegisterTypeLib=无法注册类型库: %1。

; *** Uninstall display name markings
UninstallDisplayNameMark=%1 (%2)
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32 位
UninstallDisplayNameMark64Bit=64 位
UninstallDisplayNameMarkAllUsers=所有用户
UninstallDisplayNameMarkCurrentUser=当前用户

; *** Post-installation errors
ErrorOpeningReadme=打开自述文件时发生错误。
ErrorRestartingComputer=安装程序无法重新启动电脑，请自行重新启动。

; *** Uninstaller messages
UninstallNotFound=文件“%1”不存在，无法卸载。
UninstallOpenError=无法打开文件“%1”，无法卸载
UninstallUnsupportedVer=这个版本的卸载程序无法辨识记录文件 “%1” 的格式，无法卸载。
UninstallUnknownEntry=卸载记录文件中发现未知的记录 (%1)。
ConfirmUninstall=您确定要完全移除 %1 及其相关的文件吗？
UninstallOnlyOnWin64=这个程序只能在 64 位的 Windows 上卸载。
OnlyAdminCanUninstall=这个程序要具备系统管理员权限的用户方可卸载。
UninstallStatusLabel=正在从您的电脑移除 %1 中，请稍候...
UninstalledAll=%1 已经成功从您的电脑中移除。
UninstalledMost=%1 卸载完成。%n%n某些文件及组件无法移除，您可以自行删除这些文件。
UninstalledAndNeedsRestart=要完成 %1 的卸载程序，您必须重新启动电脑。%n%n您想要现在重新启动电脑吗？
UninstallDataCorrupted=文件“%1”已经损坏，无法卸载

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=移除共享文件
ConfirmDeleteSharedFile2=系统显示下列共享文件已不再被任何程序所使用，您要移除这些文件吗?%n%n%1%n%n倘若您移除了以上文件但仍有程序需要使用它们，将造成这些程序无法正常运行，因此您若无法确定请选择 [否]。保留这些文件在您的系统中不会造成任何损害。
SharedFileNameLabel=文件名称:
SharedFileLocationLabel=位置:
WizardUninstalling=卸载状态
StatusUninstalling=正在卸载 %1...

; *** Shutdown block reasons
ShutdownBlockReasonInstallingApp=正在安装 %1。
ShutdownBlockReasonUninstallingApp=正在卸载 %1。

; The custom messages below aren't used by Setup itself, but if you make
; use of them in your scripts, you'll want to translate them.

[CustomMessages]

NameAndVersion=%1 版本 %2
AdditionalIcons=附加图标:
CreateDesktopIcon=创建桌面图标(&D)
CreateQuickLaunchIcon=创建快速启动图标(&Q)
ProgramOnTheWeb=%1 的网站
UninstallProgram=卸载 %1
LaunchProgram=启动 %1
AssocFileExtension=将 %1 与文件扩展名 %2 产生关联(&A)
AssocingFileExtension=正在将 %1 与文件扩展名 %2 产生关联...
AutoStartProgramGroupDescription=打开:
AutoStartProgram=自动打开 %1
AddonHostProgramNotFound=%1 无法在您所选择的文件夹中找到。%n%n您是否还要继续？
