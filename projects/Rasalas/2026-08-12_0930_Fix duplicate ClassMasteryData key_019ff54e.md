# Fix duplicate ClassMasteryData key

- Project: Rasalas
- Session ID: `019ff54e-ad55-7962-9bd0-6ff06263c974`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-08-12T09:30:02.068Z
- Updated: 2026-08-12T09:30:13.7381761Z
- Messages exported: 7

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

2026.08.12-18.28.54.107 [Info] shc serverMove : _newUserGameDBIdDic add (110), count:0 (ServerMoveDbManager.cs:83)
2026.08.12-18.28.55.608 [Info] SecurityManager filePath:F:\Egon_dev3\Trunk\qa\Server\EgonServer\bin\Debug\net8.0\uncheater\ (SecurityManager.cs:35)
2026.08.12-18.29.06.054 [Error] [HealthSnapshot] reason:ServerStatus loop stall detected. loopGapMs:7853.3 | ThreadPool busyWorker:3/1000(min:100) availWorker:997 availIo:1000/1000 pending:0 poolThreads:4 completed:1300 | GC gen0:3 gen1:2 gen2:1 pauseDeltaMs:277.2 heapMB:1261 [ProcessUpdate() -> LogHealthSnapshot()] (ThreadModel_ServerStatus.cs:173)
Unhandled exception. System.ArgumentException: An item with the same key has already been added. Key: 1
   at System.Collections.Generic.Dictionary`2.TryInsert(TKey key, TValue value, InsertionBehavior behavior)
   at System.Collections.Generic.Dictionary`2.Add(TKey key, TValue value)
   at SharedLib.Data.LoaderClassMasteryData.ReadStreamAfter() in D:\Jenkins\Project\Rasalas\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:line 136
   at SharedLib.Data.DataManager.Load(eRunType loaderRunType, RuntimeTypeModel model, Boolean checkData) in D:\Jenkins\Project\Rasalas\Client\Assets\Script\SharedLib\DataManager\DataManager.cs:line 161
   at K2Server.ServerNodes.NodeConfiguration.Init(eServerType serverType, ServerGroupEntity myServerGroupEntity, Int32 dataLoaderType) in D:\Jenkins\Project\Rasalas\Server\EgonServer\ServerNodes\NodeConfiguration.cs:line 349
   at K2Server.ServerModule.Load(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataLoaderType, Int32 newServerGroupId) in D:\Jenkins\Project\Rasalas\Server\EgonServer\Server\ServerModule.cs:line 458
   at K2Server.Program.OnConsoleStart(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataLoaderType, Int32 newServerGroupId) in D:\Jenkins\Project\Rasalas\Server\EgonServer\Program.cs:line 446
   at K2Server.Program.Main(String[] args) in D:\Jenkins\Project\Rasalas\Server\EgonServer\Program.cs:line 152 이 에러의 발생 원인은 무었인가요?

### Assistant

스택 트레이스가 지목한 `LoaderClassMasteryData.cs:136`의 딕셔너리 구성 로직과 입력 데이터의 키 정의를 확인해서, 직접 원인과 앞선 stall 로그와의 관련성을 구분해 보겠습니다.

### Assistant

현재 작업본에서는 예외가 날 수 있는 핵심 구문이 `_maxClassMasteryExp[MasteryType].Add(MasteryLv, …)`와 `_classMasteryTypeLevelDic[ClassId][MasteryType].Add(MasteryLv, …)`입니다. 즉 `Key: 1`은 마스터리 레벨 1을 같은 딕셔너리에 두 번 넣었다는 뜻일 가능성이 가장 높습니다. 배포 빌드의 136행과 로컬 소스의 행 번호 차이도 함께 확인 중입니다.

### User

먼저 상황을 정확히 공유하지 못하였는데 현재 제 pc에서는 정상적으로 서버가 잘 올라오고 있습니다. 테스트가 필요하여 클라이언트에게 서버 dll 파일과 기획 변환데이터 json, 바이너리 파일을 전달한 상태에서 서버를 실행하였을때 발생한 오류입니다.

### Assistant

추가 상황을 반영하면 “전달한 데이터 자체에 중복 행이 있다”뿐 아니라, 더 유력한 가능성이 하나 있습니다. DLL과 JSON/바이너리 조합 또는 로드 방식 차이로 `ReadStreamAfter()`가 같은 로더 인스턴스에서 두 번 실행되는데, 이 함수가 일부 파생 딕셔너리를 초기화하지 않아 두 번째 실행에서 첫 레벨 키 `1`이 충돌하는 경우입니다. 로드 호출부와 실제 데이터 중복을 나눠 확인하겠습니다.

