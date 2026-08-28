# Locate initial membership reward

- Project: Astellia02
- Session ID: `01a022f1-2846-7652-a4b7-965127426df3`
- Workspace: `C:\Users\dumaclub\Documents\ChatGPT\Astellia02`
- Started: 2026-08-21T06:10:24.983Z
- Updated: 2026-08-21T06:13:27.1640033Z
- Messages exported: 8

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

멤버쉽 상품 구매 시 매일 지정된 시간에 메일 보내는 기능이 있습니다.\
아래 함수가 멤버쉽 구매 사용자에게 메일로 보상을 전달하는 함수입니다.\
public void ProcessScheduleReward(CS\_ZMQ\_PrivilegeDailyRewardRequest packet)\
private bool RequestDailyReward(int rewardKey, DateTime scheduleTime, DateTime requestTime)\
최초 구매시점에도 보상 메일을 발송하려고 하는데 어느 부분에 추가해야 하는지 알려주세요.&#x20;

### Assistant

구매 처리 흐름과 두 함수의 호출 관계를 먼저 추적해, “최초 구매 직후 1회 지급”을 넣어야 할 정확한 지점을 코드 기준으로 짚겠습니다. 현재는 변경하지 않고 분석만 하겠습니다.

### Assistant

로컬 명령 실행기가 프로세스 초기화 단계에서 종료되고 있어(코드 검색 자체가 시작되지 않음), 다른 읽기 경로로 저장소를 확인해 보겠습니다. 파일 변경은 하지 않습니다.

### Assistant

현재 체크아웃 파일에는 해당 심볼이 없어서, 삭제·이동되었거나 다른 브랜치에 있는지 Git 이력까지 확인하고 있습니다. 정확한 코드가 발견되지 않으면, 확인 가능한 호출 지점과 중복 지급 조건을 분리해 답변드리겠습니다.

### Assistant

추가 위치는 `ProcessScheduleReward()`나 `RequestDailyReward()` 내부가 아니라, **멤버십 구매가 확정되어 DB 반영까지 성공한 직후**가 적절합니다.

권장 구조는 다음과 같습니다.

```csharp
public void ProcessMembershipPurchase(...)
{
    // 결제 검증
    // 멤버십 생성/갱신
    // DB 저장 또는 트랜잭션 Commit

    if (isFirstPurchase)
    {
        RequestInitialReward(rewardKey, purchaseId, purchaseTime);
    }
}
```

`ProcessScheduleReward()`의 실제 메일 생성·발송 부분은 공통 함수로 분리해서 양쪽에서 호출하는 것이 안전합니다.

```csharp
public void ProcessScheduleReward(
    CS_ZMQ_PrivilegeDailyRewardRequest packet)
{
    SendPrivilegeRewardMail(
        packet.UserKey,
        packet.RewardKey,
        $"Daily:{packet.ScheduleTime:yyyyMMdd}");
}

public void ProcessInitialReward(
    CS_ZMQ_PrivilegeInitialRewardRequest packet)
{
    SendPrivilegeRewardMail(
        packet.UserKey,
        packet.RewardKey,
        $"Initial:{packet.PurchaseId}");
}

private void SendPrivilegeRewardMail(
    long userKey,
    int rewardKey,
    string deliveryKey)
{
    // 기존 ProcessScheduleReward의 보상 조회 및 메일 발송 로직
}
```

중요한 점은 다음 세 가지입니다.

- `ProcessScheduleReward()`를 가짜 패킷을 만들어 직접 호출하지 않는 것이 좋습니다. 이 함수는 스케줄 요청 처리용 진입점이기 때문입니다.
- `RequestDailyReward()`는 `scheduleTime` 기반 중복 검사와 지급일 계산을 할 가능성이 있으므로, 최초 구매 지급에는 별도의 `RequestInitialReward()`를 만드는 편이 명확합니다.
- 결제 재시도나 서버 재처리로 메일이 중복 지급되지 않도록 `purchaseId` 기준의 고유 지급 키가 필요합니다.

예를 들면 다음과 같습니다.

```text
Initial:{UserKey}:{PurchaseId}:{RewardKey}
Daily:{UserKey}:{RewardKey}:{ScheduleDate}
```

구매 즉시 보상이 당일 정기 보상을 대체하는 정책이라면 최초 보상 발송 시 당일 지급 이력도 함께 기록해야 합니다. 반대로 구매 보상이 정기 보상과 별도라면 지급 이력을 분리해야 합니다.

