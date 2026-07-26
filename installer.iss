; Inno Setup Script for PC Power Control
; Compile with: iscc.exe installer.iss

[Setup]
AppName=PC Power Control
AppVersion=1.0.0
DefaultDirName={pf}\PCPowerControl
DefaultGroupName=PC Power Control
UninstallDisplayIcon={app}\PCPowerControl.exe
OutputDir=dist
OutputBaseFilename=PCPowerControl_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
DisableProgramGroupPage=yes

[Files]
Source: "dist\PCPowerControl.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PC Power Control Dashboard"; Filename: "http://localhost:5000"
Name: "{group}\PC Power Control (Server)"; Filename: "{app}\PCPowerControl.exe"
Name: "{group}\Uninstall PC Power Control"; Filename: "{uninstallexe}"

[Run]
Filename: "http://localhost:5000"; Description: "Dashboard öffnen"; Flags: shellexec postinstall nowait

[UninstallRun]
Filename: "taskkill"; Parameters: "/f /im PCPowerControl.exe"; Flags: runhidden
