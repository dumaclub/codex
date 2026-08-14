# eEventType EventCheck2 추가

- Project: Astellia02
- Session ID: `019ff466-66d7-7e02-9d2e-285941fa544a`
- Workspace: `C:\Users\dumaclub\Documents\ChatGPT\Astellia02`
- Started: 2026-08-12T05:16:19.927Z
- Updated: 2026-08-12T05:16:23.4572117Z
- Messages exported: 12

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

eEventType 추가 요청
클라이언트에서 UI 분기 이슈가 있어서 기획데이터에서 사용하는 eEventType 타입값중 EventCheck 값을 EventCheck2 로 하나더 생성하고 기능은 EventCheck과 모든행동을 일치하도록 하는 기능이 필요합니다.
eEventType.EventCheck 과 매칭되는 값은 UserEventType.AttendEvent 가 맞나요?
수정해야 할 부분이 많은지 확인해 주세요.

    public enum eEventType
    {
        EventPass = 1,
        EventCheck = 2,
        EventLoginKeep = 3,
        EventExchange = 4,
        EventMission = 5,
        EventDailyMission = 6,
        EventDailyCash = 7,
        EventDailyMarion = 8,
        EventDgnTmDouble = 9,
        EventGuildGive = 10,
        EventCashAttend = 11,
        EventNPC = 12,
        EventBanner = 13,
        EventNewUser = 14,
        EventReturnUser = 15,
        EventGuildDungeon = 16,
        EventRoulette = 17,
        EventWebLink = 18,

#if UNITY_CLIENT
        //클라 전용
        EventBannerClientOnly = 101,
#endif
    }

    public enum UserEventType : byte
    {
        None = 0,
        BattlePass = 1,
        BattlePassMission = 2,
        Attend = 3,
        AttendEvent = 4,
        LoginKeep = 5,
        DailyMission = 6,
        DailySubMission = 7,
        EventMission = 8,
        EventExchange = 9,
        EventDailyCash = 10,
        EventDailyMarion = 11,
        EventGuildGive = 12,
        EventCashAttend = 13,
        EventBanner = 14,
        EventNewUser = 15,
        EventReturnUser = 16,
        EventRoulette = 17,
    }

### Assistant

두 enum의 실제 변환 지점과 `EventCheck` 분기 사용처를 전부 추적해 보겠습니다. 우선 코드 수정은 하지 않고, `EventCheck2`를 추가할 때 서버·클라이언트·기획데이터에 미치는 범위와 `AttendEvent` 매핑이 맞는지 근거로 정리하겠습니다.

### Assistant

첫 검색은 Unity `Temp`와 SVN 보관 파일이 섞여 실제 소스 결과가 가려졌습니다. 생성물·메타데이터를 제외하고 C# 및 기획데이터 파일만 다시 좁혀서, enum 정의 → 변환 함수 → UI 조건문 순서로 확인 중입니다.

### Assistant

핵심 매핑은 확인됐습니다. `EventCheck` 데이터는 서버에서 실제로 `UserEventType.AttendEvent` 엔티티를 생성·복원하고, 클라이언트도 같은 타입의 패킷을 조회해 출석 UI를 구성합니다. 다만 `EventCheck2`를 enum에만 추가하면 서버의 활성 이벤트 조회와 DB 복원 조건에서 누락되므로 동작하지 않습니다. 지금은 “동일 행동”을 보장하기 위한 필수 분기 수를 최종 산정하고 있습니다.

### Assistant

네. `eEventType.EventCheck`에 대응하는 사용자 이벤트 타입은 `UserEventType.AttendEvent`가 맞습니다.

서버에서 출석 엔티티를 `AttendEvent`로 생성하고([UserEventModel.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/ServerNodes/GameNode/Models/UserEventModel.cs:1649)), 클라이언트도 같은 타입으로 패킷을 조회합니다([UIEventListPopup.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/UI/EventPopup/UIEventListPopup.cs:150)).

수정 범위는 크지 않지만 enum만 추가해서는 동작하지 않습니다. 필수 범위는 약 5개 파일, 9개 지점입니다.

- [EventHubPageInfo.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/SharedLib/DataManager/DataClass/EventHubPageInfo.cs:7)
  - 기존 값을 유지하기 위해 `EventCheck2 = 19` 추가 권장
  - `EventCheck2 = EventCheck` 같은 숫자 별칭은 UI에서 구분할 수 없으므로 사용하면 안 됩니다.

- [UserEventModel.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/ServerNodes/GameNode/Models/UserEventModel.cs:384)
  - DB에서 `AttendEvent` 복원 시 `EventCheck2`도 유효 이벤트로 인정
  - 일일 출석 처리 대상 조회에 `EventCheck2` 목록도 포함
  - 처리할 때도 `UserEventType.AttendEvent`를 그대로 사용

- [UIEventListPopup.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/UI/EventPopup/UIEventListPopup.cs:19)
  - `EventCheck2`를 동일한 `UIWeekAttendance` 페이지에 연결
  - 완료 여부 검사 시 `AttendEvent`로 매핑

- [EventUtil.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/UI/EventPopup/EventUtil.cs:98)
  - 이벤트/출석 목록 분류
  - 출석 이벤트 수집
  - 레드닷 제외 여부에서 `EventCheck`와 동일하게 처리

