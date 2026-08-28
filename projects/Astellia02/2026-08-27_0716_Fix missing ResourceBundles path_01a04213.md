# Fix missing ResourceBundles path

- Project: Astellia02
- Session ID: `01a04213-492d-7c60-b984-3fd87db1d892`
- Workspace: `C:\Users\dumaclub\Documents\ChatGPT\Astellia02`
- Started: 2026-08-27T07:15:55.592Z
- Updated: 2026-08-27T07:16:43.0432638Z
- Messages exported: 32

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

18|Chatting        | 2026.08.27-16.13.04.698 [Info] SerialGenerator init, serverIndex: 1 (D:\ProjectA\Trunk\Dev\Server\EgonServer\Util\SerialGenerator.cs:120)
18|Chatting        | Unhandled exception.
18|Chatting        | &#x20;
18|Chatting        | System.IO.DirectoryNotFoundException: Could not find a part of the path '/dotnet/Server/Client/Assets/ResourceBundles/Data/'.
18|Chatting        |    at System.IO.FileSystem.GetAttributes(String fullPath)
18|Chatting        |    at K2Server.ServerModule.CheckDir\_md5(UInt32& hashKey, String \_path) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Server\ServerModule.cs:line 2069
18|Chatting        |    at K2Server.ServerModule.Createmd5(String \_path) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Server\ServerModule.cs:line 2062
18|Chatting        |    at K2Server.ServerModule.Load(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataloadeType, Int32 newServerGroupId) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Server\ServerModule.cs:line 447
18|Chatting        |    at K2Server.Program.OnConsoleStart(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataloadeType, Int32 newServerGroupId) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Program.cs:line 197
18|Chatting        |    at K2Server.Program.Main(String[] args) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Program.cs:line 168
위의 오류 확인해 주세요.&#x20;

### Assistant

스택 트레이스의 경로가 왜 `/dotnet/Server/Client/...`로 만들어지는지부터 추적하겠습니다. `ServerModule.Load/Createmd5/CheckDir_md5`와 실행 설정·컨테이너 경로를 함께 확인해 원인과 수정 지점을 정리하겠습니다.

### Assistant

코드상 예외는 `RES_PATH` 유효성 검사 전에 `File.GetAttributes()`를 호출하면서 발생합니다. 현재 확인된 `RES_PATH`는 상대경로이며, 컨테이너의 현재 작업 디렉터리를 기준으로 정규화되면서 `/dotnet/Server/Client/...`를 가리키고 있습니다. 배포 이미지에 실제 데이터가 어느 위치로 복사되는지도 이어서 대조하겠습니다.

### Assistant

확인 결과, 원인은 `RES_PATH`가 잘못 해석되어 존재하지 않는 디렉터리를 가리키는 것입니다.

- 오류 경로: `/dotnet/Server/Client/Assets/ResourceBundles/Data/`
- 예상 경로: `/dotnet/Client/Assets/ResourceBundles/Data/`
- 발생 위치: [ServerModule.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Server/ServerModule.cs:447)에서 `RES_PATH`로 MD5 생성
- 직접 예외 위치: [ServerModule.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Server/ServerModule.cs:2069)의 `File.GetAttributes(_path)`

현재 설정은 상대경로라 실행 작업 디렉터리에 따라 달라집니다. 예를 들어 Chatting 작업 디렉터리가 `/dotnet/Server/bin/bin02/bin03/Chatting`이라면:

- `../../../../Client/...` → `/dotnet/Server/Client/...` ← 현재 오류와 일치
- `../../../../../Client/...` → `/dotnet/Client/...` ← 예상 위치

즉시 조치는 실제 Chatting 서버가 읽는 `config.txt`, 또는 실행 인자 `dataLoadType`에 따른 `config_1.txt`/`config_2.txt`의 값을 절대경로로 지정하는 것이 가장 안전합니다.

```text
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
```

컨테이너에서 다음도 확인해야 합니다.

```bash
pwd
grep '^RES_PATH:' config*.txt
ls -ld /dotnet/Client/Assets/ResourceBundles/Data/
```

마지막 `ls`도 실패한다면 설정뿐 아니라 배포 과정에서 Client 데이터 복사 또는 볼륨 마운트가 누락된 것입니다.

