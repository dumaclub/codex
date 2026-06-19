# Fix uncheater DLL load failure

- Project: Astellia
- Session ID: `019ed350-be50-75f2-ba7f-c16bf8d7add8`
- Workspace: `E:\ProjectA02\Trunk\Dev`
- Started: 2026-06-17T02:02:24.720Z
- Updated: 2026-06-17T02:02:32.5788775Z
- Messages exported: 5

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

<environment_context>
  <cwd>E:\ProjectA02\Trunk\Dev</cwd>
  <shell>powershell</shell>
  <current_date>2026-06-17</current_date>
  <timezone>Asia/Seoul</timezone>
  <filesystem><workspace_roots><root>E:\ProjectA02\Trunk\Dev</root></workspace_roots><permission_profile type="managed"><file_system type="restricted"><entry access="read"><special>:root</special></entry><entry access="write"><path>E:\ProjectA02\Trunk\Dev</path></entry><entry access="write"><special>:slash_tmp</special></entry><entry access="write"><special>:tmpdir</special></entry><entry access="read"><path>E:\ProjectA02\Trunk\Dev\.git</path></entry><entry access="read"><path>E:\ProjectA02\Trunk\Dev\.agents</path></entry><entry access="read"><path>E:\ProjectA02\Trunk\Dev\.codex</path></entry></file_system></permission_profile></filesystem>
</environment_context>

### User

5|Gateway02         | 2026.06.17-10.01.38.626 [System] InfoDbManager: Registered loader [InfoDBPveDungeonServerGroup] table=[pve_dungeon_server_group] (E:\ProjectA02\Trunk\Dev\Server\EgonServer\Managers\InfoDbManager.cs:127)
0|Gateway01         | 2026.06.17-10.01.39.181 [System] uncheater xmlDir : ./uncheater/, license:sTFcppdbtNrmKR, fielPath : /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater/ (E:\ProjectA02\Trunk\Dev\Server\EgonServer\ServerNodes\GatewayNode\Managers\Securi
0|Gateway01         | tyManager.cs:26)
0|Gateway01         | Unhandled exception.
0|Gateway01         |  
0|Gateway01         | System.DllNotFoundException: Unable to load shared library 'uncheater_server_x64.so' or one of its dependencies. In order to help diagnose loading problems, consider using a tool like strace. If you're using glibc, consider setting the LD_DEBUG environment variable: 
0|Gateway01         | /usr/lib64/dotnet/shared/Microsoft.NETCore.App/8.0.15/uncheater_server_x64.so: cannot open shared object file: No such file or directory
0|Gateway01         | /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater_server_x64.so: cannot open shared object file: No such file or directory
0|Gateway01         | /usr/lib64/dotnet/shared/Microsoft.NETCore.App/8.0.15/libuncheater_server_x64.so: cannot open shared object file: No such file or directory
0|Gateway01         | /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/libuncheater_server_x64.so: cannot open shared object file: No such file or directory
0|Gateway01         | /usr/lib64/dotnet/shared/Microsoft.NETCore.App/8.0.15/uncheater_server_x64.so.so: cannot open shared object file: No such file or directory
0|Gateway01         | /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater_server_x64.so.so: cannot open shared object file: No such file or directory
0|Gateway01         | /usr/lib64/dotnet/shared/Microsoft.NETCore.App/8.0.15/libuncheater_server_x64.so.so: cannot open shared object file: No such file or directory
0|Gateway01         | /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/libuncheater_server_x64.so.so: cannot open shared object file: No such file or directory
0|Gateway01         |    at uncheater_server_cs.UncheaterServer.BinderLinux64.UncServerInit(String license, String dir)
0|Gateway01         |    at uncheater_server_cs.UncheaterServer.Binder.UncServerInit(String license, String dir)
0|Gateway01         |    at uncheater_server_cs.UncheaterServer.UncServerInit(String license, String dir)
0|Gateway01         |    at K2Server.ServerNodes.GatewayNode.Managers.SecurityManager.Init() in E:\ProjectA02\Trunk\Dev\Server\EgonServer\ServerNodes\GatewayNode\Managers\SecurityManager.cs:line 30
0|Gateway01         |    at K2Server.ServerNodes.NodeConfiguration.Init(eServerType serverType, ServerGroupEntity myServerGroupEntity, Int32 dataLoaderType) in E:\ProjectA02\Trunk\Dev\Server\EgonServer\ServerNodes\NodeConfiguration.cs:line 217
0|Gateway01         |    at K2Server.ServerModule.Load(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataloadeType, Int32 newServerGroupId) in E:\ProjectA02\Trunk\Dev\Server\EgonServer\Server\ServerModule.cs:line 446
0|Gateway01         |    at K2Server.Program.OnConsoleStart(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataloadeType, Int32 newServerGroupId) in E:\ProjectA02\Trunk\Dev\Server\EgonServer\Program.cs:line 194
0|Gateway01         |    at K2Server.Program.Main(String[] args) in E:\ProjectA02\Trunk\Dev\Server\EgonServer\Program.cs:line 165
5|Gateway02         | 2026.06.17-10.01.39.356 [System] InfoDBDominationMatch.Reload() channels:2, serverGroups:2 (E:\ProjectA02\Trunk\Dev\Server\EgonServer\Managers\InfoDb\InfoDBBase.cs:58)
5|Gateway02         | 2026.06.17-10.01.39.415 [System] InfoDBPveDungeonServerGroup.Reload() count:2 (E:\ProjectA02\Trunk\Dev\Server\EgonServer\Managers\InfoDb\InfoDBBase.cs:58)
5|Gateway02         | 2026.06.17-10.01.39.416 [System] NodeConfiguration Init serverType:Gateway, serverGroup:interGroup1 (E:\ProjectA02\Trunk\Dev\Server\EgonServer\ServerNodes\NodeConfiguration.cs:44)
5|Gateway02         | 2026.06.17-10.01.39.416 [Info] gameDataPath : ../../../../../../Client/Assets/ResourceBundles/Data/../../1_NFTData/GameData/, nftDataPath : ../../../../../../Client/Assets/ResourceBundles/Data/../../1_NFTData/, 2 (E:\ProjectA02\Trunk\Dev\Server\EgonServer\ServerNodes\NodeConfiguration.cs:60)
PM2                 | App [Gateway01:0] exited with code [0] via signal [SIGABRT]  이것은 무슨 에러인가요?

