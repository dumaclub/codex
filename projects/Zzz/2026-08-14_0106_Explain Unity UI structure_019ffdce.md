# Explain Unity UI structure

- Project: Zzz
- Session ID: `019ffdce-6295-75a1-844c-9676a1c1d4ad`
- Workspace: `C:\Users\dumaclub\Documents\New project`
- Started: 2026-08-14T01:06:29.505Z
- Updated: 2026-08-14T01:06:35.1222375Z
- Messages exported: 3

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

unity UI 구조에 대해서 설명해 주세요. 기본적인 개념을 알고 있어야 할것 같아서요.

### Assistant

Unity UI는 현재 크게 `uGUI(Canvas 기반)`와 `UI Toolkit` 두 계열로 이해하면 쉽습니다. 두 구조의 공통 개념부터 각각의 계층과 레이아웃 방식까지, 입문 관점에서 정리해 보겠습니다. 최신 Unity 공식 문서 기준도 함께 확인하겠습니다.

### Assistant

Unity UI를 이해할 때는 먼저 “화면에 보이는 요소들이 부모–자식 트리 구조로 배치되고, 별도의 스크립트가 상태와 입력을 연결한다”라고 생각하면 됩니다.

Unity 6에는 `uGUI`, `UI Toolkit`, `IMGUI`가 있습니다. 게임 런타임 UI의 공식 기본 권장 시스템은 여전히 uGUI이고, 복잡한 다중 해상도 메뉴에는 UI Toolkit도 좋은 선택입니다. 에디터 확장 UI는 UI Toolkit이 권장됩니다. [Unity UI 시스템 비교](https://docs.unity3d.com/kr/current/Manual/UI-system-compare.html)

## 1. 가장 흔한 방식: uGUI

uGUI는 Hierarchy에 `Canvas`, `Panel`, `Button`, `Image` 같은 GameObject를 배치하는 방식입니다.

```text
Scene
├─ Main Camera
├─ GameManager
├─ EventSystem
└─ Canvas
   ├─ SafeArea
   │  ├─ HUD
   │  │  ├─ HPBar
   │  │  ├─ MiniMap
   │  │  └─ QuestText
   │  └─ BottomButtons
   ├─ ScreenLayer
   │  ├─ InventoryScreen
   │  └─ SettingsScreen
   └─ PopupLayer
      ├─ ConfirmPopup
      └─ LoadingPanel
```

핵심 구성요소는 다음과 같습니다.

### Canvas

모든 uGUI 요소의 최상위 렌더링 영역입니다. 일반적으로 `Image`, `Text`, `Button` 등은 Canvas 아래에 있어야 화면에 표시됩니다.

Canvas에는 세 가지 주요 렌더 모드가 있습니다.

- `Screen Space - Overlay`: 카메라와 관계없이 화면 위에 표시
- `Screen Space - Camera`: 지정한 카메라를 기준으로 표시
- `World Space`: UI를 3D 월드 안의 오브젝트처럼 배치

일반적인 HUD나 메뉴는 `Screen Space - Overlay`, 캐릭터 머리 위 체력바나 VR 패널은 `World Space`를 많이 사용합니다.

### Canvas Scaler

해상도가 달라져도 UI 크기를 일정하게 보이도록 조정합니다.

대부분의 게임에서는 다음과 같이 시작합니다.

```text
UI Scale Mode       : Scale With Screen Size
Reference Resolution: 1920 × 1080
Screen Match Mode   : Match Width Or Height
Match               : 0.5
```

`Match`가 0이면 너비, 1이면 높이를 더 중요하게 맞춥니다. 모바일 게임은 기기 비율 차이가 크므로 이 설정과 실제 기기 테스트가 중요합니다.

### RectTransform

UI 오브젝트는 일반 `Transform` 대신 `RectTransform`을 사용합니다.

특히 네 개념을 알아두면 좋습니다.

- `Anchor`: 부모 영역의 어느 지점을 기준으로 배치할지
- `Pivot`: 자신의 회전·크기 변경 기준점
- `Anchored Position`: Anchor를 기준으로 한 위치
- `Size Delta`: Anchor로 계산된 크기에 더해지는 크기 차이

예를 들어 오른쪽 위에 고정되는 버튼은 Anchor를 오른쪽 위로 설정해야 합니다. 화면 중앙 좌표만 보고 직접 배치하면 해상도가 바뀔 때 위치가 무너지기 쉽습니다.

### UI 요소

uGUI의 요소는 크게 두 종류로 볼 수 있습니다.

- 표시 요소: `Image`, `RawImage`, `TextMeshProUGUI`
- 상호작용 요소: `Button`, `Toggle`, `Slider`, `ScrollRect`, `TMP_InputField`

실제 프로젝트에서는 기존 `Text`보다 TextMesh Pro 계열을 사용하는 경우가 일반적입니다.

### EventSystem

마우스 클릭, 터치, 키보드 및 게임패드 선택 같은 입력을 UI 요소에 전달합니다. 보통 UI를 처음 생성하면 Unity가 자동으로 만들어 줍니다.

`Button.onClick`, `Toggle.onValueChanged` 등이 EventSystem을 통해 동작합니다. 클릭이 안 될 때는 다음을 확인하면 됩니다.

- 씬에 EventSystem이 있는가
- Canvas에 Graphic Raycaster가 있는가
- 투명한 Image가 클릭을 가리고 있지 않은가
- `Raycast Target`이 불필요하게 활성화되어 있지 않은가
- 상위 Canvas Group의 `Interactable` 또는 `Blocks Raycasts`가 꺼져 있지 않은가

### Layout 컴포넌트

요소를 자동 정렬할 때 사용합니다.

- `Horizontal Layout Group`
- `Vertical Layout Group`
- `Grid Layout Group`
- `Content Size Fitter`
- `Layout Element`
- `Aspect Ratio Fitter`

인벤토리 아이템처럼 반복되는 UI는 직접 좌표를 지정하기보다 `Grid Layout Group`과 프리팹을 사용하는 편이 좋습니다.

다만 부모의 `Content Size Fitter`와 자식의 Layout 계산이 서로 크기를 계속 변경하는 순환 구조는 피해야 합니다.

## 2. UI Toolkit의 구조

UI Toolkit은 웹 개발과 비슷하게 구조, 디자인, 동작을 분리합니다.

```text
GameObject
└─ UIDocument
   ├─ Panel Settings
   └─ MainMenu.uxml

MainMenu.uxml
└─ VisualElement
   ├─ Label
   ├─ Button
   └─ VisualElement
```

각 구성은 다음 역할을 합니다.

- `UIDocument`: 씬과 UI 문서를 연결하는 컴포넌트
- `PanelSettings`: 해상도, 스케일, 렌더링 설정
- `UXML`: UI 요소와 계층 구조
- `USS`: 색상, 글꼴, 간격, 레이아웃 등의 스타일
- `C#`: 이벤트와 게임 로직
- `Visual Tree`: 런타임에 생성된 실제 UI 요소 트리

Unity 공식 문서도 UXML을 구조, Panel Settings를 렌더링 담당으로 설명합니다. [UI Document 구성](https://docs.unity3d.com/kr/current/Manual/UIE-create-ui-document-component.html) UI Toolkit은 UI 트리를 메모리에 유지하는 retained-mode 구조이며, 기본 레이아웃에는 Flexbox 방식을 사용합니다. [UI Toolkit 소개](https://docs.unity3d.com/kr/6000.0/Manual/ui-systems/introduction-ui-toolkit.html)

간단한 예는 다음과 같습니다.

```xml
<ui:VisualElement class="menu">
    <ui:Label text="게임 메뉴" class="title" />
    <ui:Button name="startButton" text="시작" />
</ui:VisualElement>
```

```css
.menu {
    flex-grow: 1;
    align-items: center;
    justify-content: center;
}

.title {
    font-size: 32px;
    margin-bottom: 20px;
}
```

```csharp
private void OnEnable()
{
    var root = GetComponent<UIDocument>().rootVisualElement;
    var startButton = root.Q<Button>("startButton");

    startButton.clicked += StartGame;
}
```

UXML은 HTML, USS는 CSS와 비슷하다고 생각하면 이해하기 쉽습니다. [UXML 구조 설명](https://docs.unity3d.com/kr/current/Manual/UIE-UXML.html)

## 3. 실전에서는 화면과 로직을 분리합니다

규모가 조금만 커져도 다음처럼 나누는 것이 좋습니다.

```text
게임 데이터
    ↓
UI Controller / Presenter
    ↓
UI View
    ↓
Button, Text, Image
```

예를 들어 체력 UI라면:

- `PlayerHealth`: 실제 체력 데이터를 관리
- `HUDController`: 체력 변경 이벤트를 받음
- `HealthBarView`: Slider와 숫자만 갱신

`HealthBarView`가 플레이어의 피해 계산까지 담당하게 만들면 나중에 UI 교체, 테스트, 멀티플레이 동기화가 어려워집니다.

## 4. 입문 학습 순서

처음에는 uGUI로 다음 순서대로 배우는 것이 무난합니다.

1. Canvas와 Canvas Scaler
2. RectTransform의 Anchor와 Pivot
3. Image, TextMeshPro, Button
4. Layout Group과 ScrollRect
5. Prefab을 이용한 반복 UI
6. 화면·팝업 계층 분리
7. UI와 게임 데이터 간 이벤트 연결
8. 이후 UI Toolkit의 UXML, USS, Flexbox

가장 중요한 기초는 `Canvas`, `RectTransform`, `Anchor`, `EventSystem`, 그리고 “UI 표시 코드와 게임 로직을 분리한다”는 원칙입니다. 이 다섯 가지가 잡히면 HUD, 인벤토리, 팝업 같은 대부분의 UI 구조를 이해할 수 있습니다.
