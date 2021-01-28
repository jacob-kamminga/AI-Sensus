[Setup]
AppName=Labeling App
AppVersion=0.3
WizardStyle=modern
DefaultDirName={autopf}\Labeling App
DefaultGroupName=Labeling App
UninstallDisplayIcon={app}\LabelingApp.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Labeling App Output

[Files]
;Source: "C:\Users\Dennis\Documents\work\labeling_app\LabelingApp\dist\main\*"; Excludes: "main.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "C:\Users\Dennis\Documents\work\labeling_app\LabelingApp\dist\main\main.exe"; DestDir: "{app}"; DestName: "LabelingApp.exe"
;Source: "C:\Users\Dennis\Documents\work\labeling_app\LabelingApp\Lib\*"; DestDir: "{app}\Lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Jacob\PycharmProjects\LabelingApp\dist\main\*"; Excludes: "main.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Jacob\PycharmProjects\LabelingApp\dist\main\main.exe"; DestDir: "{app}"; DestName: "LabelingApp.exe"
Source: "C:\Users\Jacob\PycharmProjects\LabelingApp\Lib\*"; DestDir: "{app}\Lib"; Flags: ignoreversion recursesubdirs createallsubdirs

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  { look for the path with leading and trailing semicolon }
  { Pos() returns 0 if not found }
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

[Setup]
; Tell Windows Explorer to reload the environment
ChangesEnvironment=True

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};C:\Program Files (x86)\Labeling App\Lib\exiftool"; \
    Check: NeedsAddPath('C:\Program Files (x86)\Labeling App\Lib\exiftool')

Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};C:\Program Files (x86)\Labeling App\Lib\ffprobe"; \
    Check: NeedsAddPath('C:\Program Files (x86)\Labeling App\Lib\ffprobe')

[Icons]
Name: "{group}\Labeling App"; Filename: "{app}\LabelingApp.exe"