### Assistant

코드상 서버는 시작 시 바이너리가 아니라 `loadJson`으로 로드하고, Debug에서는 실행 인자 `dataLoaderType=1`이면 일반 `GameData`가 아닌 `../../0_BalanceData/GameData`를 읽습니다. 따라서 전달한 파일이 실제 로드 경로에 들어갔는지와, `LoaderClassMasteryData`가 포함된 공유 DLL까지 같은 빌드로 교체됐는지가 핵심입니다. 특히 신규 마스터리 데이터와 구형 공유 DLL의 조합이면 `MasteryLv=1` 충돌이 정확히 재현될 수 있습니다.

### Assistant

직접 원인은 `ClassMasteryData`를 딕셔너리로 재구성하면서 이미 존재하는 키 `1`을 다시 `Add()`한 것입니다. 여기서 `1`은 정황상 `MasteryLv = 1`일 가능성이 높습니다.

다만 현재 상황에서는 단순 기획 데이터 중복보다 “DLL과 데이터가 서로 다른 버전으로 섞여 배포된 것”이 가장 유력합니다.

핵심 근거는 다음과 같습니다.

- 오류가 발생한 로더는 [LoaderClassMasteryData.cs](E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:108)이며, 이 코드는 `EgonServer.dll`이 아니라 `SharedLib.dll`에 포함됩니다.
- 따라서 `EgonServer.dll`만 전달하고 클라이언트 PC의 `SharedLib.dll`이 구버전이라면, 신규 JSON과 구버전 로더가 함께 실행됩니다.
- 신규 데이터에는 일반 마스터리와 마스터 마스터리 모두 `MasteryLv=1`이 존재합니다. 구버전 로더가 `MasteryType`을 딕셔너리 키에 포함하지 않는 구조라면 두 번째 레벨 1을 넣는 순간 정확히 `Key: 1` 오류가 발생할 수 있습니다.
- 현재 로컬의 일반 및 밸런스 `ClassMasteryData.json`을 검사한 결과 `(ClassId, MasteryType, MasteryLv)` 중복은 없었습니다.

또한 서버의 Develop 실행 경로에서는 [NodeConfiguration.cs](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\NodeConfiguration.cs:345)처럼 JSON을 직접 읽습니다. 전달한 바이너리 파일은 이 시작 경로의 오류와 직접 관련이 없습니다.

Debug 빌드에서는 실행 인자 `dataLoaderType`도 중요합니다.

- `dataLoaderType=0`: `RES_PATH/GameData/`
- `dataLoaderType=1`: `RES_PATH/../../0_BalanceData/GameData/`

서버 로그에 출력되는 다음 줄을 반드시 확인해야 합니다.

```text
gameDataPath : 실제경로, dataLoaderType
```

권장 조치는 다음과 같습니다.

1. 클라이언트에게 `EgonServer.dll`만 전달하지 말고, 동일 빌드에서 생성된 `bin\Debug\net8.0` 전체를 묶어서 전달합니다.
2. 최소한 `EgonServer.dll`, `SharedLib.dll`, `Packet.dll`은 반드시 같은 빌드 결과물이어야 합니다.
3. 로그의 `gameDataPath`에 표시된 실제 경로에 JSON이 배치됐는지 확인합니다.
4. 양쪽 PC에서 아래 파일의 SHA-256을 비교합니다.

```powershell
Get-FileHash .\bin\Debug\net8.0\EgonServer.dll
Get-FileHash .\bin\Debug\net8.0\SharedLib.dll
Get-FileHash .\bin\Debug\net8.0\Packet.dll
Get-FileHash <실제로 읽는 경로>\ClassMasteryData.json
```

결론적으로 가장 가능성 높은 원인은 다음 조합입니다.

```text
신규 ClassMasteryData.json
        +
클라이언트 PC에 남아 있던 구버전 SharedLib.dll
        =
MasteryLv 1 중복 등록 → ArgumentException
```

앞의 `HealthSnapshot loop stall` 로그는 서버 종료의 직접 원인이 아닙니다. 데이터 로딩 중 메인 루프가 약 7.8초 정지했다는 경고이며, 실제 종료 원인은 뒤의 딕셔너리 중복 예외입니다.
