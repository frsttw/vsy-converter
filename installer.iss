#define MyAppName "VS Conversor"
#define MyAppVersion "2.3.0"
#define MyAppPublisher "frsttw"
#define MyAppExeName "VS Conversor.exe"

[Setup]
AppId={{8D79474E-87A2-49E0-92F9-00D41EF6F230}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\VS Conversor
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer-output
OutputBaseFilename=Instalador-VS-Conversor
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
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "LEIA-ME.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENCAS-DE-TERCEIROS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "vendor\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "vendor\ImageMagick-installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: checkedonce

[Run]
Filename: "{tmp}\ImageMagick-installer.exe"; Parameters: "/VERYSILENT /NORESTART /SP-"; StatusMsg: "Instalando o ImageMagick..."; Flags: waituntilterminated; Check: not ImageMagickInstalled
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir o VS Conversor"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: files; Name: "{app}\Conversor de Imagens.exe"

[Code]
function ImageMagickInstalled: Boolean;
var
  Paths: TArrayOfString;
begin
  Result := RegGetSubkeyNames(HKLM64, 'SOFTWARE\ImageMagick', Paths) or
            FileExists(ExpandConstant('{autopf}\ImageMagick-7.1.2-Q16-HDRI\magick.exe'));
end;