장기적으로는 상대경로를 제거하고, `Directory.Exists()`로 먼저 검사하여 서버가 `Unhandled exception`으로 종료되지 않고 정확한 설정 오류를 출력하도록 보완하는 것이 좋습니다. 이번 확인에서는 코드는 변경하지 않았습니다.

### User

# Files pasted by the user:

## "PM2 | App [Hive:54] online 58|Gateway02 | 2026.08.27-16.27.16.302 [Info] DbCont…": C:\Users\dumaclub\.codex/attachments/741febe9-ddf1-4025-9ec0-b0b5499f26b6/pasted-text.txt

## My request:
다른 오류가 발생되었는데 확인해 주세요.&#x20;

### Assistant

새 로그의 최초 예외와 내부 예외 체인을 확인한 뒤, 이전 경로 문제와 연관된 후속 오류인지 별개의 초기화 문제인지 구분하겠습니다.

### Assistant

원인이 구체적으로 좁혀졌습니다. Gateway02가 만든 연결 문자열 자체가 `Server=;Port=0;Database=...`이므로 MySQL 장애가 아니라 DB 접속 정보가 비어 있습니다. 특히 현재 빌드 출력의 `config_2.txt`가 0바이트인 정황이 있어, 배포된 각 서버의 `config_2.txt` 상태와 설정 선택 로직을 대조하고 있습니다.

### Assistant

원인은 MySQL 서버 장애가 아니라 `Gateway02/config_2.txt`가 비어 있어 DB 접속 정보가 생성되지 않은 것입니다.

로그의 핵심 증거:

```text
realPath : .../Hive/config_2.txt
ServerId: 0
Server=;Port=0;Database=;Uid=user;...
The value cannot be an empty string. (Parameter 'host')
```

현재 로컬 빌드 출력도 동일합니다.

```text
config.txt   0 bytes
config_1.txt 0 bytes
config_2.txt 0 bytes
```

발생 과정은 다음과 같습니다.

1. `dataLoadType=2`이므로 [ConfigLoader.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Util/ConfigLoader.cs:46)가 `config_2.txt`를 선택합니다.
2. 파일은 존재하므로 `config.txt`로 폴백하지 않습니다.
3. 0바이트 파일도 현재 로더는 정상 로드로 처리합니다.
4. `GLOBAL_CONNECTION_INFO`가 없으므로 [ServerModule.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Server/ServerModule.cs:364)에서 PM2 실행 인자를 사용합니다.
5. DB IP·포트·DB명이 비어 있어 `Server=;Port=0;Database=;`가 생성되고 접속이 실패합니다.

조치는 서버별 `config_2.txt`를 완전한 설정으로 복원하는 것입니다. 최소한 다음 키가 필요합니다.

```text
SERVER_ID:...
GLOBAL_CONNECTION_INFO:Server=...;Port=...;Database=...;
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
DEVELOP_MODE:false
```

배포 서버에서 먼저 확인하십시오.

```bash
cd /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway02
wc -c config.txt config_1.txt config_2.txt
grep -E '^(SERVER_ID|GLOBAL_CONNECTION_INFO|RES_PATH):' config_2.txt
```

`config.txt`가 정상이라면 빈 `config_2.txt`를 제거하여 폴백시킬 수도 있지만, 현재 로컬에서는 세 파일 모두 0바이트이므로 배포 원본부터 복원하는 것이 안전합니다.

추가로 필요한 코드 보완은 다음 두 가지입니다.

- 빈 설정 파일이나 필수 키 누락 시 `LoadConfig()`가 실패하도록 검증
- DB 접속 오류 로그에서 `Pwd`를 마스킹

이번 오류는 이전 `RES_PATH` 오류와 예외 내용은 다르지만, 둘 다 배포 설정 파일이 잘못 만들어진 동일 계열의 문제입니다.

### User

# Files pasted by the user:

## "81|Inter | at MySql.Data.MySqlClient.MySqlConnection.OpenAsync(Boolean execAsyn…": C:\Users\dumaclub\.codex/attachments/5cdcc83c-6792-4d02-b977-4a8006916379/pasted-text.txt

Pasted text contains the user's request.

## My request:

### Assistant

