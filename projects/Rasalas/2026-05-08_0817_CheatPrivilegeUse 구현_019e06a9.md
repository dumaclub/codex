# CheatPrivilegeUse 구현

- Project: Rasalas
- Session ID: `019e06a9-9afa-73f3-b75b-767be9e1122a`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-05-08T08:17:19.144Z
- Updated: 2026-05-08T08:17:33.6160833Z
- Messages exported: 14

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

특권이 없는 상황에서 치트키를 사용하여 특권을 사용할 수 있도록 처리하는 기능을 추가하려고 합니다. 
아래의 과정으로 작업하고 있는데 CheatPrivilegeUse 함수에서 작업을 완료해 주세요.  (서버작업만 하면 됩니다. )  
                        case eCheatCommand.privilegeuse:
                            isSuccess = PrivilegeUse(user, int.Parse(parserText[1]));
                            break;
private bool PrivilegeUse(UserGameModel user, int groupId)
public static void OnCheatPrivielegeCmd(BaseZoneCmd baseCmd)
public void CheatPrivilegeUse(int groupId)

### Assistant

먼저 서버 쪽 흐름이 어디까지 이미 연결돼 있는지 확인하겠습니다. `privilegeuse` 커맨드, 패킷 핸들러, 그리고 `CheatPrivilegeUse` 구현부를 따라가서 기존 권한/특권 사용 로직에 맞춰 마무리할게요.

### Assistant

전체 검색은 Unity 임시/라이브러리 파일까지 걸려서 너무 넓었습니다. 이제 서버 소스만 좁혀서 해당 커맨드 경로를 다시 찾고 있습니다.

### Assistant

핵심 연결은 이미 되어 있네요. `/privilegeuse groupId`는 존 커맨드까지 들어오고, 현재 빈 곳은 `BMModel.CheatPrivilegeUse`입니다. 이제 일반 특권 구매가 BM 엔티티와 종료 시간을 어떻게 세팅하는지 맞춰보겠습니다.

### Assistant

일반 구매 경로를 보니 특권은 `BMStoreData`의 `PrivilegeGroup`과 BM 엔티티의 `lastRefreshDate + PrivilegeDayCount`로 활성 기간을 계산합니다. 치트에서는 과금/보상 지급 없이 그 활성 상태만 만들어 주고, 클라이언트 갱신 패킷까지 보내는 쪽으로 `CheatPrivilegeUse`를 채우겠습니다.

### Assistant

`CheatPrivilegeUse`에 특권 BM 엔티티 생성/갱신, 특권 종료 시간 갱신, 특권 스탯 즉시 적용, `SC_RefreshNotify` 전송까지 넣었습니다. 이제 빌드 전 문법과 주변 메서드 배치를 한 번 확인하겠습니다.

### Assistant

특권 출석도 같은 BM 데이터의 `LinkTableEventID`에 붙어 있어서, 새로 특권을 활성화한 경우에는 기존 구매 경로처럼 이벤트 엔티티도 만들어 주도록 보강하겠습니다. 이미 활성 중인 특권을 다시 치트로 호출했을 때 출석 진행도가 리셋되지 않도록 그 경우는 건드리지 않게 두겠습니다.

### Assistant

이제 서버 솔루션을 복원 없이 빌드해서 컴파일 오류가 없는지 확인하겠습니다. 외부 패키지 다운로드 없이 현재 체크아웃된 의존성만 쓰는 방식으로 돌려볼게요.

### Assistant

빌드는 샌드박스 안에서는 `Packet.dll` 쓰기 권한 때문에 한 번 막혔고, 승인된 MSBuild로 다시 돌렸을 때 서버 솔루션은 정상 빌드됐습니다. 남은 출력은 기존 경고들(패키지 취약성, 아키텍처 경고, 숨김/미사용 경고 등)이고 이번 변경으로 인한 컴파일 오류는 없습니다.

### Assistant

패치 도구가 추가한 블록만 LF 줄바꿈으로 들어가서 파일 안에 CRLF/LF가 섞인 상태가 됐습니다. 코드 내용은 그대로 두고 줄바꿈만 기존 파일 형식에 맞춰 정리하겠습니다.

### Assistant

줄바꿈도 기존 형식으로 정리됐습니다. 마지막으로 같은 서버 빌드를 한 번 더 확인해서 파일 정리 이후 상태까지 검증하겠습니다.

### Assistant

완료했습니다. [BMModel.cs](<E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\BMModel.cs:1021>)의 `CheatPrivilegeUse`를 구현해서 특권이 없을 때 치트로 특권 BM 엔티티를 생성/갱신하고, `PrivilegeDayCount` 기준 종료 시간을 반영하며, 특권 스탯과 특권 출석 이벤트도 적용되도록 했습니다. 마지막에 `SC_RefreshNotify`로 클라에 특권 종료 시간도 갱신합니다.

검증도 끝냈습니다. `Server.sln`을 `Debug|x64`, `/restore:false`로 빌드했고 성공했습니다. 출력에는 기존 경고들이 남아 있지만 이번 변경으로 인한 컴파일 오류는 없습니다.

### User

특권이 있을경우에는 어떻게 처리하도록 작업 되었나요?

### Assistant

현재 구현은 “특권이 이미 있는 경우” 이렇게 동작합니다.

[BMModel.cs](<E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\BMModel.cs:1021>) 기준으로:

- 기존 BM 엔티티가 있으면 새로 만들지 않고 그대로 사용합니다.
- `BuyItem(1)`을 호출해서 `buyCount`와 `lastRefreshDate`는 갱신됩니다.
- `SetPrivilegeBmItem()`에서 종료 시간이 `현재 + PrivilegeDayCount`보다 짧으면 그 시점까지 보정됩니다.
- 이미 활성 특권이면 `BuyEventDailyCashPrivilege()`는 호출하지 않아서 특권 출석 이벤트 진행도는 리셋하지 않습니다.
- 특권 스탯은 이미 적용돼 있으면 중복 적용하지 않고, 누락돼 있으면 다시 적용합니다.

중요한 점은, 현재 작업은 “남은 기간에 28일을 더하는 방식”은 아닙니다. 이미 특권이 있으면 종료 시간을 최소한 `현재 + PrivilegeDayCount`까지 맞추는 방식입니다. 즉 남은 기간이 10일이면 28일로 늘어나고, 남은 기간이 40일이면 그대로 40일 유지됩니다.
