# Fix Redis ECONNREFUSED error

- Project: Zzz
- Session ID: `019fb5eb-21e3-7e23-a947-6febd9e329e0`
- Workspace: `C:\Users\dumaclub\Documents\New project`
- Started: 2026-07-31T02:05:13.884Z
- Updated: 2026-07-31T02:05:22.3433083Z
- Messages exported: 8

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

Client On Error: Error: connect ECONNREFUSED 10.10.20.207:6379 Config right?
현재 로컬서버에서 개발서버 redis로 접속시 위와 같이 오류 발생되었는데 레디스 환경파일에 모든 접속 허용하는 부분을 확인해 보면 될까요?
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bind 127.0.0.1 -::1
위에 처럼 되어 있습니다. 개발서버는 linux 입니다.

### Assistant

네, 우선 `bind` 설정을 확인하는 방향이 맞습니다. 다만 `ECONNREFUSED`는 인증 실패가 아니라 개발 서버의 `6379` 포트가 외부 인터페이스에서 수신 중이 아니거나 방화벽에서 거절되는 경우가 핵심입니다. 공식 Redis 기준과 함께 안전한 점검 순서를 정리하겠습니다.

### Assistant

네. 현재 설정이 원인일 가능성이 매우 높습니다.

```conf
bind 127.0.0.1 -::1
```

이 설정은 Redis가 개발 서버의 로컬 접속만 받도록 합니다.

- `127.0.0.1`: IPv4 localhost
- `-::1`: IPv6 localhost가 존재하면 바인딩
- 따라서 외부의 로컬 개발 PC가 `10.10.20.207:6379`로 접속하면 받을 수 없습니다.

안전하게는 Redis 서버의 사설 IP만 추가하세요.

```conf
bind 127.0.0.1 10.10.20.207 -::1
protected-mode yes
```

`bind 0.0.0.0`도 모든 IPv4 인터페이스에서 수신하게 만들지만, Redis를 광범위하게 노출하므로 권장하지 않습니다. Redis 공식 문서도 신뢰할 수 있는 클라이언트만 방화벽으로 허용하라고 권고합니다. [Redis 보안 문서](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)

변경 전후로 개발 서버에서 확인하세요.

```bash
# Redis 서비스 이름은 배포판에 따라 둘 중 하나
sudo systemctl status redis-server
sudo systemctl status redis

# 실제 수신 주소 확인
sudo ss -lntp | grep 6379

# Redis 서버 내부 접속 확인
redis-cli -h 127.0.0.1 -p 6379 ping

# 서버가 실제로 가진 IP 확인
ip -br addr
```

현재는 `ss` 결과가 대략 이렇게 나올 가능성이 큽니다.

```text
127.0.0.1:6379
```

설정 변경 후에는 다음처럼 나와야 합니다.

```text
10.10.20.207:6379
```

Redis를 재시작합니다.

```bash
sudo systemctl restart redis-server
sudo journalctl -u redis-server -n 50 --no-pager
```

그리고 방화벽에서 로컬 개발 PC의 IP만 허용하세요. UFW를 사용한다면:

```bash
sudo ufw allow from <로컬개발PC_IP> to any port 6379 proto tcp
sudo ufw status
```

클라우드/VPC 서버라면 보안 그룹이나 네트워크 ACL도 동일하게 확인해야 합니다. 설정 후 로컬 PC에서 테스트합니다.

```bash
redis-cli -h 10.10.20.207 -p 6379 ping
```

정상이면 `PONG`이 반환됩니다.

추가로 외부 접속을 허용할 때는 Redis 6 이상이면 ACL 사용자와 비밀번호를 설정하는 것이 좋습니다. `ECONNREFUSED`가 해결된 뒤 `NOAUTH`가 나온다면 네트워크는 연결됐고 인증 설정만 남았다는 뜻입니다. 반대로 계속 `ECONNREFUSED`라면 적용한 `redis.conf`가 실제 서비스가 사용하는 파일인지, 서비스 실행 여부와 `ss` 결과부터 확인해야 합니다.

### User

# Files mentioned by the user:

## codex-clipboard-970f00c6-0c3a-44a1-a03e-b1f44f3e912a.png: C:/Users/dumaclub/AppData/Local/Temp/codex-clipboard-970f00c6-0c3a-44a1-a03e-b1f44f3e912a.png