새 로그 전체에서 가장 안쪽 예외와 실제 연결 문자열 상태를 확인하고, 앞서 확인한 빈 설정 파일 문제의 연속인지 구분하겠습니다.

### Assistant

이번 로그는 새로운 오류가 아니라 앞서 확인한 `config_2.txt` 문제의 확산입니다. Inter, Gateway02뿐 아니라 GlobalGame, Chatting, Community 등 전체 서버가 영향을 받고 있습니다.

근거:

```text
Config Path() => .../<서버명>/config_2.txt
ServerId: 0
Server=;Port=0;Database=;
The value cannot be an empty string. (Parameter 'host')
```

`config_2.txt`가 비었거나 필수 키가 없어서 다음 값이 모두 사라졌습니다.

- `SERVER_ID`
- `GLOBAL_CONNECTION_INFO`
- `RES_PATH`

PM2의 `online` 표시는 정상 구동을 의미하지 않습니다. 현재 프로세스는 시작 직후 `SIGABRT`로 종료되고 PM2가 계속 재시작하는 상태입니다.

우선 재시작 루프를 멈추고 모든 설정을 검사해야 합니다.

```bash
pm2 stop all

find /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer \
  -name 'config_2.txt' -printf '%p : %s bytes\n'
```

각 서버 디렉터리의 `config_2.txt`를 서버별 정상 설정으로 복원하십시오. `SERVER_ID`가 서로 다르므로 하나의 파일을 모든 서버에 동일하게 복사하면 안 됩니다.

복원 후 필수 키를 확인합니다.

```bash
grep -H -E '^(SERVER_ID|GLOBAL_CONNECTION_INFO|RES_PATH):' \
  /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/*/config_2.txt
```

그다음 순차적으로 재시작하여 확인하는 편이 안전합니다.

```bash
pm2 start Gateway02
pm2 logs Gateway02 --lines 100
```

정상 기준은 다음과 같습니다.

```text
ServerId: 0이 아닌 서버별 ID
Server=<DB 호스트>;Port=<정상 포트>;Database=<DB명>;
```

또한 현재 로그에 DB 비밀번호가 평문으로 노출되어 있으므로, 설정 복구 후 비밀번호 변경과 로그 마스킹이 필요합니다. 코드에서는 [ConfigLoader.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Util/ConfigLoader.cs:40)가 빈 파일을 성공으로 처리하지 않도록 보완해야 재발을 막을 수 있습니다.

### User

[ec2-user\@Ast-New-QA dotnet]$ ^C
[ec2-user\@Ast-New-QA dotnet]$ find /dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer \\
&#x20; -name 'config\_2.txt' -printf '%p : %s bytes\n'
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Gateway01/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Hive/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Inter/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Certify/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Chatting/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Gateway02/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Game01/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Community/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/Database01/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/GlobalTrade/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/InterCommunity/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/GlobalGame/config\_2.txt : 0 bytes
/dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/GlobalCommunity/config\_2.txt : 0 bytes
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$ grep -H -E '^(SERVER\_ID|GLOBAL\_CONNECTION\_INFO|RES\_PATH):' \\
&#x20; /dotnet/Server/EgonServer/bin/NFT\_SERVER/GameServer/\*/config\_2.txt
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;

### Assistant

확인 결과 원인이 완전히 확정되었습니다. 모든 서버의 `config_2.txt`가 0바이트이며, `grep` 결과가 없는 것도 필수 설정이 하나도 없기 때문입니다.

현재 상태에서는 전체 서버가 동일하게 실패하므로 PM2 재시작은 중지하고 정상 설정 원본부터 찾아야 합니다.

```bash
pm2 stop all

game_config_root=/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer

find "$game_config_root" -maxdepth 2 -type f \
  \( -name 'config.txt' -o -name 'config_1.txt' -o -name 'config_2.txt' \) \
  -printf '%p : %s bytes\n'
```

정상 설정 후보도 검색하십시오. 값은 출력하지 않고 파일명만 표시합니다.

```bash
grep -rl '^GLOBAL_CONNECTION_INFO:' "$game_config_root" \
  --include='config*.txt'
```

특히 아래 원본 디렉터리가 배포 서버에도 있는지 확인해야 합니다.

```bash
find "$game_config_root/ConfigFile" -type f -name 'config*.txt' \
  -printf '%p : %s bytes\n' 2>/dev/null
```

