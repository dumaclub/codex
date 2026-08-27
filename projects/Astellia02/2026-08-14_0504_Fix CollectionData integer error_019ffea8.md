# Fix CollectionData integer error

- Project: Astellia02
- Session ID: `019ffea8-23d6-75d0-8918-d2059ee98ca1`
- Workspace: `C:\Users\dumaclub\Documents\ChatGPT\Astellia02`
- Started: 2026-08-14T05:04:20.243Z
- Updated: 2026-08-14T05:04:24.2565508Z
- Messages exported: 11

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

BaseLoaderFileReader(CollectionData) :: 데이터 이상!!! Could not convert string to integer: `. Path 'CollectionData[0].CollectionItemDataId'.
위의 에러 발생 원인 확인해 주세요.

### Assistant

에러 문자열이 생성되는 코드와 `CollectionItemDataId`의 정의·입력 파일을 함께 추적해 보겠습니다. 우선 역직렬화 타입과 실제 데이터 첫 행(`CollectionData[0]`)을 대조해 원인을 좁히겠습니다.

### Assistant

현재 확인된 핵심은 `CollectionItemDataId`가 코드상 정수형인데, 로더가 읽은 JSON의 첫 번째 항목에 숫자가 아닌 문자열이 들어왔다는 점입니다. 이제 실제로 어떤 `CollectionData.json`이 선택되는지와 첫 항목 값이 빈 문자열인지 특수문자인지 확인 중입니다.

### Assistant

원본이 `Table_0_Update/CollectionData.xlsx`에서 생성되는 구조임을 확인했습니다. 현재 생성된 JSON들은 첫 항목이 정상(`110001`)이라, 오류 발생 시점의 원본 셀 또는 다른 배포본에만 잘못된 문자가 있었을 가능성이 큽니다. 원본 엑셀의 실제 셀 값·형식을 확인하기 위해 스프레드시트 검사 절차를 적용하겠습니다.

### Assistant

스프레드시트 전용 분석 런타임이 이 워크북을 불러오는 단계에서 결과 없이 종료되어, 해당 절차로는 셀 위치를 확정하지 못했습니다. 원본 파일은 수정하지 않고 XLSX 내부 XML을 읽는 방식으로 동일 값을 교차 확인하겠습니다.

### Assistant

확인 결과, 원인은 `CollectionItemDataId`에 숫자가 아닌 문자열이 들어간 상태로 JSON 역직렬화를 시도한 것입니다.

- `CollectionItemDataId`는 `int`로 선언되어 있습니다: [CollectionData.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/SharedLib/DataManager/DataClass/CollectionData.cs:145)
- JSON 객체를 `CollectionData`로 변환하는 과정에서 예외가 발생합니다: [BaseLoaderFileReader.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/SharedLib/DataManager/BaseLoaderFileReader.cs:140)
- `Path 'CollectionData[0].CollectionItemDataId'`는 배열의 첫 번째 데이터가 문제라는 의미입니다.
- 메시지를 그대로 보면 입력값은 백틱 문자 `` ` ``입니다. 백틱이 메시지 서식용이었다면 빈 문자열이 입력된 경우입니다.

현재 작업본은 정상입니다.

- 기본/업데이트 JSON의 첫 항목 값은 모두 `110001`입니다: [기본 JSON](D:/ProjectA/Trunk/Dev/Client/Assets/ResourceBundles/Data/GameData/CollectionData.json:14), [업데이트 JSON](D:/ProjectA/Trunk/Dev/Client/Assets/ResourceBundles/Data_0_Update/GameData/CollectionData.json:14)
- 전체 ResourceBundles의 `CollectionData.json`을 검사했지만 문자열 형식의 `CollectionItemDataId`는 없었습니다.
- 현재 원본 엑셀에서도 백틱 문자는 발견되지 않았습니다. :codex-file-citation{path="D:/ProjectA/Trunk/Dev/Table_0_Update/CollectionData.xlsx" purpose="source" artifact_kind="workbook"}

따라서 이 오류는 현재 저장소 데이터가 아니라 다음 중 하나에서 발생한 것으로 판단됩니다.

1. 오류 발생 당시 엑셀 첫 데이터 행에 백틱/빈 문자열이 있었고 이후 수정됨
2. 이전 Addressables 빌드 또는 캐시에 잘못된 `CollectionData.json`이 남아 있음
3. 런타임이 현재 파일이 아닌 다른 데이터 버전의 동명 파일을 읽음

특히 런타임은 경로가 아니라 파일명 `CollectionData`만으로 preload 자산을 가져옵니다: [UnityRuntimeDataStream.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/Util/UnityRuntimeDataStream.cs:78). 따라서 Addressables 캐시 제거 후 재빌드하고, 실제 로드된 `TextAsset`의 첫 번째 `CollectionItemDataId`를 출력해 보면 문제 배포본을 확정할 수 있습니다.

### User

기획자분이 엑셀 파일을 올려주셨는데 해당 컬럼에서 잘못된 문자가 포함되어 있는지 확인해 주세요. 어떤 내용인지도 알려주세요.

### Assistant

스프레드시트 검사 절차를 사용해 최근 변경된 `CollectionData` 엑셀을 식별한 뒤, `CollectionItemDataId` 열 전체에서 숫자가 아닌 값·숨은 문자·수식 오류를 확인하겠습니다. 발견되면 시트명, 셀 주소, 행 식별자와 실제 문자 코드까지 알려드리겠습니다.

### Assistant

가장 최근에 올라온 파일은 오늘 14:31에 갱신된 [CollectionData_New.xlsx](D:/ProjectA/Trunk/Dev/Table_1_New/CollectionData_New.xlsx)입니다. 이 파일을 대상으로 셀 저장 형식까지 읽어 `CollectionItemDataId` 열의 비정상 값을 전수 검사하겠습니다.

### Assistant

문제 문자를 찾았습니다. `CollectionData` 시트의 `K2` 셀에 숫자 대신 백틱 한 글자(`, Unicode `U+0060`)가 들어 있습니다. 같은 행의 ID와 주변 필드를 확인해 어떤 데이터인지까지 정리하겠습니다.

### Assistant

확인했습니다. 잘못된 값은 정확히 1건입니다.

- 파일: `Table_1_New/CollectionData_New.xlsx`
- 시트/셀: `CollectionData!K2`
- 행 ID: `110001` (`B2`)
- 현재 값: 백틱 `` ` ``
- 문자 정보: `U+0060`, 길이 1
- 관련 데이터: `CollectionGroupName = Collection_Item_110001`
- 정상 예상값: `110001`

:codex-file-citation{path="D:/ProjectA/Trunk/Dev/Table_1_New/CollectionData_New.xlsx" purpose="source" artifact_kind="workbook" sheet="CollectionData" range="K2"}

비교 파일인 `Table_1_NewUpdate`의 동일 셀에는 정상적으로 `110001`이 들어 있습니다. 따라서 `K2`의 백틱을 `110001`로 교체해야 합니다.

해당 열의 데이터 3,254행을 전수 검사했으며, 이외의 잘못된 문자나 숨은 문자는 발견되지 않았습니다. 파일은 수정하지 않았습니다.
