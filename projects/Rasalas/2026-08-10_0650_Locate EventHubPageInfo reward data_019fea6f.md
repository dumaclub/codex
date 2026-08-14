# Locate EventHubPageInfo reward data

- Project: Rasalas
- Session ID: `019fea6f-f2c5-7002-b413-c4678bd0301a`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-08-10T06:50:33.163Z
- Updated: 2026-08-10T06:50:39.5125225Z
- Messages exported: 25

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

이벤트 정보 확인 EventHubPageInfo 에 아래의 이벤트 보상 정보는 어떤 기획데이터에서 확인할 수 있나요?
EventId     117007
EventType   11
BMStoreID   4600007

### Assistant

해당 ID들이 서버/클라이언트 어느 기획 데이터와 연결되는지 코드와 데이터 파일에서 역추적해보겠습니다. 먼저 `EventHubPageInfo`, `117007`, `4600007` 참조를 찾아보겠습니다.

### Assistant

전체 에셋 검색에 바이너리 모델 데이터가 섞여 결과가 과다했습니다. 실제 기획 JSON과 데이터 클래스/로더로 범위를 좁혀, 보상 테이블로 넘어가는 키를 확인 중입니다.

### Assistant

연결 관계가 확인됐습니다. `EventType 11`은 `EventCashAttend`이고, 일차별 보상은 `EventCashData`에서 `EventId=117007`로 조회합니다. 이제 `Reward` 값이 최종 아이템/수량으로 풀리는 다음 보상 테이블까지 확인하겠습니다.

### Assistant

실제 원본 기획 엑셀도 존재하므로, JSON 결과만이 아니라 `Table`/`Table_Balance`의 어느 시트·행에서 확인되는지 검증하겠습니다. 엑셀 구조 확인에는 스프레드시트 스킬의 읽기/검증 절차를 적용하겠습니다.

### Assistant

원본 엑셀 기준으로도 핵심 위치가 확인됐습니다. `EventCashData`의 1446~1475행이 1~30일차 보상이고, `EventHubPageInfo`에는 반복 완료 보상(`RepeatDayReward`)이 별도로 있습니다. 마지막으로 `BMStoreID`는 보상표가 아니라 구매상품 연결 정보인지 원본 행을 확인하겠습니다.

### Assistant

확인 결과, 해당 이벤트의 보상은 주로 **`EventCashData` 기획 데이터**에서 확인할 수 있습니다.

- `EventType 11` = `EventCashAttend`
- `EventCashData`에서 `EventId = 117007` 조회
- 1~30일차 보상이 있으며 `RewardConfirmId`는 `11620137 ~ 11620166`입니다. :codex-file-citation{path="E:/Rasalas/Trunk/qa/Table/EventCashData.xlsx" purpose="source" artifact_kind="workbook" sheet="EventCashData" range="A1446:I1475"}

최종 아이템과 수량은 다음 순서로 추적합니다.

`EventCashData.Reward` → `RewardConfirm` → `RewardGroup` → `RewardList`

예를 들어 1일차는:

`11620137` → `1162013701` → `116201370101` → `ItemId 41911051 × 1`

추가로:

- `EventHubPageInfo.RepeatDayReward = 11620136`은 전체 보상 수령 후 반복 시 사용하는 별도 보상입니다. 최종 구성은 `ItemId 2104110 × 1`입니다. :codex-file-citation{path="E:/Rasalas/Trunk/qa/Table/EventHubPageInfo.xlsx" purpose="source" artifact_kind="workbook" sheet="EventHubPageInfo" range="A416:AL416"}
- `BMStoreID 4600007`은 보상 데이터가 아니라 **“특권 : 성장 보급 패스” 구매상품 정보**이며, `BMStoreData`에서 `LinkTableEventID = 117007`로 연결됩니다.

따라서 기획 데이터 확인 순서는 **`EventCashData.xlsx` → `RewardConfirm.xlsx` → `RewardGroup.xlsx` → `RewardList.xlsx`**입니다.

### User

계정당 이벤트라 특정 uId가 A서버에서 3번 보상을 받다가 그 이후부터는 B서버에서 보상을 받을 수 있을것 같은데 어떤 로그를 확인해 봐야 알 수 있나요?

### Assistant

계정 단위(`ApplyAreaType=3`)에서 서버를 바꿨을 때 수령 상태가 어디에 저장·조회되는지 코드 경로를 따라가고, 실제 확인해야 할 게임/DB 로그 키워드를 정리하겠습니다. 우선 보상 요청 처리와 계정 이벤트 엔티티 저장 경로를 확인하겠습니다.

### Assistant

핵심은 `uId`별 `accountevent` 레코드입니다. 이 이벤트는 생성 시 `AccountEventEntity`를 사용하고, 수령 진행도는 `clearCountList`와 날짜 필드에 저장됩니다. 이제 수령 성공 로그 이름과 DB 조회 컬럼을 정확히 좁히고 있습니다.

### Assistant

가능합니다. 같은 `uId`이고 B서버도 이벤트 적용 대상이면, A서버에서 받은 3회 진행도를 이어서 B서버에서 4일차 보상을 받을 구조입니다. 단, 계정 단위이므로 A에서 오늘 이미 받았다면 B에서도 같은 날 추가 수령은 불가능합니다.