## codex-clipboard-7fe3bbc9-5365-4974-b3be-be655efd40f0.png: C:/Users/dumaclub/AppData/Local/Temp/codex-clipboard-7fe3bbc9-5365-4974-b3be-be655efd40f0.png

## codex-clipboard-b35b307c-75be-400b-b372-4a54cdc526b0.png: C:/Users/dumaclub/AppData/Local/Temp/codex-clipboard-b35b307c-75be-400b-b372-4a54cdc526b0.png

## codex-clipboard-334c70ed-c185-4a9b-84de-0e76983b6ce8.png: C:/Users/dumaclub/AppData/Local/Temp/codex-clipboard-334c70ed-c185-4a9b-84de-0e76983b6ce8.png

## My request for Codex:
말씀하신 대로 수정하였는데 접속이 정상적으로 안되는것 같습니다. 1번캡처는 cmd 창에서 접속 요청시 결과이고 2번은 redis client manager 프로그램에서 접속한 내용 3번은 개발서버 설정변경 내용, 4번은 현재 프로세스 상황입니다.

<image name=[Image #1] path="C:\Users\dumaclub\AppData\Local\Temp\codex-clipboard-970f00c6-0c3a-44a1-a03e-b1f44f3e912a.png">

</image>

<image name=[Image #2] path="C:\Users\dumaclub\AppData\Local\Temp\codex-clipboard-7fe3bbc9-5365-4974-b3be-be655efd40f0.png">

</image>

<image name=[Image #3] path="C:\Users\dumaclub\AppData\Local\Temp\codex-clipboard-b35b307c-75be-400b-b372-4a54cdc526b0.png">

</image>

<image name=[Image #4] path="C:\Users\dumaclub\AppData\Local\Temp\codex-clipboard-334c70ed-c185-4a9b-84de-0e76983b6ce8.png">

</image>

### Assistant

캡처상 네트워크 연결 자체는 이미 성공했습니다. 1번의 `-DENIED ... protected mode`는 포트 접근은 되었지만 Redis 보안 정책에서 요청을 거절한 상태입니다. 설정 파일과 실제 실행 프로세스가 서로 다르게 적용된 흔적도 보여서, 네 장을 기준으로 원인을 정확히 짚어보겠습니다.

### Assistant

캡처 결과를 보면 `ECONNREFUSED` 문제는 해결됐습니다. 현재는 Redis까지 TCP 연결은 성공했지만, `protected-mode`가 인증되지 않은 외부 요청을 차단하고 있습니다.

1번 메시지가 원인을 정확히 보여줍니다.

```text
-DENIED Redis is running in protected mode because protected mode is enabled
and no password is set for the default user
```

3번 설정은 다음과 같은 상태입니다.

```conf
bind 127.0.0.1 10.10.20.207 -::1
protected-mode yes
```

외부 IP 바인딩은 되었지만 `protected-mode yes` 상태에서 비밀번호가 없어서 차단되는 것입니다.

가장 권장하는 해결 방법은 비밀번호를 설정하는 것입니다.

`/etc/redis/redis.conf`에 다음을 추가하세요.

```conf
bind 127.0.0.1 10.10.20.207 -::1
protected-mode yes

requirepass 충분히_길고_복잡한_비밀번호
```

예시는 다음과 같습니다.

```conf
requirepass DevRedis_긴임의문자열
```

실제 운영 비밀번호는 예시보다 충분히 길고 무작위로 생성하세요.

설정 후 Redis를 재시작합니다.

```bash
sudo systemctl restart redis-server
sudo systemctl status redis-server --no-pager
```

배포판에 따라 서비스 이름이 `redis`라면 다음 명령을 사용합니다.

```bash
sudo systemctl restart redis
sudo systemctl status redis --no-pager
```

실제 설정 적용 여부는 서버에서 다음과 같이 확인하세요.

```bash
redis-cli -h 127.0.0.1 CONFIG GET bind
redis-cli -h 127.0.0.1 CONFIG GET protected-mode
redis-cli -h 127.0.0.1 INFO server | grep config_file
sudo ss -lntp | grep 6379
```

예상 결과는 대략 다음과 같습니다.

```text
bind
127.0.0.1 10.10.20.207 -::1

protected-mode
yes
```

`ss` 결과에는 다음 주소가 포함되어야 합니다.

```text
10.10.20.207:6379
```

4번의 다음 프로세스 표시는 Redis가 실행 중이라는 뜻입니다.

```text
/usr/bin/redis-server 127.0.0.1:6379
```

다만 `ps`의 프로세스 제목만으로 모든 바인딩 주소를 판단하기는 어렵습니다. `CONFIG GET bind`와 `ss -lntp` 결과가 더 정확합니다. 특히 아래 명령의 `config_file` 값이 `/etc/redis/redis.conf`인지 확인하세요.

```bash
redis-cli -h 127.0.0.1 INFO server | grep config_file
```

설정 파일이 비어 있거나 다른 경로라면 서비스가 수정한 파일을 사용하지 않는 것입니다. 그때는 다음으로 실제 실행 설정을 확인합니다.

```bash
systemctl cat redis-server | grep ExecStart
```

Redis Desktop Manager에는 다음과 같이 입력하면 됩니다.

```text
Host:     10.10.20.207
Port:     6379
Username: default
Password: redis.conf에 설정한 비밀번호
```

Redis 버전이나 클라이언트에 따라 `Username`은 공란으로 두고 `Password`만 입력해도 됩니다. 먼저 `default`로 시도하고, 실패하면 Username을 비워보세요.

애플리케이션 연결 설정에도 동일한 인증 정보를 추가해야 합니다. 예를 들어 URI 형식을 사용한다면:

```text
redis://:비밀번호@10.10.20.207:6379
```

Redis 6 이상의 사용자명 포함 형식은 다음과 같습니다.

```text
redis://default:비밀번호@10.10.20.207:6379
```

비밀번호 없이 사용하려면 아래처럼 바꿀 수는 있습니다.

```conf
protected-mode no
```

하지만 Redis 명령 전체가 무인증으로 노출될 수 있어 권장하지 않습니다. 반드시 사설망이고 방화벽에서 특정 개발 PC IP만 허용한 경우에만 제한적으로 고려해야 합니다. Redis 공식 문서도 방화벽과 인증을 함께 적용할 것을 권장합니다. [Redis 보안 문서](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)

정리하면 현재 상태는 다음과 같습니다.

```text
로컬 PC → 10.10.20.207:6379 연결 성공
                    ↓
           Redis protected-mode에서 거절
                    ↓
      비밀번호 설정 + Redis 재시작 필요
```

가장 먼저 `requirepass`를 추가하고 재시작한 다음, Redis Manager에 같은 비밀번호를 입력하면 됩니다.

### User

비밀번호는 사용하지 않으려고 하는데 protect mode 만 설정에서 제거하고 레디스 서버를 재시작 하면 될까요?

### Assistant

네. 다만 `protected-mode` 설정을 “제거”하면 기본값인 `yes`가 적용될 수 있으므로, 명시적으로 `no`로 변경해야 합니다.

```conf
bind 127.0.0.1 10.10.20.207 -::1
protected-mode no
```

그다음 재시작하세요.

```bash
sudo systemctl restart redis-server
sudo systemctl status redis-server --no-pager
```

적용 여부를 확인합니다.

```bash
redis-cli -h 127.0.0.1 CONFIG GET bind
redis-cli -h 127.0.0.1 CONFIG GET protected-mode
sudo ss -lntp | grep 6379
```

예상 결과:

```text
protected-mode
no
```

이후 Redis Manager에서는:

```text
Host: 10.10.20.207
Port: 6379
Username: 비워둠
Password: 비워둠
```

단, 비밀번호 없이 `protected-mode no`를 사용하면 Redis에 접속 가능한 사용자는 데이터를 조회·변경·삭제할 수 있습니다. 최소한 방화벽에서 접속이 필요한 개발 PC 또는 사내 대역만 허용하세요.

예를 들어 UFW 사용 시:

```bash
sudo ufw allow from <개발PC_IP> to any port 6379 proto tcp
sudo ufw status
```

공용 인터넷에 `6379` 포트를 개방하면 안 됩니다. 현재처럼 `bind`를 사설 IP `10.10.20.207`로 제한하고 방화벽까지 제한된 개발망이라면 사용할 수 있습니다.
