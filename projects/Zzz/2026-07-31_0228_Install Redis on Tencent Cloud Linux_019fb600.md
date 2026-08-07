# Install Redis on Tencent Cloud Linux

- Project: Zzz
- Session ID: `019fb600-1779-7a80-8613-b1161a306977`
- Workspace: `C:\Users\dumaclub\Documents\New project`
- Started: 2026-07-31T02:28:07.468Z
- Updated: 2026-07-31T02:28:51.4423101Z
- Messages exported: 10

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

[root@VM-16-13-tencentos ~]# uname -a
Linux VM-16-13-tencentos 5.4.241-24.0017.23 #1 SMP Thu Jul 24 19:45:18 CST 2025 x86_64 x86_64 x86_64 GNU/Linux
tencent cloud linux 에서 redis 서버 설치하는 방법을 알려주세요.

### Assistant

TencentOS의 정확한 릴리스에 따라 저장소와 패키지명이 달라질 수 있어서, 현재 공식 문서를 기준으로 가장 안전한 설치 절차를 확인해 정리하겠습니다. 먼저 OS 버전을 확인하고, 패키지 설치와 소스 설치 중 맞는 경로를 선택할 수 있게 안내할게요.

### Assistant

커널 버전상 TencentOS Server 3.3 계열로 보입니다. TencentOS 3은 `dnf`를 지원하므로 저장소 패키지로 설치하는 방법이 가장 간단합니다. [TencentOS 공식 문서](https://cloud.tencent.com/document/product/1397/72782)와 [Redis 공식 설치 문서](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-linux/) 기준입니다.

### 1. OS 버전 확인

```bash
cat /etc/os-release
```

### 2. Redis 설치

현재 저장소에서 제공되는 버전을 먼저 확인합니다.

```bash
dnf makecache
dnf info redis
```

설치합니다.

```bash
dnf install -y redis
```

만약 `dnf`가 없으면 동일하게 `yum`을 사용하세요.

```bash
yum install -y redis
```

### 3. 서비스 시작 및 자동 시작 설정

```bash
systemctl enable --now redis
systemctl status redis --no-pager
```

`active (running)`이면 정상입니다.

### 4. 동작 확인

```bash
redis-server --version
redis-cli ping
```

정상 응답:

```text
PONG
```

로그 확인은 다음과 같이 합니다.

```bash
journalctl -u redis -n 100 --no-pager
```

### 5. 기본 설정 파일 확인

일반적으로 설정 파일은 `/etc/redis/redis.conf`입니다. 정확한 위치는 다음 명령으로 확인할 수 있습니다.

```bash
rpm -ql redis | grep 'redis.conf$'
```

같은 서버의 애플리케이션에서만 Redis를 사용한다면 다음 설정을 유지하는 것이 안전합니다.

```conf
bind 127.0.0.1
protected-mode yes
port 6379
```

설정 변경 후에는 다음 명령을 실행합니다.

```bash
redis-server /etc/redis/redis.conf --test-memory 2
systemctl restart redis
redis-cli ping
```

### 다른 서버에서 접속해야 하는 경우

공인 인터넷에 `6379` 포트를 개방하면 안 됩니다. Redis 공식 보안 문서도 Redis 포트를 인터넷에서 차단하고 특정 인터페이스에만 바인딩하도록 권고합니다. [Redis 보안 문서](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)

예를 들어 Redis 서버의 사설 IP가 `10.0.1.10`이라면:

```conf
bind 127.0.0.1 10.0.1.10
protected-mode yes
requirepass 여기에_충분히_긴_비밀번호
```

적용 및 테스트:

```bash
systemctl restart redis
redis-cli -h 127.0.0.1 -a '여기에_충분히_긴_비밀번호' ping
```

Tencent Cloud 보안 그룹에서는 `6379/TCP`의 출발지를 애플리케이션 서버의 사설 IP 또는 보안 그룹으로만 제한하세요. `0.0.0.0/0`은 사용하지 않는 것이 좋습니다.

참고로 현재 커널 `5.4.241-24.0017.23`은 TencentOS가 공지한 3.3 계열 보안 수정 커널 `5.4.241-24.0017.32.2`보다 낮아 보입니다. 운영 서버라면 점검 후 업데이트를 권장합니다.

```bash
dnf update -y kernel
reboot
uname -r
```

관련 내용은 [TencentOS 보안 공지](https://cloud.tencent.com/document/product/1397/131324)에서 확인할 수 있습니다.

### User

회사 아이피는 접속할 수 있게 하려면 어떻게 해야 하나요?

### Assistant

회사 공인 IP만 허용하려면 Redis 설정, Tencent Cloud 보안 그룹, 서버 방화벽의 세 지점을 함께 제한해야 합니다. 공인 IP가 고정인지 확인한 뒤 `/32` 단일 IP 규칙으로 구성하는 방법을 정리하겠습니다.

### Assistant

가능합니다. 다만 Redis 인증정보는 기본적으로 암호화되지 않으므로, 인터넷에 `6379`를 직접 공개하기보다 SSH 터널이나 VPN을 권장합니다. [Redis 공식 문서](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)도 신뢰할 수 없는 네트워크에 Redis를 직접 노출하지 말라고 안내합니다.

## 권장 방법: SSH 터널

Redis는 로컬 접속만 유지합니다.

```conf
# /etc/redis/redis.conf
bind 127.0.0.1
protected-mode yes
```

회사 공인 IP만 Tencent Cloud 보안 그룹의 `TCP:22`에 허용한 뒤, 회사 PC에서 터널을 연결합니다.

```bash
ssh -N -L 6379:127.0.0.1:6379 root@서버_공인_IP
```

다른 터미널에서 Redis에 접속합니다.

```bash
redis-cli -h 127.0.0.1 -p 6379
```

이 방법은 Redis 포트와 인증정보가 인터넷에 직접 노출되지 않습니다.

## 직접 접속이 꼭 필요한 경우

예시:

```text
회사 공인 IP: 203.0.113.25
Redis 서버 사설 IP: 10.0.1.10
Redis 서버 공인 IP: Tencent Cloud에 표시된 공인 IP
```

먼저 회사 네트워크에서 공인 IP를 확인합니다.

```bash
curl -4 https://api.ipify.org
```

고정 IP인지도 네트워크 담당자에게 확인하세요. IP가 유동적이면 보안 그룹 규칙을 계속 수정해야 하므로 VPN이 적합합니다.

### 1. Redis 설정

서버의 사설 IP를 확인합니다.

```bash
ip -4 addr show scope global
```

설정 파일을 백업하고 편집합니다.

```bash
cp -a /etc/redis/redis.conf /etc/redis/redis.conf.bak
vi /etc/redis/redis.conf
```

다음처럼 설정합니다.

```conf
bind 127.0.0.1 10.0.1.10
protected-mode yes
port 6379
requirepass 충분히_길고_무작위인_비밀번호
```

비밀번호 생성 예:

```bash
openssl rand -base64 48
```

공인 IP는 보통 NAT로 연결되므로 `bind`에는 서버 네트워크 인터페이스에 실제로 존재하는 사설 IP를 지정합니다. `bind 0.0.0.0`은 피하는 편이 안전합니다.

적용하고 확인합니다.

```bash
systemctl restart redis
systemctl status redis --no-pager
ss -lntp | grep 6379
```

로컬 인증 테스트:

```bash
redis-cli -h 127.0.0.1 -p 6379 --askpass ping
```

정상이면 `PONG`이 출력됩니다.

### 2. Tencent Cloud 보안 그룹

Tencent Cloud 콘솔에서 다음 경로로 이동합니다.

```text
CVM → 해당 인스턴스 → 보안 → 보안 그룹 → 인바운드 규칙 추가
```

규칙은 다음처럼 만듭니다.

| 항목 | 값 |
|---|---|
| 출발지 | `203.0.113.25/32` |
| 프로토콜/포트 | `TCP:6379` |
| 정책 | 허용 |
| 설명 | 회사 Redis 접속 |

`203.0.113.25`는 실제 회사 공인 IP로 바꾸세요. `0.0.0.0/0 → TCP:6379` 규칙이 존재하면 반드시 제거해야 합니다. Tencent Cloud는 단일 IPv4 주소를 `/32` CIDR로 제한할 수 있습니다. [Tencent Cloud 보안 그룹 규칙 문서](https://cloud.tencent.com/document/product/213/112614)

### 3. 서버 방화벽도 제한

`firewalld`가 실행 중인지 확인합니다.

```bash
systemctl is-active firewalld
```

`active`라면 회사 IP만 허용합니다.

```bash
firewall-cmd --permanent \
  --add-rich-rule='rule family="ipv4" source address="203.0.113.25/32" port port="6379" protocol="tcp" accept'

firewall-cmd --reload
firewall-cmd --list-rich-rules
```

기존에 전체에 공개된 규칙이 있다면 확인합니다.

```bash
firewall-cmd --list-ports
```

`6379/tcp`가 일반 허용 포트로 표시된다면, 위의 회사 IP 제한 규칙을 만든 후 전체 허용을 제거합니다.

```bash
firewall-cmd --permanent --remove-port=6379/tcp
firewall-cmd --reload
```

### 4. 회사 PC에서 테스트

Redis CLI가 설치되어 있다면:

```bash
redis-cli -h 서버_공인_IP -p 6379 --askpass ping
```

Windows에서 포트 연결만 확인하려면:

```powershell
Test-NetConnection -ComputerName 서버_공인_IP -Port 6379
```

직접 연결 방식에서는 비밀번호와 Redis 데이터가 TLS 없이 평문으로 전달될 수 있습니다. 실제 운영 데이터라면 SSH 터널, VPN 또는 Redis TLS 구성을 사용하세요.

### User

# Files mentioned by the user:

## codex-clipboard-0493f53a-e2d1-4530-8c36-908139e71213.png: C:/Users/dumaclub/AppData/Local/Temp/codex-clipboard-0493f53a-e2d1-4530-8c36-908139e71213.png

## codex-clipboard-36d6c742-d0c4-4024-ba03-68f014f2df0a.png: C:/Users/dumaclub/AppData/Local/Temp/codex-clipboard-36d6c742-d0c4-4024-ba03-68f014f2df0a.png

## My request for Codex:
tencent cloud 방화벽 설정은 모두 통과하도록 설정되어 있습니다. redis.conf 파일에 있는 bind 항목에 추가가 필요한지가 궁금합니다.

<image name=[Image #1] path="C:\Users\dumaclub\AppData\Local\Temp\codex-clipboard-0493f53a-e2d1-4530-8c36-908139e71213.png">

</image>

<image name=[Image #2] path="C:\Users\dumaclub\AppData\Local\Temp\codex-clipboard-36d6c742-d0c4-4024-ba03-68f014f2df0a.png">

</image>

### Assistant

네, 추가가 필요합니다. 현재 화면상 Redis가 `127.0.0.1:6379`에서만 수신 중이라 외부에서는 방화벽 설정과 관계없이 접속할 수 없습니다.

Tencent Cloud 공인 IP가 아니라 서버의 사설 IP를 `bind`에 추가하세요.

### 1. 서버 사설 IP 확인

```bash
ip -4 addr show scope global
```

예를 들어 사설 IP가 `10.0.1.10`이면 `/etc/redis/redis.conf`를 다음처럼 변경합니다.

```conf
bind 127.0.0.1 10.0.1.10
protected-mode yes
requirepass 충분히_긴_비밀번호
```

Tencent Cloud 공인 IP는 보통 NAT로 연결되므로 `bind`에 공인 IP를 넣으면 시작 오류가 발생할 수 있습니다.

### 2. 적용 및 확인

```bash
redis-server /etc/redis/redis.conf --test-memory 2
systemctl restart redis
systemctl status redis --no-pager
ss -lntp | grep 6379
```

정상이라면 다음처럼 사설 IP가 표시됩니다.

```text
127.0.0.1:6379
10.0.1.10:6379
```

프로세스 표시도 다음과 비슷하게 바뀔 수 있습니다.

```text
redis-server 10.0.1.10:6379
```

### 3. 회사에서 접속

회사는 Redis 서버의 공인 IP로 접속합니다.

```bash
redis-cli -h 서버_공인_IP -p 6379 --askpass ping
```

정상 응답:

```text
PONG
```

중요한 점은 Tencent Cloud 보안 그룹이 정말로 “모두 허용(`0.0.0.0/0`)" 상태라면 위험하다는 것입니다. `6379/TCP`는 다음과 같이 회사 공인 IP만 허용해야 합니다.

```text
회사_공인_IP/32 → TCP 6379 → 허용
```

간단히 `bind 0.0.0.0`으로 설정해도 접속은 되지만, Redis가 모든 인터페이스에서 수신하게 됩니다. 보안 그룹이 회사 IP로 확실하게 제한된 경우에만 사용해야 합니다.

```conf
bind 0.0.0.0
protected-mode yes
requirepass 충분히_긴_비밀번호
```

권장 설정은 `bind 127.0.0.1 서버_사설_IP`입니다.

### User

bind 0.0.0.0 으로 설정하니 접속이 되는데 bind 127.0.0.1 xx.xxx.xx.xx 이런식으로 2개의 아이피를 설정해 놓으니 접속이 안되고 있습니다. 원인을 알려주세요.

### Assistant

원인은 거의 확실히 `bind`의 의미를 잘못 적용했기 때문입니다.

`bind`에는 “접속을 허용할 회사 IP”가 아니라, Redis 서버가 실제로 보유한 로컬 네트워크 인터페이스 IP를 적어야 합니다.

예를 들어 다음 IP를 넣으면 안 됩니다.

- 회사의 공인 IP
- Tencent Cloud 콘솔에 표시되는 서버 공인 IP(NAT 환경인 경우)

Tencent Cloud 공인 IP는 일반적으로 서버의 네트워크 인터페이스에 직접 할당되지 않고 NAT로 연결됩니다. 그래서 다음과 같은 오류가 발생할 수 있습니다.

```text
bind: Cannot assign requested address
```

`bind 0.0.0.0`에서 접속되는 이유는 Redis가 서버의 모든 로컬 인터페이스(사설 IP 포함)에서 수신하기 때문입니다.

### 올바른 설정

먼저 서버가 실제로 보유한 IP를 확인합니다.

```bash
ip -4 -br addr
```

예상 출력:

```text
lo      UNKNOWN  127.0.0.1/8
eth0    UP       10.0.1.10/24
```

이 경우 Redis 설정은 다음과 같아야 합니다.

```conf
bind 127.0.0.1 10.0.1.10
protected-mode yes
requirepass 충분히_긴_비밀번호
```

한 줄에 함께 작성하세요. 회사 IP나 서버 공인 IP는 넣지 않습니다.

적용합니다.

```bash
systemctl restart redis
systemctl status redis --no-pager -l
ss -lntp | grep 6379
```

정상 출력 예:

```text
LISTEN 0 511 127.0.0.1:6379
LISTEN 0 511 10.0.1.10:6379
```

회사에서는 계속 서버의 공인 IP로 접속합니다.

```bash
redis-cli -h 서버_공인_IP -p 6379 --askpass ping
```

접속 가능한 회사 IP 제한은 `bind`가 아니라 Tencent Cloud 보안 그룹에서 설정합니다.

```text
출발지: 회사_공인_IP/32
프로토콜/포트: TCP:6379
정책: 허용
```

현재 정확한 오류도 확인하려면 다음 명령을 실행하세요.

```bash
journalctl -u redis -n 50 --no-pager
```

아래 메시지가 있다면 로컬에 존재하지 않는 IP를 `bind`에 넣은 것이 원인입니다.

```text
Cannot assign requested address
```

정리하면:

```text
bind = Redis 서버가 수신할 서버 자체 IP
보안 그룹 = 접속을 허용할 회사 IP
```

따라서 `bind 127.0.0.1 서버_사설_IP`가 권장 설정입니다.