가장 정확한 확인 대상은 로그보다 먼저 AccountGameDB의 `accountevent`입니다.

```sql
SELECT
    uId,
    eventId,
    eventType,
    currentCount,
    clearCount,
    premiumCount,
    updateDate,
    checkDate,
    fromServerId,
    versionDate,
    isDelete
FROM accountevent
WHERE uId = {확인할_uId}
  AND eventId = 117007;
```

A서버에서 3회 정상 수령했다면 대략 다음 상태여야 합니다.

```text
eventType     = 13        -- EventCashAttend
currentCount  = 3
clearCount    = 11700536,11700537,11700538,
premiumCount  = 1
isDelete      = 0
```

`accountevent`는 `(uId, eventId)`가 유니크 키이고, 캐릭터나 서버 ID는 키에 포함되지 않습니다. [UserEventMap.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Mappings/UserEventMap.cs:92)
B서버 로그인 때도 `uId`로 AccountGameDB의 이벤트를 불러옵니다. [DatabaseController.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Controllers/DatabaseController.cs:1663)

수령 이력은 로그 DB의 `gamelog_partition`에서 로그 ID `10002(DlyAtdPkg)`를 확인하면 됩니다.

```sql
SELECT
    idx,
    date,
    uId,
    charId,
    p1 AS eventId,
    p2 AS rewardDay,
    parameterString
FROM gamelog_partition
WHERE logId = 10002
  AND uId = {확인할_uId}
  AND p1 = 117007
ORDER BY date, idx;
```

필드 의미는 다음과 같습니다.

- `charId`: 어느 서버 캐릭터로 받았는지 구분
- `p1`: 이벤트 ID `117007`
- `p2`: 수령 일차
- `parameterString.eId`: 이벤트 ID
- `parameterString.cId`: `EventCashData.Id`
- `parameterString.day`: 수령 일차
- `parameterString.item`: 실제 지급 아이템

정상적인 서버 이동 결과는 다음처럼 보여야 합니다.

```text
A서버 charId → day 1, cId 11700536
A서버 charId → day 2, cId 11700537
A서버 charId → day 3, cId 11700538
B서버 charId → day 4, cId 11700539
```

이 로그는 보상 지급 성공 후 기록됩니다. [UserEventModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/UserEventModel.cs:3677) 서버별로 로그 DB가 분리되어 있다면 A/B 서버 로그 DB를 모두 조회해야 합니다.

상품 구매 여부도 함께 확인하려면 로그 ID `11002(BM_Buy)`를 조회합니다.

```sql
SELECT date, uId, charId, p1 AS bmStoreId, parameterString
FROM gamelog_partition
WHERE logId = 11002
  AND uId = {확인할_uId}
  AND p1 = 4600007
ORDER BY date;
```

`parameterString`의 `"isS":"true"`이면 구매 성공입니다.

B서버 수령 시에는 다음 패킷 결과도 확인하면 좋습니다.

```text
CS_GetEventCashReward
eventId     = 117007
eventDataId = 11700539   -- 4일차
earlyFlag   = false

SC_GetEventCashReward.result
```

결과별 의미:

- `Success`: A서버 진행도를 이어 B서버에서 정상 수령
- `AlreadyGetEventReward`: 같은 일일 초기화 구간에 이미 수령했거나 전체 보상 완료
- `NeedMoreEventCashClearCount`: 서버가 인식한 다음 보상 순서와 `eventDataId`가 다름
- `NotFoundEventData`: B서버 메모리에 `accountevent`가 로드되지 않았거나 `uId`가 다름

만약 A서버 로그에는 3회가 있지만 `accountevent.currentCount`가 3이 아니라면, A서버 상태가 AccountGameDB에 저장되기 전에 B서버로 이동했거나 계정 데이터 저장이 실패했을 가능성이 있습니다. 이 경우 DBNode 로그에서 `query error =>`와 해당 `uId`를 우선 확인해야 합니다.

### User

이벤트캐시 보상로그를 확인할 수 있는 쿼리도 알려주세요.

### Assistant

이벤트 캐시 보상 수령 로그는 로그 DB의 `gamelog_partition`에서 `logId = 10002`로 조회합니다.

```sql
SELECT
    idx,
    date,
    uId,
    charId,
    p1 AS eventId,
    p2 AS rewardDay,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.cId')) AS eventCashDataId,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.item')) AS rewardItems,
    parameterString
FROM gamelog_partition
WHERE logId = 10002
  AND uId = {확인할_uId}
  AND p1 = 117007
ORDER BY date ASC, idx ASC;
```

JSON 함수 사용이 불가능한 DB 버전이면 다음처럼 조회하면 됩니다.

```sql
SELECT
    idx,
    date,
    uId,
    charId,
    p1 AS eventId,
    p2 AS rewardDay,
    parameterString
FROM gamelog_partition
WHERE logId = 10002
  AND uId = {확인할_uId}
  AND p1 = 117007
ORDER BY date ASC, idx ASC;
```

주요 필드:

- `charId`: 보상을 받은 캐릭터
- `p1`: 이벤트 ID, 여기서는 `117007`
- `p2`: 보상 일차
- `cId`: `EventCashData.Id`
- `item`: 실제 지급 아이템 ID와 수량

A/B 서버의 캐릭터별 수령 현황을 집계하려면:

```sql
SELECT
    charId,
    COUNT(*) AS rewardCount,
    MIN(p2) AS firstRewardDay,
    MAX(p2) AS lastRewardDay,
    MIN(date) AS firstRewardDate,
    MAX(date) AS lastRewardDate
FROM gamelog_partition
WHERE logId = 10002
  AND uId = {확인할_uId}
  AND p1 = 117007
GROUP BY charId
ORDER BY firstRewardDate;
```

특정 일차가 중복 지급됐는지 확인하려면:

```sql
SELECT
    p2 AS rewardDay,
    COUNT(*) AS receiveCount,
    GROUP_CONCAT(charId ORDER BY date) AS receivedCharIds,
    GROUP_CONCAT(date ORDER BY date) AS receivedDates
FROM gamelog_partition
WHERE logId = 10002
  AND uId = {확인할_uId}
  AND p1 = 117007
GROUP BY p2
HAVING COUNT(*) > 1
ORDER BY rewardDay;
```

로그 DB가 서버 그룹별로 분리되어 있다면 A서버와 B서버의 로그 DB에서 각각 조회한 후 결과를 합쳐야 합니다. 로그 기록 코드는 [UserEventModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/UserEventModel.cs:3677)에 있습니다.

### User

4600007 상품 구매한 로그 확인하는 법도 알려주세요. 위에 알려주신 로그로 확인하지 못했습니다.

### Assistant

`4600007`은 일반 BM 구매 경로가 아니라 `SkipInventory=Privilege` 상품이라, 결제 방식에 따라 `11002`가 아닌 빌링/보관함 로그에 남을 가능성이 있습니다. `PriceType=2`와 실제 구매 처리 분기를 따라가서 정확한 조회 로그와 쿼리를 확인하겠습니다.

### Assistant

확인해보니 `4600007`은 현재 데이터상 `PriceType=2(다이아)`, `SkipInventory=4(DailyCashEvent)` 상품이라 정상 상점 구매라면 `11002`에 남는 것이 맞습니다. 로그가 없다면 로그 DB 파티션/서버 그룹이 다르거나, QA·GM 우회 지급으로 이벤트만 생성됐을 가능성도 있어 구매 DB 엔티티까지 확인하겠습니다.

### Assistant

가장 가능성 높은 원인은 **A서버에서 구매했는데 B서버 그룹의 LogDB를 조회한 경우**입니다. `11002` 로그는 구매 당시 `serverGroupId`의 LogDB에 저장됩니다.

`4600007`은 `PriceType=2(다이아)` 상품이므로 정상 구매라면 `logId=11002`, `p1=4600007`로 기록됩니다.

먼저 `uId` 조건 없이 A서버 LogDB에서 확인해 보세요.

```sql
SELECT
    idx,
    date,
    uId,
    charId,
    p1 AS bmStoreId,
    p2 AS priceType,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.isS')) AS isSuccess,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.fReason')) AS failReason,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.cnt')) AS buyCount,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.pCurrency')) AS beforeDiamond,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.price')) AS price,
    JSON_UNQUOTE(JSON_EXTRACT(parameterString, '$.currency')) AS afterDiamond,
    parameterString
FROM gamelog_partition
WHERE logId = 11002
  AND p1 = 4600007
  AND date >= '2026-04-08 00:00:00'
ORDER BY date DESC;
```

특정 계정 조회:

```sql
SELECT
    idx,
    date,
    uId,
    charId,
    p1 AS bmStoreId,
    p2 AS priceType,
    parameterString
FROM gamelog_partition
WHERE logId = 11002
  AND uId = {확인할_uId}
  AND p1 = 4600007
ORDER BY date DESC;
```

정상 구매라면 다음 값이 나옵니다.

```text
p1        = 4600007
p2        = 2
isS       = true
cnt       = 1
price     = 4000
```

A/B 서버 LogDB가 분리된 경우:

```sql
SELECT 'A' AS sourceServer, idx, date, uId, charId, p1, p2, parameterString
FROM A서버_LOG_DB.gamelog_partition
WHERE logId = 11002
  AND uId = {확인할_uId}
  AND p1 = 4600007

UNION ALL

SELECT 'B' AS sourceServer, idx, date, uId, charId, p1, p2, parameterString
FROM B서버_LOG_DB.gamelog_partition
WHERE logId = 11002
  AND uId = {확인할_uId}
  AND p1 = 4600007

ORDER BY date DESC;
```

구매 상태는 Account DB의 `bm_account`에서도 확인할 수 있습니다. `4600007`은 `LimitUnit=3(AccountLimit)`이므로 정상 구매 시 이 테이블에 기록됩니다.

```sql
SELECT
    idx,
    uId,
    bmStoreId,
    buyCount,
    regDate,
    lastRefreshDate,
    endDate,
    versionDate,
    isDelete
FROM bm_account
WHERE uId = {확인할_uId}
  AND bmStoreId = 4600007;
```

판단 기준은 다음과 같습니다.

- `bm_account` 있음 + `11002` 없음
  → 다른 서버 그룹 LogDB, 로그 보관기간 만료 또는 로그 누락 가능성
- `bm_account` 없음 + `accountevent` 있음
  → QA/GM 우회 처리, 이벤트 직접 생성 또는 구매 처리 중간 실패 가능성
