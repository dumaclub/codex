# 로컬 접속 BindServerGroupId 오류

- Project: Astellia
- Session ID: `019fef7d-3a76-76a1-af14-a3bac7702a14`
- Workspace: `E:\ProjectA02\Trunk\Dev`
- Started: 2026-08-11T06:23:09.569Z
- Updated: 2026-08-11T06:23:13.2743759Z
- Messages exported: 6

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

2026.08.11-15.20.10.290 [System] [Gateway(100) => Unknown(1001) ] SendZMQ Send (0, SC_ZMQ_CheckAccountSession) (ServerController.cs:1952)
2026.08.11-15.20.10.291 [System] CheckAccountSession 34 resolve hiveId (2314903192013596787), hiveId (1001) (VisitorThreadManager.cs:272)
2026.08.11-15.20.11.293 [Info] Gateway task : cmdType(GatewayCheckAccountSession), uId(98) (ThreadModel_GatewayWorker.cs:54)
2026.08.11-15.20.11.295 [Error] BindServerGroupId failed, serverGroupId(10) -> interServerGroupId failed [SelectServerGroup() -> BindServerGroupId()] (UserGatewayModel.cs:376)

로컬 접속시 계속 위의 오류 발생되면서 접속이 안되는데 어떤 원인 때문인가요?

### Assistant

로그의 호출 지점과 `serverGroupId(10)` 매핑 경로를 코드에서 추적해 원인을 좁혀보겠습니다. 우선 관련 메서드와 로컬 설정을 함께 확인하겠습니다.

### Assistant

첫 검색은 저장소 규모/제외 규칙 때문에 결과가 나오지 않았습니다. 서버 소스와 설정 디렉터리로 범위를 나눠서 실제 구현과 그룹 ID 정의를 찾겠습니다.

### Assistant

오류 지점은 확인됐습니다. 인증 세션 자체는 성공했고, 이후 선택된 게임 그룹 `10`을 월드(Inter) 그룹으로 변환하는 사전에 키가 없어 실패합니다. 이제 이 사전이 어떤 로컬 데이터에서 구성되는지 추적해, 수정해야 할 설정/DB 항목까지 특정하겠습니다.

### Assistant

현재 실행 중인 서버는 이 작업공간(`E:\ProjectA02`) 빌드가 아니라 `D:\ProjectA\...\EgonServer.exe`입니다. 따라서 실제 실행본의 설정과 시작 로그를 읽기 전용으로 대조해, DB 데이터 문제인지 로컬 개발모드 그룹 선택 문제인지 확인하겠습니다.

### Assistant

원인은 로컬 Global DB의 서버 그룹 매핑 불일치입니다.

현재 실제 접속 흐름은 다음과 같습니다.

- 클라이언트가 게임 서버 그룹 `10` 선택
- Gateway가 `_interServerGroupIdDic`에서 `10 → InterGroup` 매핑 조회
- 로컬 DB의 InterGroup `100`은 `groupInfo='110'`으로 설정됨
- 따라서 사전에는 `110 → 100`만 등록되고 `10` 키가 없어 접속 실패

확인된 로컬 DB 데이터:

```text
게임 그룹:  groupId=10
InterGroup: groupId=100, groupInfo=110   ← 잘못된 값
GlobalGame: groupId=1000, groupInfo=110  ← 이것도 불일치
```

실제 게임/커뮤니티 서버는 모두 그룹 `10`을 사용하고 있습니다.

즉시 수정하려면 로컬 `astellia_global.server_group`에서 최소한 다음 값을 맞춰야 합니다.

```sql
UPDATE server_group
SET groupInfo = '10'
WHERE groupId = 100;
```

GlobalGame도 로컬 그룹 `10`을 사용해야 한다면 함께 수정합니다.

```sql
UPDATE server_group
SET groupInfo = '10'
WHERE groupId = 1000;
```

수정 후에는 서버 그룹 Reload만 하지 말고 `EgonServer`를 재시작하는 것이 안전합니다. 현재 코드상 매핑은 서버 시작 시 [`AddServerGroupInfo()`](/D:/ProjectA/Trunk/Dev/Server/EgonServer/Controllers/ServerController.cs:646)에서 생성되고, 기존 그룹 Reload 시에는 매핑 사전을 다시 구성하지 않습니다.

참고로 현재 실행 중인 서버는 `E:\ProjectA02`가 아니라 `D:\ProjectA`의 실행 파일이며, 설정도 실행 폴더의 `config.txt`가 아니라 `C:\AstelM\config.txt`를 읽고 있습니다. 해당 설정의 DB가 `127.0.0.1/astellia_global`로 확인됐습니다. 인증 세션은 정상 성공했으며 `CheckAccountSession` 로그는 원인이 아닙니다.