복원 우선순위는 다음과 같습니다.

1. 배포 백업 또는 이전 정상 버전의 서버별 `config_2.txt`
2. `ConfigFile/config_<서버명>.txt`
3. 각 서버 디렉터리의 정상적인 `config.txt` 또는 `config_1.txt`

`SERVER_ID`가 서버마다 다르므로 하나의 공통 설정을 전체 디렉터리에 복사하면 안 됩니다. 정상 원본을 찾은 후 각 서버별로 다음 세 키가 존재하는지 확인해야 합니다.

```text
SERVER_ID
GLOBAL_CONNECTION_INFO
RES_PATH
```

현재 상황은 배포 과정에서 0바이트 placeholder `config_2.txt`가 모든 서버 디렉터리에 복사된 것으로 보입니다. 정상 설정 파일 목록과 크기를 확인하기 전에는 파일 복사를 진행하지 않는 것이 안전합니다.

### User

# Files pasted by the user:

## "[ec2-user@Ast-New-QA dotnet]$ find /dotnet/Server/EgonServer/bin/NFT_SERVER/Gam…": C:\Users\dumaclub\.codex/attachments/e06930c2-3db9-4aa7-abbf-ab4322088c56/pasted-text.txt

Pasted text contains the user's request.

## My request:

### Assistant

서버에서 확인된 설정 파일 목록을 바탕으로 정상 원본이 남아 있는지와 안전하게 복구할 수 있는 경로를 판별하겠습니다. 비밀번호 같은 접속 값은 다시 노출하지 않고 파일 상태와 키 존재 여부만 보겠습니다.

### Assistant

0바이트 문제는 해소됐지만, 현재 모든 `config_2.txt`가 동일한 376바이트 파일로 채워졌습니다. 특히 모든 서버의 `SERVER_ID`가 `100`이고 `RES_PATH`도 이전 실패 경로를 다시 만드는 값이라, 이 상태로 전체 재시작하면 서버 역할 중복과 경로 예외가 이어질 가능성이 큽니다. 저장소의 서버별 기준 설정과 대조하겠습니다.

### Assistant

DB 접속 정보는 이제 들어갔지만, 복구 방식이 잘못되었습니다. 모든 서버에 같은 설정 파일이 복사되어 `SERVER_ID:100`으로 통일됐습니다.

현재 상태:

- DB 호스트·포트·DB명: 복구됨
- `SERVER_ID`: 전체가 100 → 잘못됨
- `RES_PATH`: `../../../../../Client/...` → 이전 `/dotnet/Server/Client/...` 오류 재발 가능
- 모든 파일 크기 376바이트 → 공통 `net8.0/config_2.txt`를 일괄 복사한 것으로 추정

저장소 기준으로도 서버 ID는 서로 다릅니다.

```text
Gateway01       100
Gateway02       101
Hive            200
Certify         300
Game01          1001
Community       1002
Database01      1003
Inter           3001
Chatting        8000
GlobalCommunity 20000
```

GlobalTrade, InterCommunity, GlobalGame은 운영 DB의 `server_info` 값으로 확인해야 합니다.

```bash
mysql -p -D astellia_global \
  -e "SELECT ServerName, server_id FROM server_info WHERE state=1 ORDER BY ServerName;"
```

각 서버의 `config_2.txt`에서 다음을 서버별로 수정해야 합니다.

```text
SERVER_ID:<server_info에 등록된 해당 서버 ID>
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
```

수정 후 중복 여부를 확인하십시오.

```bash
grep -H '^SERVER_ID:' \
  /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/*/config_2.txt \
  | sort -t: -k3n
```

그리고 데이터 경로도 확인합니다.

```bash
test -d /dotnet/Client/Assets/ResourceBundles/Data \
  && echo "RES_PATH OK" \
  || echo "RES_PATH NOT FOUND"
```

현재 상태에서는 `pm2 restart all`을 실행하면 안 됩니다. 모든 프로세스가 서버 ID 100으로 접속해 자신을 Gateway01로 인식할 수 있습니다. 서버별 ID와 `RES_PATH`를 바로잡은 뒤 한 서버씩 시작해 `ServerId`와 `StartServer` 로그를 확인해야 합니다.

### User