- `bm_account.buyCount >= 1` + `accountevent.eventId=117007` 있음
  → 상품 구매 및 이벤트 등록까지 반영된 상태
- `11002`에서 `"isS":"false"`
  → `fReason`으로 구매 실패 원인 확인

이 상품의 구매 성공 로그는 [BMModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/BMModel.cs:2687)에서 기록되고, 로그는 구매 서버 그룹의 LogDB로 라우팅됩니다. [DBNodeLogTaskManager.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/DBNode/Managers/DBNodeLogTaskManager.cs:25)

### User

계정별 이벤트 인데 서버별 이벤트로 변경되는 이벤트가 발생되어 DB작업이 필요합니다.
작업과정을 아래와 같이 진행하려고 하는데 맞는지 확인해 주세요.

1) 이벤트 구매 사용자 확인
SELECT * FROM rasalas_account_game.accountevent WHERE eventId = 117007;

2) 사용자 아이디 추출
CREATE TABLE test.event_117007 SELECT DISTINCT uId FROM `rasalas_account_game`.accountevent WHERE eventId = 117007

3) 게임로그에서 데이터 추출
INSERT INTO test.event_117007_3
SELECT *, 71 AS svrId FROM `rasalas_w01_log_71_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007 UNION ALL
SELECT *, 72 AS svrId FROM `rasalas_w01_log_72_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007 UNION ALL
SELECT *, 73 AS svrId FROM `rasalas_w01_log_73_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007 UNION ALL
SELECT *, 74 AS svrId FROM `rasalas_w01_log_74_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007 UNION ALL
SELECT *, 81 AS svrId FROM `rasalas_w01_log_81_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007 UNION ALL
SELECT *, 82 AS svrId FROM `rasalas_w01_log_82_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007 UNION ALL
SELECT *, 83 AS svrId FROM `rasalas_w01_log_83_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007 UNION ALL
SELECT *, 84 AS svrId FROM `rasalas_w01_log_84_new`.gamelog_partition WHERE uId IN (SELECT * FROM test.event_117007) AND logId = 11002 AND p1 = 4600007

4) 가장 마지막에 구매한 서버 정보 확인
SELECT *
FROM (
    SELECT t.*,
           ROW_NUMBER() OVER (PARTITION BY t.uId ORDER BY t.`date` DESC, t.idx DESC) AS rn
    FROM test.event_117007_3 t
    WHERE t.uId IN (SELECT uId FROM test.event_117007)
) X
WHERE rn = 1
ORDER BY uId;

5) 4)번에서 추출한 사용자 수와 1)번에서 추출한 유저수가 맞는지? 1)번의 유저가 모두 있는지?

6) svrId 별로 userevent 테이블로 데이터 이전 (서버 합병되어 사라진 서버는 각 서버에 맞게 이동) 72 -> 71, 74 -> 73, 82 -> 81, 84 -> 83
rasalas_w01_g71.userevent
rasalas_w01_g73.userevent
rasalas_w01_g81.userevent
rasalas_w01_g83.userevent

7) 이전 완료한 사용자 rasalas_account_game.accountevent 테이블에서 삭제

### Assistant

작업 방향은 맞지만, 현재 절차 그대로 실행하면 오배치·누락 가능성이 있습니다. 특히 `11002`에는 구매 실패 로그도 포함되고, 이벤트 적용 서버 목록의 `85`가 빠져 있습니다. 스키마 호환성, PK 충돌, 캐시/Redis 영향까지 코드 기준으로 점검해 안전한 순서로 정리하겠습니다.

### Assistant

추가로 중요한 범위가 하나 있습니다. 이벤트 진행도만 `accountevent → userevent`로 옮겨도 상품 `4600007`의 구매 제한은 현재 `LimitUnit=3(AccountLimit)`이라 `bm_account`에 남습니다. “서버별 이벤트”가 구매 횟수까지 서버별이라는 의미라면 `bm_account → bm_user` 이전과 기획 데이터 변경도 함께 필요합니다. 이 부분의 로딩 충돌 여부를 확인 중입니다.

### Assistant

큰 방향은 맞지만, 현재 SQL 그대로 실행하면 오배치·누락 가능성이 있습니다. 특히 아래 항목은 반드시 수정해야 합니다.

핵심 수정사항:

1. `11002`에는 구매 실패 로그도 있으므로 `isS=true`만 사용
2. 이벤트 적용 서버에 `85`도 포함되어 있으므로 누락 여부 확인
3. 단순 건수 비교가 아니라 `uId` 기준 양방향 누락 검증
4. `accountevent`와 `userevent` 컬럼이 다르므로 `SELECT *` 사용 금지
5. 동일 `(uId,eventId)` 및 `idx` 충돌 사전 검사
6. 점검 시간 동안 구매·보상 수령·로그인을 중지하고 강제 저장
7. 상품 구매 정보인 `bm_account`도 서버 단위 전환 대상인지 결정

현재 이벤트 적용 서버 목록에는 `850`이 포함되어 있습니다. [EventHubPageInfo.json](E:/Rasalas/Trunk/qa/Client/Assets/ResourceBundles/Data/GameData/EventHubPageInfo.json:8488)

## 권장 작업 순서

### 0. 작업 전 서비스 정지

DB 이전 중에는 반드시 다음 상태가 필요합니다.

- `117007` 이벤트 구매 및 보상 수령 차단
- 대상 사용자 로그아웃 및 DB 저장 완료
- GameNode 재기동 또는 관련 사용자 세션 제거
- 원본 테이블 백업

온라인 상태에서 작업하면 메모리에 남은 `AccountEventEntity`가 삭제 이후 다시 저장될 수 있습니다.

---

### 1. 원본 이벤트 데이터 백업

`isDelete=0`, `eventType=13` 조건도 추가하는 것이 안전합니다.

```sql
CREATE TABLE test.event_117007_source
LIKE rasalas_account_game.accountevent;