- 기획데이터
  - 대상 `EventHubPageInfo` 행의 `EventType`을 `19`로 설정
  - 연결된 `AttendCheckData` 구조는 그대로 사용 가능
  - 실제 운영 테이블과 JSON/Binary 산출물은 기존 테이블 빌드 절차로 재생성해야 합니다.

다음 부분은 수정하지 않아도 됩니다.

- `UserEventType` enum: `AttendEvent2` 추가 불필요
- 패킷 구조 및 DB 스키마
- [UIWeekAttendance.cs](D:/ProjectA/Trunk/Dev/Client/Assets/Script/UI/EventPopup/Attendance/UIWeekAttendance.cs:48): 이미 기본값이 `AttendEvent`
- 출석 보상 수령 로직: `eventId` 기반이어서 동일하게 동작
- `UserEventEntity`: 이미 `AttendEvent` 처리 지원

결론적으로 작은 수정입니다. 다만 서버의 DB 복원과 활성 이벤트 조회를 빠뜨리면 `EventCheck2` 데이터가 UI에는 보이더라도 출석 카운트나 기존 진행 데이터가 정상적으로 연결되지 않을 수 있습니다.

### User

클라는 이미 UserEventType 에 AttendEvent2 = 19, 이걸로 처리하고 있다고 하여 서버에서도 이 값으로 DB에 저장해야 할것 같습니다. 내용에 맞게 코드 수정해 주세요.

### Assistant

요구사항을 `eEventType.EventCheck2` ↔ `UserEventType.AttendEvent2(19)`의 독립 매핑으로 반영하겠습니다. 기존 `EventCheck/AttendEvent` 경로는 유지하고, 서버 DB 생성·복원·일일 카운트와 클라이언트 UI 조회가 새 타입을 끝까지 보존하도록 수정한 뒤 빌드 영향까지 확인하겠습니다.

### Assistant

클라이언트 쪽에는 이미 `EventCheck2 = 19`, `AttendEvent2 = 19` 및 UI 분기가 반영되어 있음을 확인했습니다. 따라서 해당 변경은 건드리지 않고, 서버의 누락된 네 경로—DB 엔티티 초기화/잔여시간, DB 복원 검증, 신규 생성·일일 카운트, 출석 치트 처리—만 보완하겠습니다.

### Assistant

서버 처리 분리를 완료했습니다. `EventCheck2` 이벤트를 조회할 때 `GetEventBaseEntity(..., AttendEvent2, ...)`로 생성하므로 신규 DB 레코드의 `eventType` 값이 19로 저장되며, 재접속 시에도 19와 `EventCheck2` 조합만 유효하게 복원됩니다. 이제 서버 프로젝트를 컴파일해 enum 공유와 switch 누락 여부를 검증하겠습니다.

### Assistant

첫 서버 빌드는 이번 수정 파일에 도달하기 전에 공유 프로젝트의 기존 조건부 컴파일 문제(`DataManager.cs`의 `K2Client` 참조)로 중단됐습니다. 수정 코드 오류와 구분하기 위해 서버에서 실제 사용하는 구성/전처리 상수를 확인하고 맞는 구성으로 다시 검증하겠습니다.

### Assistant

수정 파일 자체는 현재 공유 enum/패킷 프로젝트를 갱신한 상태에서 컴파일 오류가 없음을 확인했습니다. 전체 `EgonServer` 빌드는 이번 변경과 무관한 기존 API 불일치(`Program.cs`, `ServerModule.cs`, `ActionSync.cs` 등) 때문에 완료되지는 않았고, 검증 중 생성된 임시 스텁과 추적 바이너리는 모두 제거·복원했습니다. 마지막으로 변경 파일만 다시 점검하겠습니다.

### Assistant

서버 코드를 수정했습니다. `EventCheck2`는 이제 `AttendEvent2(19)`로 생성·DB 저장·복원됩니다.

변경 내용:

- [UserEventModel.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/ServerNodes/GameNode/Models/UserEventModel.cs:384)
  - DB 복원 시 `AttendEvent2`를 `EventCheck2`와 검증
  - `EventCheck`와 `EventCheck2`를 각각 조회
  - `EventCheck2` 신규 엔티티 생성 시 `AttendEvent2` 전달
  - 출석 치트 및 초기화에도 `AttendEvent2` 포함

- [UserEventEntity.cs](D:/ProjectA/Trunk/Dev/Server/EgonServer/Database/Entities/UserEventEntity.cs:290)
  - `AttendEvent2` 초기화 지원
  - 이벤트 종료 잔여시간 계산 지원

`GetEventBaseEntity()`에서 전달된 `AttendEvent2`가 `Initialize()`를 거쳐 그대로 DB의 `eventType=19`로 저장됩니다. 기존 `EventCheck/AttendEvent` 동작은 유지됩니다.

공유 enum과 Packet 프로젝트 컴파일은 통과했고 변경 파일 관련 컴파일 오류도 없습니다. 전체 서버 빌드는 기존의 `Program.cs`, `ServerModule.cs`, `ActionSync.cs` 등 다른 파일의 API 불일치 오류로 완료되지 않았습니다. 클라이언트 코드는 이미 대응되어 있어 수정하지 않았습니다.