# Files pasted by the user:

## "[ec2-user@Ast-New-QA dotnet]$ ^C [ec2-user@Ast-New-QA dotnet]$ find /dotnet/Ser…": C:\Users\dumaclub\.codex/attachments/1e2e9e54-35ca-4a4c-aa2a-b1ff9922cabd/pasted-text.txt

Pasted text contains the user's request.

## My request:

### Assistant

추가 실행 결과를 확인해 서버별 ID와 리소스 경로가 정상화됐는지, 아직 남은 차단 요인이 무엇인지 판별하겠습니다.

### Assistant

아직 정상화되지 않았습니다. DB 접속 정보는 복구됐지만 두 가지 치명적인 설정 오류가 남아 있습니다.

1. 모든 서버가 `SERVER_ID:100`입니다. 각 프로세스가 모두 Gateway01로 인식될 수 있습니다.
2. `RES_PATH`가 `../../../../../`에서 `../../../../`로 변경됐습니다. `../`가 하나 더 줄어 잘못된 경로가 더 깊어졌습니다.

파일 크기가 376바이트에서 373바이트로 정확히 3바이트 줄어든 것도 `../` 하나가 제거된 결과입니다.

`RES_PATH`는 상대경로 대신 다음 절대경로로 통일하십시오.

```text
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
```

대상 파일을 백업하면서 경로만 안전하게 수정하는 명령입니다.

```bash
game_root=/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer
backup_suffix=$(date +%Y%m%d_%H%M%S)

for config_file in "$game_root"/*/config_2.txt; do
  cp -a "$config_file" "${config_file}.bak_${backup_suffix}"
  sed -i \
    's|^RES_PATH:.*|RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/|' \
    "$config_file"
done
```

서버 ID는 실제 DB 설정을 조회해야 합니다.

```bash
mysql -h 43.155.248.237 -P 3306 -u user -p astellia_global \
  -e "SELECT ServerName, server_id, type, state FROM server_info ORDER BY ServerName;"
```

조회 결과에 따라 각 디렉터리의 `SERVER_ID`를 서로 다르게 설정하십시오. 수정 후 검증합니다.

```bash
grep -H -E '^(SERVER_ID|RES_PATH):' "$game_root"/*/config_2.txt
```

중복 ID 검사:

```bash
awk -F: '/^SERVER_ID:/{print $2}' "$game_root"/*/config_2.txt \
  | sort -n | uniq -c
```

정상이라면 각 ID 앞의 개수가 대부분 `1`이어야 합니다. 현재처럼 `100`이 13개 나오면 전체 재시작하면 안 됩니다. 서버별 ID까지 수정한 후 한 프로세스씩 기동해 확인해야 합니다.

### User

105|Gatewa | 2026.08.27-16.43.31.787 [Info] eAddServer serverId:21000, zmqIp:127.0.0.1, zmqPort:16800, customSocketCount:12 (D:\ProjectA\Trunk\Dev\Server\EgonServer\Controllers\SendController.cs:109)
105|Gatewa | 2026.08.27-16.43.31.791 [Info] SerialGenerator init, serverIndex: 1 (D:\ProjectA\Trunk\Dev\Server\EgonServer\Util\SerialGenerator.cs:120)

/home/ec2-user/.pm2/logs/Gateway01-error.log last 15 lines:
105|Gatewa | Unhandled exception. System.IO.DirectoryNotFoundException: Could not find a part of the path '/dotnet/Server/EgonServer/Client/Assets/ResourceBundles/Data/'.
105|Gatewa |    at System.IO.FileSystem.GetAttributes(String fullPath)
105|Gatewa |    at K2Server.ServerModule.CheckDir\_md5(UInt32& hashKey, String \_path) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Server\ServerModule.cs:line 2069
105|Gatewa |    at K2Server.ServerModule.Createmd5(String \_path) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Server\ServerModule.cs:line 2062
105|Gatewa |    at K2Server.ServerModule.Load(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataloadeType, Int32 newServerGroupId) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Server\ServerModule.cs:line 447
105|Gatewa |    at K2Server.Program.OnConsoleStart(Int32 serverId, String dbIP, Int32 dbPort, String dbName, String dbId, String dbPassword, String svrName, Int32 dataloadeType, Int32 newServerGroupId) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Program.cs:line 197
105|Gatewa |    at K2Server.Program.Main(String[] args) in D:\ProjectA\Trunk\Dev\Server\EgonServer\Program.cs:line 168