INSERT INTO test.event_117007_source
SELECT *
FROM rasalas_account_game.accountevent
WHERE eventId = 117007
  AND eventType = 13
  AND isDelete = 0;
```

사용자 목록은 PK를 생성해 조인 성능을 확보합니다.

```sql
CREATE TABLE test.event_117007_users
(
    uId BIGINT NOT NULL,
    PRIMARY KEY (uId)
);

INSERT INTO test.event_117007_users (uId)
SELECT DISTINCT uId
FROM test.event_117007_source;
```

---

### 2. 구매 성공 로그만 추출

현재 쿼리는 실패한 구매 시도까지 포함합니다. `11002`는 성공·실패 모두 기록되므로 반드시 `isS=true` 조건을 넣어야 합니다. [BMModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/BMModel.cs:2563)

```sql
INSERT INTO test.event_117007_buy_log
(
    idx,
    `date`,
    uId,
    charId,
    logId,
    p1,
    p2,
    p3,
    parameterString,
    svrId
)
SELECT
    g.idx,
    g.`date`,
    g.uId,
    g.charId,
    g.logId,
    g.p1,
    g.p2,
    g.p3,
    g.parameterString,
    71
FROM rasalas_w01_log_71_new.gamelog_partition g
JOIN test.event_117007_users u ON u.uId = g.uId
WHERE g.logId = 11002
  AND g.p1 = 4600007
  AND g.p2 = 2
  AND JSON_VALID(g.parameterString)
  AND JSON_UNQUOTE(JSON_EXTRACT(g.parameterString, '$.isS')) = 'true';
```

동일한 방식으로 `72, 73, 74, 81, 82, 83, 84`를 넣습니다.

그리고 `85` 서버가 실제 존재하거나 과거 구매 가능했다면 반드시 추가합니다.

```sql
INSERT INTO test.event_117007_buy_log (...)
SELECT ..., 85
FROM rasalas_w01_log_85_new.gamelog_partition g
JOIN test.event_117007_users u ON u.uId = g.uId
WHERE g.logId = 11002
  AND g.p1 = 4600007
  AND g.p2 = 2
  AND JSON_VALID(g.parameterString)
  AND JSON_UNQUOTE(JSON_EXTRACT(g.parameterString, '$.isS')) = 'true';
```

`p2=2`는 해당 상품의 가격 타입이 다이아인지 추가 검증하는 조건입니다.

---

### 3. 마지막 구매 서버 및 합병 대상 서버 결정

```sql
CREATE TABLE test.event_117007_owner AS
SELECT
    x.uId,
    x.svrId AS purchaseSvrId,
    CASE x.svrId
        WHEN 72 THEN 71
        WHEN 74 THEN 73
        WHEN 82 THEN 81
        WHEN 84 THEN 83
        ELSE x.svrId
    END AS targetSvrId,
    x.`date` AS purchaseDate,
    x.idx AS purchaseLogIdx
FROM
(
    SELECT
        t.*,
        ROW_NUMBER() OVER
        (
            PARTITION BY t.uId
            ORDER BY t.`date` DESC, t.idx DESC, t.svrId DESC
        ) AS rn
    FROM test.event_117007_buy_log t
) x
WHERE x.rn = 1;

ALTER TABLE test.event_117007_owner
ADD PRIMARY KEY (uId);
```

마지막 구매 서버를 귀속 서버로 사용한다는 것은 기술 규칙이 아니라 운영 정책입니다. 마지막 보상 수령 서버를 기준으로 해야 한다면 `10002` 로그를 사용해야 합니다.

---

### 4. 사용자 누락 검증

건수만 같다고 완전 일치하는 것은 아닙니다.

```sql
SELECT
    (SELECT COUNT(*) FROM test.event_117007_users) AS sourceUsers,
    (SELECT COUNT(*) FROM test.event_117007_owner) AS mappedUsers;
```

구매 로그가 없는 사용자:

```sql
SELECT s.*
FROM test.event_117007_users s
LEFT JOIN test.event_117007_owner o ON o.uId = s.uId
WHERE o.uId IS NULL;
```

위 결과가 1건이라도 있으면 자동 이전하면 안 됩니다. 해당 사용자는 다음 자료로 별도 판정해야 합니다.

- `10002` 이벤트 보상 로그의 마지막 수령 서버
- `bm_account`
- 운영툴/QA 지급 여부
- 로그 보관기간 만료 여부

구매 횟수와 이벤트 회차도 비교하는 것이 좋습니다.

```sql
SELECT
    s.uId,
    s.premiumCount,
    COUNT(l.idx) AS successfulPurchaseLogs
