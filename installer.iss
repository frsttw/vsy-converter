#define MyAppName "Vsy Converter"
#define MyAppVersion "2.9.0"
#define MyAppPublisher "frsttw"
#define MyAppExeName "Vsy Converter.exe"

[Setup]
AppId={{8D79474E-87A2-49E0-92F9-00D41EF6F230}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Vsy Converter
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer-output
OutputBaseFilename=Instalador-Vsy-Converter
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=assets\vs-conversor.ico
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD-PARTY-LICENSES.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "vendor\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "vendor\ImageMagick-installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{tmp}\ImageMagick-installer.exe"; Parameters: "/VERYSILENT /NORESTART /SP-"; StatusMsg: "Installing ImageMagick..."; Flags: waituntilterminated; Check: not ImageMagickInstalled
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Vsy Converter"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: files; Name: "{app}\Conversor de Imagens.exe"
Type: files; Name: "{app}\VS Conversor.exe"
Type: files; Name: "{autodesktop}\VS Conversor.lnk"
Type: files; Name: "{autoprograms}\VS Conversor.lnk"
Type: files; Name: "{autodesktop}\Vsy Converter.lnk"
Type: files; Name: "{app}\LEIA-ME.txt"
Type: files; Name: "{app}\LICENCAS-DE-TERCEIROS.txt"

[Code]
function ImageMagickInstalled: Boolean;
var
  Paths: TArrayOfString;
begin
  Result := RegGetSubkeyNames(HKLM64, 'SOFTWARE\ImageMagick', Paths) or
            FileExists(ExpandConstant('{autopf}\ImageMagick-7.1.2-Q16-HDRI\magick.exe'));
end;
