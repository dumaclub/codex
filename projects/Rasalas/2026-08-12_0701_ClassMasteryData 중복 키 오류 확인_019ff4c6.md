# ClassMasteryData 중복 키 오류 확인

- Project: Rasalas
- Session ID: `019ff4c6-93e9-7261-80b0-72f73fec3b2f`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-08-12T07:01:22.675Z
- Updated: 2026-08-12T07:01:31.9037973Z
- Messages exported: 28

> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.

## Conversation

### User

C_데이터생성기.bat 실행파일로 ClassMasteryData.xlsx 엑셀파일을 json, 바이터리 파일 추출하려고 하니 아래의 오류 발생되고 있습니다. 원인 확인해 주세요.


E:\Rasalas\Trunk\qa\Table>"C:\WINDOWS\System32\cscript.exe" //nologo //B _Excel2Json.js E:\Rasalas\Trunk\qa\Table\ClassMasteryData.xlsx ../Client/Assets/ResourceBundles/Data/GameData/

E:\Rasalas\Trunk\qa\Table>_BinaryBuilder.exe --jsonReadPath ../Client/Assets/ResourceBundles/Data/GameData/ --bytesWritePath ../Client/Assets/ResourceBundles/Data/Binary/  --log 0
json 읽기 경로 - ../Client/Assets/ResourceBundles/Data/GameData/
binary 쓰기 경로 - ../Client/Assets/ResourceBundles/Data/Binary/
path : ../Client/Assets/ResourceBundles/Data/GameData/
path : ../Client/Assets/ResourceBundles/Data/Binary/

바이너리 생성 1

