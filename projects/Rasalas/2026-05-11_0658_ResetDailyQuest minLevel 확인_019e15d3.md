# ResetDailyQuest minLevel 확인

- Project: Rasalas
- Session ID: `019e15d3-64f0-73f2-a0d0-e495958a480c`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-05-11T06:57:16.016Z
- Updated: 2026-05-11T06:58:22.2219345Z
- Messages exported: 11

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

<environment_context>
  <cwd>E:\Rasalas\Trunk\qa</cwd>
  <shell>powershell</shell>
  <current_date>2026-05-11</current_date>
  <timezone>Asia/Seoul</timezone>
</environment_context>

### User

ActorUserModel_Quest.cs 파일의 public ePacketCommonResult ResetDailyQuest(int zoneId) 함수에서 minLevel 을 사용하고 있는데 코드로 보면 없는 것이나 마찮가지 인것 같습니다. 맞나요?

### Assistant

해당 함수 주변 흐름을 먼저 확인해볼게요. `minLevel`이 실제 필터로 작동하는지, 아니면 값만 잡고 의미 없이 지나가는지 호출 경로까지 짧게 따라가보겠습니다.

### Assistant

검색 범위가 넓어서 패키지/Unity 임시 파일까지 걸렸지만, 목표 파일 위치와 관련 라인은 잡혔습니다. 이제 함수 본문과 `GetDailyQuestZoneMinLevel()`의 데이터 로딩 방식을 같이 보겠습니다.

### Assistant

네, **`ResetDailyQuest(int zoneId)` 안에서는 `minLevel`이 사실상 동작하지 않는 게 맞습니다.**

근거는 여기입니다:

- [ActorUserModel_Quest.cs:2386](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2386) 에서 `limitLevel = GetMaxLevel()`
- [ActorUserModel_Quest.cs:2387](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2387) 에서 zone별 `minLevel`을 가져옴
- [ActorUserModel_Quest.cs:2388](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2388) 에서 `limitLevel`을 보정함
- 그런데 실제 필터링 조건인  
  `if (dailyQuestInfo.RequestLevelMin > limitLevel) { continue; }` 가 [ActorUserModel_Quest.cs:2396](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2396) 에서 주석 처리되어 있습니다.

그래서 현재 `randomDqList`에는 레벨 조건 없이 `dailyQuestInfoList`의 모든 일일 퀘스트가 들어갑니다. 즉 `minLevel`과 `limitLevel` 계산은 남아 있지만, **랜덤 일일 퀘스트 선정에는 아무 영향이 없습니다.**

다만 완전히 데이터가 없는 건 아닙니다. `GetDailyQuestZoneMinLevel()`은 [LoaderQuestData.cs:179](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/DataManager/Loader/LoaderQuestData.cs:179) 부근에서 zone별 `RequestLevelMin` 최솟값을 저장하고, [LoaderQuestData.cs:478](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/DataManager/Loader/LoaderQuestData.cs:478) 에서 반환합니다.

정리하면: **데이터와 계산은 있지만, `ResetDailyQuest()` 기준으로는 현재 없는 것이나 마찬가지입니다.** 실제 레벨 제한은 이후 `AcceptDailyQuest()`에서 [ActorUserModel_Quest.cs:2130](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2130) 의 `questData.RequestLevelMin > GetMaxLevel()` 체크로 막히는 구조입니다.

### User

public ePacketCommonResult ResetDailyQuest(int zoneId) 같은 함수에 minLevel 레벨이 적용되도록 수정하였는데 맞게 되었는지 확인해 주세요.

### Assistant

수정된 부분을 기준으로 diff와 주변 흐름을 같이 확인해보겠습니다. 특히 `minLevel`이 퀘스트 선정 단계에 실제로 적용되는지, 그리고 낮은 레벨에서 빈 리스트/부분 채움 같은 부작용이 없는지 보겠습니다.

### Assistant

현재 작업 폴더에서는 `.git`이 안 잡혀서 diff는 바로 못 봤지만, 파일 본문 기준으로 변경 위치는 확인됐습니다. `minLevel` 체크가 함수 초반에 추가된 것처럼 보여서 그 앞뒤와 반환값 의미까지 이어서 보겠습니다.

### Assistant

확인해보니 지금 수정은 `minLevel > GetMaxLevel()`이면 함수 초반에 반환하도록 바뀌어 있습니다. 이 방식은 “존의 일일퀘 최소 레벨 미만이면 리셋 자체를 하지 않는다”는 의미라서 방향은 맞는데, 같은 zone 안에 레벨대가 섞이는 경우까지 막는지는 한 가지 더 확인해야 합니다.

### Assistant

SVN 작업본이라 `git diff` 대신 `svn diff`로 변경 내용을 확인할 수 있을지 보겠습니다. 파일 본문만으로도 핵심 판단은 가능하지만, 변경 전후를 보면 더 정확히 말할 수 있습니다.

### Assistant

**확인 결과**

수정 방향은 맞습니다. 지금은 [ActorUserModel_Quest.cs:2259](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2259) 에서 `minLevel > GetMaxLevel()`이면 바로 `NotMatchLevel`을 반환하므로, 예전처럼 `minLevel`을 계산만 하고 버리는 상태는 아닙니다. 비용 차감이나 DB 초기화 전에 체크하는 위치도 좋습니다.

다만 주의할 점이 2개 있습니다.

1. [ActorUserModel_Quest.cs:2264](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2264) 의 `ErrorLog`는 조금 위험합니다. `CheckAllResetDailyQuestProc()`가 모든 daily quest zone을 돌면서 `ResetDailyQuest(zoneId)`를 호출하므로, 저레벨 유저가 아직 못 여는 zone마다 정상 상황인데도 에러 로그가 찍힐 수 있습니다. 이건 `ErrorLog` 없이 반환하거나, 필요하면 Debug/Info 성격 로그가 더 맞아 보입니다.

2. 이 수정은 “zone의 최소 레벨”만 막습니다. 같은 zone 안에 `RequestLevelMin`이 다른 일일퀘가 섞이면, [ActorUserModel_Quest.cs:2399](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_Quest.cs:2399) 의 개별 퀘스트 레벨 필터가 아직 주석이라 고레벨 퀘스트가 랜덤 배정될 수 있습니다. 현재 기획 데이터가 zone별 동일 레벨이라는 전제라면 괜찮고, 섞일 가능성이 있으면 이 필터도 살리는 게 맞습니다.

정리하면: **zone minLevel 적용 자체는 맞게 됐습니다.** 다만 자동 체크 경로의 에러 로그는 정리하는 쪽을 추천합니다. 빌드는 돌리지 않고 코드 흐름만 확인했습니다.