&#x20;아직 이 오류가 있습니다.&#x20;

### Assistant

오류 경로가 `/dotnet/Server/EgonServer/Client/...`인 것으로 보아 Gateway01의 `config_2.txt`가 아직 다음 상대경로를 사용하고 있습니다.

```text
RES_PATH:../../../../Client/Assets/ResourceBundles/Data/
```

이 값을 절대경로로 수정해야 합니다.

```bash
pm2 stop Gateway01

gateway_config=/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/Gateway01/config_2.txt
cp -a "$gateway_config" "${gateway_config}.bak"

sed -i \
  's|^RES_PATH:.*|RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/|' \
  "$gateway_config"

grep '^RES_PATH:' "$gateway_config"
test -d /dotnet/Client/Assets/ResourceBundles/Data \
  && echo "RESOURCE DIRECTORY OK" \
  || echo "RESOURCE DIRECTORY NOT FOUND"
```

정상 출력은 다음과 같아야 합니다.

```text
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
RESOURCE DIRECTORY OK
```

그 후 Gateway01만 다시 시작합니다.

```bash
pm2 restart Gateway01
pm2 logs Gateway01 --lines 100
```

만약 `RESOURCE DIRECTORY NOT FOUND`가 출력된다면 설정 문제가 아니라 `/dotnet/Client/Assets/ResourceBundles/Data/` 데이터 배포 자체가 누락된 것입니다.

참고로 다음 로그는 오류가 아닙니다.

```text
eAddServer serverId:21000
SerialGenerator init, serverIndex:1
```

각각 다른 서버 등록 정보와 내부 시리얼 인덱스입니다. 현재 종료 원인은 오직 `RES_PATH`입니다. Gateway01 정상 구동을 확인한 다음 다른 서버의 `RES_PATH`도 같은 절대경로로 변경하되, 다른 서버들의 `SERVER_ID:100` 문제는 별도로 반드시 수정해야 합니다.

### User

[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$ sed -i \\
&#x20; 's|^RES\_PATH:.\*|RES\_PATH:/dotnet/Client/Assets/ResourceBundles/Data/|' \\
&#x20; "$gateway\_config"
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$ grep '^RES\_PATH:' "$gateway\_config"
test -d /dotnet/Client/Assets/ResourceBundles/Data \\
&#x20; && echo "RESOURCE DIRECTORY OK" \\
&#x20; || echo "RESOURCE DIRECTORY NOT FOUND"
RES\_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
RESOURCE DIRECTORY OK
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;
[ec2-user\@Ast-New-QA dotnet]$&#x20;

### Assistant

Gateway01의 리소스 경로는 정상적으로 수정됐고 실제 디렉터리도 존재합니다.

Gateway01 ID도 확인한 후 단독 재시작하십시오.

```bash
grep '^SERVER_ID:' "$gateway_config"

pm2 restart Gateway01
pm2 logs Gateway01 --lines 100
```

Gateway01은 저장소 기준 `SERVER_ID:100`이 맞습니다. 로그에서 아래 항목을 확인하면 됩니다.

- `DirectoryNotFoundException`이 더 이상 발생하지 않음
- `StartServer : Gateway01`
- PM2가 반복 재시작하지 않음

Gateway01이 정상화되면 나머지 `config_2.txt`의 `RES_PATH`도 동일한 절대경로로 변경할 수 있습니다. 다만 다른 서버는 아직 `SERVER_ID:100`으로 복제된 상태이므로 ID를 수정하기 전에는 시작하지 마십시오.

### User

맞게 수정된건가요?&#x20;

### Assistant

네, Gateway01의 `RES_PATH`는 올바르게 수정되었습니다.

```text
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
RESOURCE DIRECTORY OK
```

즉, 이전 `DirectoryNotFoundException`의 원인은 해결된 상태입니다.

다만 최종 확인은 Gateway01 재시작 후 해야 합니다.

```bash
pm2 restart Gateway01
pm2 logs Gateway01 --lines 100
```

로그에 `DirectoryNotFoundException`이 없고 `StartServer : Gateway01`이 나오면 정상입니다.

주의: 다른 서버들은 아직 `SERVER_ID:100`일 가능성이 있으므로 전체 재시작은 하지 마십시오. Gateway01의 ID 100만 정상입니다.

### User

나머지도 다 수정하는 스크립트 만들어 주세요.&#x20;

### Assistant

나머지 서버의 `config_2.txt`에서 `RES_PATH`만 일괄 수정하는 안전한 Bash 스크립트를 만들겠습니다. 수정 전 모든 파일을 검사하고 개별 백업을 만든 뒤 적용하며, `SERVER_ID`는 서버별 값이 아직 확정되지 않았으므로 건드리지 않고 목록만 출력하도록 하겠습니다.

### Assistant

모든 서버의 `config_2.txt`에서 `RES_PATH`를 일괄 수정하는 스크립트를 만들었습니다.

[fix_all_res_paths.sh](C:/Users/dumaclub/Documents/ChatGPT/Astellia02/fix_all_res_paths.sh)

EC2 서버로 복사한 후 실행하십시오.

```bash
chmod +x fix_all_res_paths.sh
./fix_all_res_paths.sh
```

스크립트는 다음 작업을 합니다.

- 대상 리소스 디렉터리 존재 여부 확인
- 모든 `config_2.txt` 사전 검사
- 각 설정 파일 백업 생성
- `RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/`로 변경
- 변경 결과와 `SERVER_ID` 목록 출력
- PM2는 재시작하지 않음

`SERVER_ID`는 서버별 DB 매핑이 필요하므로 변경하지 않습니다. 출력 결과를 확인한 뒤 전체 재시작 여부를 결정해야 합니다.

### User

[ec2-user\@Ast-New-QA dotnet]$
[ec2-user\@Ast-New-QA dotnet]$ cat pm2\_setting.sh
pm2 delete all

dbName="astellia\_global"

query="SELECT ServerName FROM server\_info WHERE state = 1;"
echo $query;
serverlist=`echo $query | mysql -h 127.0.0.1 -u user -pqwer1234 ${dbName} | awk 'NR>1'`

\#serverlist="Dev\_1"

echo $serverlist;

for NAME in $serverlist
do
echo "Name is ${NAME} ==================================================="
```bash
    mkdir -p /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/${NAME}

    cd /dotnet/Server/EgonServer/bin/NFT_SERVER/net8.0/
    cp -rf * ./../GameServer/${NAME}

    query="SELECT server_id FROM server_info WHERE ServerName=\""${NAME}"\"";
    server_id=`echo $query | mysql -h 127.0.0.1 -u user -pqwer1234 ${dbName} | awk 'NR>1'`

    cd /dotnet/Server/EgonServer/bin/NFT_SERVER/AWS_QA/
    pwd
    cp -f ./ConfigFile/config_default.txt ./../GameServer/${NAME}/config.txt
    sed -i 's/SVID/'${server_id}'/g' ./../GameServer/${NAME}/config.txt
    sed -i 's/DBNM/'${dbName}'/g' ./../GameServer/${NAME}/config.txt

    cd /dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/${NAME}/
    echo $NAME $server_id
```

# pm2 start "dotnet EgonServer.dll" --name ${NAME}
```swift
    /usr/local/bin/pm2 start "dotnet EgonServer.dll \"\" \"\" \"\" \"\" \"\" \"\" \"2\" \"2\"" --name ${NAME}
```

done

pm2 flush

pm2 restart all

pm2 logs

[ec2-user\@Ast-New-QA dotnet]$

위에는 서버 실행 프로세스 입니다.

[ec2-user\@Ast-New-QA AWS\_QA]$ pwd
/dotnet/Server/EgonServer/bin/NFT\_SERVER/AWS\_QA
[ec2-user\@Ast-New-QA AWS\_QA]$
[ec2-user\@Ast-New-QA AWS\_QA]$
[ec2-user\@Ast-New-QA AWS\_QA]$
[ec2-user\@Ast-New-QA AWS\_QA]$
[ec2-user\@Ast-New-QA AWS\_QA]$ cat ./ConfigFile/config\_default.txt
SERVER\_KIND:QA
SERVER\_ID:SVID
GLOBAL\_CONNECTION\_INFO:Server=127.0.0.1;Port=3306;Database=DBNM;
RES\_PATH:../../../../../../Client/Assets/ResourceBundles/Data/
DEVELOP\_MODE:false
REDIS\_KEY\_PREFIX:true
DEBUGLOG:false
DEBUGLOGTYPE:Status\_Effect
[ec2-user\@Ast-New-QA AWS\_QA]$

잘못 설정된 부분이 있나요?

### Assistant

실행 스크립트와 설정 선택 로직을 대조하면 원인이 명확합니다. `config.txt`는 서버별로 정상 생성하지만, PM2 인자 `"2"` 때문에 프로그램은 복사돼 있던 `config_2.txt`를 우선 읽어 `config.txt`를 완전히 무시합니다. `"2"`가 다른 데이터 로딩에도 쓰이는지 확인한 뒤 가장 안전한 수정안을 정리하겠습니다.

### Assistant

네. 핵심적으로 잘못된 부분이 정확히 확인됐습니다.

현재 동작 순서는 다음과 같습니다.

1. `net8.0/*`를 복사하면서 `config_1.txt`, `config_2.txt`까지 복사
2. 서버별 ID는 `config.txt`에만 설정
3. PM2 실행 인자로 `dataLoadType=2` 전달
4. 프로그램이 `config.txt` 대신 `config_2.txt`를 우선 로드
5. 서버별 ID와 올바른 경로가 들어간 `config.txt`는 무시됨

문제가 되는 부분:

```bash
cp -rf * ./../GameServer/${NAME}
```

```bash
pm2 start "dotnet EgonServer.dll \"\" \"\" \"\" \"\" \"\" \"\" \"2\" \"2\"" --name ${NAME}
```

코드상 7번째 인자 `"2"`가 `dataLoadType`이며, [ConfigLoader.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Util/ConfigLoader.cs:44)가 `config_2.txt`를 선택하게 합니다.

수정된 핵심 부분은 다음과 같습니다.

```bash
target_dir=/dotnet/Server/EgonServer/bin/NFT_SERVER/GameServer/${NAME}
binary_dir=/dotnet/Server/EgonServer/bin/NFT_SERVER/net8.0
template_file=/dotnet/Server/EgonServer/bin/NFT_SERVER/AWS_QA/ConfigFile/config_default.txt

mkdir -p "$target_dir"

cp -rf "$binary_dir"/. "$target_dir"/

# 복사된 공통 typed 설정 제거
rm -f "$target_dir/config_1.txt"
rm -f "$target_dir/config_2.txt"

# 서버별 설정 생성
cp -f "$template_file" "$target_dir/config.txt"
sed -i "s/SVID/${server_id}/g" "$target_dir/config.txt"
sed -i "s/DBNM/${dbName}/g" "$target_dir/config.txt"

# dataLoadType=0으로 config.txt를 직접 사용
/usr/local/bin/pm2 start \
  "dotnet EgonServer.dll \"\" \"\" \"\" \"\" \"\" \"\" \"0\" \"0\"" \
  --name "${NAME}"
```

템플릿의 `RES_PATH`도 절대경로로 변경하는 것이 안전합니다.

```text
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
```

즉, `config_default.txt`는 다음처럼 수정하십시오.

```text
SERVER_KIND:QA
SERVER_ID:SVID
GLOBAL_CONNECTION_INFO:Server=127.0.0.1;Port=3306;Database=DBNM;
RES_PATH:/dotnet/Client/Assets/ResourceBundles/Data/
DEVELOP_MODE:false
REDIS_KEY_PREFIX:true
DEBUGLOG:false
DEBUGLOGTYPE:Status_Effect
```

수정 후 정상 로그에서는 반드시 다음처럼 `config.txt`가 선택되어야 합니다.

```text
Config Path() => .../GameServer/Gateway01/config.txt
```

`config_2.txt`가 표시되면 아직 잘못된 실행 인자나 파일이 남은 것입니다.

추가로 마지막 `"2"`는 현재 Linux 실행 코드에서 사용되지 않으며, `pm2 restart all`도 이미 모든 앱을 `start`했으므로 중복입니다. DB 비밀번호가 스크립트에 평문으로 저장된 점도 추후 MySQL option file 방식으로 변경하는 것이 좋습니다.
