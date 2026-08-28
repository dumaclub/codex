# Fix NetMQ port conflict

- Project: Astellia02
- Session ID: `01a04211-639a-7b83-baaa-232c38633836`
- Workspace: `C:\Users\dumaclub\Documents\ChatGPT\Astellia02`
- Started: 2026-08-27T07:13:51.338Z
- Updated: 2026-08-27T07:14:43.4785296Z
- Messages exported: 5

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

# Files pasted by the user:

## "18|Chatting | 2026.08.27-16.13.04.272 [System] CreateDealerSocket connectionInf…": C:\Users\dumaclub\.codex/attachments/1417157c-32c3-44dc-a77c-c4bdaae1ee08/pasted-text.txt

## My request:
&#x20;

### Assistant

요청 내용이 비어 있어, 우선 첨부된 로그의 범위와 오류 단서를 확인하겠습니다. 확인 후 어떤 분석이 가능한지 바로 정리해 드릴게요.

### Assistant

첨부 내용에는 실제 요청이 포함되어 있네요. 핵심은 `InterCommunity` 시작 중 NetMQ 바인드 주소가 이미 사용 중이라는 오류입니다. 이제 포트 산정 방식과 `InterCommunity`가 실제로 어떤 주소를 바인드하는지 코드에서 추적하겠습니다.

### Assistant

코드상 개발 모드에서는 각 ZMQ 기준 포트부터 연속 12개를 바인드합니다. DB 값만 계산하면 `Inter`는 `15400~15411`, `InterCommunity`는 `16500~16511`이며 서로 겹치지 않습니다. 따라서 현재 자료만으로는 DB 중복보다는 같은 호스트의 기존 리스너/중복 실행 가능성이 더 높고, 실행 설정까지 확인해 원인을 좁히겠습니다.

### Assistant

확인 결과, 원인은 DB 포트 중복이 아니라 실행 호스트에서 ZMQ 포트가 이미 사용 중인 상황입니다.

개발 모드에서는 각 `zmqPort`부터 연속 12개 포트를 바인드합니다.

- `Inter`: `15400~15411`
- `InterCommunity`: `16500~16511`

제공된 `server_info` 전체를 이 기준으로 계산해도 포트 범위끼리 겹치지 않습니다.

코드 흐름은 다음과 같습니다.

- 개발 모드에서 소켓 수를 12개로 설정: [ServerController.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Controllers/ServerController.cs:164)
- `zmqPort + i`를 `127.0.0.1`에 바인드: [ServerController.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Controllers/ServerController.cs:391)
- 실제 예외 발생 위치: [ServerController.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Controllers/ServerController.cs:397)
- 모든 개발 서버 타입을 순차적으로 바인드하는 호출부: [ServerModule.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Server/ServerModule.cs:1808)

따라서 `[InterCommunity]` 로그 접두사만으로 `16500` 충돌이라고 단정하면 안 됩니다. 정확한 충돌 포트는 예외 직전에 출력된 아래 로그의 주소입니다.

```text
BindRouterForDevelop() - connectionInfo : tcp://127.0.0.1:xxxxx
```

`Chatting`의 `CreateDealerSocket ... 15410/15411`은 해당 포트로 연결하는 클라이언트 로그이며, 그 자체가 포트를 점유했다는 의미는 아닙니다.

Linux 실행 서버에서 다음을 확인하면 점유 프로세스를 찾을 수 있습니다.

```bash
pgrep -af EgonServer
sudo ss -ltnp | grep -E ':(152|153|154|155|156|157|158|159|160|165|166|167|168)[0-9]{2}\b'
```

가장 가능성 높은 원인은 다음 순서입니다.

1. 이전 `EgonServer` 프로세스가 완전히 종료되지 않음
2. 시작 스크립트 또는 서비스 관리자가 `EgonServer`를 중복 실행
3. 다른 프로세스가 해당 포트를 사용 중
4. 로그에 제공되지 않은 `server_info` 레코드나 다른 DB 환경의 포트 중복

점유 프로세스를 확인해 기존 서버를 정상 종료한 뒤 하나만 재시작하는 것이 우선 조치입니다. 코드 수정은 하지 않았습니다. 향후에는 397번 바인드를 예외 처리해 충돌한 `connectionInfo`와 프로세스 정보를 명확히 남기도록 보강하는 것이 좋습니다.