현재 접근 가능한 체크아웃에서는 질문에 적힌 두 함수의 구현을 찾지 못해 정확한 파일과 줄 번호까지 특정하지는 못했습니다. 두 함수 본문과 멤버십 구매 완료 처리 함수를 제공해 주시면 실제로 어느 줄 다음에 넣어야 하는지 구체적으로 짚을 수 있습니다.

### User

테스트 진행하려고 만든 함수가 있는데 private bool Test(UserGameModel user, string guildName) 이 형태로 만들어서 전송하면 맞게 되나요?

### Assistant

`Test` 함수 시그니처만으로는 전송 여부를 판단하기 어려워서, 현재 코드에서 `UserGameModel`, `guildName`, 보상 요청 함수가 연결되는 방식을 확인하겠습니다. 변경 없이 호출 가능 여부만 보겠습니다.

### Assistant

현재 형태는 **기존 일일 보상 발송 경로를 테스트하는 용도라면 거의 맞지만**, 몇 가지 수정이 필요합니다.

가장 먼저 `guildName`은 사용하지 않지만 호출부에서 `parserText[1]`을 전달하므로 현재는 `/test`만 입력하면 안 되고 다음처럼 인자가 필요합니다.

```text
/test dummy
```

호출부가 [CheatManager.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/ServerNodes/GameNode/Managers/CheatManager.cs:921)에 있기 때문입니다.

더 깔끔하게 하려면 아래처럼 변경하는 것이 좋습니다.

```csharp
case eCheatCommand.test:
    isSuccess = Test(user);
    break;

private bool Test(UserGameModel user)
{
    // 테스트 코드
}
```

그리고 테스트 함수의 마지막 부분은 다음처럼 큐 등록까지만 하는 편이 안전합니다.

```csharp
PrivilegeDailyRewardGameManager.Instance.ProcessScheduleReward(packet);
return true;
```

아래 호출은 제거하는 것을 권장합니다.

```csharp
PrivilegeDailyRewardGameManager.Instance.ProcessQueuedScheduleReward();
```

큐 처리는 이미 별도 작업 스레드가 수행하고 있습니다([ThreadModel_PrivilegeDailyRewardGame.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/ServerNodes/GameNode/Thread/ThreadModel_PrivilegeDailyRewardGame.cs:19)). 치트 처리 스레드에서 직접 호출하면 작업 스레드와 동시에 큐를 처리할 가능성이 있습니다.

또한 `rewardKey`는 날짜 형식으로 생성하는 것이 좋습니다.

```csharp
var now = K2Common.GetDateTime();

packet.rewardKey =
    now.Year * 10000 +
    now.Month * 100 +
    now.Day;

packet.scheduleTime = now;
packet.requestTime = now;
```

현재 값인 `2026054`는 `yyyyMMdd` 형식이 아니므로 날짜 키를 의도했다면 잘못된 값입니다.

다만 중요한 점이 하나 있습니다. 현재 테스트 함수는 **“구매 즉시 보상” 테스트가 아니라 기존 일일 보상 로직 테스트**입니다. 일일 로직은 [PrivilegeDailyRewardGameManager.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/ServerNodes/GameNode/Managers/PrivilegeDailyRewardGameManager.cs:320)에서 최초 보상 시각을 다음 지정 시각으로 계산합니다.

따라서 지정 시각이 지난 뒤 멤버십을 구매했다면:

```text
멤버십 시작 시각: 오늘 15:00
지정 시각: 매일 06:00
최초 일일 보상 시각: 내일 06:00
```

이 경우 테스트 패킷을 지금 전송해도 `rewardDate > lastRewardDate` 조건으로 메일이 발송되지 않습니다.

결론적으로:

- 기존 정기 보상 테스트: 현재 패킷 방식 사용 가능
- 구매 즉시 보상 테스트: 현재 방식으로는 보장되지 않음
- `guildName` 제거 권장
- `ProcessQueuedScheduleReward()` 직접 호출 제거 권장
- `rewardKey`를 `yyyyMMdd` 형식으로 생성 권장
- 사용자에게 해당 `privilegeGroup = 2` 멤버십이 실제 적용돼 있어야 발송됨

구매 즉시 보상 기능을 테스트하려는 목적이라면, 일일 보상 계산을 우회하지 말고 별도의 `ProcessInitialReward(user, privilegeGroup)` 경로를 만들어 테스트하는 것이 맞습니다.
