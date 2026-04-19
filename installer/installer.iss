; Inno Setup Script for agapis-lapis App
; Safe to share publicly — contains no private data
; Paths are relative, version is auto-updated by build script

#define MyAppName "Agapis Lapis"
#ifndef MyAppVersion
#define MyAppVersion "0.0.0"
#endif
#define MyAppPublisher "MetaDusk Inc."
#define MyAppURL ""
#define MyAppExeName "agapis-lapis.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".al"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; Make sure to always generate a GUID with Inno Setup Compiler in #AppId.
; Replace only the "{}" and leave the open {, so it'll be like "{{}".
AppId={{3F6963C7-0E75-4B5E-BDEE-4CBD2F5E26A0}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=no
DisableProgramGroupPage=yes
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist\installer

; Change your installer name in #OutputBaseFilename if you don't like this format.
OutputBaseFilename={#MyAppName}-v{#MyAppVersion}-Win64-Installer

Compression=lzma
SolidCompression=yes
WizardStyle=modern

; #SetupIconFile is optional, but I think its path is best stored in the assets, so that
; it won't interfere with the main icon for the app itself.
SetupIconFile=..\src\assets\images\icon.ico

; Setting up the #SignTool will take a while, so just refer to a tutorial online on how to
; make a `certificate.pfx` file. This will also need a `signtool.exe` that can be found in
; the directories of your OS. It will also need a password, as this is used to login with
; your given `certificate.pfx`.
SignTool=signtool

SignedUninstaller=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\src\assets\images\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent