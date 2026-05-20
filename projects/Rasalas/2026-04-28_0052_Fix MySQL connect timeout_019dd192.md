# Fix MySQL connect timeout

- Project: Rasalas
- Session ID: `019dd192-b533-7f93-9055-6b030be1e591`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-04-28T00:52:26.082Z
- Updated: 2026-04-28T00:52:32.7106328Z
- Messages exported: 26

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

ServerType : Database
ServerName : KR_Database_05
ServerID : 305
IP : 10.0.5.185
ZmqIP : 10.0.5.185
1Exception : query error => NHibernate.TransactionException: Begin failed with SQL exception
 ---> MySql.Data.MySqlClient.MySqlException (0x80004005): Unable to connect to any of the specified MySQL hosts.
 ---> MySql.Data.MySqlClient.MySqlException (0x80004005): Timeout expired.  The timeout period elapsed prior to completion of the operation or the server is not responding.
 ---> System.TimeoutException: The operation has timed out.
   at MySql.Data.Common.StreamCreator.GetTcpStreamAsync(MySqlConnectionStringBuilder settings, CancellationToken cancellationToken, Boolean execAsync)
   at MySql.Data.Common.StreamCreator.GetStreamAsync(MySqlConnectionStringBuilder settings, CancellationToken cancellationToken, Boolean execAsync)
   at MySql.Data.MySqlClient.NativeDriver.OpenAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.NativeDriver.OpenAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.Driver.OpenAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.Driver.CreateAsync(MySqlConnectionStringBuilder settings, Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.Driver.CreateAsync(MySqlConnectionStringBuilder settings, Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.MySqlPool.CreateNewPooledConnectionAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.MySqlPool.GetPooledConnectionAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.MySqlPool.TryToGetDriverAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.MySqlPool.GetConnectionAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.MySqlConnection.OpenAsync(Boolean execAsync, CancellationToken cancellationToken)
   at MySql.Data.MySqlClient.MySqlConnection.Open()
   at NHibernate.Connection.DriverConnectionProvider.GetConnection(String connectionString)
   at NHibernate.AdoNet.ConnectionManager.GetConnection()
   at NHibernate.Transaction.AdoTransaction.Begin(IsolationLevel isolationLevel)
   --- End of inner exception stack trace ---
   at NHibernate.Transaction.AdoTransaction.Begin(IsolationLevel isolationLevel)
   at NHibernate.Impl.AbstractSessionImpl.BeginTransaction(IsolationLevel isolationLevel)
   at K2Server.Database.UnitOfWork.Init() in D:\Rasalas\Rasalas_KR\Server\EgonServer\Database\UnitOfWork.cs:line 41
   at K2Server.Controllers.DatabaseController.SelectOne[T](Expression`1 expression) in D:\Rasalas\Rasalas_KR\Server\EgonServer\Controllers\DatabaseController.cs:line 229

위의 에러는 어떤 경우에 발생되는 건가요? 원인도 같이 확인해 주세요.

### Assistant

로그 기준으로는 애플리케이션 쪽 쿼리 문법보다 MySQL TCP 연결 자체가 열리지 않는 케이스에 가깝습니다. 코드/설정에서 연결 문자열이나 타임아웃 설정을 같이 보면 더 정확히 원인 범위를 좁힐 수 있어서 관련 위치를 먼저 찾아보겠습니다.

### Assistant

전체 검색은 패키지/Unity 임시 파일까지 타면서 너무 넓게 걸렸습니다. 이제 스택트레이스에 나온 `Server\EgonServer` 쪽만 좁혀서, 실제 연결 문자열을 어떻게 만들고 트랜잭션을 어디서 여는지 확인하겠습니다.

### Assistant

스택 경로를 보면 `UnitOfWork.Init()`에서 `BeginTransaction()`을 호출하는 순간 NHibernate가 세션 연결을 확보하려다 실패합니다. 연결 문자열 생성부도 같이 보니 `DatabaseInfoEntity`의 `ip/writeIp/readIp` 기반으로 `Server=...;Port=3306;Database=...`를 조립하는 구조입니다. 실제 대상 `10.0.5.185:3306` 포트가 이 실행 환경에서 열리는지도 간단히 확인해 보겠습니다.

### Assistant

`Test-NetConnection`도 20초 안에 응답을 못 받아 타임아웃이 났습니다. 이 작업 PC/환경에서 바로 판단하면 `10.0.5.185:3306`이 닫혀 있거나 라우팅/방화벽에서 막히는 증상과 일치합니다. 마지막으로 호출 흐름과 풀 초기화 부분만 더 확인해서 “왜 BeginTransaction에서 보이는지”까지 정리하겠습니다.

### Assistant

원인은 **DB 쿼리 실패가 아니라 MySQL 서버 접속 실패**입니다.

로그 흐름은 이렇습니다.

- `DatabaseController.SelectOne()`에서 read DB 풀을 가져옴  
  [DatabaseController.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Controllers/DatabaseController.cs:229)
- `DbPool.Get()`이 `work.Init()` 호출  
  [DbPool.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Database/DbPool.cs:43)
- `UnitOfWork.Init()`에서 `Session.BeginTransaction()` 실행  
  [UnitOfWork.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Database/UnitOfWork.cs:53)
- 이 순간 NHibernate가 MySQL 커넥션을 열려고 했지만 `10.0.5.185` 접속이 타임아웃됨

핵심 에러는 이 부분입니다.

```text
Unable to connect to any of the specified MySQL hosts.
Timeout expired.
The operation has timed out.
```

즉 발생 조건은 보통 아래 중 하나입니다.

1. `KR_Database_05 / 10.0.5.185` 서버가 내려가 있음
2. MySQL 데몬이 죽었거나 `3306` 포트 리스닝 안 함
3. DB 서버 방화벽, 보안그룹, ACL, 네트워크 라우팅 문제
4. 애플리케이션 서버에서 `10.0.5.185:3306` 접근 불가
5. 설정의 `readIp`가 잘못되었거나, read DB만 장애
6. MySQL `max_connections` 초과 또는 서버 부하로 신규 연결을 못 받음

제가 현재 작업 환경에서 `10.0.5.185:3306`도 확인해 봤는데 `Test-NetConnection`이 20초 내 응답 없이 타임아웃됐습니다. 이 환경 기준으로는 해당 포트가 열려 있다고 확인되지 않습니다.

추가로 코드상 write 연결 문자열에는 `Connection Timeout=60`이 붙지만 read 연결 문자열에는 없습니다. 해당 에러는 `SelectOne()`에서 read endpoint를 쓰는 중 발생했으므로, read 쪽은 기본 연결 타임아웃으로 실패했을 가능성이 큽니다. 우선 DB 서버에서 MySQL 상태와 3306 포트, 그리고 애플리케이션 서버에서 `10.0.5.185:3306` 접근 가능 여부를 확인하는 게 1순위입니다.

### User

라이브에서 활성화 되어 있는 서버 목록입니다. type 값이 5인 서버들 모두 위에 전달드린 Exception 이 발생되었습니다. 공통원인으로 찾아볼 수 있는게 있나요?

[Image attached: base64 payload omitted]

### Assistant

type 5가 전부 Database 노드로 보이고, 공통으로 같은 MySQL 연결 타임아웃이면 개별 DB 머신 장애보다 “DB 노드들이 공통으로 참조하는 대상/경로”를 먼저 의심하는 게 맞습니다. 서버 타입 매핑과 DB 초기화 흐름을 조금 더 확인해서 공통 지점을 짚어보겠습니다.

### Assistant

`DbManager` 기준으로 Database 노드(type 5)는 global DB의 `database_info` 목록을 읽어서 game/community/trade/manager/log/payment/event/account/global-community DB 컨트롤러를 모두 초기화합니다. 그래서 type 5 전체에서 동시에 같은 에러면, 각 type 5 프로세스 자체보다 그들이 공통으로 접속하는 MySQL IP/포트 또는 `database_info` 설정 쪽 가능성이 큽니다.

### Assistant

네. **type=5 서버 전체에서 동일한 `Unable to connect ... Timeout`이면 공통 원인으로는 `server_info`보다 `database_info` 쪽을 먼저 봐야 합니다.**

코드상 type 5, 즉 `eServerType.Database` 노드는 기동 시 global DB에서 `DatabaseInfoEntity` 목록을 읽고, 각 row의 `writeIp/readIp/port/dbName`으로 MySQL 연결 풀을 만듭니다.

관련 흐름:

- global DB 접속: [ServerModule.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Server/ServerModule.cs:362)
- `database_info` 전체 조회: [DbManager.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Managers/DbManager.cs:41)
- `DatabaseController.Init(databaseInfo, ...)` 호출: [DbManager.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Managers/DbManager.cs:65)
- 실제 연결 문자열 생성: [DatabaseController.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Controllers/DatabaseController.cs:72)

따라서 공통 원인 후보는 아래 순서로 보는 게 좋습니다.

1. **global DB의 `database_info`에 등록된 `readIp/writeIp/port`가 잘못됨**
   - 지금 보여주신 건 `server_info`입니다.
   - 실제 MySQL 접속 대상은 `database_info`입니다.
   - 특히 에러는 `SelectOne()`에서 read endpoint를 쓰다가 발생했으므로 `readIp` 확인이 중요합니다.

2. **type=5 Database 서버들이 공통으로 접근해야 하는 MySQL 3306 포트가 막힘**
   - 방화벽, 보안그룹, ACL, 라우팅, VPN/서브넷 문제
   - 모든 type=5에서 동시에 발생했다면 개별 DB보다는 네트워크 정책 변경 가능성이 큽니다.

3. **MySQL 서비스가 각 DB 호스트에서 내려갔거나 3306 리스닝이 안 됨**
   - `KR_Database_01~05`가 각각 `10.0.1.139`, `10.0.2.231`, `10.0.1.83`, `10.0.5.36`, `10.0.5.185`라면 각 장비에서 MySQL 상태 확인 필요합니다.

4. **DB 접속 계정/비밀번호 문제는 가능성이 낮음**
   - 계정 오류면 보통 `Access denied for user`가 나옵니다.
   - 현재는 `Timeout expired`, `Unable to connect`라서 인증 전 TCP 연결 단계에서 막힌 증상입니다.

5. **read/write IP 불일치**
   - 코드상 write 연결 문자열에는 `Connection Timeout=60`이 붙지만 read 연결 문자열에는 없습니다.
   - `SelectOne()`은 read DB를 사용합니다.
   - `database_info.readIp`가 빈 값, 잘못된 IP, VIP 장애, replica 장애라면 전체 조회성 쿼리에서 같은 예외가 납니다.

확인 쿼리는 이쪽이 핵심입니다.

```sql
SELECT id, serverId, serverGroupId, role, dbName, writeIp, readIp, port
FROM rasalas_global.database_info
WHERE state = 1
ORDER BY role, serverGroupId, serverId;
```

그리고 각 type=5 서버에서 다음 확인이 필요합니다.

```powershell
Test-NetConnection 10.0.5.185 -Port 3306
Test-NetConnection 10.0.5.36 -Port 3306
Test-NetConnection 10.0.2.231 -Port 3306
Test-NetConnection 10.0.1.139 -Port 3306
Test-NetConnection 10.0.1.83 -Port 3306
```

정리하면, **공통 원인은 “Database 서버 프로세스 장애”라기보다 type=5 노드들이 공통으로 읽는 `database_info`의 MySQL 접속 대상 또는 3306 네트워크 경로 장애**일 가능성이 가장 큽니다.

### User

databaseinfo 정보입니다. writeIp와 readIp 모두 동일하고 같은 포트를 사용하고 있습니다. 현재 서비스 중인데 금일 오전에 갑자기 모든 database node 들에게서 동일한 오류가 발생되었습니다. 계정과 패스워도드 모두 동일하며 라이브 서비스 중이였기 때문에 전혀 문제가 없었습니다. aws 를 사용하다 tencent cloud 로 넘어오고 처음 발생되는 현상입니다. aws 에서는 2년동안 한번도 발생된적이 없는 오류였습니다.

[Image attached: base64 payload omitted]

### Assistant

네, 이 정보면 원인이 훨씬 좁혀집니다.

`databaseinfo`의 모든 DB role이 사실상 **단일 MySQL 엔드포인트 `10.0.100.7:3306`**를 바라보고 있습니다. 그래서 모든 type=5 Database node에서 같은 예외가 동시에 발생했다면, 공통 원인은 거의 이쪽입니다.

```text
10.0.100.7:3306 접속 경로 또는 해당 MySQL 인스턴스 문제
```

계정/패스워드 문제 가능성은 낮습니다. 인증 문제면 보통 `Access denied for user`가 나오는데, 지금은 `Timeout expired`, `Unable to connect`라서 **인증 전 TCP 연결 단계에서 응답을 못 받은 상황**입니다.

가장 의심되는 순서는 이렇습니다.

1. **Tencent Cloud 보안그룹 / 네트워크 ACL / 라우팅 문제**
   - Database node들이 있는 서브넷에서 `10.0.100.7:3306`으로 가는 트래픽이 순간적으로 막혔을 가능성
   - AWS에서 2년간 없었다면 Tencent 전환 후 VPC, SG, ACL, CDB whitelist 정책 차이를 먼저 봐야 합니다.

2. **`10.0.100.7` MySQL 인스턴스의 connection limit / backlog / 과부하**
   - 모든 DB가 한 host/port로 몰려 있습니다.
   - 오전 특정 시간에 접속 증가, 재접속 폭증, batch, log flush, 백업, 점검, failover가 겹치면 신규 TCP 연결이 timeout 날 수 있습니다.
   - MySQL `max_connections` 초과면 경우에 따라 명확한 MySQL 에러가 아니라 클라이언트 쪽 connect timeout처럼 보일 수 있습니다.

3. **Tencent Cloud CDB/CLB/VIP 계층의 일시 장애 또는 failover**
   - `10.0.100.7`이 TencentDB 사설 VIP라면, 내부 failover/maintenance/HA 전환 중 짧게 연결 timeout이 발생할 수 있습니다.
   - AWS RDS와 Tencent CDB의 failover/idle/session 처리 방식 차이도 확인 대상입니다.

4. **DB 서버 OS 레벨 리소스 고갈**
   - self-hosted MySQL이면 파일 디스크립터, SYN backlog, conntrack, accept queue, CPU steal, I/O wait 확인 필요합니다.
   - 특히 `nf_conntrack table full`, `Too many open files`, `max_connections` 근처 로그가 있으면 거의 정답입니다.

바로 확인할 항목은 이겁니다.

```sql
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Max_used_connections';
SHOW GLOBAL STATUS LIKE 'Aborted_connects';
SHOW GLOBAL STATUS LIKE 'Connection_errors%';
SHOW VARIABLES LIKE 'max_connections';
SHOW PROCESSLIST;
```

각 Database node 서버에서는 장애 시간대에 아래가 성공했는지 확인하세요.

```powershell
Test-NetConnection 10.0.100.7 -Port 3306
```

또는 Linux라면:

```bash
nc -vz 10.0.100.7 3306
mysql -h 10.0.100.7 -P 3306 -u admin -p -e "select 1"
```

Tencent Console에서는 장애 발생 시간 기준으로 다음을 보시면 됩니다.

- CDB/MySQL connection count
- CPU, memory, IOPS, slow query, active sessions
- `max_connections` 도달 여부
- failover / HA switch / maintenance event
- 보안그룹 변경 이력
- VPC ACL / route table 변경 이력
- DB whitelist에 Database node 서브넷이 모두 포함되어 있는지

정리하면, 지금 케이스는 **각 Database node의 개별 문제가 아니라 모든 노드가 공통으로 바라보는 `10.0.100.7:3306`의 네트워크 또는 MySQL 수용 능력 문제**로 보는 게 맞습니다. Tencent Cloud 전환 후 처음 발생했다면, 저는 1순위로 **Tencent CDB/VPC 보안 정책 또는 CDB connection/failover 이벤트**, 2순위로 **단일 MySQL 엔드포인트에 대한 연결 폭주/connection limit**을 보겠습니다.

### User

이게 좀 의심스러운 점은 dbnode 서버에 dbnode 하나의 프로세스만 떠 있는것이 아니라 game 서버, community 서버, trade 서버도 있습니다. 다른 서버들도 db 커넥션이 있는데 dbnode 만 발생하였다는게 조금 이상한 점입니다.

[Image attached: base64 payload omitted]

[Image attached: base64 payload omitted]

### User

<turn_aborted>
The user interrupted the previous turn on purpose. Any running unified exec processes may still be running in the background. If any tools/commands were aborted, they may have partially executed.
</turn_aborted>

### User

Variable_name	Value
Threads_connected	262

Variable_name	Value
Max_used_connections	304

Variable_name	Value
Aborted_connects	265

Variable_name	Value
Connection_errors_accept	0
Connection_errors_internal	0
Connection_errors_max_connections	0
Connection_errors_peer_address	0
Connection_errors_select	0
Connection_errors_tcpwrap	0

Variable_name	Value
max_connections	16500

이게 좀 의심스러운 점은 dbnode 서버에 dbnode 하나의 프로세스만 떠 있는것이 아니라 game 서버, community 서버, trade 서버도 있습니다. 다른 서버들도 db 커넥션이 있는데 dbnode 만 발생하였다는게 조금 이상한 점입니다.

[Image attached: base64 payload omitted]

[Image attached: base64 payload omitted]

### Assistant

맞습니다. **같은 VM 안의 game/community/trade는 정상인데 dbnode 프로세스만 발생**했다면, 단순한 `10.0.100.7:3306` 전체 네트워크 차단 가능성은 낮아집니다.

이 경우 공통 원인은 “서버 머신”보다 **dbnode 프로세스의 DB 사용 패턴** 쪽으로 좁혀보는 게 맞습니다.

가장 가능성 높은 시나리오는 이겁니다.

**1. dbnode만 신규 커넥션 생성/재생성이 몰림**

현재 `SHOW PROCESSLIST`에는 정상 Sleep 커넥션이 보입니다. 즉 DB가 완전히 막힌 상태는 아닙니다. 그런데 예외는 `BeginTransaction()` 시점에 MySQL 커넥션을 새로 열다가 timeout 난 것입니다.

즉 기존 연결은 살아 있는데, 특정 순간 dbnode가 새 커넥션을 만들거나 끊긴 pooled session을 재연결하려다 실패했을 수 있습니다.

특히 코드상 `Database` 타입은 [DbManager.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Managers/DbManager.cs:41)에서 `databaseinfo` 전체를 순회하면서 여러 DB role을 초기화합니다.

type 5는 다음 role들을 많이 물고 갑니다.

```text
gameDB
communityDB
manageDB
logDB
eventDB
accountGameDB
globalCommunityDB
infoDB
```

반면 game/community/trade 프로세스는 자기 역할에 필요한 일부 DB만 사용합니다. 그래서 같은 서버에 떠 있어도 **dbnode가 훨씬 많은 DB pool/session을 만들고, 요청도 집중해서 처리**합니다.

**2. dbnode가 중앙 DB worker라 요청 부하가 몰림**

game/community/trade가 직접 DB 커넥션을 갖고 있어도, 많은 실제 DB 작업은 ZMQ로 Database node에 위임되는 구조로 보입니다. 그래서 오전 특정 시점에 유저 접속, 이벤트, 정산, 로그, 랭킹, 우편, 길드 같은 요청이 몰리면 dbnode만 커넥션 재확보가 폭증할 수 있습니다.

현재 지표도 `max_connections=16500`, `Max_used_connections=304`라서 MySQL 전체 connection limit은 아닙니다. 즉 **DB max_connections 부족은 거의 아닙니다.**

**3. Tencent 환경에서 TCP 재연결/idle connection 처리 차이**

AWS에서 없었고 Tencent 이전 후 처음이라면 이게 꽤 수상합니다.

가능한 케이스:

```text
Tencent CDB/VPC/LB가 idle TCP connection을 더 빨리 정리
dbnode의 NHibernate/MySql.Data pool이 죽은 연결을 들고 있다가 재사용
재사용 실패 후 새 연결 시도
특정 순간 재연결이 몰리며 일부 timeout
```

이 경우 game/community/trade는 연결 수나 요청 빈도가 낮아서 안 터지고, dbnode만 터질 수 있습니다.

**4. dbnode 프로세스 단위 리소스 문제**

같은 VM이어도 프로세스별로 차이가 납니다.

확인할 것:

```bash
ulimit -n
ls /proc/34243/fd | wc -l
ss -tanp | grep 34243 | wc -l
ss -tanp | grep 10.0.100.7:3306
ss -s
dmesg | egrep -i "conntrack|syn|tcp|too many open files|reset"
```

특히 장애 시점에 dbnode PID 기준으로 아래 상태가 많았는지 보세요.

```text
SYN-SENT
TIME-WAIT
CLOSE-WAIT
ESTABLISHED 과다
```

**지금 결론**

현재 정보 기준으로는 “DB 계정/패스워드/전체 DB 장애”보다는 아래 쪽이 더 그럴듯합니다.

```text
dbnode 프로세스에만 DB 요청/재연결이 집중됨
+ Tencent Cloud 환경에서 MySQL TCP idle/reconnect/네트워크 처리 특성이 AWS와 다름
+ 순간적으로 dbnode의 MySql.Data/NHibernate 연결 재확보가 timeout
```

바로 보고 싶은 쿼리는 이겁니다.

```sql
SELECT SUBSTRING_INDEX(Host, ':', 1) AS host, db, Command, COUNT(*) cnt
FROM information_schema.PROCESSLIST
GROUP BY SUBSTRING_INDEX(Host, ':', 1), db, Command
ORDER BY cnt DESC;
```

그리고 장애 시간대 dbnode 로그에서 `query error` 직전에 요청이 몰린 packet/handler가 같은지 확인하면 좋습니다. 같은 handler나 같은 DB role에서 집중 발생했다면 네트워크 전체 문제가 아니라 **dbnode 특정 DB pool 또는 특정 업무 부하**로 거의 좁혀집니다.

### User

아래는 요청하신 쿼리 결과입니다. 

host	db	Command	cnt
10.0.1.139	rasalas_w01_g73	Sleep	20
10.0.1.139	rasalas_w01_g71	Sleep	16
10.0.5.36	rasalas_w01_g72	Sleep	12
10.0.1.139	rasalas_account_game	Sleep	11
10.0.2.231	rasalas_w01_g01_01	Sleep	8
10.0.5.36	rasalas_account_game	Sleep	7
10.0.2.231	rasalas_w01_g03_01	Sleep	6
10.0.5.185	rasalas_w01_g01_04	Sleep	6
10.0.1.139	rasalas_global	Sleep	6
10.0.1.83	rasalas_w01_g01_02	Sleep	6
10.0.5.36	rasalas_w01_g03_03	Sleep	6
10.0.2.231	rasalas_account_game	Sleep	5
10.0.5.36	rasalas_global	Sleep	5
10.0.1.83	rasalas_account_game	Sleep	4
10.0.5.185	rasalas_account_game	Sleep	4
10.0.5.36	rasalas_w01_g01_03	Sleep	4
10.0.5.185	rasalas_w01_g03_04	Sleep	4
10.0.1.83	rasalas_w01_g03_02	Sleep	4
10.0.1.83	rasalas_global	Sleep	3
10.0.2.231	rasalas_global	Sleep	3
10.0.5.36	rasalas_w01_community71	Sleep	2
10.0.5.36	rasalas_w01_community01	Sleep	2
10.0.1.139	rasalas_w01_community72	Sleep	2
10.0.2.231	rasalas_w01_community73	Sleep	2
10.0.5.185	rasalas_w01_community73	Sleep	2
10.0.1.83	rasalas_w01_community73	Sleep	2
10.0.1.139	rasalas_w01_log_73_new	Sleep	2
10.0.5.36	rasalas_w01_log_72_new	Sleep	2
10.0.5.36	rasalas_w01_community72	Sleep	2
10.0.5.185	rasalas_w01_community72	Sleep	2
10.0.1.83	rasalas_gloabl_trade_02	Sleep	2
10.0.1.139	rasalas_gloabl_trade_01	Sleep	2
10.0.1.83	rasalas_w01_community71	Sleep	2
10.0.1.83	rasalas_w01_community01	Sleep	2
10.0.5.36	rasalas_w01_community03	Sleep	2
10.0.5.185	rasalas_w01_community01	Sleep	2
10.0.1.83	rasalas_w01_community03	Sleep	2
10.0.5.185	rasalas_global	Sleep	2
10.0.1.139	rasalas_w01_community73	Sleep	2
10.0.1.139	rasalas_w01_log_71_new	Sleep	2
10.0.5.36	rasalas_w01_community73	Sleep	2
10.0.1.139	rasalas_w01_community01	Sleep	2
10.0.2.231	rasalas_w01_log_01_new	Sleep	2
10.0.1.83	rasalas_w01_community72	Sleep	2
10.0.1.139	rasalas_w01_manage	Sleep	1
10.0.5.185	rasalas_w01_manage	Sleep	1
10.0.1.139	rasalas_w01_g01_03	Sleep	1
10.0.5.185	rasalas_w01_community71	Sleep	1
220.76.91.93	\N	Query	1
10.0.1.139	rasalas_w01_community71	Sleep	1
10.0.2.231	rasalas_w01_log_03_new	Sleep	1
10.0.1.83	rasalas_w01_g03_04	Sleep	1
10.0.2.231	rasalas_w01_g01_04	Sleep	1
10.0.5.185	rasalas_w01_log_03_new	Sleep	1
10.0.5.185	rasalas_w01_g73	Sleep	1
10.0.1.83	rasalas_log_global	Sleep	1
10.0.2.231	rasalas_w01_community01	Sleep	1
10.0.5.36	rasalas_w01_log_01_new	Sleep	1
10.0.1.241	rasalas_global	Sleep	1
10.0.5.185	rasalas_w01_community03	Sleep	1
10.0.1.139	rasalas_log_global	Sleep	1
10.0.1.232	rasalas_global	Sleep	1
10.0.1.83	rasalas_w01_manage	Sleep	1
10.0.2.231	rasalas_w01_community72	Sleep	1
10.0.2.231	rasalas_w01_community03	Sleep	1
10.0.1.139	rasalas_w01_g72	Sleep	1
10.0.2.231	rasalas_w01_g73	Sleep	1
10.0.1.42	rasalas_global	Sleep	1
10.0.1.83	rasalas_w01_log_03_new	Sleep	1
10.0.2.231	rasalas_w01_manage	Sleep	1
10.0.5.36	rasalas_log_global	Sleep	1
10.0.5.36	rasalas_w01_manage	Sleep	1
10.0.5.185	rasalas_w01_log_01_new	Sleep	1
10.0.2.207	rasalas_global	Sleep	1
10.0.2.231	rasalas_w01_community71	Sleep	1
10.0.2.231	rasalas_log_global	Sleep	1
10.0.1.83	rasalas_w01_g73	Sleep	1
10.0.1.83	rasalas_w01_log_01_new	Sleep	1
10.0.1.139	rasalas_w01_community03	Sleep	1
10.0.5.36	rasalas_w01_log_03_new	Sleep	1
10.0.1.148	rasalas_global	Sleep	1
10.0.5.185	rasalas_log_global	Sleep	1

### Assistant

쿼리 결과를 보면 현재 시점의 DB 상태는 꽤 정상에 가깝습니다.

- `Threads_connected=262`, `Max_used_connections=304`
- `max_connections=16500`
- `Connection_errors_max_connections=0`
- `PROCESSLIST` 대부분 `Sleep`
- active query/lock 대기/connection 폭주는 안 보임

그래서 이건 **MySQL 전체 커넥션 부족이나 DB 서버가 계속 과부하인 상황은 아닙니다.** 더 정확히는 “장애 당시 순간적으로 DBNode가 새 TCP 커넥션을 만들 때 실패했고, 지금은 회복된 상태”에 가깝습니다.

의심 포인트는 여전히 DBNode 쪽입니다. 같은 머신에 game/community/trade가 떠 있어도, DBNode는 역할이 다릅니다. DBNode는 여러 gameDB/communityDB/logDB/accountDB/manageDB 등을 모두 물고 있고, `databaseinfo`의 DB별로 별도 connection string/pool이 생깁니다. 반면 game/community/trade는 일부 DB만 쓰거나, 기존에 살아있는 커넥션만 계속 재사용했을 가능성이 큽니다.

즉 이런 그림이 가능합니다.

```text
game/community/trade:
  기존 연결 유지 또는 적은 수의 DB pool 사용 → 정상

dbnode:
  여러 DB pool 사용 + 요청 집중 + 특정 시간대 신규 연결/재연결 발생 → 일부 timeout
```

특히 Tencent Cloud 전환 후 처음이라면 저는 아래를 강하게 의심합니다.

1. **Tencent CDB 또는 VPC 경로의 순간적인 connect timeout**
   - 기존 연결은 살아 있어서 다른 프로세스는 정상처럼 보임
   - 신규 연결을 만들던 DBNode만 실패

2. **DBNode의 연결 풀 lazy open / reconnect burst**
   - MySql.Data pool은 connection string 단위로 나뉩니다.
   - DBNode는 DB 종류가 많아 특정 시간대에 여러 pool에서 동시에 신규 연결을 만들 수 있습니다.

3. **Tencent 쪽 per-source 또는 connection-rate 제한성 동작**
   - `max_connections`는 충분하지만, 짧은 시간의 신규 TCP handshake가 일부 timeout될 수 있습니다.
   - MySQL `Connection_errors_*`가 0인 점도 “MySQL까지 도달한 뒤 거절”보다는 “TCP 단계에서 지연/드랍” 쪽과 맞습니다.

다음 확인은 장애 시간대 기준으로 봐야 합니다.

```sql
SHOW GLOBAL STATUS LIKE 'Connections';
SHOW GLOBAL STATUS LIKE 'Aborted_connects';
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Max_used_connections';
```

이 값을 10초 간격으로 찍어서, 장애 순간에 `Connections` 또는 `Aborted_connects`가 급증했는지 보시면 좋습니다.

DBNode 서버에서는 장애 시간대에 이걸 같이 남기면 원인 분리가 됩니다.

```bash
ss -tanp | grep 10.0.100.7:3306 | awk '{print $1}' | sort | uniq -c
ss -s
```

특히 `SYN-SENT`가 많으면 네트워크/CDB accept 지연이고, `TIME-WAIT`가 폭증하면 짧은 연결 생성/해제가 많다는 뜻입니다.

현재 결론은 이렇습니다.

**DB 서버의 max connection 부족은 아니고, DBNode 프로세스가 특정 시점에 신규 MySQL TCP 연결을 만들다가 Tencent 환경에서 timeout을 맞은 케이스가 가장 유력합니다.** AWS에서 없었다면 Tencent CDB의 failover/maintenance 이벤트, VPC 보안정책, connection-rate/idle TCP 처리 차이를 먼저 확인하는 게 맞습니다.

### User

[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ulimit -n
ls /proc/34243/fd | wc -l
ss -tanp | grep 34243 | wc -l
ss -tanp | grep 10.0.100.7:3306
ss -s
dmesg | egrep -i "conntrack|syn|tcp|too many open files|reset"
65535
2160
1914
ESTAB     0      0         10.0.1.139:47474    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2071))
ESTAB     0      0         10.0.1.139:41852    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2105))
ESTAB     0      0         10.0.1.139:34074    10.0.100.7:3306  users:(("dotnet",pid=34205,fd=1605))
ESTAB     0      0         10.0.1.139:55526    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1977))
ESTAB     0      0         10.0.1.139:37368    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2076))
ESTAB     0      0         10.0.1.139:60420    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2069))
ESTAB     0      0         10.0.1.139:47398    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1094))
ESTAB     0      0         10.0.1.139:48294    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1146))
ESTAB     0      0         10.0.1.139:32962    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1144))
ESTAB     0      0         10.0.1.139:33026    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1127))
ESTAB     0      0         10.0.1.139:39686    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1117))
ESTAB     0      0         10.0.1.139:34664    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1113))
ESTAB     0      0         10.0.1.139:57414    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1105))
ESTAB     0      0         10.0.1.139:56654    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2073))
ESTAB     0      0         10.0.1.139:36812    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1137))
ESTAB     0      0         10.0.1.139:38584    10.0.100.7:3306  users:(("dotnet",pid=34205,fd=185)) 
ESTAB     0      0         10.0.1.139:43658    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1100))
ESTAB     0      0         10.0.1.139:52340    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1141))
ESTAB     0      0         10.0.1.139:49050    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2067))
ESTAB     0      0         10.0.1.139:57190    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1090))
ESTAB     0      0         10.0.1.139:41740    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2116))
ESTAB     0      0         10.0.1.139:37378    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1092))
ESTAB     0      0         10.0.1.139:57664    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1102))
TIME-WAIT 0      0         10.0.1.139:37688    10.0.100.7:3306                                      
ESTAB     0      0         10.0.1.139:45592    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2074))
ESTAB     0      0         10.0.1.139:34670    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1110))
ESTAB     0      0         10.0.1.139:33028    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1104))
ESTAB     0      0         10.0.1.139:43178    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1091))
ESTAB     0      0         10.0.1.139:58496    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1108))
ESTAB     0      0         10.0.1.139:54968    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1098))
TIME-WAIT 0      0         10.0.1.139:37672    10.0.100.7:3306                                      
ESTAB     0      0         10.0.1.139:58506    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1099))
ESTAB     0      0         10.0.1.139:37208    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1114))
ESTAB     0      0         10.0.1.139:50764    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1132))
ESTAB     0      0         10.0.1.139:42160    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1123))
ESTAB     0      0         10.0.1.139:37682    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1093))
ESTAB     0      0         10.0.1.139:33182    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1116))
ESTAB     0      0         10.0.1.139:51720    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1097))
ESTAB     0      0         10.0.1.139:56184    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1095))
TIME-WAIT 0      0         10.0.1.139:57648    10.0.100.7:3306                                      
TIME-WAIT 0      0         10.0.1.139:37690    10.0.100.7:3306                                      
ESTAB     0      0         10.0.1.139:41664    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2108))
ESTAB     0      0         10.0.1.139:38288    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1145))
ESTAB     0      0         10.0.1.139:54006    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1126))
ESTAB     0      0         10.0.1.139:47316    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1149))
ESTAB     0      0         10.0.1.139:53398    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1133))
ESTAB     0      0         10.0.1.139:47652    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2176))
ESTAB     0      0         10.0.1.139:55006    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1130))
TIME-WAIT 0      0         10.0.1.139:37692    10.0.100.7:3306                                      
TIME-WAIT 0      0         10.0.1.139:33674    10.0.100.7:3306                                      
ESTAB     0      0         10.0.1.139:52324    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1128))
ESTAB     0      0         10.0.1.139:58954    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1124))
ESTAB     0      0         10.0.1.139:34306    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=185)) 
ESTAB     0      0         10.0.1.139:48054    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1125))
ESTAB     0      0         10.0.1.139:51722    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1107))
ESTAB     0      0         10.0.1.139:43314    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1112))
ESTAB     0      0         10.0.1.139:60426    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2070))
ESTAB     0      0         10.0.1.139:51222    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2080))
ESTAB     0      0         10.0.1.139:41770    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2110))
ESTAB     0      0         10.0.1.139:36000    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1121))
ESTAB     0      0         10.0.1.139:47804    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1129))
ESTAB     0      0         10.0.1.139:41856    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2168))
ESTAB     0      0         10.0.1.139:52230    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1139))
ESTAB     0      0         10.0.1.139:60242    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1115))
ESTAB     0      0         10.0.1.139:60172    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1118))
ESTAB     0      0         10.0.1.139:52834    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1122))
ESTAB     0      0         10.0.1.139:47494    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1147))
ESTAB     0      0         10.0.1.139:48418    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1119))
ESTAB     0      0         10.0.1.139:38394    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1111))
ESTAB     0      0         10.0.1.139:40966    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1131))
ESTAB     0      0         10.0.1.139:46684    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1143))
ESTAB     0      0         10.0.1.139:58518    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1109))
ESTAB     0      0         10.0.1.139:43384    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1096))
ESTAB     0      0         10.0.1.139:36538    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1103))
TIME-WAIT 0      0         10.0.1.139:33672    10.0.100.7:3306                                      
ESTAB     0      0         10.0.1.139:47554    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1885))
ESTAB     0      0         10.0.1.139:37352    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1138))
ESTAB     0      0         10.0.1.139:45204    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1106))
ESTAB     0      0         10.0.1.139:47898    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2075))
ESTAB     0      0         10.0.1.139:39158    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=1101))
TIME-WAIT 0      0         10.0.1.139:37704    10.0.100.7:3306                                      
ESTAB     0      0         10.0.1.139:47596    10.0.100.7:3306  users:(("dotnet",pid=34243,fd=2072))
Total: 6457
TCP:   6238 (estab 6139, closed 8, orphaned 0, timewait 8)

Transport Total     IP        IPv6
RAW	  1         0         1        
UDP	  3         2         1        
TCP	  6230      6224      6        
INET	  6234      6226      8        
FRAG	  0         0         0        

dmesg: read kernel buffer failed: Operation not permitted
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$

### Assistant

이 출력은 꽤 중요합니다. 이제 방향이 더 선명해졌습니다.

`ulimit -n=65535`, fd `2160`이라서 **파일 디스크립터 부족은 아닙니다.** 그런데 문제는 이쪽입니다.

```text
ss -tanp | grep 34243 | wc -l  = 1914
ss -s: TCP estab 6139
```

즉 이 서버 한 대 안에서 TCP ESTABLISHED가 6천 개 이상이고, **DBNode 프로세스(pid 34243) 혼자 약 1,900개 TCP 연결**을 들고 있습니다. MySQL 쪽 `Threads_connected=262`와 안 맞아 보이는 건, `ss -tanp | grep 34243`이 MySQL뿐 아니라 ZMQ/서버 간 TCP까지 모두 포함하기 때문일 가능성이 큽니다.

그래도 결론은 이렇습니다.

**DBNode만 발생한 이유는 DBNode 프로세스가 다른 프로세스보다 훨씬 많은 TCP 연결을 유지하고 있고, Tencent 환경에서 이 연결 수/재연결 패턴이 순간적으로 connect timeout을 만든 가능성이 큽니다.**

특히 Tencent Cloud에서는 AWS와 달리 다음 제한이나 동작이 걸릴 수 있습니다.

- ENI/NAT/보안그룹의 connection tracking 한계
- VPC 내부 east-west 트래픽 connection tracking
- per-instance concurrent connection 또는 new connection rate 제한
- CDB VIP 앞단의 connection tracking/idle timeout
- 보안장비/클라우드 네트워크 계층의 SYN 처리 지연

현재 MySQL 자체 지표는 여유가 있는데 애플리케이션은 `GetTcpStreamAsync`에서 timeout이므로, **MySQL 프로세스 내부보다 TCP handshake/클라우드 네트워크 계층**이 더 의심됩니다.

다음 확인을 바로 해보세요. DBNode pid 기준으로 포트별 연결 수를 나눠야 합니다.

```bash
ss -tanp | grep 'pid=34243' | awk '{print $5}' | sed 's/.*://' | sort | uniq -c | sort -nr | head -20
```

목적지 IP별:

```bash
ss -tanp | grep 'pid=34243' | awk '{print $5}' | sed 's/:.*//' | sort | uniq -c | sort -nr | head -20
```

상태별:

```bash
ss -tanp | grep 'pid=34243' | awk '{print $1}' | sort | uniq -c
```

MySQL만 정확히:

```bash
ss -tanp | grep 'pid=34243' | grep '10.0.100.7:3306' | awk '{print $1}' | sort | uniq -c
```

만약 여기서 DBNode의 대부분 연결이 `:20000`, `:20100`, `:20300` 같은 ZMQ 포트라면, DBNode가 DB뿐 아니라 서버 간 커넥션 허브처럼 동작하면서 Tencent 네트워크 conntrack을 많이 쓰는 그림입니다.

운영 대응으로는 우선 이 두 가지를 권장합니다.

1. **Tencent Cloud에 해당 시간대 ENI/VPC/CDB connection tracking, packet drop, SYN drop, security group drop 로그 확인 요청**
   - “MySQL max_connections는 여유인데, 특정 CVM의 dotnet DBNode에서 CDB private IP `10.0.100.7:3306` connect timeout 발생”이라고 전달하면 됩니다.

2. **DBNode의 TCP 연결 수를 프로세스/포트별로 모니터링**
   - 장애 시점에 `SYN-SENT`가 늘면 네트워크/CDB VIP 문제
   - `ESTAB`만 계속 많으면 연결 유지 구조/풀 설정 문제
   - `TIME-WAIT`가 폭증하면 짧은 연결 생성/해제 문제

현재 증거만 보면, “DB 계정, 비밀번호, MySQL max_connections”보다는 **Tencent 전환 후 DBNode의 높은 TCP 연결 수와 클라우드 네트워크 계층의 연결 처리 특성**이 가장 그럴듯한 공통 원인입니다.

### User

[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | awk '{print $5}' | sed 's/.*://' | sort | uniq -c | sort -nr | head -20
     69 3306
     22 *
     11 20019
     11 20018
     11 20017
     11 20016
     11 20015
     11 20014
     11 20013
     11 20012
     11 20011
     11 20010
     11 20009
     11 20008
     11 20007
     11 20006
     11 20005
     11 20004
     11 20003
     11 20002
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | awk '{print $5}' | sed 's/:.*//' | sort | uniq -c | sort -nr | head -20
    940 127.0.0.1
    160 10.0.1.232
    120 10.0.1.83
    120 10.0.1.139
     80 10.0.5.36
     80 10.0.5.185
     80 10.0.2.231
     80 10.0.1.136
     71 10.0.100.7
     40 10.0.2.207
     40 10.0.1.42
     40 10.0.1.241
     40 10.0.1.148
     21 0.0.0.0
      1 [
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | awk '{print $1}' | sort | uniq -c
   1891 ESTAB
     22 LISTEN
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | grep '10.0.100.7:3306' | awk '{print $1}' | sort | uniq -c
     71 ESTAB
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$

### Assistant

이 결과면 **DBNode의 MySQL 연결 자체가 과도한 상태는 아닙니다.** pid `34243` 기준으로 MySQL은 `10.0.100.7:3306`에 `71 ESTAB`뿐입니다.

반대로 DBNode의 연결 대부분은 이쪽입니다.

```text
127.0.0.1        940
다른 서버 IP들     다수
10.0.100.7:3306   71
총 ESTAB        1891
```

그래서 “DBNode가 MySQL 커넥션을 너무 많이 만들어서 MySQL이 못 받았다”는 가설은 약해졌습니다. `max_connections`도 여유였고요.

더 수상한 건 **DBNode의 local/ZMQ 계층**입니다. `127.0.0.1` 연결이 940개이고, 목적 포트가 `20001~20019` 등에 11개씩 반복됩니다. 즉 DBNode는 DB보다 **ZMQ/서버 간 통신 연결을 훨씬 많이 유지**하고 있습니다.

이 상황에서 DBNode만 DB timeout을 낸다면 가능한 그림은 이겁니다.

```text
DBNode 프로세스 내부에서 ZMQ/worker/handler 부하 또는 threadpool 지연 발생
→ DB query 처리 타이밍이 밀림
→ NHibernate/MySql.Data가 커넥션 확보/BeginTransaction 단계에서 timeout처럼 터짐
→ game/community/trade는 같은 서버에 있어도 해당 부하 경로를 안 타서 정상
```

특히 예외가 `BeginTransaction()`에서 발생했지만, 이것이 꼭 MySQL 서버 장애만 뜻하진 않습니다. .NET threadpool starvation, 프로세스 내부 과부하, socket 처리 지연이 있으면 `Open()`이 제때 처리되지 못하고 timeout으로 보일 수 있습니다.

현재 우선순위는 이렇게 바뀝니다.

1. **DBNode 프로세스 내부 부하/스레드 지연**
   - CPU는 0%로 보여도 threadpool, GC, lock 대기, ZMQ receive/send queue 적체는 별개입니다.
   - PM2의 CPU만으로는 판단이 어렵습니다.

2. **ZMQ/localhost 연결 폭증 또는 비정상 유지**
   - `127.0.0.1` 940개는 꽤 큽니다.
   - AWS에서는 문제가 없었더라도 Tencent에서 네트워크/스케줄링/커널 파라미터 차이로 임계점이 낮아졌을 수 있습니다.

3. **Tencent 네트워크는 여전히 후보지만, MySQL 방향보다는 서버 간/ZMQ 연결 처리 쪽**
   - MySQL 연결 71개는 정상 범위입니다.
   - 전체 TCP 6000+, DBNode 1900개가 더 눈에 띕니다.

다음으로는 DBNode의 `127.0.0.1` 연결이 무엇인지 확인하는 게 좋습니다.

```bash
ss -tanp | grep 'pid=34243' | grep '127.0.0.1' | awk '{print $4, $5}' | sed 's/.*://' | sort | uniq -c | sort -nr | head -30
```

그리고 로컬 연결의 양쪽 프로세스까지 확인:

```bash
ss -tanp | grep 'pid=34243' | grep '127.0.0.1' | head -30
```

.NET 런타임 상태도 가능하면 장애 전후로 확인하세요.

```bash
dotnet-counters ps
dotnet-counters monitor --process-id 34243 System.Runtime Microsoft.AspNetCore.Hosting
```

중점 지표:

```text
ThreadPool Queue Length
ThreadPool Thread Count
GC Heap Size
% Time in GC
Exception Count
Monitor Lock Contention Count
```

결론적으로, 지금까지 나온 증거 기준으로는 **MySQL 서버/계정/커넥션 한도 문제가 아니라 DBNode 프로세스의 통신 연결 수와 내부 처리 지연이 DB 커넥션 timeout으로 표출된 가능성**이 더 높습니다. 특히 `127.0.0.1` 940개가 정상 설계상 기대값인지부터 확인해보는 게 다음 핵심입니다.

### User

[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | grep '127.0.0.1' | awk '{print $4, $5}' | sed 's/.*://' | sort | uniq -c | sort -nr | head -30
      2 55008
      2 52230
      2 48220
      2 47886
      2 45380
      2 39442
      2 36756
      2 34962
      2 34054
      2 33720
      1 60974
      1 60884
      1 60870
      1 60750
      1 60660
      1 60632
      1 60454
      1 60446
      1 60394
      1 60378
      1 60324
      1 60214
      1 60132
      1 60092
      1 59984
      1 59974
      1 59774
      1 59586
      1 59584
      1 59362
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | grep '127.0.0.1' | head -30
ESTAB     0      0          127.0.0.1:35718       127.0.0.1:33717 users:(("dotnet",pid=34243,fd=736)) 
ESTAB     0      0          127.0.0.1:37935       127.0.0.1:51000 users:(("dotnet",pid=34243,fd=768)) 
ESTAB     1      0          127.0.0.1:38601       127.0.0.1:37312 users:(("dotnet",pid=34243,fd=340)) 
ESTAB     0      0          127.0.0.1:46049       127.0.0.1:44142 users:(("dotnet",pid=34243,fd=324)) 
ESTAB     1      0          127.0.0.1:34771       127.0.0.1:59086 users:(("dotnet",pid=34243,fd=486)) 
ESTAB     0      0          127.0.0.1:45062       127.0.0.1:34183 users:(("dotnet",pid=34243,fd=734)) 
ESTAB     0      0          127.0.0.1:41952       127.0.0.1:42685 users:(("dotnet",pid=34243,fd=1086))
ESTAB     0      0          127.0.0.1:50136       127.0.0.1:38581 users:(("dotnet",pid=34243,fd=1569))
ESTAB     0      0          127.0.0.1:42110       127.0.0.1:43859 users:(("dotnet",pid=34243,fd=550)) 
ESTAB     0      0          127.0.0.1:57796       127.0.0.1:46447 users:(("dotnet",pid=34243,fd=1307))
ESTAB     0      0          127.0.0.1:36488       127.0.0.1:35419 users:(("dotnet",pid=34243,fd=1286))
ESTAB     0      0          127.0.0.1:34476       127.0.0.1:43113 users:(("dotnet",pid=34243,fd=1331))
ESTAB     0      0          127.0.0.1:43628       127.0.0.1:46833 users:(("dotnet",pid=34243,fd=1295))
ESTAB     1      0          127.0.0.1:42129       127.0.0.1:42886 users:(("dotnet",pid=34243,fd=1412))
ESTAB     0      0          127.0.0.1:53862       127.0.0.1:44421 users:(("dotnet",pid=34243,fd=1376))
ESTAB     1      0          127.0.0.1:39491       127.0.0.1:56024 users:(("dotnet",pid=34243,fd=1062))
ESTAB     0      0          127.0.0.1:51076       127.0.0.1:46237 users:(("dotnet",pid=34243,fd=383)) 
ESTAB     1      0          127.0.0.1:34259       127.0.0.1:54872 users:(("dotnet",pid=34243,fd=1329))
ESTAB     1      0          127.0.0.1:45309       127.0.0.1:60750 users:(("dotnet",pid=34243,fd=1263))
ESTAB     1      0          127.0.0.1:38931       127.0.0.1:35358 users:(("dotnet",pid=34243,fd=1251))
ESTAB     0      0          127.0.0.1:39010       127.0.0.1:42289 users:(("dotnet",pid=34243,fd=630)) 
ESTAB     0      0          127.0.0.1:45108       127.0.0.1:34449 users:(("dotnet",pid=34243,fd=1352))
ESTAB     0      0          127.0.0.1:34918       127.0.0.1:34865 users:(("dotnet",pid=34243,fd=571)) 
ESTAB     1      0          127.0.0.1:34355       127.0.0.1:46926 users:(("dotnet",pid=34243,fd=2199))
ESTAB     0      0          127.0.0.1:43624       127.0.0.1:37253 users:(("dotnet",pid=34243,fd=1241))
ESTAB     0      0          127.0.0.1:53098       127.0.0.1:45263 users:(("dotnet",pid=34243,fd=638)) 
ESTAB     0      0          127.0.0.1:41935       127.0.0.1:60446 users:(("dotnet",pid=34243,fd=270)) 
ESTAB     0      0          127.0.0.1:52870       127.0.0.1:43661 users:(("dotnet",pid=34243,fd=1289))
ESTAB     0      0          127.0.0.1:42090       127.0.0.1:41963 users:(("dotnet",pid=34243,fd=752)) 
ESTAB     0      0          127.0.0.1:35318       127.0.0.1:34389 users:(("dotnet",pid=34243,fd=985)) 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ dotnet-counters ps
dotnet-counters monitor --process-id 34243 System.Runtime Microsoft.AspNetCore.Hosting
^C
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ dotnet-counters ps
-bash: dotnet-counters: command not found
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ dotnet-counters monitor --process-id 34243 System.Runtime Microsoft.AspNetCore.Hosting
-bash: dotnet-counters: command not found

### Assistant

`127.0.0.1` 결과를 보면 특정 고정 포트에 몰린 게 아니라 **DBNode 프로세스 내부에서 loopback TCP connection pair가 대량 생성되어 유지되는 형태**로 보입니다. 포트가 랜덤 ephemeral port끼리 연결되어 있고, 양쪽 모두 `dotnet(pid=34243)`입니다.

즉 이건 외부 Tencent 네트워크 문제가 아니라, 적어도 `127.0.0.1` 940개에 대해서는 **같은 DBNode 프로세스 안에서 만든 로컬 TCP 연결**입니다. NetMQ/inproc 대신 TCP loopback을 쓰는 구조거나, 내부 worker/channel/socket이 연결을 많이 만드는 구조일 가능성이 큽니다.

다만 이것만으로 DB timeout의 직접 원인이라고 단정하긴 어렵습니다. 현재 중요한 사실은:

```text
DBNode MySQL 연결: 71개, 정상 ESTAB
DBNode 전체 TCP 연결: 약 1,900개
그중 loopback: 약 940개
fd: 2,160 / ulimit 65,535
MySQL max_connections: 여유
```

그래서 지금 가장 유력한 원인은:

```text
DBNode 프로세스 내부의 socket/thread/event-loop/worker 처리 지연
→ DB 작업 처리 중 MySQL 신규 연결 또는 pooled connection 재확보가 지연
→ BeginTransaction/Open 단계에서 timeout
```

`dotnet-counters`가 없으니 대체로 아래를 장애 전후에 찍어보면 좋습니다.

**1. DBNode 스레드 수**

```bash
ps -o pid,nlwp,pcpu,pmem,rss,vsz,etime,cmd -p 34243
cat /proc/34243/status | egrep 'Threads|FDSize|VmRSS|VmSize|voluntary|nonvoluntary'
```

**2. DBNode 소켓 상태 요약**

```bash
ss -tanp | grep 'pid=34243' | awk '{print $1}' | sort | uniq -c
ss -tanp | grep 'pid=34243' | awk '{print $5}' | sed 's/:.*//' | sort | uniq -c | sort -nr | head -30
```

**3. 프로세스별 TCP 연결 비교**

```bash
for p in 34243 34140 34169 34205; do
  echo "PID=$p"
  ss -tanp | grep "pid=$p" | awk '{print $1}' | sort | uniq -c
done
```

**4. dotnet tool 설치가 가능하면 가장 좋음**

```bash
dotnet tool install --global dotnet-counters
export PATH="$PATH:$HOME/.dotnet/tools"
dotnet-counters monitor --process-id 34243 System.Runtime
```

봐야 할 값은 `ThreadPool Queue Length`, `ThreadPool Thread Count`, `% Time in GC`, `Exception Count`, `Monitor Lock Contention Count`입니다.

그리고 코드 쪽에서 한 가지 체크가 필요합니다. 현재 `DatabaseController.Init()`의 read connection string에는 `Connection Timeout=60`이 없습니다.

```csharp
connectionInfo_write ... + ";Connection Timeout=60";
connectionInfo_read ... // timeout 없음
```

그런데 `SelectOne()`은 read endpoint를 사용합니다. 즉 read 쪽은 기본 timeout으로 실패할 수 있습니다. write/read IP가 같다면 read에도 동일하게 `Connection Timeout=60`을 붙이는 게 운영 안정성에는 맞습니다. 원인 해결은 아니지만, Tencent 전환 후 순간 지연에 대한 완충으로는 효과가 있을 수 있습니다.

정리하면, 현재까지는 **MySQL 서버 한도/계정 문제가 아니라 DBNode 프로세스 내부 연결/처리 지연 + read 커넥션 기본 timeout이 결합된 증상**으로 보는 게 제일 자연스럽습니다. `dotnet-counters` 또는 `/proc/34243/status`의 스레드/컨텍스트 스위치/GC 쪽 지표가 나오면 더 좁힐 수 있습니다.

### User

-bash: dotnet-counters: command not found
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ps -o pid,nlwp,pcpu,pmem,rss,vsz,etime,cmd -p 34243
    PID NLWP %CPU %MEM   RSS    VSZ     ELAPSED CMD
  34243   73 27.0 14.0 4531548 277903724 5-19:04:39 dotnet EgonServer.dll 301
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ cat /proc/34243/status | egrep 'Threads|FDSize|VmRSS|VmSize|voluntary|nonvoluntary'
FDSize:	4096
VmSize:	277903696 kB
VmRSS:	 4531524 kB
Threads:	71
voluntary_ctxt_switches:	503510
nonvoluntary_ctxt_switches:	1083
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | awk '{print $1}' | sort | uniq -c
   1899 ESTAB
     22 LISTEN
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ ss -tanp | grep 'pid=34243' | awk '{print $5}' | sed 's/:.*//' | sort | uniq -c | sort -nr | head -30
    940 127.0.0.1
    160 10.0.1.232
    120 10.0.1.83
    120 10.0.1.139
     80 10.0.5.36
     80 10.0.5.185
     80 10.0.2.231
     80 10.0.1.136
     79 10.0.100.7
     40 10.0.2.207
     40 10.0.1.42
     40 10.0.1.241
     40 10.0.1.148
     21 0.0.0.0
      1 [
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ for p in 34243 34140 34169 34205; do
  echo "PID=$p"
  ss -tanp | grep "pid=$p" | awk '{print $1}' | sort | uniq -c
done
PID=34243
   1899 ESTAB
     22 LISTEN
PID=34140
   1480 ESTAB
     22 LISTEN
PID=34169
   1423 ESTAB
     22 LISTEN
PID=34205
   1342 ESTAB
     22 LISTEN
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ 
[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$ dotnet tool install --global dotnet-counters
export PATH="$PATH:$HOME/.dotnet/tools"
dotnet-counters monitor --process-id 34243 System.Runtime

Welcome to .NET 8.0!
---------------------
SDK Version: 8.0.404

Telemetry
---------
The .NET tools collect usage data in order to help us improve your experience. It is collected by Microsoft and shared with the community. You can opt-out of telemetry by setting the DOTNET_CLI_TELEMETRY_OPTOUT environment variable to '1' or 'true' using your favorite shell.

Read more about .NET CLI Tools telemetry: https://aka.ms/dotnet-cli-telemetry

----------------
Installed an ASP.NET Core HTTPS development certificate.
To trust the certificate, view the instructions: https://aka.ms/dotnet-https-linux

----------------
Write your first app: https://aka.ms/dotnet-hello-world
Find out what's new: https://aka.ms/dotnet-whats-new
Explore documentation: https://aka.ms/dotnet-docs
Report issues and find source on GitHub: https://github.com/dotnet/core
Use 'dotnet --help' to see available commands or visit: https://aka.ms/dotnet-cli
--------------------------------------------------------------------------------------
An issue was encountered verifying workloads. For more information, run "dotnet workload update".
You can invoke the tool using the following command: dotnet-counters
Tool 'dotnet-counters' (version '9.0.661903') was successfully installed.
--counters is unspecified. Monitoring System.Runtime counters by default.
Press p to pause, r to resume, q to quit.
    Status: Waiting for initial payload...

Name                                                                                                                                                                                                              Current Value
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 Size (B)                                                                                                                                                                                                   1.4632e+09
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 Size (B)                                                                                                                                                                                                   1.4632e+09
    LOH Size (B)                                                                                                                                                                                                     7.8684e+08
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 Size (B)                                                                                                                                                                                                   1.4632e+09
    LOH Size (B)                                                                                                                                                                                                     7.8684e+08
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    POH (Pinned Object Heap) Size (B)                                                                                                                                                                               133,800    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 Size (B)                                                                                                                                                                                                   1.4632e+09
    LOH Size (B)                                                                                                                                                                                                     7.8684e+08
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    Number of Assemblies Loaded                                                                                                                                                                                         113    
    POH (Pinned Object Heap) Size (B)                                                                                                                                                                               133,800    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 Size (B)                                                                                                                                                                                                   1.4632e+09
    IL Bytes Jitted (B)                                                                                                                                                                                              1.3771e+09
    LOH Size (B)                                                                                                                                                                                                     7.8684e+08
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    Number of Assemblies Loaded                                                                                                                                                                                         113    
    POH (Pinned Object Heap) Size (B)                                                                                                                                                                               133,800    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  22,189,584    
    CPU Usage (%)                                                                                                                                                                                                         3.142
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,865.662
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 Size (B)                                                                                                                                                                                                   1.4632e+09
    IL Bytes Jitted (B)                                                                                                                                                                                              1.3771e+09
    LOH Size (B)                                                                                                                                                                                                     7.8684e+08
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        19    
    Number of Active Timers                                                                                                                                                                                               4    
    Number of Assemblies Loaded                                                                                                                                                                                         113    
    Number of Methods Jitted                                                                                                                                                                                     54,251,732    
    POH (Pinned Object Heap) Size (B)                                                                                                                                                                               133,800    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,709    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Working Set (MB)                                                                                                                                                                                                  4,641.763
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                              Current Value
[System.Runtime]                                                                                                                                                                                                               
    % Time in GC since last GC (%)                                                                                                                                                                                        0    
    Allocation Rate (B / 1 sec)                                                                                                                                                                                  27,544,120    
    CPU Usage (%)                                                                                                                                                                                                         2.727
    Exception Count (Count / 1 sec)                                                                                                                                                                                       0    
    GC Committed Bytes (MB)                                                                                                                                                                                           4,279.783
    GC Fragmentation (%)                                                                                                                                                                                                 21.26 
    GC Heap Size (MB)                                                                                                                                                                                                 1,992.616
    Gen 0 GC Budget (MB)                                                                                                                                                                                              1,342    
    Gen 0 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 0 Size (B)                                                                                                                                                                                                        0    
    Gen 1 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 1 Size (B)                                                                                                                                                                                               30,859,424    
    Gen 2 GC Count (Count / 1 sec)                                                                                                                                                                                        0    
    Gen 2 Size (B)                                                                                                                                                                                                   1.4632e+09
    IL Bytes Jitted (B)                                                                                                                                                                                              1.3771e+09
    LOH Size (B)                                                                                                                                                                                                     7.8684e+08
    Monitor Lock Contention Count (Count / 1 sec)                                                                                                                                                                        15    
    Number of Active Timers                                                                                                                                                                                               4    
    Number of Assemblies Loaded                                                                                                                                                                                         113    
    Number of Methods Jitted                                                                                                                                                                                     54,252,125    
    POH (Pinned Object Heap) Size (B)                                                                                                                                                                               133,800    
    ThreadPool Completed Work Item Count (Count / 1 sec)                                                                                                                                                              1,667    
    ThreadPool Queue Length                                                                                                                                                                                               0    
    ThreadPool Thread Count                                                                                                                                                                                              10    
    Time paused by GC (ms / 1 sec)                                                                                                                                                                                        0    
    Time spent in JIT (ms / 1 sec)                                                                                                                                                                                       21.634
    Working Set (MB)                                                                                                                                                                                                  4,642.132

[ec2-user@Rasalas-Live-w01-g01-Game01 ~]$

### Assistant

현재 `dotnet-counters` 결과를 보면 **지금 이 순간 DBNode 프로세스 내부 병목은 보이지 않습니다.**

핵심 지표가 정상 쪽입니다.

```text
CPU Usage: 2~3%
ThreadPool Queue Length: 0
ThreadPool Thread Count: 10
% Time in GC: 0
Time paused by GC: 0
Exception Count: 0
MySQL 연결: 약 79개
fd: 2160 / ulimit 65535
```

그래서 기존 가설 중 **ThreadPool starvation, GC pause, fd 부족, MySQL max_connections 부족**은 현재 증거로는 가능성이 낮습니다.

오히려 지금까지 나온 정보를 종합하면 가장 그럴듯한 원인은 이쪽입니다.

```text
장애 시점에 Tencent Cloud 내부 네트워크 또는 CDB VIP 계층에서
10.0.100.7:3306 신규 TCP 연결이 순간적으로 지연/드랍됨
기존 연결은 살아 있어서 다른 프로세스는 정상처럼 보임
DBNode는 DB 요청을 가장 많이 처리하므로 신규 연결/재연결 타이밍에만 예외가 집중됨
```

특히 MySQL 지표에서:

```text
Connection_errors_* = 0
max_connections 여유
processlist 대부분 Sleep
```

이면 MySQL 서버가 “받고 나서 거절”한 게 아니라, **MySQL까지 정상적으로 도달하지 못했거나 TCP handshake 단계에서 지연된 케이스**와 더 잘 맞습니다.

DBNode만 발생한 이유도 이렇게 설명됩니다.

- game/community/trade는 기존 커넥션을 계속 재사용했을 수 있음
- DBNode는 실제 DB query worker 역할이라 특정 시간대에 `BeginTransaction()`이 더 자주 발생
- read/write 모두 같은 IP라도 connection pool은 `Database=...`별 connection string 단위로 나뉨
- 여러 DB를 물고 있는 DBNode가 특정 DB pool에서 새 연결을 만들다가 timeout을 맞음

그리고 코드상 보완 포인트가 하나 있습니다.

[DatabaseController.cs](/E:/Rasalas/Trunk/qa/Server/EgonServer/Controllers/DatabaseController.cs:72)에서 write에는 `Connection Timeout=60`이 붙지만 read에는 없습니다.

```csharp
connectionInfo_write ... ";Connection Timeout=60"
connectionInfo_read ... // timeout 없음
```

그런데 예외 난 `SelectOne()`은 read endpoint를 탑니다. read/write IP가 같다면 read에도 동일하게 `Connection Timeout=60`을 붙이는 것이 맞습니다. 근본 원인 해결은 아니지만 Tencent 환경의 순간 지연에는 완충 효과가 있습니다.

운영 확인은 Tencent에 아래 항목을 시간대와 함께 요청하는 게 좋아 보입니다.

```text
CVM 10.0.1.139/10.0.5.185/10.0.5.36/... → CDB 10.0.100.7:3306
장애 시간대 TCP SYN drop, connection tracking drop, CDB VIP failover/HA switch,
보안그룹/ACL drop, packet loss, CDB maintenance event 확인
```

추가로 같은 문제가 재발하면 그 순간에 이 세 개만 바로 찍으면 원인 분리가 됩니다.

```bash
date
ss -tanp | grep 'pid=34243' | awk '{print $1}' | sort | uniq -c
ss -tanp | grep '10.0.100.7:3306' | awk '{print $1}' | sort | uniq -c
dotnet-counters monitor --process-id 34243 System.Runtime
```

재발 시 `SYN-SENT`가 늘면 Tencent/CDB 네트워크 계층 쪽이 거의 확정이고, `ThreadPool Queue Length`가 튀면 프로세스 내부 병목입니다. 현재 데이터만 보면 전자 쪽이 더 강합니다.
