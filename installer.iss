; MCC Monitoring System Installer
; Copyright (c) 2026 Clan
; MIT License

[Setup]
AppName=MCC Condition Monitoring System
AppVersion=1.0.0
AppPublisher=Clan
AppCopyright=Copyright (c) 2026 Clan
DefaultDirName={pf}\Clan\MCC Monitoring System
DefaultGroupName=Clan\MCC Monitoring System
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=MCC_Monitoring_System_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\MCC_Monitoring_System.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\MCC Monitoring System"; Filename: "{app}\MCC_Monitoring_System.exe"
Name: "{group}\Uninstall MCC Monitoring System"; Filename: "{uninstallexe}"
Name: "{commondesktop}\MCC Monitoring System"; Filename: "{app}\MCC_Monitoring_System.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MCC_Monitoring_System.exe"; Description: "Launch MCC Monitoring System"; Flags: nowait postinstall skipifsilent