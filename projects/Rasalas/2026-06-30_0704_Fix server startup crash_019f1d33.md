# Fix server startup crash

- Project: Rasalas
- Session ID: `019f1d33-d51c-78e2-b97c-fa71bd8681b7`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-06-30T07:04:32.291Z
- Updated: 2026-06-30T07:04:35.6513221Z
- Messages exported: 7

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

<environment_context>
  <cwd>E:\Rasalas\Trunk\qa</cwd>
  <shell>powershell</shell>
  <current_date>2026-06-30</current_date>
  <timezone>Asia/Seoul</timezone>
  <filesystem><workspace_roots><root>E:\Rasalas\Trunk\qa</root></workspace_roots><permission_profile type="managed"><file_system type="restricted"><entry access="read"><special>:root</special></entry><entry access="write"><path>E:\Rasalas\Trunk\qa</path></entry><entry access="write"><special>:slash_tmp</special></entry><entry access="write"><special>:tmpdir</special></entry><entry access="read"><path>E:\Rasalas\Trunk\qa\.git</path></entry><entry access="read"><path>E:\Rasalas\Trunk\qa\.agents</path></entry><entry access="read"><path>E:\Rasalas\Trunk\qa\.codex</path></entry></file_system></permission_profile></filesystem>
</environment_context>

### User

2026.06.30-16.03.34.537 [Info] databaseInfo Role :accountGameDB, type:Develop, serverGroupId:1 (DbManager.cs:50)
2026.06.30-16.03.34.807 [Info] databaseInfo Role :globalCommunityDB, type:Develop, serverGroupId:1 (DbManager.cs:50)
2026.06.30-16.03.36.350 [Info] SecurityManager filePath:E:\Rasalas\Trunk\qa\Server\EgonServer\bin\Debug\net8.0\uncheater\ (SecurityManager.cs:35)
2026.06.30-16.03.37.268 [Error] BaseLoaderFileReader(StatParameterType) :: 데이터 이상!!! Error converting value "Total_StiffnessResistReduce" to type 'SharedLib.Data.eStatParameterType'. Path 'StatParameterType[203].Id'. [GetDataFromJson() -> DataLoadLogError()] (SLogManager.cs:720)
2026.06.30-16.03.40.771 [Error] !!!BMStore(4032013) - RewardConfirm에 RewardConfirmId(0) 보상 설정 없음!!! [PrintLogError() -> DataLoadLogError()] (SLogManager.cs:720)
Unhandled exception. System.Collections.Generic.KeyNotFoundException: The given key 'Game' was not present in the dictionary.
   at System.Collections.Generic.Dictionary`2.get_Item(TKey key)
   at K2Server.ServerModule.GetMyServerGroupId(eServerType type) in F:\Rasalas_Sub2\Server\EgonServer\Server\ServerModule.cs:line 127
   at K2Server.ServerNodes.TradeNode.Managers.TradeManager.Init() in F:\Rasalas_Sub2\Server\EgonServer\ServerNodes\TradeNode\Managers\TradeManager.cs:line 63
   at K2Server.ServerNodes.NodeConfiguration.Init(eServerType serverType, ServerGroupEntity myServerGroupEntity, Int32 dataLoaderType) in F:\Rasalas_Sub2\Server\EgonServer\ServerNodes\NodeConfiguration.cs:line 361
   at K2Server.ServerModule.Load(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataLoaderType, Int32 newServerGroupId) in F:\Rasalas_Sub2\Server\EgonServer\Server\ServerModule.cs:line 451
   at K2Server.Program.OnConsoleStart(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataLoaderType, Int32 newServerGroupId) in F:\Rasalas_Sub2\Server\EgonServer\Program.cs:line 446
   at K2Server.Program.Main(String[] args) in F:\Rasalas_Sub2\Server\EgonServer\Program.cs:line 152

위의 오류는 어떤 오류인가요?

### Assistant

로그만 봐도 핵심은 `KeyNotFoundException`인데, 원인을 코드 기준으로 더 정확히 찍어보려고 스택에 나온 위치들을 확인해볼게요.

### Assistant

방금 줄 범위 출력 문법이 PowerShell에서 살짝 걸렸어요. 같은 파일을 괄호 범위로 다시 읽어서 실제 접근하는 딕셔너리를 보겠습니다.

### Assistant

확인해보니 기본 인자로 `eServerType.Game`을 조회하고 있고, 개발 모드용 서버 정보 딕셔너리에 `Game` 키가 없어서 바로 터지는 구조입니다. 이제 그 딕셔너리가 어디서 채워지는지도 같이 확인해볼게요.

### Assistant

치명 예외와 별도로 앞쪽의 데이터 로드 오류 2개도 보입니다. 이 둘은 서버를 바로 죽인 스택은 아니지만, 데이터 테이블/JSON 쪽에서 따로 고쳐야 할 가능성이 큽니다.

### Assistant

핵심 오류는 **`KeyNotFoundException`**, 즉 딕셔너리에서 `Game` 키를 찾지 못한 오류입니다.

스택 기준으로는:

- [TradeManager.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/TradeNode/Managers/TradeManager.cs:63) 에서 `ServerModule.Instance.GetMyServerGroupId()` 호출
- 기본 인자가 `eServerType.Game`
- [ServerModule.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Server/ServerModule.cs:127) 에서 개발 모드용 `_developServerInfoDic[type]` 접근
- 그런데 `_developServerInfoDic` 안에 `Game` 키가 없어서 서버가 죽었습니다.

즉 직접 원인은:

```text
개발 모드 서버 정보 딕셔너리에 eServerType.Game 서버 정보가 없음
```

확인할 것은 DB/설정 쪽입니다.

- `ServerInfo` 테이블에 `type = Game` 서버가 `Open` 상태로 있는지
- 해당 `Game` 서버의 `groupId`가 기본 `GameGroup` 또는 실행 시 지정한 `newServerGroupId`와 맞는지
- 기동 로그에 `_developServerInfoDic.Add(Game, ...)` 가 찍히는지
- Trade/Community 등을 띄우는 개발 모드에서 참조할 Game 서버 정보가 누락되지 않았는지

그리고 위쪽의 두 에러도 별도 데이터 오류입니다.

```text
Total_StiffnessResistReduce -> eStatParameterType enum 변환 실패
BMStore(4032013) -> RewardConfirmId(0) 보상 설정 없음
```

다만 서버를 실제로 종료시킨 치명 오류는 마지막의 `KeyNotFoundException: The given key 'Game' was not present in the dictionary.` 입니다.