FROM test.event_117007_source s
LEFT JOIN test.event_117007_buy_log l ON l.uId = s.uId
GROUP BY s.uId, s.premiumCount
HAVING s.premiumCount <> COUNT(l.idx);
```

불일치는 로그 보관기간 때문에 발생할 수도 있으므로 바로 오류로 단정하면 안 됩니다.

---

### 5. 목적지 충돌 검사

목적지별로 다음 두 검사를 모두 수행해야 합니다.

```sql
-- 동일 사용자/이벤트 존재 검사
SELECT s.uId, d.idx
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
JOIN rasalas_w01_g71.userevent d
  ON d.uId = s.uId
 AND d.eventId = 117007
WHERE o.targetSvrId = 71;
```

```sql
-- PK idx 충돌 검사
SELECT s.uId, s.idx
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
JOIN rasalas_w01_g71.userevent d ON d.idx = s.idx
WHERE o.targetSvrId = 71;
```

결과가 있으면 `INSERT IGNORE`나 `REPLACE`로 넘기지 말고 개별 병합 규칙을 정해야 합니다.

---

### 6. `userevent`로 이전

`accountevent`에는 `fromServerId`가 있지만 `userevent`에는 없으므로 명시적 컬럼을 사용해야 합니다. [UserEventMap.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Mappings/UserEventMap.cs:6)

```sql
INSERT INTO rasalas_w01_g71.userevent
(
    idx,
    uId,
    eventId,
    eventType,
    currentCount,
    clearCount,
    premiumCount,
    customSelectNum,
    updateDate,
    checkDate,
    versionDate,
    isDelete
)
SELECT
    s.idx,
    s.uId,
    s.eventId,
    s.eventType,
    s.currentCount,
    s.clearCount,
    s.premiumCount,
    s.customSelectNum,
    s.updateDate,
    s.checkDate,
    s.versionDate,
    0
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
WHERE o.targetSvrId = 71;
```

동일 방식으로 `73`, `81`, `83`, 필요하면 `85`까지 처리합니다.

---

### 7. 이전 검증 후 원본 비활성화

처음부터 물리 삭제하기보다 `isDelete=1`로 비활성화한 후 안정화 기간을 두는 것이 안전합니다.

```sql
UPDATE rasalas_account_game.accountevent a
JOIN test.event_117007_owner o ON o.uId = a.uId
SET
    a.isDelete = 1,
    a.versionDate = NOW()
WHERE a.eventId = 117007
  AND a.isDelete = 0;
```

중요한 점은 **목적지 이전이 성공한 사용자만** 비활성화해야 한다는 것입니다. 미매칭 사용자는 원본에 남겨야 합니다.

---

## `bm_account` 처리 결정

`4600007`은 현재 `LimitUnit=3(AccountLimit)`이라 구매 횟수가 `bm_account`에 저장됩니다. [BMStoreData.json](E:/Rasalas/Trunk/qa/Client/Assets/ResourceBundles/Data/GameData/BMStoreData.json:32199)

따라서 두 가지 중 하나를 명확히 결정해야 합니다.

- 이벤트 진행도만 서버별
  → `accountevent → userevent`만 이전하고 `bm_account`는 유지
- 구매 횟수와 재구매 제한도 서버별
  → BMStoreData의 `LimitUnit` 변경과 함께 `bm_account → bm_user` 이전 및 기존 `bm_account` 비활성화 필요

두 번째 경우 `bm_account.buyCount` 전체를 마지막 서버에 단순 이동할지, 성공 구매 로그를 서버별로 집계해서 분배할지도 운영 정책 확인이 필요합니다.

결론적으로 1~5번의 방향은 맞지만, **성공 로그 필터, 85 서버, 미매칭 처리, 목적지 충돌 검사, 명시적 컬럼 이전, 유지보수 모드, `bm_account` 처리**를 추가한 뒤 6~7번을 진행해야 합니다.

### User

INSERT INTO `egon_game_71`.userevent
SELECT * FROM `egon_account_game`.accountevent WHERE uId = 10001306 AND eventId = 117007

테스트 서버에서 테스트 진행중인데 위의 쿼리를 실행하면 아래의 오류가 발생됩니다.

오류 코드: 1136
COLUMN COUNT doesn't match value count at row 1

CREATE TABLE `accountevent` (
  `idx` bigint NOT NULL,
  `uId` bigint NOT NULL,
  `eventId` int NOT NULL,
  `eventType` varchar(255) NOT NULL,
  `currentCount` int NOT NULL,
  `clearCount` varchar(8192) DEFAULT NULL,
  `premiumCount` int NOT NULL,
  `customSelectNum` varchar(128) NOT NULL DEFAULT '0',
  `updateDate` datetime NOT NULL,
  `checkDate` datetime DEFAULT NULL,
  `fromServerId` int NOT NULL,
  `versionDate` datetime DEFAULT NULL,
  `isDelete` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`idx`),
  UNIQUE KEY `uId` (`uId`,`eventId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3

