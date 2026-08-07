# FocusEndConditionType 오류 확인

- Project: Astellia
- Session ID: `019ef8f8-4868-75a3-a40b-bc11747ffdb2`
- Workspace: `E:\ProjectA02\Trunk\Dev`
- Started: 2026-06-24T09:31:21.979Z
- Updated: 2026-06-24T09:31:27.4889949Z
- Messages exported: 7

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

E:\ProjectA02\Trunk\Dev\Table_NFT 폴더에서 TutorialData_NFT.xlsx 파일을 T_데이터생성기 - 복사본.bat 파일로 변환 시도하니


E:\ProjectA02\Trunk\Dev\Table_NFT>for %F in (E:\ProjectA02\Trunk\Dev\Table_NFT\TutorialData_NFT.xlsx) do ("C:\WINDOWS\System32\cscript.exe" //nologo //B "E:\ProjectA02\Trunk\Dev\Table_NFT\_Excel2Json.js" "%~F" "../Client/Assets/1_NFTData/GameData/" )

E:\ProjectA02\Trunk\Dev\Table_NFT>("C:\WINDOWS\System32\cscript.exe" //nologo //B "E:\ProjectA02\Trunk\Dev\Table_NFT\_Excel2Json.js" "E:\ProjectA02\Trunk\Dev\Table_NFT\TutorialData_NFT.xlsx" "../Client/Assets/1_NFTData/GameData/" )

E:\ProjectA02\Trunk\Dev\Table_NFT>_BinaryBuilder.exe --jsonReadPath ../Client/Assets/1_NFTData/GameData/ --bytesWritePath ../Client/Assets/1_NFTData/Binary/  --log 0
json 읽기 경로 - ../Client/Assets/1_NFTData/GameData/
binary 쓰기 경로 - ../Client/Assets/1_NFTData/Binary/
path : ../Client/Assets/1_NFTData/GameData/
path : ../Client/Assets/1_NFTData/Binary/

바이너리 생성 1
BaseLoaderFileReader(TutorialData) :: 데이터 이상!!! Error converting value "FocusBMStoreSummonSP" to type 'SharedLib.Data.eFocusEndConditionType'. Path 'TutorialData[98].FocusEndConditionType'.
BaseLoaderFileReader(TutorialData) :: 데이터 이상!!! Error converting value "FocusMainTabSummonAvatarSP" to type 'SharedLib.Data.eFocusEndConditionType'. Path 'TutorialData[99].FocusEndConditionType'.

FocusBMStoreSummonSP, FocusMainTabSummonAvatarSP 데이터 이상 오류가 발생되었는데 원인 확인해 주세요.

### Assistant

변환 파이프라인의 enum 정의와 엑셀 원본 셀, 생성된 JSON을 서로 대조해 원인을 좁히겠습니다. 우선 관련 파일과 두 문자열의 참조 위치부터 찾겠습니다.

### Assistant

현재 소스 코드의 enum에는 두 값이 이미 존재하고, 생성 JSON에도 문자열이 정상 출력됩니다. 따라서 엑셀 오타보다는 `_BinaryBuilder.exe`가 로드하는 `SharedLib` 버전 불일치 가능성이 큽니다. 엑셀 내부 값까지 정확히 확인하기 위해 스프레드시트 스킬의 검증 절차를 적용하겠습니다.

### Assistant

소스 enum과 JSON은 일치합니다. 이제 실행 파일 자체에 두 enum 이름이 포함되어 있는지, 그리고 이 실행 파일을 만드는 `Resource_Trunk\Tools\BinaryBuilder`가 어느 `TutorialData.cs`를 참조하는지 확인하겠습니다. 여기서 불일치가 잡히면 원인이 확정됩니다.

### Assistant

프로젝트 경로를 계산해 보니 `BinaryBuilder.csproj`의 소스 직접 포함 경로는 현재 존재하지 않아 실제로는 `Server\SharedLib\bin\x64\Debug\netstandard2.0\SharedLib.dll`을 참조해 빌드됩니다. 그 DLL이 최신 소스보다 오래된지와 DLL 내부 enum 목록을 직접 확인하겠습니다.

### Assistant

엑셀 원본도 확인됐습니다. `TutorialData` 시트의 `M102`, `M103` 값은 각각 두 enum 문자열로 정상이며, JSON의 배열 인덱스 98·99에도 그대로 변환됐습니다. 마지막으로 실행 파일에 내장된 `SharedLib.dll`까지 확인해 빌드 시점의 의존 DLL 불일치를 확정하겠습니다.

### Assistant

원인은 엑셀 데이터가 아니라 `_BinaryBuilder.exe`에 포함된 `SharedLib.dll`이 오래된 것입니다.

확인 결과:

- 엑셀 `TutorialData!M102`, `M103` 값은 정상입니다.
- 생성된 JSON도 [TutorialData.json](/E:/ProjectA02/Trunk/Dev/Client/Assets/1_NFTData/GameData/TutorialData.json:1696)에 정상 출력됩니다.
- 최신 소스 enum에는 두 값이 존재합니다: [TutorialData.cs](/E:/ProjectA02/Trunk/Dev/Client/Assets/Script/SharedLib/DataManager/DataClass/TutorialData.cs:46)
- 그러나 `BinaryBuilder`가 참조하는 [SharedLib.dll 경로](/E:/ProjectA02/Resource_Trunk/Tools/BinaryBuilder/BinaryBuilder.csproj:81)의 실제 DLL에는 다음 값들이 없습니다.
  - `FocusBMStoreMain`
  - `FocusBMStoreSummonSP`
  - `FocusMainTabSummonAvatarSP`

`TutorialData.cs`는 2026-06-24 17:32에 수정됐지만, `SharedLib.dll`은 12:58에 빌드되어 소스 변경이 반영되지 않았습니다. 이후 `_BinaryBuilder.exe`를 다시 만들어도 오래된 DLL을 그대로 내장했기 때문에 역직렬화 오류가 발생합니다.

해결 순서는 다음과 같습니다.

1. `Server\SharedLib\SharedLib.csproj`를 `Debug | x64`로 다시 빌드
2. `Table_NFT\__BinaryBuilderMake.bat` 실행
3. `T_데이터생성기 - 복사본.bat`으로 다시 변환

현재 오류가 난 두 값 외에 `FocusBMStoreMain`도 동일한 잠재 오류 대상입니다.