### Assistant

이건 **C#/.NET 서버가 네이티브 라이브러리 `.so` 파일을 못 찾아서 Gateway01이 죽은 에러**입니다.

핵심 에러는 이 부분입니다:

```text
System.DllNotFoundException: Unable to load shared library 'uncheater_server_x64.so'
```

즉 `SecurityManager.Init()`에서:

```text
UncheaterServer.UncServerInit(...)
```

를 호출하는데, 내부적으로 Linux용 네이티브 라이브러리인 `uncheater_server_x64.so`를 로드하려다가 실패했습니다.

.NET이 찾으려고 한 경로는 주로 여기입니다:

```text
/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater_server_x64.so
/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/libuncheater_server_x64.so
```

그런데 파일이 없어서 Gateway01 프로세스가 `SIGABRT`로 종료된 상태입니다.

가능한 원인은 보통 이 셋 중 하나입니다.

1. `uncheater_server_x64.so` 파일이 배포 폴더에 없음
2. 파일은 있는데 그 `.so`가 필요로 하는 다른 Linux 라이브러리가 없음
3. `.so` 파일이 `Gateway01/uncheater/` 같은 하위 폴더에 있는데, .NET 로더 검색 경로에는 안 잡힘

확인 명령 예시는 서버에서:

```bash
find /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01 -name '*uncheater*'
ldd /path/to/uncheater_server_x64.so
```

해결은 보통 `uncheater_server_x64.so`를 Gateway 실행 파일이 있는 위치, 즉:

```text
/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/
```

에 같이 배포하거나, 실제 `.so`가 있는 폴더를 `LD_LIBRARY_PATH`에 추가하면 됩니다. 파일이 있는데도 같은 에러가 나면 `ldd`로 누락된 의존 라이브러리를 봐야 합니다.

### User

LD_LIBRARY_PATH 에 어떻게 추가하나요?

### Assistant

`LD_LIBRARY_PATH`에는 **`.so` 파일이 들어있는 디렉터리**를 추가하면 됩니다. 파일 경로 자체가 아니라 폴더 경로입니다.

예를 들어 실제 파일이 여기 있다면:

```bash
/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater/uncheater_server_x64.so
```

이렇게 추가합니다:

```bash
export LD_LIBRARY_PATH=/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater:$LD_LIBRARY_PATH
```

그 다음 같은 터미널에서 서버를 실행해야 적용됩니다.

PM2로 실행 중이면 보통 이렇게 합니다:

```bash
export LD_LIBRARY_PATH=/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater:$LD_LIBRARY_PATH
pm2 restart Gateway01 --update-env
```

먼저 파일 위치는 이렇게 확인하세요:

```bash
find /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01 -name '*uncheater_server_x64*'
```

PM2 `ecosystem.config.js`를 쓰고 있다면 더 안정적으로는 env에 넣습니다:

```js
module.exports = {
  apps: [
    {
      name: "Gateway01",
      script: "...",
      env: {
        LD_LIBRARY_PATH: "/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/uncheater"
      }
    }
  ]
}
```

수정 후:

```bash
pm2 restart Gateway01 --update-env
```

주의할 점은 `export LD_LIBRARY_PATH=...`는 **현재 쉘 세션에만 적용**됩니다. PM2가 이미 떠 있던 환경에서 실행된 프로세스에는 자동 적용되지 않으므로 `--update-env`가 중요합니다.