바이너리 에러
   위치: System.ThrowHelper.ThrowArgumentException(ExceptionResource resource)
   위치: System.Collections.Generic.Dictionary`2.Insert(TKey key, TValue value, Boolean add)
   위치: System.Linq.Enumerable.
   위치: System.ThrowHelper.ThrowArgumentException(ExceptionResource resource)
   위치: System.Collections.Generic.Dictionary`2.Insert(TKey key, TValue value, Boolean add)
   위치: System.Linq.Enumerable.ToDictionary[TSource,TKey,TElement](IEnumerable`1 source, Func`2 keySelector, Func`2 elementSelector, IEqualityComparer`1 comparer)
   위치: System.Linq.Enumerable.ToDictionary[TSource,TKey,TElement](IEnumerable`1 source, Func`2 keySelector, Func`2 elementSelector)
   위치: SharedLib.Data.LoaderClassMasteryData.ReadStream(eRunType loadType) 파일 F:\Egon_dev2\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:줄 57
   위치: SharedLib.Data.DataManager.Load(eRunType loaderRunType, RuntimeTypeModel model, Boolean checkData) 파일 F:\Egon_dev2\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\DataManager.cs:줄 158
   위치: BinaryBuilder.Program.Main(String[] args)

!!! 바이너리 생성 실패!!!
익셉션 - 동일한 키를 사용하는 항목이 이미 추가되었습니다.

### Assistant

오류 스택의 `LoaderClassMasteryData.cs:57`과 실제 생성된 JSON, 원본 엑셀의 키 열을 서로 대조해 중복 키가 어디서 생겼는지 확인하겠습니다. 우선 배치·로더·변환 스크립트와 관련 파일 상태를 읽겠습니다.

### Assistant

원본 `.xlsx`의 실제 행까지 확인해야 하므로 스프레드시트 분석 절차를 적용하겠습니다. 생성 JSON에서 충돌 키를 먼저 특정한 뒤, 엑셀의 시트/행과 매칭해 원인이 원본 데이터인지 변환 문제인지 구분하겠습니다.

### Assistant

현재 생성 JSON에서 첫 충돌 후보가 확인됐습니다. `ClassMasteryConfig` 안에 `MasterCoinMaxPoint`, `RedSlotRate` 등 동일 `Id`가 두 번 들어가며, 로더는 이를 `Id` 기준 Dictionary로 바꾸는 순간 예외가 납니다. 이제 중복 항목 전체와 엑셀의 정확한 행 번호를 확인하겠습니다.

### Assistant

엑셀에서도 중복 위치가 확인됐습니다. `ClassMasteryConfig` 시트의 B3:B10 블록 중 7개 키가 B12:B19에 그대로 반복됩니다. 반면 다른 데이터 섹션의 Dictionary 키(`ClassMasteryId` 또는 `Id`)에는 중복이 없어, 이번 실패 원인은 Config 키 중복으로 한정됩니다. 기존 데이터와 의도된 명명 규칙도 비교해 보겠습니다.

### Assistant

원인은 `ClassMasteryConfig`의 중복 `Id`입니다. JSON 변환은 성공했지만, 바이너리 변환 시 중복 키 때문에 실패합니다.

엑셀 `ClassMasteryConfig` 시트에서 다음 키가 두 번 존재합니다. :codex-file-citation{path="E:\Rasalas\Trunk\qa\Table\ClassMasteryData.xlsx" purpose="source" artifact_kind="workbook" sheet="ClassMasteryConfig" range="B3:C19"}

- `MasterCoinMaxPoint`: 3행, 12행
- `RedSlotRate`: 5행, 14행
- `BlueSlotRate`: 6행, 15행
- `GreenSlotRate`: 7행, 16행
- `PresetMaxPage`: 8행, 17행
- `PresetNeedItem`: 9행, 18행
- `PresetOpenCost`: 10행, 19행

생성된 [ClassMasteryData.json](E:/Rasalas/Trunk/qa/Client/Assets/ResourceBundles/Data/GameData/ClassMasteryData.json:44)에도 동일하게 7개 키가 중복 출력되어 있습니다.

로더에서는 Config 데이터를 다음과 같이 `Id` 기준 Dictionary로 변환합니다.

```csharp
_classMasteryConfig = classMasteryConfigDatas.ToDictionary(
    x => x.Id,
    x => x.Value);
```

[LoaderClassMasteryData.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/DataManager/Loader/LoaderClassMasteryData.cs:56)

`Dictionary` 키는 반드시 고유해야 하므로 두 번째 `MasterCoinMaxPoint`를 읽는 시점에 “동일한 키를 사용하는 항목이 이미 추가되었습니다” 예외가 발생합니다.

수정 방향은 다음과 같습니다.

- 12행의 `MasterCoinMaxPoint`와 17~19행의 공통 설정이 불필요한 반복이면 해당 행을 제거합니다.
- 14~16행은 코드상 마스터 마스터리 전용 키인 아래 이름을 사용하는 것이 의도에 맞아 보입니다.
  - `MasterRedSlotRate`
  - `MasterBlueSlotRate`
  - `MasterGreenSlotRate`

실제로 로더도 이 이름을 조회합니다: [LoaderClassMasteryData.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/DataManager/Loader/LoaderClassMasteryData.cs:178).

다른 섹션의 키 중복 여부도 확인했으며 `ClassMasteryData`, `ClassMasterySlotStatData`, `ClassMasteryBingoCheckData`, `ClassMasteryBingoStatData`, `ClassMasteryChangeData`에는 중복 키가 없습니다. 따라서 이번 오류는 `ClassMasteryConfig` 중복으로 특정됩니다.

참고로 스택의 `F:\Egon_dev2\...:57`은 빌드 당시 PDB에 기록된 소스 경로이며, 현재 작업본에서는 같은 코드가 56행에 있습니다. 원인과는 무관합니다. 파일은 수정하지 않고 원인만 확인했습니다.

### User

기획자분께 변경된 엑셀파일을 받았는데 다시 에러가 발생되었습니다.  엑셀파일에 또 중복된 키값이 있나요?

E:\Rasalas\Trunk\qa\Table>"C:\WINDOWS\System32\cscript.exe" //nologo //B _Excel2Json.js E:\Rasalas\Trunk\qa\Table\ClassMasteryData.xlsx ../Client/Assets/ResourceBundles/Data/GameData/

E:\Rasalas\Trunk\qa\Table>_BinaryBuilder.exe --jsonReadPath ../Client/Assets/ResourceBundles/Data/GameData/ --bytesWritePath ../Client/Assets/ResourceBundles/Data/Binary/  --log 0
json 읽기 경로 - ../Client/Assets/ResourceBundles/Data/GameData/
binary 쓰기 경로 - ../Client/Assets/ResourceBundles/Data/Binary/
path : ../Client/Assets/ResourceBundles/Data/GameData/
path : ../Client/Assets/ResourceBundles/Data/Binary/

바이너리 생성 1

바이너리 에러
   위치: System.ThrowHelper.ThrowArgumentException(ExceptionResource resource)
   위치: System.Collections.Generic.Dictionary`2.Insert(TKey key, TValue value, Boolean add)
   위치: SharedLib.Data.LoaderCl
   위치: System.ThrowHelper.ThrowArgumentException(ExceptionResource resource)
   위치: System.Collections.Generic.Dictionary`2.Insert(TKey key, TValue value, Boolean add)
   위치: SharedLib.Data.LoaderClassMasteryData.ReadStreamAfter() 파일 E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:줄 137
   위치: SharedLib.Data.DataManager.Load(eRunType loaderRunType, RuntimeTypeModel model, Boolean checkData) 파일 E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\DataManager.cs:줄 161
   위치: BinaryBuilder.Program.Main(String[] args)

!!! 바이너리 생성 실패!!!
익셉션 - 동일한 키를 사용하는 항목이 이미 추가되었습니다.

데이터 읽기 처리 중 오류가 생겼습니다!!! 프로그래머에게 문의 해 주세요

### Assistant

이번에는 최초 Config 로딩이 아니라 `ReadStreamAfter():137`에서 발생했으므로, 이전과 다른 복합 키 중복일 가능성이 큽니다. 변경된 엑셀·생성 JSON과 137행에서 구성하는 Dictionary 키 조합을 다시 대조하겠습니다. 스프레드시트 분석 절차로 원본 행까지 특정하겠습니다.

### Assistant

이전의 단일 `Id` 중복은 모두 해소되었습니다. 새 오류는 137행의 `_maxClassMasteryExp.Add(cmData.MasteryLv, …)`에서 발생하며, 특정 클래스 데이터에 동일한 `MasteryLv`가 여러 건 들어온 경우입니다. 해당 클래스 값과 충돌 레벨·엑셀 행을 바로 추적하고 있습니다.

### Assistant

확인 결과, 이전과 같은 단순 `Id` 중복은 없습니다. 이번 오류는 `MasteryType`이 다른 데이터에서 `MasteryLv`가 겹치는데, 로더가 레벨만 Dictionary 키로 사용해서 발생합니다.

최초 충돌 데이터는 다음 두 행입니다.

- 엑셀 2행: `ClassMasteryId=1101`, `ClassId=1`, `MasteryType=1`, `MasteryLv=1`
- 엑셀 114행: `ClassMasteryId=1117`, `ClassId=1`, `MasteryType=2`, `MasteryLv=1`

일반 마스터리의 1~9레벨: :codex-file-citation{path="E:\Rasalas\Trunk\qa\Table\ClassMasteryData.xlsx" purpose="source" artifact_kind="workbook" sheet="ClassMasteryData" range="B2:F10"}

마스터 마스터리의 1~9레벨: :codex-file-citation{path="E:\Rasalas\Trunk\qa\Table\ClassMasteryData.xlsx" purpose="source" artifact_kind="workbook" sheet="ClassMasteryData" range="B114:F122"}

로더 137행은 `MasteryType`을 고려하지 않고 `MasteryLv`만 키로 추가합니다.

```csharp
_maxClassMasteryExp.Add(cmData.MasteryLv, totVal);
```

[LoaderClassMasteryData.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/DataManager/Loader/LoaderClassMasteryData.cs:137)

따라서 Type 1의 `Lv.1`이 먼저 등록된 후 Type 2의 `Lv.1`을 등록하면서 중복 키 예외가 발생합니다. 1~9레벨이 모두 겹치며, ClassId 1~7에서도 동일한 구조입니다.

정리하면:

- `ClassMasteryConfig.Id`: 중복 없음
- `ClassMasteryData.ClassMasteryId`: 중복 없음
- 다른 시트의 `Id`: 중복 없음
- `(ClassId, MasteryType, MasteryLv)` 조합: 중복 없음
- 로더가 실제 사용하는 `MasteryLv` 단독 키: 중복 있음

이번 건은 엑셀의 잘못된 기본 키라기보다, 새 `MasteryType=2` 데이터 구조를 기존 로더가 처리하지 못하는 문제에 가깝습니다. 이전 Config 오류가 해결되면서 다음 단계에 숨어 있던 오류가 드러난 것입니다.

수정 방법은 경험치 테이블의 기획 의도에 따라 결정해야 합니다.

- 타입별 경험치가 별도라면 Dictionary 키를 `(MasteryType, MasteryLv)`로 변경
- 타입들이 같은 경험치 테이블을 공유한다면 한 `MasteryType` 데이터만 사용하거나 레벨별 데이터를 한 번만 누적
- Type 2가 1~16 전체 기준 테이블이라면 Type 2만 대상으로 `_maxClassMasteryExp`를 구성

엑셀의 Type 2 레벨을 임의로 10부터 바꾸는 방식은 게임 레벨 의미가 달라질 수 있어 권장하지 않습니다. 이번에는 프로그래머 쪽 로더 수정이 필요합니다.

### User

2026.08.12-18.47.53.418 [Exception] query error => NHibernate.QueryException: could not resolve property: dbEntityState of: K2Server.Database.Entities.ClassMasteryExpEntity [.Count[K2Server.Database.Entities.ClassMasteryExpEntity, EgonServer, Version=1.0.0.3, Culture=neutral, PublicKeyToken=[credential redacted], EgonServer, Version=1.0.0.3, Culture=neutral, PublicKeyToken=[credential redacted], Quote((e, ) => (AndAlso(Equal(e.uId, p1<System.Int64>), Equal(Convert(e.dbEntityState.isDelete), p2<System.Int32>)))), ), )]
   at NHibernate.Hql.Ast.ANTLR.Tree.FromElementType.GetPropertyType(String propertyName, String propertyPath)
   at NHibernate.Hql.Ast.ANTLR.Tree.DotNode.Resolve(Boolean generateJoin, Boolean implicitJoin, String classAlias, IASTNode parent)
   at NHibernate.Hql.Ast.ANTLR.Tree.DotNode.ResolveFirstChild()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.addrExprDot(Boolean root)
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.addrExpr(Boolean root)
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.expr()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.functionCall()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.expr()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.exprOrSubquery()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.comparisonExpr()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.logicalExpr()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.logicalExpr()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.whereClause()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.unionedQuery()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.query()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.selectStatement()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlWalker.statement()
   at NHibernate.Hql.Ast.ANTLR.HqlSqlTranslator.Translate()
   at NHibernate.Hql.Ast.ANTLR.QueryTranslatorImpl.Analyze(String collectionRole)
   at NHibernate.Hql.Ast.ANTLR.QueryTranslatorImpl.DoCompile(IDictionary`2 replacements, Boolean shallow, String collectionRole)
   at NHibernate.Hql.Ast.ANTLR.ASTQueryTranslatorFactory.CreateQueryTranslators(IQueryExpression queryExpression, IASTNode ast, String queryIdentifier, String collectionRole, Boolean shallow, IDictionary`2 filters, ISessionFactoryImplementor factory)
   at NHibernate.Hql.Ast.ANTLR.ASTQueryTranslatorFactory.CreateQueryTranslators(IQueryExpression queryExpression, String collectionRole, Boolean shallow, IDictionary`2 filters, ISessionFactoryImplementor factory)
   at NHibernate.Engine.Query.QueryPlanCache.GetHQLQueryPlan(IQueryExpression queryExpression, Boolean shallow, IDictionary`2 enabledFilters)
   at NHibernate.Impl.AbstractSessionImpl.GetHQLQueryPlan(IQueryExpression queryExpression, Boolean shallow)
   at NHibernate.Impl.AbstractSessionImpl.CreateQuery(IQueryExpression queryExpression)
   at NHibernate.Linq.DefaultQueryProvider.PrepareQuery(Expression expression, IQuery& query)
   at NHibernate.Linq.DefaultQueryProvider.Execute[TResult](Expression expression)
   at K2Server.Controllers.DatabaseController.SelectByDB[T](List`1& list, UnitOfWork unitOfWork, Expression`1 expression, Int32 limits) in E:\Rasalas\Trunk\qa\Server\EgonServer\Controllers\DatabaseController.cs:line 1108
   at K2Server.Controllers.DatabaseController.SelectUserInfo(UnitOfWork unitOfWork, Int64 uId, ActorEntityData& data) in E:\Rasalas\Trunk\qa\Server\EgonServer\Controllers\DatabaseController.cs:line 1649
   at K2Server.Controllers.DatabaseController.LoadUserDataByDB(Int64 uId, Int64 charId, ActorEntityData& data) in E:\Rasalas\Trunk\qa\Server\EgonServer\Controllers\DatabaseController.cs:line 1244 (SLogManager.cs:421)
2026.08.12-18.47.53.419 [Error] LoadForUser failed, uid: 105 [DispatchPacketForZMQ() -> OnCS_ZMQ_QueryActorData()] (DBHandler.cs:744)
2026.08.12-18.47.53.419 [System] [Gateway(100) => Unknown(100) ] SendZMQ Send (105, SC_ZMQ_QueryActorData) (ServerController.cs:1897)
2026.08.12-18.47.53.419 [Error] Invoke [1] Proccess Time Over id:12011 [PacketProcessForZMQ() -> DispatchPacketForZMQ()] (ServerModule.cs:1753)
2026.08.12-18.47.53.481 [Error] QueryActorData filed, kick user, uid: 105, result:FailedLoadDbInfo [DispatchPacketForZMQ() -> OnSC_ZMQ_QueryActorData()] (RepHandler.cs:69)
2026.08.12-18.47.53.482 [System] [Gateway(100) => Unknown(100) ] SendZMQ Send (105, CS_ZMQ_GatewayKick) (ServerController.cs:1897)  해당 오류 원인 확인해 주세요.

### Assistant

이번 오류는 DB 컬럼 자체보다 NHibernate 매핑에서 `ClassMasteryExpEntity.dbEntityState` 속성을 찾지 못한 상태입니다. 엔티티 상속 구조, 매핑 파일/Fluent 매핑, 그리고 `SelectUserInfo`의 실제 LINQ 조건을 대조해 누락된 매핑인지 잘못된 타입 선언인지 확인하겠습니다.

### Assistant

원인이 거의 특정됐습니다. `ClassMasteryExpEntity`에는 `dbEntityState` 프로퍼티가 있지만 `ClassMasteryExpMap`에는 그 Component 매핑이 없습니다. 그런데 사용자 로딩 쿼리는 `e.dbEntityState.isDelete`를 조건으로 사용하므로 NHibernate가 SQL 생성 전에 속성 경로를 해석하지 못합니다. 동일 기능의 Slot 엔티티와 DB 스키마까지 확인해 영향 범위를 확정하겠습니다.

### Assistant

원인은 `ClassMasteryExpEntity`의 `dbEntityState`가 NHibernate 매핑에서 누락된 것입니다. DB 데이터 값이나 사용자 UID 105의 데이터 문제는 아닙니다.

오류 발생 흐름:

1. 사용자 데이터 로딩 시 아래 조건으로 조회합니다.

```csharp
e => e.uId == uId && e.dbEntityState.isDelete == 0
```

[DatabaseController.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Controllers/DatabaseController.cs:1649)

2. 엔티티에는 `dbEntityState` 프로퍼티가 실제로 존재합니다.

```csharp
public virtual RedisVersionEntityState dbEntityState { get; protected set; }
```

[ClassMasteryEntity.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Entities/ClassMasteryEntity.cs:291)

3. 하지만 Fluent NHibernate 매핑에는 `dbEntityState` 등록이 없습니다.

[ClassMasteryMap.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Mappings/ClassMasteryMap.cs:6)

현재 `ClassMasteryExpMap`은 `panelCount`까지만 매핑되어 있습니다. 따라서 NHibernate가 `e.dbEntityState.isDelete`를 SQL로 변환하는 단계에서 `dbEntityState`라는 속성을 찾지 못해 예외가 발생합니다. SQL 실행 전 쿼리 해석 단계의 오류입니다.

필요한 수정 형태는 다른 정상적인 매핑들과 동일하게 다음 Component를 추가하는 것입니다.

```csharp
Component(x => x.dbEntityState, m =>
{
    m.Map(x => x.versionDate);
    m.Map(x => x.isDelete).Not.Nullable().Default("0");
});
```

중요한 점은 `ClassMasteryExpMap`뿐 아니라 `ClassMasterySlotMap`에도 같은 매핑이 빠져 있다는 것입니다. 현재는 Exp 조회가 먼저 실패하지만, Exp만 수정하면 다음 조회에서 Slot도 동일한 오류가 날 가능성이 높습니다.

따라서 아래 두 매핑에 모두 추가해야 합니다.

- `ClassMasteryExpMap`
- `ClassMasterySlotMap`

그리고 실제 DB의 다음 테이블에 두 컬럼이 존재하는지도 확인해야 합니다.

- `class_mastery_exp`
- `class_mastery_slot`
- 필요 컬럼: `versionDate`, `isDelete`

컬럼이 없다면 매핑 추가 후에는 `Unknown column` 계열 SQL 오류가 발생하므로 DB 스키마도 함께 반영해야 합니다.

추가로 서버 이전용 컨트롤러에서도 똑같이 `dbEntityState.isDelete` 조건을 사용하고 있어 같은 영향을 받습니다.

- [ServerMoveDBController.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/CommunityNode/Controllers/ServerMoveDBController.cs:1458)
- [ServerMoveDBController.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/CommunityNode/Controllers/ServerMoveDBController.cs:1459)

결론적으로, 이번 오류의 직접 원인은 `ClassMasteryMap.cs`에서 두 클래스 마스터리 엔티티의 `dbEntityState` Component 매핑이 누락된 것입니다. 이후의 유저 강제 종료 로그는 DB 로딩 실패에 따른 후속 결과입니다.

### User

제가 수정했는데 동일한 오류 발생되고 있습니다. 수정이 맞게 되었는지 확인 후 맞지 않다면 다시 수정해 주세요.

### Assistant

현재 수정된 `ClassMasteryMap.cs`와 실제 빌드 대상 프로젝트를 확인하겠습니다. 매핑 코드가 올바르면 실행 중인 서버가 구 DLL을 사용하고 있는지까지 추적하고, 코드가 잘못됐다면 두 엔티티 모두 정상 매핑되도록 수정한 뒤 빌드로 검증하겠습니다.

### Assistant

현재 작업본의 `ClassMasteryMap.cs`에는 수정 내용이 전혀 반영되어 있지 않습니다. 파일 수정 시각도 8월 5일이며 두 Map 모두 `dbEntityState` Component가 없는 원본 상태입니다. 혹시 다른 위치나 다른 파일을 수정했는지 검색한 뒤, 이 빌드 대상 파일에 정확히 반영하겠습니다.

### Assistant

수정하신 내용은 두 조회문에서 `dbEntityState.isDelete == 0` 조건을 제거한 것입니다. 이 방식은 매핑 오류를 우회하지만 삭제 처리된 데이터까지 다시 로드할 수 있어 올바른 수정은 아닙니다. 또한 새 로그에 여전히 해당 조건이 표현되어 있으므로 현재 실행 서버는 수정 전 DLL을 사용 중입니다. 조회 조건을 복원하고, 원인인 Exp/Slot 매핑을 두 곳 모두 수정하겠습니다.

### Assistant

코드는 이제 두 Map 모두 동일한 방식으로 매핑되었고, 삭제 제외 조건도 복원됐습니다. 다음으로 실제 서버 솔루션을 빌드해 Fluent NHibernate 매핑 코드가 컴파일되는지 확인하겠습니다. 빌드 성공 후에는 새 DLL의 생성 시각도 확인해 구 DLL 실행 가능성을 구분하겠습니다.

### Assistant

Debug x64 서버 빌드는 오류 없이 성공했고 새 `EgonServer.dll`이 생성됐습니다. 이제 실행 중인 서버 프로세스가 어느 경로의 DLL을 로드했는지 확인해, 동일 오류가 계속 보이는 이유가 재기동/배포 누락인지 판단하겠습니다. DB 접속이나 서버 재시작은 하지 않고 실행 경로만 확인합니다.

### User

제가 isDelete 구문을 지운것은 해당 테이블이 삭제되는 테이블이 아니기 때문입니다. 스키마 정보 공유 드립니다. CREATE TABLE `class_mastery_exp` (
  `idx` BIGINT NOT NULL,
  `uId` BIGINT NOT NULL,
  `classType` INT NOT NULL,
  `masteryType` INT NOT NULL DEFAULT '1',
  `masteryExp` BIGINT NOT NULL,
  `masteryLv` INT NOT NULL,
  `masteryPoint` BIGINT NOT NULL,
  `masteryCoin` BIGINT NOT NULL,
  `regDate` DATETIME NOT NULL,
  `integrateNum` INT NOT NULL DEFAULT '0',
  `curPanel` INT NOT NULL DEFAULT '0',
  `panelCount` INT NOT NULL DEFAULT '0',
  PRIMARY KEY (`idx`),
  KEY `index_uid` (`uId`)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb3

CREATE TABLE `class_mastery_slot` (
  `idx` BIGINT NOT NULL,
  `uId` BIGINT NOT NULL,
  `panel` INT NOT NULL DEFAULT '0',
  `classType` INT NOT NULL,
  `masteryType` INT NOT NULL,
  `masteryId` INT NOT NULL,
  `masteryLv` INT NOT NULL,
  `slotId` INT NOT NULL,
  `slotColor` INT NOT NULL,
  `isLocked` TINYINT NOT NULL,
  `activeFlag` TINYINT NOT NULL,
  `regDate` DATETIME NOT NULL,
  `integrateNum` INT NOT NULL DEFAULT '0',
  PRIMARY KEY (`idx`),
  KEY `index_uid` (`uId`)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb3

### Assistant

스키마 기준으로 말씀하신 수정 방향이 맞습니다. 두 테이블에 `versionDate`, `isDelete` 컬럼이 없으므로 제가 추가한 Component 매핑은 오히려 다음 단계에서 컬럼 없음 오류를 만들게 됩니다. 제가 추가한 매핑을 제거하고, 두 일반/서버이전 조회문 모두 `uId` 조건만 사용하도록 되돌린 뒤 다시 빌드하겠습니다.

### Assistant

현재 소스는 공유해 주신 스키마와 일치합니다. `ClassMasteryMap`은 실제 컬럼만 매핑하고, 네 조회문 모두 매핑되지 않은 `dbEntityState`를 참조하지 않습니다. 같은 구성으로 서버를 다시 빌드해 최종 검증하겠습니다.

### Assistant

공유해 주신 스키마 기준으로는 `isDelete` 조건을 제거한 수정이 맞습니다. 제가 앞서 추가했던 `dbEntityState` Component 매핑은 다시 제거했습니다.

수정 상태:

- 일반 사용자 로딩 쿼리에서 `uId`만 조회
  - [DatabaseController.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Controllers/DatabaseController.cs:1649)
- 서버 이전 로딩 쿼리도 동일하게 수정
  - [ServerMoveDBController.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/CommunityNode/Controllers/ServerMoveDBController.cs:1458)
- `ClassMasteryExpMap`, `ClassMasterySlotMap`에는 실제 스키마 컬럼만 매핑
  - [ClassMasteryMap.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Mappings/ClassMasteryMap.cs:6)

최종 쿼리는 다음 형태입니다.

```csharp
SelectByDB(ref data.cmExpList, unitOfWork, e => e.uId == uId);
SelectByDB(ref data.cmSlotList, unitOfWork, e => e.uId == uId);
```

Debug x64 전체 서버 빌드도 성공했고 새 DLL이 생성됐습니다.

[EgonServer.dll](E:/Rasalas/Trunk/qa/Server/EgonServer/bin/Debug/net8.0/EgonServer.dll)

동일 오류가 계속 발생했던 이유는 로그의 쿼리 표현식에 여전히 아래 조건이 포함되어 있기 때문입니다.

```text
Equal(Convert(e.dbEntityState.isDelete), ...)
```

즉, 해당 로그를 발생시킨 서버는 수정 전 `EgonServer.dll`을 실행하고 있었습니다. 새 DLL을 실제 실행 경로에 배포한 뒤 DB Node를 포함한 관련 서버 프로세스를 완전히 재시작해야 합니다. 재시작 후에도 로그에 `dbEntityState.isDelete`가 표시된다면 다른 출력 폴더 또는 다른 서버 인스턴스의 구 DLL을 실행 중인 것입니다.

### User

# Files mentioned by the user:

## 2026.08.12-19.10.07.640 [Exception] query error => NHibernate.Exceptions.Generi…: C:\Users\dumaclub\.codex/attachments/d1954629-9e7c-4d74-affd-edabbd56d6c9/pasted-text.txt

## My request:
다른 오류가 발생되었습니다. 실제 테이블과 엔테티사이에 맞지 않는 부분이 있나요?

### Assistant

새 로그의 실제 SQL 예외 메시지와 생성된 쿼리를 읽고, 공유하신 두 테이블 스키마를 엔티티 및 Fluent 매핑의 컬럼·타입·Null 여부와 항목별로 대조하겠습니다.

### Assistant

이번 오류는 앞서 확인한 `class_mastery_exp/slot`이 아니라 `equip_set_option` 테이블에서 발생했습니다. 엔티티/매핑에는 `spClassMasterySet`이 추가됐지만 실제 DB 테이블에는 해당 컬럼이 없다는 명확한 오류입니다. 관련 엔티티·Map·DB 마이그레이션을 찾아 누락 범위가 이 컬럼 하나인지 확인하겠습니다.

### Assistant

네. 이번 오류는 `equip_set_option` 테이블과 엔티티/매핑 불일치입니다.

직접 원인은 다음 컬럼입니다.

```text
Unknown column 'equipsetop0_.spClassMasterySet' in 'field list'
```

서버 매핑에는 `spClassMasterySet`이 존재합니다.

```csharp
Map(x => x.classMasterySet).Not.Nullable();
Map(x => x.spClassMasterySet).Not.Nullable();
```

[OptionMap.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Mappings/OptionMap.cs:36)

엔티티에도 해당 속성이 있고 실제 마스터 마스터리 프리셋 처리에서 사용됩니다.

```csharp
public override int spClassMasterySet { get; set; }
```

[OptionEntity.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Entities/OptionEntity.cs:143)

따라서 매핑을 제거하기보다는 실제 DB 테이블에 컬럼을 추가하는 것이 맞습니다. 우선 운영 중인 DB에서 확인하십시오.

```sql
SHOW CREATE TABLE equip_set_option;
```

`classMasterySet`과 동일한 타입 및 기본값으로 추가해야 합니다. 예를 들어 기존 컬럼이 `INT NOT NULL DEFAULT 0`이라면:

```sql
ALTER TABLE equip_set_option
ADD COLUMN spClassMasterySet INT NOT NULL DEFAULT 0
AFTER classMasterySet;
```

정확한 기본값은 기존 `classMasterySet` 정의와 맞추는 것을 권장합니다.

현재 쿼리에 포함된 컬럼은 다음과 같습니다.

- `idx`
- `uId`
- `charId`
- `equipSet`
- `praySet`
- `spPraySet`
- `faithSet`
- `spFaithSet`
- `classMasterySet`
- `spClassMasterySet` ← 실제 테이블에 없음

MySQL이 마지막 컬럼만 `Unknown column`으로 보고했으므로 현재 확인되는 불일치는 `spClassMasterySet` 하나입니다. 다만 `SHOW CREATE TABLE equip_set_option` 결과를 매핑 전체와 한 번 대조하는 편이 안전합니다.

또한 이번 로그가 이전 `dbEntityState` 오류를 지나 `SelectCharInfo()`까지 진행했다는 점에서, 앞서 수정한 클래스 마스터리 조회 코드는 새 DLL에 정상 반영된 것으로 보입니다. 이번 것은 별도의 DB 스키마 반영 누락입니다.