CREATE TABLE `userevent` (
  `idx` bigint NOT NULL,
  `uId` bigint NOT NULL,
  `eventId` int NOT NULL,
  `eventType` varchar(255) NOT NULL,
  `currentCount` int NOT NULL,
  `clearCount` varchar(4096) DEFAULT NULL,
  `premiumCount` int NOT NULL,
  `customSelectNum` varchar(128) NOT NULL DEFAULT '0',
  `updateDate` datetime NOT NULL,
  `checkDate` datetime DEFAULT NULL,
  `versionDate` datetime DEFAULT NULL,
  `isDelete` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`idx`),
  UNIQUE KEY `uId` (`uId`,`eventId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3

### Assistant

오류 원인은 컬럼 수 차이입니다.

- `accountevent`: 13개 컬럼
- `userevent`: 12개 컬럼
- `accountevent`에만 `fromServerId`가 존재

따라서 `SELECT *` 대신 대상 컬럼을 명시하고 `fromServerId`를 제외해야 합니다.

```sql
INSERT INTO `egon_game_71`.userevent
(
    idx,
    uId,
    eventId,
    eventType,
    currentCount,
    clearCount,
    premiumCount,
    customSelectNum,
    updateDate,
    checkDate,
    versionDate,
    isDelete
)
SELECT
    idx,
    uId,
    eventId,
    eventType,
    currentCount,
    clearCount,
    premiumCount,
    customSelectNum,
    updateDate,
    checkDate,
    versionDate,
    isDelete
FROM `egon_account_game`.accountevent
WHERE uId = 10001306
  AND eventId = 117007
  AND isDelete = 0;
```

실행 전에는 다음 두 가지를 확인하세요.

### 중복 키 검사

```sql
SELECT
    a.idx,
    a.uId,
    a.eventId,
    CASE
        WHEN u1.idx IS NOT NULL THEN 'IDX_DUPLICATE'
        WHEN u2.idx IS NOT NULL THEN 'UID_EVENT_DUPLICATE'
        ELSE 'OK'
    END AS checkResult
FROM `egon_account_game`.accountevent a
LEFT JOIN `egon_game_71`.userevent u1
       ON u1.idx = a.idx
LEFT JOIN `egon_game_71`.userevent u2
       ON u2.uId = a.uId
      AND u2.eventId = a.eventId
WHERE a.uId = 10001306
  AND a.eventId = 117007;
```

`OK`가 아니면 INSERT 전에 기존 데이터를 비교해야 합니다. `INSERT IGNORE`나 `REPLACE` 사용은 권장하지 않습니다.

### clearCount 길이 검사

원본은 `varchar(8192)`, 대상은 `varchar(4096)`이므로 길이도 확인해야 합니다.

```sql
SELECT
    uId,
    eventId,
    CHAR_LENGTH(clearCount) AS clearCountLength
FROM `egon_account_game`.accountevent
WHERE uId = 10001306
  AND eventId = 117007;
```

`clearCountLength <= 4096`이어야 안전합니다.

테스트 시에는 트랜잭션으로 검증할 수 있습니다.

```sql
START TRANSACTION;

-- 위 INSERT 실행

SELECT *
FROM `egon_game_71`.userevent
WHERE uId = 10001306
  AND eventId = 117007;

-- 검증만 할 경우
ROLLBACK;

-- 실제 반영할 경우
-- COMMIT;
```

즉, `fromServerId`를 제외한 명시적 컬럼 INSERT가 올바른 처리입니다.

### User

6. userevent로 이전
INSERT INTO rasalas_w01_g71.userevent(idx, uId, eventId, eventType, currentCount, clearCount, premiumCount, customSelectNum, updateDate, checkDate, versionDate, isDelete)
SELECT s.idx, s.uId, s.eventId, s.eventType, s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum, s.updateDate, s.checkDate, s.versionDate, 0 FROM test.event_117007_source s JOIN test.event_117007_owner o ON o.uId = s.uId WHERE o.svrId = 71;

INSERT INTO rasalas_w01_g73.userevent(idx, uId, eventId, eventType, currentCount, clearCount, premiumCount, customSelectNum, updateDate, checkDate, versionDate, isDelete)
SELECT s.idx, s.uId, s.eventId, s.eventType, s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum, s.updateDate, s.checkDate, s.versionDate, 0 FROM test.event_117007_source s JOIN test.event_117007_owner o ON o.uId = s.uId WHERE o.svrId = 73;

INSERT INTO rasalas_w01_g81.userevent(idx, uId, eventId, eventType, currentCount, clearCount, premiumCount, customSelectNum, updateDate, checkDate, versionDate, isDelete)
SELECT s.idx, s.uId, s.eventId, s.eventType, s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum, s.updateDate, s.checkDate, s.versionDate, 0 FROM test.event_117007_source s JOIN test.event_117007_owner o ON o.uId = s.uId WHERE o.svrId = 81;

INSERT INTO rasalas_w01_g83.userevent(idx, uId, eventId, eventType, currentCount, clearCount, premiumCount, customSelectNum, updateDate, checkDate, versionDate, isDelete)
SELECT s.idx, s.uId, s.eventId, s.eventType, s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum, s.updateDate, s.checkDate, s.versionDate, 0 FROM test.event_117007_source s JOIN test.event_117007_owner o ON o.uId = s.uId WHERE o.svrId = 83;

6번에 4개의 쿼리가 필요한데 맞는지 확인해 주세요.

### Assistant

네, 최종 목적지 게임 DB가 `71, 73, 81, 83` 네 곳이라면 INSERT 쿼리도 4개가 필요한 것이 맞습니다.

다만 `o.svrId`가 “구매 당시 서버”인지 “합병 후 목적지 서버”인지 확인해야 합니다.

- 원본 서버 값이라면 `72, 74, 82, 84` 사용자가 누락됩니다.
- 이미 `72→71`, `74→73`, `82→81`, `84→83`으로 변환한 값이라면 현재 쿼리가 맞습니다.
- 앞에서 만든 테이블 구조대로라면 `o.svrId`가 아니라 `o.targetSvrId`를 사용하는 것이 안전합니다.

## 권장 쿼리

```sql
INSERT INTO rasalas_w01_g71.userevent
(
    idx, uId, eventId, eventType,
    currentCount, clearCount, premiumCount, customSelectNum,
    updateDate, checkDate, versionDate, isDelete
)
SELECT
    s.idx, s.uId, s.eventId, s.eventType,
    s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum,
    s.updateDate, s.checkDate, s.versionDate, 0
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
WHERE o.targetSvrId = 71;
```

```sql
INSERT INTO rasalas_w01_g73.userevent
(
    idx, uId, eventId, eventType,
    currentCount, clearCount, premiumCount, customSelectNum,
    updateDate, checkDate, versionDate, isDelete
)
SELECT
    s.idx, s.uId, s.eventId, s.eventType,
    s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum,
    s.updateDate, s.checkDate, s.versionDate, 0
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
WHERE o.targetSvrId = 73;
```

```sql
INSERT INTO rasalas_w01_g81.userevent
(
    idx, uId, eventId, eventType,
    currentCount, clearCount, premiumCount, customSelectNum,
    updateDate, checkDate, versionDate, isDelete
)
SELECT
    s.idx, s.uId, s.eventId, s.eventType,
    s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum,
    s.updateDate, s.checkDate, s.versionDate, 0
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
WHERE o.targetSvrId = 81;
```

```sql
INSERT INTO rasalas_w01_g83.userevent
(
    idx, uId, eventId, eventType,
    currentCount, clearCount, premiumCount, customSelectNum,
    updateDate, checkDate, versionDate, isDelete
)
SELECT
    s.idx, s.uId, s.eventId, s.eventType,
    s.currentCount, s.clearCount, s.premiumCount, s.customSelectNum,
    s.updateDate, s.checkDate, s.versionDate, 0
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
WHERE o.targetSvrId = 83;
```

## 실행 전 분배 현황 확인

```sql
SELECT
    targetSvrId,
    COUNT(*) AS userCount
FROM test.event_117007_owner
GROUP BY targetSvrId
ORDER BY targetSvrId;
```

결과에 `71, 73, 81, 83` 외 값이 있으면 현재 네 쿼리만으로는 누락됩니다.

```sql
SELECT *
FROM test.event_117007_owner
WHERE targetSvrId NOT IN (71, 73, 81, 83)
   OR targetSvrId IS NULL;
```

이 결과는 반드시 0건이어야 합니다.

## 목적지 중복 검사

INSERT 전에 네 DB 모두 검사해야 합니다.

```sql
SELECT '71' AS targetServer, s.uId, s.idx, 'UID_EVENT_DUPLICATE' AS reason
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
JOIN rasalas_w01_g71.userevent d
  ON d.uId = s.uId
 AND d.eventId = s.eventId
WHERE o.targetSvrId = 71

UNION ALL

SELECT '71', s.uId, s.idx, 'IDX_DUPLICATE'
FROM test.event_117007_source s
JOIN test.event_117007_owner o ON o.uId = s.uId
JOIN rasalas_w01_g71.userevent d ON d.idx = s.idx
WHERE o.targetSvrId = 71;
```

이를 `73, 81, 83`에도 수행하고 결과가 0건인지 확인해야 합니다.

## 이전 후 건수 검증

```sql
SELECT
    (SELECT COUNT(*)
       FROM test.event_117007_source s
       JOIN test.event_117007_owner o ON o.uId = s.uId)
    AS sourceCount,

    (
        (SELECT COUNT(*)
           FROM rasalas_w01_g71.userevent
          WHERE eventId = 117007
            AND uId IN (
                SELECT uId FROM test.event_117007_owner
                WHERE targetSvrId = 71
            ))
        +
        (SELECT COUNT(*)
           FROM rasalas_w01_g73.userevent
          WHERE eventId = 117007
            AND uId IN (
                SELECT uId FROM test.event_117007_owner
                WHERE targetSvrId = 73
            ))
        +
        (SELECT COUNT(*)
           FROM rasalas_w01_g81.userevent
          WHERE eventId = 117007
            AND uId IN (
                SELECT uId FROM test.event_117007_owner
                WHERE targetSvrId = 81
            ))
        +
        (SELECT COUNT(*)
           FROM rasalas_w01_g83.userevent
          WHERE eventId = 117007
            AND uId IN (
                SELECT uId FROM test.event_117007_owner
                WHERE targetSvrId = 83
            ))
    ) AS insertedCount;
```

`sourceCount = insertedCount`인지 확인한 뒤에만 `accountevent`를 비활성화하거나 삭제해야 합니다.

결론적으로 **네 개의 INSERT는 맞지만, 조건 컬럼은 합병 변환이 완료된 `targetSvrId`를 사용하는 것이 핵심**입니다. `svrId`에 원본 서버 값이 들어 있다면 현재 쿼리는 `72, 74, 82, 84` 사용자를 누락시킵니다.
