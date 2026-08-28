# ClassMasteryData 중복 키 오류 확인

- Project: Rasalas
- Session ID: `019ff4c6-93e9-7261-80b0-72f73fec3b2f`
- Workspace: `E:\Rasalas\Trunk\qa`
- Started: 2026-08-12T07:01:22.675Z
- Updated: 2026-08-12T07:01:31.9037973Z
- Messages exported: 126

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

### User

숙련도 기능에 eMasteryType.MASTER_MASTERY 값이 추가되었습니다. 경험치를 증가시키면 레벨이 증가되고 레벨이 증가되면 ClassMasterySlotEntity 값이 생성되는데 기존에 있던 NORMAL_MASTERY 는 정상적으로 값이 생성되는데 MASTER_MASTERY 는 slotId 값이 0으로 생성됩니다. 원인 확인해 주세요.

### Assistant

`MASTER_MASTERY` 레벨업 시 슬롯 생성 경로를 따라가면서 `slotId`가 어디서 결정되는지, `NORMAL_MASTERY`와 분기 차이가 무엇인지 확인하겠습니다. 서버 모델의 경험치 증가 → 레벨업 → `ClassMasterySlotEntity.Initialize()` 호출과 테이블 로더 조회 키를 순서대로 대조하겠습니다.

### Assistant

`slotId=0`은 엔티티 초기값이 그대로 저장된 것이 아니라, `GetSlotRandomStat()`가 `null`을 반환할 때 코드가 명시적으로 `Id=0` 객체를 만들어 설정하는 동작입니다. 이제 `MASTER_MASTERY`용 `ClassMasterySlotStatData`가 실제 생성 JSON에 있는지, 조회에 사용되는 `(MasterySlotId, ClassId, MasteryType)` 키가 일치하는지 확인하겠습니다.

### Assistant

원인이 확인됐습니다. `MASTER_MASTERY`용 슬롯 확률 데이터는 정상 존재하지만, 슬롯 번호를 `MasteryLv`가 아니라 `masteryId % 100`으로 계산하고 있습니다. MASTER ID가 `1117`부터 시작하므로 첫 레벨도 슬롯 번호가 17로 계산되고, 최대 슬롯 수 16을 초과해 즉시 `null`을 반환합니다. 상수와 전체 ID/레벨 대응을 추가 확인해 영향 범위를 정리하겠습니다.

### Assistant

원인은 `MASTER_MASTERY` 슬롯 데이터 누락이 아니라, 슬롯 번호 계산 방식입니다.

현재 `GetSlotRandomStat()`은 슬롯 번호를 다음처럼 계산합니다.

```csharp
var slotId = masteryId % 100;
if (slotId > slotCount)
    return null;
```

[ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:985)

`NORMAL_MASTERY`는 ID와 레벨이 우연히 일치합니다.

- Lv.1: `MasteryId=1101` → `1101 % 100 = 1`
- Lv.9: `MasteryId=1109` → `1109 % 100 = 9`

반면 `MASTER_MASTERY`는 다음과 같습니다.

- Lv.1: `MasteryId=1117` → 계산된 슬롯 `17`
- Lv.2: `MasteryId=1118` → 계산된 슬롯 `18`
- …
- Lv.16: `MasteryId=1132` → 계산된 슬롯 `32`

실제 MASTER 최대 슬롯 수는 16이므로 첫 레벨부터 다음 조건에 걸립니다.

```csharp
if (slotId > 16)
    return null;
```

MASTER Lv.1 데이터는 정상적으로 존재합니다: [ClassMasteryData.json](E:/Rasalas/Trunk/qa/Client/Assets/ResourceBundles/Data/GameData/ClassMasteryData.json:827)

MASTER 슬롯 확률 데이터도 `MasterySlotId=1`, `MasteryType=2`로 정상 존재합니다: [ClassMasteryData.json](E:/Rasalas/Trunk/qa/Client/Assets/ResourceBundles/Data/GameData/ClassMasteryData.json:5037)

`null` 반환 후 레벨업 코드가 명시적으로 `Id=0` 데이터를 만들어 엔티티에 설정합니다.

```csharp
if (cmSlotStatInfo == null)
{
    cmSlotStatInfo = new ClassMasterySlotStatData();
    cmSlotStatInfo.Id = 0;
}

cmSlotEntity.SetSlot(cmSlotStatInfo.Id, (int)cmSlotColor);
```

[ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:899)

따라서 DB에 `slotId=0`이 저장됩니다.

수정 방향은 `MasteryId` 뒷자리 대신 실제 `MasteryLv`를 슬롯 번호로 사용하는 것입니다.

```csharp
var masteryInfo =
    DataManager.Get<LoaderClassMasteryData>()
        .GetClassMasteryData(masteryId);

if (masteryInfo == null)
    return null;

var slotId = masteryInfo.MasteryLv;

if (slotId < 1 || slotId > slotCount)
    return null;
```

단순히 MASTER일 때 `16`을 빼는 방법도 현재 데이터에는 맞지만, ID 규칙이 변경되면 다시 깨질 수 있으므로 `MasteryLv` 사용이 안전합니다.

동일 함수가 다음 기능에서도 사용되므로 함께 해결됩니다.

- 레벨업 슬롯 생성
- 다른 패널 슬롯 생성
- 슬롯 능력치 재추첨

결론적으로 `MASTER_MASTERY`의 ID가 17부터 시작하는데 기존 코드가 ID 뒷자리를 슬롯 번호로 간주한 것이 직접 원인입니다.

### User

NORMAL_MASTERY 일반 마스터리도 레벨로 계산하는게 더 안전하지 않을까요? 코드 수정해 주세요.

### Assistant

맞습니다. `NORMAL_MASTERY`도 ID 규칙에 의존하지 않고 실제 `MasteryLv`를 사용해야 두 타입이 동일하고 안전하게 동작합니다. `GetSlotRandomStat()` 한 곳을 수정하면 레벨업·재추첨·다른 패널 생성 경로에 모두 적용되므로, 해당 함수만 일관되게 변경하고 서버 빌드로 검증하겠습니다.

### Assistant

수정은 완료됐습니다. 이제 일반/마스터 모두 `ClassMasteryData.MasteryLv`를 슬롯 키로 사용하며, 존재하지 않는 데이터나 타입별 최대 슬롯 범위를 벗어나는 경우도 방어합니다. Debug x64 전체 서버 빌드를 실행해 컴파일 결과를 확인하겠습니다.

### Assistant

수정 완료했습니다. 이제 `NORMAL_MASTERY`와 `MASTER_MASTERY` 모두 `MasteryId`가 아닌 실제 `MasteryLv`로 슬롯 번호를 계산합니다.

변경 내용:

```csharp
var masteryInfo = loader.GetClassMasteryData(masteryId);
if (masteryInfo == null) { return null; }

var slotId = masteryInfo.MasteryLv;
if (slotId < 1 || slotId > slotCount) { return null; }
```

수정 파일: [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:985)

이 변경은 다음 경로에 공통 적용됩니다.

- 레벨업 슬롯 생성
- 다른 패널 슬롯 생성
- 슬롯 능력치 재추첨
- 일반/마스터 마스터리 모두 적용

Debug x64 전체 서버 빌드도 성공했습니다. 기존 경고는 있으나 이번 수정과 관련된 컴파일 오류는 없습니다. 새 [EgonServer.dll](E:/Rasalas/Trunk/qa/Server/EgonServer/bin/Debug/net8.0/EgonServer.dll)을 배포하고 관련 서버를 재시작해야 반영됩니다.

### User

slotId 값은 정상적으로 수정되었는데 slotColor 값이 0으로 셋팅되고 있습니다. 오류 원인 확인 후 수정해 주세요.

### Assistant

`slotColor=0`은 `GetRandomSlotColor()`이 `None`을 반환한 결과입니다. MASTER 전용 색상 확률 설정 키가 로더 기대값과 일치하는지, 합계가 0인지, 랜덤 범위 문제가 있는지를 확인한 뒤 원인 지점에서 수정하고 빌드 검증하겠습니다.

### Assistant

원인이 확인됐습니다. `MASTER_MASTERY` 색상 확률을 로더가 `MasterRedSlotRate` 계열로 찾고 있지만, 실제 생성된 데이터의 키는 `RedSlotRate2`, `BlueSlotRate2`, `GreenSlotRate2`입니다. 세 값이 모두 0으로 읽혀 `None(0)`이 반환되는 상태라, 로더의 키 매핑을 실제 데이터와 맞추겠습니다.

### Assistant

매핑 수정은 완료했습니다. 이제 서버 전체 빌드로 로더 변경이 정상 컴파일되는지 확인하고, 색상 선택 경로에서 더 이상 0 확률로 빠지지 않는지도 함께 점검하겠습니다.

### Assistant

원인 확인 및 수정 완료했습니다.

- 실제 JSON 키: `RedSlotRate2`, `BlueSlotRate2`, `GreenSlotRate2`
- 기존 코드가 존재하지 않는 `MasterRedSlotRate` 계열을 조회
- 모든 확률이 0으로 로드되어 `eMasterySlotColor.None(0)` 반환

[LoaderClassMasteryData.cs](E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:186)의 `MASTER_MASTERY` 매핑을 실제 JSON 키로 변경했습니다.

확률은 정상적으로 합계 10,000입니다.

- Red: 3,334
- Blue: 3,333
- Green: 3,333

서버 전체 Debug/x64 빌드도 오류 없이 성공했습니다. 기존 DB에 이미 `slotColor=0`으로 저장된 데이터는 자동 변경되지 않으므로, 해당 데이터는 재생성하거나 별도로 보정해야 합니다. 새로 생성되는 슬롯부터 정상 색상이 설정됩니다.

### User

바이너리 생성 1

바이너리 에러
   위치: System.ThrowHelper.ThrowArgumentException(ExceptionResource resource)
   위치: System.Collections.Generic.Dictionary`2.Insert(TKey key, TValue value, Boolean add)
   위치: SharedLib.Data.LoaderCl
   위치: System.ThrowHelper.ThrowArgumentException(ExceptionResource resource)
   위치: System.Collections.Generic.Dictionary`2.Insert(TKey key, TValue value, Boolean add)
   위치: SharedLib.Data.LoaderClassMasteryData.ReadStreamAfter() 파일 F:\Egon_dev2\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:줄 136
   위치: SharedLib.Data.DataManager.Load(eRunType loaderRunType, RuntimeTypeModel model, Boolean checkData) 파일 F:\Egon_dev2\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\DataManager.cs:줄 161
   위치: BinaryBuilder.Program.Main(String[] args)

!!! 바이너리 생성 실패!!!
익셉션 - 동일한 키를 사용하는 항목이 이미 추가되었습니다.
데이터 읽기 처리 중 오류가 생겼습니다!!! 프로그래머에게 문의 해 주세요


E:\Rasalas\Trunk\qa\Table\ClassMasteryData.xlsx 파일을 C_데이터생성기.bat 이용하여 변환하는데 위의 에러가 발생되었습니다. 오류 원인 확인해 주세요.

### Assistant

현재 엑셀 원본과 `ReadStreamAfter()`의 136번째 줄에서 구성하는 Dictionary 키를 함께 대조하겠습니다. `.xlsx` 구조와 중복값 검증이 필요하므로 스프레드시트 분석 절차를 사용해 원본 시트별 중복 키를 정확히 찾아보겠습니다.

### Assistant

현재 로더에서 중복 예외가 날 수 있는 핵심 키는 `(MasteryType, MasteryLv)` 및 `(ClassId, MasteryType, MasteryLv)` 조합입니다. 엑셀의 모든 시트를 읽어 실제 중복 행과 셀 위치를 추출하고, 생성된 JSON 결과와도 교차 확인하겠습니다.

### Assistant

엑셀의 실제 데이터 구간에서는 기본 키와 `(ClassId, MasteryType, MasteryLv)` 중복이 발견되지 않았습니다. 따라서 단순한 엑셀 행 중복이 아니라, 변환 결과 JSON과 현재 실행 중인 `_BinaryBuilder.exe`가 기대하는 로더 구조가 어긋났을 가능성을 확인하고 있습니다. 특히 오류의 소스 경로가 현재 `E:`가 아니라 `F:\Egon_dev2`로 찍히는 점도 함께 대조하겠습니다.

### Assistant

원인은 엑셀의 잘못된 중복 키가 아니라, 수정 전 `SharedLib`가 포함된 구버전 `_BinaryBuilder.exe`입니다.

확인 결과:

- 각 시트의 `Id` 및 `ClassMasteryId` 중복: 없음
- `(ClassId, MasteryType, MasteryLv)` 중복: 없음
- 다만 나이트의 `MasteryLv 1~9`는 `MasteryType 1`과 `2`에 각각 존재합니다. 이는 정상 데이터입니다. :codex-file-citation{path="E:/Rasalas/Trunk/qa/Table/ClassMasteryData.xlsx" purpose="source" artifact_kind="workbook" sheet="ClassMasteryData" range="B2:E122"}

현재 `_BinaryBuilder.exe` 내부 로더는 구버전 구조라 `MasteryType`을 키에 포함하지 않습니다. 따라서 아래 두 정상 데이터를 동일한 `MasteryLv=1` 키로 인식합니다.

- 2행: `ClassMasteryId=1101`, `MasteryType=1`, `MasteryLv=1`
- 114행: `ClassMasteryId=1117`, `MasteryType=2`, `MasteryLv=1`

현재 소스는 이미 `MasteryType → MasteryLv` 구조로 수정되어 있습니다.

- [LoaderClassMasteryData.cs](E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:10)
- `_BinaryBuilder.exe` 생성 시간: `2026-08-14 10:46:25`
- 수정된 로더 시간: `2026-08-14 20:53:19`

즉 수정된 로더보다 바이너리 생성기가 오래되었습니다. 스택의 `F:\Egon_dev2\...` 경로도 해당 실행 파일이 다른 작업공간에서 컴파일된 구버전임을 보여주는 PDB 경로입니다.

조치 방법은 다음과 같습니다.

1. 현재 QA 소스로 `SharedLib`를 빌드합니다.
2. [__BinaryBuilderMake.bat](E:\Rasalas\Trunk\qa\Table\__BinaryBuilderMake.bat)을 실행해 `_BinaryBuilder.exe`를 다시 생성합니다.
3. 새 실행 파일의 시간이 로더 수정 시간보다 최신인지 확인합니다.
4. `C_데이터생성기.bat`을 다시 실행합니다.

엑셀에서 `MasteryType 2` 행을 삭제하거나 레벨 값을 변경할 필요는 없습니다. 단순히 서버 빌드만 해서는 `_BinaryBuilder.exe` 내부에 포함된 `SharedLib`가 갱신되지 않으므로, 바이너리 생성기를 반드시 다시 빌드해야 합니다.

### User

마스터리 레벨이 9에서 더이상 오르지 않는데 CLASS_MASTERY_BASE_SLOT_COUNT 로 레벨 제한 적용되어 있어서 그런것은 아닌가요?

### Assistant

`CLASS_MASTERY_BASE_SLOT_COUNT`가 실제 레벨 상한으로 사용되는지, 아니면 슬롯 생성 개수에만 쓰이는지 경험치 증가 → 레벨 계산 → 슬롯 생성 경로를 따라 확인하겠습니다. 특히 9레벨 이후 데이터를 조회할 때 `MasteryType` 구분이 누락되는지도 함께 보겠습니다.

### Assistant

확인 결과 `CLASS_MASTERY_BASE_SLOT_COUNT=9`는 단순 슬롯 반복 횟수뿐 아니라 `NORMAL_MASTERY`의 누적 경험치 상한 계산에도 직접 사용되고 있습니다. 다만 `MASTER_MASTERY` 경로는 별도로 16을 사용하므로, 어떤 타입의 경험치를 올리고 있는지까지 확인해야 정확한 결론이 납니다. 레벨 증가 지점과 타입 전달 경로를 조금 더 확인하겠습니다.

### Assistant

맞습니다. `NORMAL_MASTERY`가 9레벨에서 멈추는 것은 `CLASS_MASTERY_BASE_SLOT_COUNT = 9`가 사실상 레벨 제한으로도 사용되기 때문입니다.

| 타입 | 경험치 상한 | 레벨업 반복 | 데이터 레벨 |
|---|---:|---:|---:|
| `NORMAL_MASTERY` | 9레벨 | 9회 | 1~9 |
| `MASTER_MASTERY` | 16레벨 | 16회 | 1~16 |

근거는 다음과 같습니다.

- [K2Const.cs](E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\K2Const.cs:93): 일반 9, 마스터 16
- [ClassMasteryModel.cs](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Section\ClassMasteryModel.cs:249): 일반 경험치를 9레벨 누적 경험치까지만 증가
- [ActorUserModel_ClassMastery.cs](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Actor\ActorUserModel_ClassMastery.cs:323): 일반 레벨업 검사도 최대 9회
- 일반 마스터리 데이터 역시 현재 9레벨까지만 존재하므로 `nextLv=10` 조회가 실패합니다.

반면 `MASTER_MASTERY`가 9에서 멈추는 경우에는 이 상수가 원인이 아닙니다. 마스터 경로는 이미 `CLASS_MASTERY_MASTER_SLOT_COUNT=16`을 사용합니다.

다만 별도 문제도 확인됩니다. [LoaderClassMasteryData.cs](E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:130)의 누적 경험치 `totVal`이 `MasteryType` 변경 시 초기화되지 않아, 마스터 경험치 기준에 일반 마스터리 누적 경험치 `115,800,000`이 더해지고 있습니다. 현재 마스터 10레벨 요구 누적 경험치는 코드상 `281,600,000`으로 계산됩니다.

따라서:

- `NORMAL_MASTERY`를 10레벨 이상 올리려는 것이라면 상수와 엑셀 데이터 모두 확장해야 합니다.
- `MASTER_MASTERY`가 9에서 멈춘 것이라면 `totVal`을 타입별로 분리하는 수정이 필요합니다. 단순히 `CLASS_MASTERY_BASE_SLOT_COUNT`만 16으로 변경하면 일반 10~16레벨 데이터가 없어 경험치 계산이 잘못됩니다.

### User

오류 수정해 주세요.

### Assistant

`MASTER_MASTERY` 누적 경험치에 `NORMAL_MASTERY` 누적치가 이어 붙는 부분을 타입별 누적으로 분리하겠습니다. 동시에 데이터 순서에 따라 누적값이 달라지지 않도록 `MasteryType`, `MasteryLv` 순으로 계산한 뒤 서버 빌드로 검증하겠습니다.

### Assistant

타입별 누적 계산으로 수정했습니다. 이제 `MASTER_MASTERY` 10레벨 기준은 일반 누적치를 포함한 `281,600,000`이 아니라 마스터 자체 누적치인 `165,800,000`이 됩니다. 컴파일과 데이터 기준값을 검증하겠습니다.

### Assistant

서버 빌드는 성공했습니다. 이전에 확인된 것처럼 데이터 생성기는 `SharedLib`를 실행 파일 내부에 포함하므로, 이번 로더 수정도 반영되도록 `_BinaryBuilder.exe`까지 다시 빌드해 교체하겠습니다.

### Assistant

새 `_BinaryBuilder.exe`도 교체되었습니다. 실제 현재 JSON 전체를 임시 출력 경로로 변환해 중복 키 예외가 재발하지 않는지 마지막으로 확인하겠습니다.

### Assistant

수정 완료했습니다.

[LoaderClassMasteryData.cs](E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\DataManager\Loader\LoaderClassMasteryData.cs:130)에서 누적 경험치를 `MasteryType`별로 분리하고, 레벨 순서대로 계산하도록 변경했습니다.

- 마스터 9레벨: `115,800,000`
- 마스터 10레벨: `165,800,000`
- 마스터 16레벨: `465,800,000`
- 일반 마스터리는 기존대로 최대 9레벨 유지

서버 Debug/x64 전체 빌드에 성공했으며, 수정된 `SharedLib`를 포함하도록 [\_BinaryBuilder.exe](E:\Rasalas\Trunk\qa\Table\_BinaryBuilder.exe)도 재빌드했습니다.

현재 JSON 전체를 대상으로 별도 바이너리 생성 검증도 완료했습니다.

- 결과: `바이너리 생성 성공`
- 생성 파일: 165개
- 중복 키 예외: 없음

기존 DB에 이전 기준으로 누적된 `MASTER_MASTERY` 경험치가 많다면, 서버 반영 후 다음 경험치 증가 시 충족된 레벨까지 연속 상승할 수 있습니다. 테스트 시 기존 숙련도 데이터를 초기화한 캐릭터로 확인하는 것이 가장 정확합니다.

### User

2026.08.14-21.35.00.324 [Info] Recv Packet : CS_Cheat (ServerModule.cs:1813)
2026.08.14-21.35.00.325 [System] CHEAT uid:110, charid:2503932413886918657, /addClassMasteryExp 2 100000000 (CheatManager.cs:324)
2026.08.14-21.35.00.377 [Error] EnqueueReservedItem failed, invalid itemid: 0, uid: 110 [AddReservedItem() -> EnqueueReservedItem()] (ActorModel_Inventory.cs:68)
2026.08.14-21.35.00.378 [Error] AttMasteryUpgrade baseStatInfoList is null === uId :110, classType:1, masteryType:2, masteryId:1126 [CheckClassMasteryUpgrade() -> MasteryUpgrade()] (ActorUserModel_ClassMastery.cs:831)

9레벨 이상 증가시키려고 해보니 위의 오류가 계속 발생하는데 해당 오류 때문에 레벨 증가가 안된 것인가요?

### Assistant

네, 두 번째 `baseStatInfoList is null` 오류는 `MasteryUpgrade()`가 즉시 실패를 반환하는 지점이라 레벨 증가를 직접 막습니다. `masteryId=1126`의 `StatGroupId`와 실제 스탯 그룹 데이터 존재 여부를 확인하고, 함께 발생한 `itemid: 0`의 설정 키 오류도 분리해서 확인하겠습니다.

### Assistant

네. 레벨 증가를 직접 막는 오류는 다음 로그입니다.

```text
AttMasteryUpgrade baseStatInfoList is null
masteryType:2, masteryId:1126
```

`masteryId=1126`은 `MASTER_MASTERY` 10레벨 데이터인데 현재 값이 다음과 같습니다.

```text
MasteryLv   = 10
MasteryExp  = 50,000,000
StatGroupId = 50,000,000
```

`StatGroupId=50000000`은 `StatGroupData.json`에 존재하지 않습니다. 따라서 [ActorUserModel_ClassMastery.cs](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Actor\ActorUserModel_ClassMastery.cs:828)에서 스탯 목록 조회가 실패하고, 832번째 줄에서 즉시 반환합니다. 이후의 `SetMasteryLevel()`까지 실행되지 않아 9레벨에 머뭅니다.

같은 문제가 모든 클래스의 `MASTER_MASTERY` 10~16레벨, 총 49개 데이터에 있습니다. `StatGroupId`에 `MasteryExp=50000000`이 잘못 복사된 것으로 보입니다.

또한 아래 오류는 별개 문제입니다.

```text
EnqueueReservedItem failed, invalid itemid: 0
```

[ActorUserModel_ClassMastery.cs](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Actor\ActorUserModel_ClassMastery.cs:351)에서 마스터 코인 설정을 `ExpertMasteryCoin`으로 찾지만 실제 설정 키는 `MasteryCoin2`입니다. 이 오류는 코인 아이템 생성을 실패시키지만, 레벨업을 직접 중단시키는 것은 `baseStatInfoList` 오류입니다.

필요한 수정은 두 가지입니다.

- 엑셀의 마스터리 10~16레벨 `StatGroupId`를 실제 존재하는 스탯 그룹으로 수정하거나 해당 스탯 그룹 데이터를 추가
- 코드의 `ExpertMasteryCoin`을 `MasteryCoin2`로 변경

`StatGroupId`는 기획상 적용할 능력치 그룹을 알아야 정확히 수정할 수 있습니다. 임의 ID로 변경하면 잘못된 능력치가 적용될 수 있습니다.

### User

# Files mentioned by the user:

## codex-clipboard-951586e2-3f9c-4c80-b316-d80815677017.png: C:/Users/dumaclub/AppData/Local/Temp/codex-clipboard-951586e2-3f9c-4c80-b316-d80815677017.png

## My request:
마스터 마스터리 한줄이 빙고가 되었는데 빙고 처리가 안되었습니다. 원인 확인해 주세요.

<image name=[Image #1] path="C:\Users\dumaclub\AppData\Local\Temp\codex-clipboard-951586e2-3f9c-4c80-b316-d80815677017.png">

</image>

### Assistant

스크린샷상 마스터 마스터리 상단 4개 슬롯이 모두 활성화되어 있어 가로 빙고 조건은 충족된 것으로 보입니다. 실제 판정 코드가 4칸을 검사하는지, `MASTER_MASTERY`용 빙고 데이터가 올바른 `ClassMasteryId`와 색상 조건으로 연결되는지 확인하겠습니다.

### Assistant

스크린샷의 실제 완성 줄은 오른쪽 세로 4칸이며 모두 초록색입니다. 이 조합은 데이터상 `CheckMasterySlot=1120,1121,1122,1123`, 초록 빙고 `BingoCheckId=21703`과 정확히 일치합니다. 현재 이 체크 ID에 연결된 빙고 보상 스탯 데이터가 있는지 전체 클래스 범위로 확인 중입니다.

### Assistant

원인은 빙고 판정 로직이 아니라 `ClassMasteryBingoStatData` 누락입니다.

스크린샷 기준:

- 상단 가로줄은 `초록/초록/파랑/초록`이라 빙고가 아닙니다.
- 오른쪽 세로줄은 4칸 모두 초록색이므로 정상 빙고 조건입니다.
- 해당 조합은 `CheckMasterySlot=1120,1121,1122,1123`, `BingoCheckId=21703`입니다.

`ClassMasteryBingoCheckData`에는 `21703`이 존재하지만, 연결된 `ClassMasteryBingoStatData`가 없습니다. 따라서 [ActorUserModel_ClassMastery.cs](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Actor\ActorUserModel_ClassMastery.cs:1183)에서 조회 결과가 `null`이 되고, 1187번째 줄에서 처리를 건너뜁니다. 빙고 정보 등록까지 진행되지 않아 UI에도 표시되지 않습니다.

추가 확인 결과 모든 클래스에서 다음 두 종류의 마스터 빙고 스탯이 누락되어 있습니다.

- 네 번째 세로줄
- 추가 대각선 한 줄
- 색상별 3개 × 2줄 × 7클래스 = 총 42개 누락

현재 나이트 기준 누락 ID는 다음과 같습니다.

- `21701`, `21702`, `21703`
- `21801`, `21802`, `21803`

엑셀의 `ClassMasteryBingoStatData` 시트에 해당 `BingoCheckId`들의 적용 능력치 데이터가 추가되어야 합니다. 현재 구조에서는 빙고 스탯 데이터가 최소 1개 이상 있어야 [SetClassMasteryBingoStat](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Actor\ActorUserModel_ClassMastery.cs:1421)이 호출되어 빙고로 등록됩니다.

또한 일부 다른 클래스의 마스터 빙고 체크 슬롯 ID도 잘못 입력된 것으로 확인되어, 누락된 42개 행뿐 아니라 마스터 빙고 데이터 전체 점검이 필요합니다.

### User

SC_ClassMasteryAction 클래스에 있는 아래 변수는 masteryType이 변경되면서 수정되어야 하나요? 아니면 현재 상태 그대로도 문제 없나요?
        [ProtoMember(10)]
        public Dictionary<int, List<int>> cmBingoStatList = new Dictionary<int, List<int>>();

### Assistant

`cmBingoStatList`의 키가 현재 무엇을 의미하는지(패널, `BingoCheckId`, `masteryType` 등)와 패킷 생성·수신 양쪽을 확인하겠습니다. `masteryType`이 이미 패킷의 별도 필드로 전달된다면 구조 변경 없이도 타입 구분이 가능하지만, 여러 타입의 빙고를 한 패킷에 함께 담는 경로가 있으면 충돌 가능성이 있습니다.

### Assistant

결론적으로 현재 구조 그대로 사용해도 문제없습니다. `masteryType` 추가 때문에 `cmBingoStatList` 형식을 변경할 필요는 없습니다.

현재 데이터 흐름은 다음과 같습니다.

```text
cmBingoStatList
  Key   = panel
  Value = ClassMasteryBingoStatData.Id 목록
```

클라이언트는 각 ID를 통해 타입을 복원합니다.

```text
BingoStatData.Id
→ BingoCheckId
→ BingoCheckData.ClassMasteryId
→ ClassMasteryData.MasteryType
```

실제로 [ClassMasteryContents.cs](E:\Rasalas\Trunk\qa\Client\Assets\Script\System\ContentsSystem\Contents\ClassMasteryContents.cs:466)에서 이 방식으로 `masteryType`을 구한 뒤, 일반/마스터 빙고를 별도 Dictionary에 저장합니다.

서버 내부에서는 이미 다음과 같이 타입별로 분리되어 있습니다.

```text
panel → masteryType → bingoCheckId → BingoStat 목록
```

패킷을 만들 때만 [ClassMasteryModel.cs](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Section\ClassMasteryModel.cs:138)에서 패널별 ID 목록으로 평탄화합니다. `ClassMasteryBingoStatData.Id`가 전체 타입에서 고유하므로 모호하지 않습니다.

따라서 필드는 유지하는 것이 맞습니다.

```csharp
[ProtoMember(10)]
public Dictionary<int, List<int>> cmBingoStatList
    = new Dictionary<int, List<int>>();
```

주석만 명확하게 바꾸는 것은 좋습니다.

```csharp
// Key: panel, Value: ClassMasteryBingoStatData.Id list
```

또한 기존 `[ProtoMember(10)]`의 자료형을 변경하면 구버전 클라이언트·서버와 프로토콜 호환 문제가 생길 수 있습니다. 정말 타입 정보를 패킷에 명시적으로 추가해야 한다면 기존 필드는 유지하고 새로운 `[ProtoMember(11)]` 필드를 추가해야 합니다.

앞서 발생한 마스터 빙고 미처리 문제는 이 패킷 구조 때문이 아닙니다. 서버에서 `BingoCheckId=21703`에 대응하는 `ClassMasteryBingoStatData`가 없어 패킷에 넣을 ID 자체가 생성되지 않은 것이 원인입니다.

### User

아래와 같은 데이터가 있다면 현재 상태에서는 확인할 수 없는 것 아닌가요?
idx	uId	panel	classType	masteryType	masteryId	masteryLv	slotId	slotColor	isLocked	activeFlag	regDate	integrateNum
2503743999414050049	106	1	1	1	1101	1	11028	3	0	1	0001-01-01 00:00:00	0
2503745923559415041	106	1	1	2	1117	1	0	0	0	1	0001-01-01 00:00:00	0
2503773727604792577	106	1	1	1	1102	2	12033	2	0	1	0001-01-01 00:00:00	0
2503780805711125761	106	1	1	2	1118	2	0	0	0	1	0001-01-01 00:00:00	0

### Assistant

제시하신 경우처럼 같은 `panel=1`, `classType=1`에 일반과 마스터 슬롯이 함께 존재하는 상황을 기준으로 다시 보겠습니다. 핵심은 `cmBingoStatList`가 타입을 직접 키로 갖지는 않지만, 값인 `BingoStatData.Id`에서 타입을 역추적할 수 있는지와 “스탯이 없는 빙고”까지 표현할 수 있는지가 서로 다른 문제입니다.

### Assistant

지적하신 부분은 절반은 맞습니다.

같은 `panel=1`에 `masteryType=1`과 `2`가 함께 있어도, 빙고 스탯 데이터가 존재한다면 현재 구조로 타입 구분은 가능합니다. `cmBingoStatList`의 값인 `ClassMasteryBingoStatData.Id`에서 다음 경로로 `masteryType`을 복원하기 때문입니다.

```text
BingoStatData.Id
→ BingoCheckId
→ ClassMasteryId
→ MasteryType
```

하지만 현재 구조에는 분명한 한계가 있습니다.

| 상황 | 현재 구조에서 확인 |
|---|---|
| 일반·마스터가 같은 패널에 있고 빙고 스탯도 존재 | 가능 |
| 빙고는 완성됐지만 연결된 빙고 스탯이 없음 | 불가능 |
| 슬롯의 `slotColor=0` | 빙고 조건 자체 불충족 |

제시하신 마스터 슬롯은 다음 상태입니다.

```text
masteryType=2
slotId=0
slotColor=0
```

[ClassMasterySlotPacket](E:\Rasalas\Trunk\qa\Client\Assets\Script\SharedLib\Packet\DataStruct\ClassMasteryPacketData.cs:79)에는 `masteryType`이 포함되어 있으므로 일반·마스터 슬롯 구분은 됩니다. 하지만 `slotColor=0`은 `None`이므로 이 두 슬롯은 현재 빙고 판정 대상이 될 수 없습니다.

더 중요한 문제는 `cmBingoStatList`가 이름과 달리 “완성된 빙고”가 아니라 “빙고로 적용된 스탯 ID”만 전달한다는 점입니다.

```csharp
Dictionary<int, List<int>>
// Key: panel
// Value: ClassMasteryBingoStatData.Id
```

서버도 빙고 스탯이 있어야 [SetClassMasteryBingoStat](E:\Rasalas\Trunk\qa\Server\EgonServer\ServerNodes\GameNode\Models\Section\ClassMasteryModel.cs:413)을 호출하여 빙고를 저장합니다. 따라서 앞서 확인한 `BingoCheckId=21703`처럼 빙고 체크 데이터는 있지만 스탯 데이터가 없으면, 완성 여부를 패킷에 표현할 방법이 없습니다.

결론은 다음과 같습니다.

- 같은 패널에 일반·마스터 데이터가 함께 있는 것 자체는 현재 구조로 처리 가능합니다.
- 빙고 스탯이 없는 빙고까지 표시해야 한다면 현재 `cmBingoStatList`만으로는 부족합니다.
- 이 경우 기존 `[ProtoMember(10)]`은 호환성을 위해 유지하고, 별도의 완성 빙고 필드를 추가하는 것이 안전합니다.

예를 들면:

```csharp
[ProtoMember(11)]
public List<ClassMasteryBingoPacket> cmBingoList = new();
```

```csharp
[ProtoContract]
public class ClassMasteryBingoPacket
{
    [ProtoMember(1)]
    public int panel;

    [ProtoMember(2)]
    public int masteryType;

    [ProtoMember(3)]
    public int bingoCheckId;
}
```

이렇게 하면 `panel + masteryType + bingoCheckId`로 빙고 완성 상태를 스탯 존재 여부와 무관하게 명확하게 전달할 수 있습니다. 기존 `cmBingoStatList`는 실제 능력치 적용용으로 계속 사용할 수 있습니다.

### User

```
위에 알려주신 ClassMasteryBingoPacket 클래스 형태로 구조 변경해서 수정해 주세요.
```

### Assistant

프로토콜 호환성을 유지하기 위해 기존 `cmBingoStatList`는 능력치 적용용으로 남기고, `panel + masteryType + bingoCheckId`를 담는 `ClassMasteryBingoPacket` 목록을 추가하겠습니다. 서버에서는 빙고 완성 상태를 빙고 스탯 유무와 분리해 저장하고, 클라이언트 UI는 새 목록을 기준으로 완성 표시를 구성하도록 전체 송수신 경로를 수정하겠습니다.

### Assistant

서버의 빙고 완료 상태 저장 부분은 우선 반영했습니다. 이제 모든 패킷 생성 호출부와 클라이언트 표시 로직을 새 `ClassMasteryBingoPacket` 구조에 맞춰 연결하고, 기존 `cmBingoStatList`는 능력치 전달용으로 유지하겠습니다.

### Assistant

클라이언트에서는 “빙고 완료 여부”와 “빙고로 지급된 스탯”을 분리해 저장하도록 바꾸고 있습니다. 이렇게 해야 보상 스탯 행이 없는 `MASTER_MASTERY` 빙고도 완료 색상과 상태를 정상 표시할 수 있습니다. 이전 서버 패킷과의 호환을 위해 기존 스탯 목록에서 완료 상태를 추론하는 보조 처리도 남기겠습니다.

### Assistant

두 UI 소스가 UTF-8이 아닌 기존 한글 인코딩(CP949)이라 패치 도구가 직접 읽지 못하고 있습니다. 파일 인코딩을 임시로 UTF-8로 변환해 수정한 뒤 원래 CP949로 되돌려, 불필요한 전체 파일 변경 없이 적용하겠습니다.

### Assistant

패킷 송수신 연결과 UI 표시까지 반영했습니다. 이제 서버 솔루션 빌드로 DTO 직렬화 필드, 모든 호출부, 서버 빙고 상태 로직의 컴파일 오류를 확인하겠습니다. 이후 클라이언트 쪽은 참조 누락과 호출 시그니처를 별도로 정적 점검하겠습니다.

### Assistant

재접속 초기화 흐름을 추가로 추적한 결과, 같은 패널의 일반/마스터 숙련도를 순서대로 복원할 때 `RemoveAllBingo(panel)`이 다른 `masteryType`의 빙고까지 지우는 기존 문제가 확인됐습니다. 새 구조에서도 마지막 타입만 남을 수 있으므로, 초기화 범위를 `panel + masteryType`으로 제한해 함께 바로잡겠습니다.

### Assistant

수정 완료했습니다.

- `ClassMasteryBingoPacket(panel, masteryType, bingoCheckId)` 구조를 추가했습니다: [ClassMasteryPacketData.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/Packet/DataStruct/ClassMasteryPacketData.cs:8)
- `SC_ClassMasteryInfo`, `SC_ClassMasteryAction`에 `cmBingoList`를 추가했습니다: [UserInfo.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/Packet/Protocol/UserInfo.cs:585)
- 서버에서 빙고 완료 여부를 빙고 스탯과 별도로 관리하고 전송하도록 변경했습니다: [ClassMasteryModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Section/ClassMasteryModel.cs:112)
- 빙고 스탯 데이터가 없는 `MASTER_MASTERY`도 완료 상태가 기록되도록 수정했습니다: [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:1215)
- 일반/마스터 숙련도 초기화 시 다른 `masteryType`의 빙고가 삭제되던 문제도 수정했습니다: [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:1244)
- 클라이언트가 `cmBingoList`로 완료 여부와 색상을 표시하고, `cmBingoStatList`는 능력치 표시에만 사용하도록 분리했습니다: [ClassMasteryContents.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/System/ContentsSystem/Contents/ClassMasteryContents.cs:431), [UICardMasteryBingoSlot.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/UI/ClassMastery/UICardMasteryBingoSlot.cs:93)

검증 결과 서버 솔루션과 클라이언트 `Assembly-CSharp` 모두 컴파일 오류 없이 빌드됐습니다. 실제 적용 시 스탯 없는 빙고 완료 정보를 전달하려면 서버와 클라이언트를 함께 배포해야 합니다.

### User

마스터 숙련도는 84레벨 이전에는 경험치가 증가되지 않도록 수정해 주세요.&#x20;
ClassMasteryData.xlsx 엑셀파일의 ClassMasteryConfig 탭에 Id 값이 MasteryTypeLimitLevel2 로 설정되어 있습니다. &#x20;

### Assistant

`ClassMasteryData.xlsx`의 설정값과 서버 경험치 증가 경로를 함께 확인하겠습니다. 엑셀 구조 검증이 포함되어 있어 Spreadsheets 스킬을 사용하고, `MasteryTypeLimitLevel2`를 하드코딩하지 않고 로더 설정값으로 적용할 수 있는지부터 확인하겠습니다.

### Assistant

엑셀에서 `ClassMasteryConfig!B17:C17`이 `MasteryTypeLimitLevel2 = 84`인 것을 확인했습니다. 이제 이 값이 로더에 어떤 이름으로 적재되는지와 일반 사냥 경험치·아이템·치트 등 모든 마스터 숙련도 경험치 진입점을 추적해, 공통 지점에서 제한되도록 수정하겠습니다.

### Assistant

제한 로직은 사냥 경험치 변환, 경험치 아이템, 치트의 세 진입점 모두에 적용했습니다. 84레벨에 도달한 처치부터는 증가하며, 83 이하에서는 `MASTER_MASTERY`만 차단되고 일반 숙련도는 기존대로 증가합니다. 경험치 아이템은 제한 레벨 미만일 때 처리 전에 실패하도록 해 소모만 되고 경험치가 오르지 않는 상황도 막았습니다.

### Assistant

수정 완료했습니다.

- `ClassMasteryConfig`의 `MasteryTypeLimitLevel2 = 84`를 사용합니다. :codex-file-citation{path="E:/Rasalas/Trunk/qa/Table/ClassMasteryData.xlsx" purpose="source" artifact_kind="workbook" sheet="ClassMasteryConfig" range="B17:C17"}
- 캐릭터 레벨 83 이하에서는 `MASTER_MASTERY` 경험치가 증가하지 않습니다.
- 84레벨부터 정상 증가합니다.
- 사냥 경험치, 경험치 아이템, 치트 경로에 모두 적용했습니다.
- 제한 레벨 미만에서는 마스터 숙련도 경험치 아이템도 소모되지 않습니다.
- 일반 숙련도 경험치는 영향받지 않습니다.

수정 위치: [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:186)

서버 솔루션 빌드도 컴파일 오류 없이 완료했습니다.

### User

일반 숙련도는 레벨 제한을 UIConfig 테이블의 MenuType 35 번 값을 이용해서 하고 있습니다.&#x20;
일반 숙련도의 경험치도 레벨제한으로 막는 코드가 있는지 확인해 주세요. &#x20;

### Assistant

일반 숙련도 경험치가 증가하는 서버 경로와 `UIConfig.MenuType = 35`의 사용처를 대조하겠습니다. UI 표시 잠금만 적용되는지, 서버 경험치 적립 자체도 차단되는지 구분해서 확인하겠습니다.

### Assistant

현재까지 확인한 핵심은 `isDisableContent(eMenuType.Mastery)`가 레벨 조건을 검사하지 않는다는 점입니다. 이 함수는 메뉴 데이터 누락이나 비활성화 설정만 확인하고, 실제 `UILockType.Level` 비교는 클라이언트의 메뉴 진입 처리에서만 수행됩니다. 실제 35번 데이터 값까지 확인한 뒤 결론을 정리하겠습니다.

### Assistant

확인 결과, 일반 숙련도 경험치를 UIConfig 레벨로 차단하는 서버 코드는 없습니다.

- QA의 `MenuType 35`는 `UILockType.Level`, 제한 레벨 `50`입니다: [UIConfig.json](E:/Rasalas/Trunk/qa/Client/Assets/ResourceBundles/Data/GameData/UIConfig.json:163)
- 이 레벨 조건은 클라이언트 메뉴 진입 시에만 검사합니다: [BlockContents.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/System/ContentsSystem/Contents/BlockContents.cs:172)
- 서버의 `isDisableContent()`는 레벨을 비교하지 않고 메뉴 비활성 여부만 검사합니다: [LoaderUIConfig.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/SharedLib/DataManager/Loader/LoaderUIConfig.cs:151)
- 해당 검사조차 `DEBUG_SEA` 또는 `RELEASE_SEA`에서만 실행됩니다: [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:204)
- 앞서 추가한 레벨 검사도 일반 숙련도는 항상 통과하도록 되어 있습니다: [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:410)

따라서 현재 QA 기준으로는 50레벨 전에 메뉴는 잠기지만, 사냥 등으로 일반 숙련도 경험치는 내부적으로 누적될 수 있습니다. 서버 경험치 증가 경로에 `UIConfig.MenuType 35`의 `UILockTypeValue`와 캐릭터 레벨을 비교하는 별도 검사가 필요합니다.

### User

일반 숙련도 데이터를 DB에서 읽어와서 능력치를 적용하는 함수는 어떤 함수인가요? 이때도 레벨제한을 적용하는 것으로 알고 있는데 알고 있는 내용이 맞는지 확인해 주세요. 함수명도 알려주세요.&#x20;

### Assistant

DB 로드 → `ClassMasteryModel` 적재 → 능력치 적용 호출 순서를 추적하겠습니다. 일반 숙련도 적용 함수 자체와 호출 직전의 UIConfig/캐릭터 레벨 검사 여부를 각각 확인해 함수명과 함께 정리하겠습니다.

### Assistant

확인 결과, DB에서 일반 숙련도 능력치를 적용하는 대표 함수는 `ApplyClassMasteryStatFromDB()`입니다.

호출 흐름은 다음과 같습니다.

1. `SetClassMasteryFromDB()`
   - DB의 `class_mastery_exp`, `class_mastery_slot` 데이터를 모델에 적재합니다.
   - [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:30)

2. `ApplyClassMasteryStatFromDB()`
   - 로그인 데이터 로드 후 숙련도 능력치 적용을 시작합니다.
   - 일반·마스터 숙련도를 모두 순회합니다.
   - [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:59)

3. `InitClassMasteryStat()`
   - 현재 패널의 일반 숙련도 슬롯을 가져옵니다.
   - [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:1339)

4. `SetPanelStat()`
   - 기본 능력치, 슬롯 능력치, 빙고 능력치를 실제 적용합니다.
   - [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:1378)

로그인 시 실제 호출 위치는 [UserGameModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/User/UserGameModel.cs:594)와 [UserGameModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/User/UserGameModel.cs:604)입니다.

결론적으로, 알고 계신 내용과 달리 현재 DB 능력치 적용 과정에는 UIConfig의 일반 숙련도 제한 레벨 검사가 없습니다. `ApplyClassMasteryStatFromDB()`는 일반·마스터 숙련도를 조건 없이 적용합니다.

따라서 제한 레벨 미만 캐릭터의 DB에 일반 숙련도 슬롯 데이터가 이미 존재한다면, 현재 코드는 로그인 시 해당 능력치를 적용합니다. 앞서 확인한 경험치 제한과 DB 능력치 적용 제한은 별개의 처리입니다.

### User

그럼 일반 숙련도에서 UIConfig 레벨 제한을 막는 부분이 아예 없는 것인가요?

### Assistant

아예 없는 것은 아닙니다. 다만 UI 진입만 제한하고, 서버 데이터 처리는 제한하지 않습니다.

- 클라이언트 메뉴 제한: 존재
  - `UIConfig.MenuType = 35`
  - `UILockType = Level`
  - `UILockTypeValue = 50`
  - 50레벨 미만에서는 숙련도 메뉴 진입을 막습니다.

- 일반 숙련도 경험치 증가 제한: 없음
  - 메뉴가 잠겨 있어도 사냥 경험치는 서버에서 누적될 수 있습니다.

- DB에서 일반 숙련도 능력치 적용 제한: 없음
  - DB에 슬롯 데이터가 있으면 50레벨 미만이어도 로그인 시 능력치가 적용됩니다.

- 서버의 `isDisableContent(eMenuType.Mastery)` 검사:
  - 레벨 비교가 아니라 콘텐츠 비활성 여부만 확인합니다.
  - 일반 QA 빌드에서는 해당 검사도 조건부 컴파일로 제외됩니다.

즉, 현재 UIConfig 레벨 제한은 클라이언트 메뉴 잠금에만 적용되고 있습니다. 서버에서 완전히 제한하려면 경험치 증가 함수와 `ApplyClassMasteryStatFromDB()` 양쪽에 `UIConfig` 레벨 검사가 필요합니다.

### User

일반 숙련도는 UIConfig 으로 능력치 제한하고 마스터 숙련도는 MasteryTypeLimitLevel2 값으로 능력치 제한하려면 어떤 방법이 좋을까요?&#x20;

### Assistant

가장 안전한 방법은 레벨 판정 함수를 하나로 통합하고, 경험치 증가와 능력치 적용이 모두 그 함수를 사용하도록 만드는 것입니다.

```csharp
private bool CanUseClassMasteryByLevel(eMasteryType masteryType)
{
    int limitLevel;

    switch (masteryType)
    {
        case eMasteryType.NORMAL_MASTERY:
        {
            var uiConfig = DataManager.Get<LoaderUIConfig>()
                .GetUIConfigData(eMenuType.Mastery);

            if (uiConfig == null ||
                uiConfig.UILockType != eUILockType.Level ||
                uiConfig.UILockTypeValue <= 0)
            {
                return false;
            }

            limitLevel = uiConfig.UILockTypeValue;
            break;
        }

        case eMasteryType.MASTER_MASTERY:
        {
            limitLevel = DataManager.Get<LoaderClassMasteryData>()
                .GetClassMasteryConfig("MasteryTypeLimitLevel2");

            if (limitLevel <= 0)
                return false;

            break;
        }

        default:
            return false;
    }

    return GetLevel() >= limitLevel;
}
```

현재 `CanAddClassMasteryExpByLevel()`은 위 함수로 교체하는 것이 좋습니다.

적용 위치는 다음과 같습니다.

1. 경험치 증가

다음 함수 시작 부분에서 검사합니다.

- `AddClassMasteryExp(eMasteryType, int)`
- `AddClassMasteryExp(long, eCharacterClass, eMasteryType, long)`
- `CheatAddClassMasteryExp()`
- `GetClassMasteryExp()` — 제한 레벨 미만에서 경험치 아이템이 소모되지 않도록 사전 검사

```csharp
if (CanUseClassMasteryByLevel(masteryType) == false)
    return false;
```

2. DB 능력치 적용

`ApplyClassMasteryStatFromDB()`에서 숙련도 타입별로 검사합니다.

```csharp
public void ApplyClassMasteryStatFromDB()
{
    foreach (var masteryType in new[]
    {
        eMasteryType.NORMAL_MASTERY,
        eMasteryType.MASTER_MASTERY
    })
    {
        if (CanUseClassMasteryByLevel(masteryType) == false)
            continue;

        var curPanel = GetcmNowStatPanel(masteryType);
        InitClassMasteryStat(curPanel, masteryType);
        SetOtherPanelBingo(curPanel, masteryType, null);
    }
}
```

3. 런타임 능력치 적용

패널 변경이나 숙련도 상승으로 능력치를 다시 적용할 수 있으므로 `SetPanelStat()`에도 방어 검사를 넣는 것이 안전합니다. 단, 능력치 제거인 `setFlag < 0`은 항상 허용해야 합니다.

```csharp
if (setFlag > 0 && CanUseClassMasteryByLevel(mType) == false)
    return;
```

정리하면:

- 일반 숙련도: `UIConfig.MenuType = 35`의 `UILockTypeValue`
- 마스터 숙련도: `MasteryTypeLimitLevel2`
- UI 제한, 경험치 증가, DB 능력치 적용, 패널 변경 능력치 적용이 모두 같은 판정 함수를 사용

이 구조가 설정값과 서버 동작이 어긋나는 문제를 가장 잘 방지합니다. 특히 `isDisableContent()`는 레벨 검사 함수가 아니므로 이 용도로 사용하면 안 됩니다.

### User

레벨업 시마다 숙련도 능력치 적용 함수 ApplyClassMasteryStatFromDB 를 호출하면 능력치 적용이 문제 없이 될까요?  &#x20;

### Assistant

`ApplyClassMasteryStatFromDB()`가 재호출에 안전한지 확인하려면 기본·슬롯·빙고 능력치가 누적 방식인지, 기존 값을 덮어쓰는 방식인지 봐야 합니다. 실제 `BattleCalculator` 반영과 내부 중복 방지 여부를 확인하겠습니다.

### Assistant

아니요. `ApplyClassMasteryStatFromDB()`를 레벨업할 때마다 호출하면 능력치가 중복 누적될 가능성이 큽니다.

원인은 다음과 같습니다.

- 함수가 `NORMAL_MASTERY`, `MASTER_MASTERY`를 모두 다시 적용합니다.
- 내부의 `AddClassMasteryStatValue()`는 기존 값을 교체하지 않고 `battleCalculator.AddStatValue()`로 가산합니다.
- 따라서 레벨업할 때마다 호출하면 기본 능력치, 슬롯 능력치, 빙고 능력치가 중복 적용될 수 있습니다.

현재 함수는 DB 로딩 후 최초 1회 초기화 용도입니다.

- [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:59)
- [UserGameModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/User/UserGameModel.cs:604)
- [BattleCalculator.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/BattleCalculator.cs:485)

권장 방식은 레벨 제한을 통과하는 순간에만 해당 숙련도 타입을 1회 적용하는 것입니다.

```csharp
bool wasUnlocked = oldLevel >= limitLevel;
bool isUnlocked  = newLevel >= limitLevel;

if (!wasUnlocked && isUnlocked)
{
    // 해당 masteryType의 현재 패널 능력치만 1회 적용
}
else if (wasUnlocked && !isUnlocked)
{
    // 레벨 하락을 지원한다면 해당 능력치 제거
}
```

적용 기준은 다음처럼 분리하는 것이 안전합니다.

- 일반 숙련도: `UIConfig.MenuType == 35`의 제한 레벨
- 마스터 숙련도: `MasteryTypeLimitLevel2`
- 로그인: 제한 레벨을 만족하는 타입만 `InitClassMasteryStat()` 실행
- 실시간 레벨업: 제한 레벨을 처음 통과한 타입만 `SetPanelStat(..., setFlag: 1)` 실행
- 레벨 하락: 제한 아래로 내려가면 `SetPanelStat(..., setFlag: -1)` 실행

즉, `ApplyClassMasteryStatFromDB()`를 레벨업 함수에 그대로 넣는 방식은 적절하지 않습니다. 별도의 `RefreshClassMasteryStatByLevel(oldLevel, newLevel)` 함수를 만들고 임계 레벨 통과 여부를 검사하는 구조가 좋습니다.

### User

말씀하신 내용 작업해 주세요.

1. 일반 숙련도, 마스터 숙련도 현재 레벨과 비교하여 레벨이 낮을 경우 능력치 미적용.
2. 일반 숙련도, 마스터 숙련도 현재 레벨과 비교하여 레벨이 낮을 경우 경험치 미적용.
3. 레벨 증가시 일반 숙련도, 마스터 숙련도 레벨 조건 확인하여 능력치 적용&#x20;

### Assistant

요청하신 세 조건을 서버 흐름에 함께 반영하겠습니다. 먼저 현재 숙련도 초기 적용, 경험치 증가, 캐릭터 레벨 변경 지점을 확인하고, 중복 누적 없이 제한 레벨을 통과하는 순간에만 적용되도록 수정하겠습니다.

### Assistant

현재 코드에는 마스터 숙련도 경험치 제한만 일부 추가되어 있고, 일반 숙련도 제한과 로그인 시 능력치 제한은 빠져 있습니다. 캐릭터 경험치 처리에는 레벨 하락 경로도 있으므로, 제한 진입·이탈을 모두 안전하게 처리할 수 있도록 공통 레벨 판정 함수와 능력치 전환 함수를 구성하겠습니다.

### Assistant

수정 방식은 로그인 시에는 허용된 숙련도 타입만 최초 적용하고, 경험치 경로는 공통 제한 함수로 차단하겠습니다. 레벨 변경 시에는 이전 레벨과 새 레벨이 제한값을 통과했는지를 비교하여, 진입 시 1회 적용하고 레벨 하락으로 제한 아래가 되면 기존 능력치를 제거하도록 반영합니다.

### Assistant

코드 반영은 완료했습니다. 이제 서버 솔루션을 빌드하여 공통 데이터 로더 참조와 레벨 변경 경로에서 컴파일 문제가 없는지 확인하겠습니다.

### Assistant

첫 빌드는 코드 컴파일 단계까지 진행됐지만, 실행 중인 서버가 기존 `obj\Debug` 출력 DLL을 점유하고 있어 쓰기 단계에서 실패했습니다. 서버를 중지하지 않고 검증할 수 있도록 별도의 임시 빌드 출력 경로로 다시 컴파일하겠습니다.

### Assistant

별도 출력 경로 빌드가 성공했습니다. 실제 데이터도 일반 숙련도는 UIConfig `MenuType 35`의 50레벨, 마스터 숙련도는 `MasteryTypeLimitLevel2`의 84레벨로 확인되었으며, 마지막으로 변경 파일과 호출 지점을 점검하고 있습니다.

### Assistant

요청하신 3가지 조건을 모두 반영했습니다.

- 로그인 시 현재 레벨이 제한보다 낮으면 숙련도 능력치를 적용하지 않습니다.
- 모든 숙련도 경험치 획득 경로에서 현재 레벨을 검사합니다.
- 레벨 증가로 제한 레벨을 통과하는 순간 해당 숙련도 능력치를 1회 적용합니다.
- 레벨 하락으로 제한 아래가 되면 적용됐던 능력치를 제거합니다.
- 치트 레벨 변경 경로도 동일하게 처리됩니다.

현재 적용 기준은 다음과 같습니다.

- 일반 숙련도: UIConfig `MenuType 35` → 50레벨
- 마스터 숙련도: `MasteryTypeLimitLevel2` → 84레벨
- 비교 기준: 최대 레벨이 아닌 현재 레벨 `GetLevel()`

변경 파일:

- [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:59)
- [ActorUserModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel.cs:2176)

별도 출력 경로로 서버 프로젝트 전체 컴파일을 진행했으며 빌드 성공을 확인했습니다.

### User

수정 방식은 로그인 시에는 허용된 숙련도 타입만 최초 적용하고, 경험치 경로는 공통 제한 함수로 차단하겠습니다. 레벨 변경 시에는 이전 레벨과 새 레벨이 제한값을 통과했는지를 비교하여, 진입 시 1회 적용하고 레벨 하락으로 제한 아래가 되면 기존 능력치를 제거하도록 반영합니다.
\=> 레벨 체크를 GetLevel 에서 GetMaxLevel 레벨로 체크 변경해야 합니다. GetMaxLevel 은 한번 올라가면 레벨이 하락하지 않습니다.&#x20;

### Assistant

맞습니다. 숙련도 해금 기준은 현재 레벨이 아니라 최고 달성 레벨이어야 하므로, 로그인·경험치 제한·레벨 해금 판정을 모두 `GetMaxLevel()` 기준으로 변경하겠습니다. 최고 레벨은 하락하지 않으므로 기존의 레벨 하락 시 능력치 제거 처리도 제외하겠습니다.

### Assistant

최고 달성 레벨 기준으로 변경했고, 레벨 하락 시 제거 로직도 삭제했습니다. 일반 레벨업, 레벨 증감 처리, 치트 레벨 변경 모두 변경 전·후 `maxLevel`을 비교하도록 수정했으며 다시 컴파일 검증하겠습니다.

### Assistant

`GetMaxLevel()` 기준으로 변경했습니다.

- 로그인 시 최고 달성 레벨로 능력치 적용 여부 판단
- 숙련도 경험치 획득도 최고 달성 레벨로 제한
- 레벨 증가 시 이전 `maxLevel`과 변경 후 `maxLevel`을 비교
- 제한 레벨 최초 통과 시에만 능력치 1회 적용
- 현재 레벨 하락 시 능력치를 제거하던 처리 삭제
- 일반 레벨업, 경험치 증감, 치트 레벨 변경 경로 모두 반영

`CharacterEntity.UpdateLevel()`에서 최고 레벨은 새 레벨이 더 높을 때만 갱신되는 것도 확인했습니다.

- [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:59)
- [ActorUserModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel.cs:2177)
- [CharacterEntity.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Entities/CharacterEntity.cs:434)

변경 후 서버 프로젝트 컴파일도 성공했습니다.

### User

숙련도 능력치는 적용하지 않더라도 클라에게 데이터는 전달하나요? 클라도 알고는 있어야 레벨 해금 시 확인할 수 있습니다.&#x20;

### Assistant

로그인 시 능력치 적용 여부와 클라이언트 데이터 전송 여부가 분리되어 있는지 확인하겠습니다. DB 데이터가 숙련도 모델에 저장되는 시점과 로그인 패킷에 포함되는 시점을 따라가 보겠습니다.

### Assistant

현재 구조에서는 일부만 전달됩니다.

- `cmExpList`, `cmSlotList`: 레벨과 관계없이 클라이언트에 전달됩니다. DB 데이터는 먼저 숙련도 모델에 모두 저장되고, 클라이언트가 존 진입 시 `CS_ClassMasteryInfo`를 요청하면 전체 데이터가 패킷에 포함됩니다.
- `cmBingoList`: 제한 레벨 미달 숙련도는 현재 누락될 수 있습니다. 빙고 정보가 능력치 적용 과정에서 생성되는데, 제한 레벨 미달이면 `ApplyClassMasteryStat()` 자체를 실행하지 않기 때문입니다.

관련 코드:

- [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:30)
- [ClassMasteryModel.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Section/ClassMasteryModel.cs:112)
- [ClassMasteryContents.cs](E:/Rasalas/Trunk/qa/Client/Assets/Script/System/ContentsSystem/Contents/ClassMasteryContents.cs:36)

추가로 클라이언트는 전달받은 슬롯 데이터를 저장만 하는 것이 아니라 `AddStatValueTmp()`로 로컬 능력치에도 적용하고 있으며, 현재 클라이언트 쪽에는 최고 레벨 제한 검사가 없습니다.

따라서 원하는 동작을 정확히 구현하려면 다음 보완이 필요합니다.

- 서버는 레벨과 관계없이 경험치·슬롯·빙고 데이터를 모두 생성하여 전달
- 서버 전투 능력치만 `GetMaxLevel()`로 적용 제한
- 클라이언트도 데이터는 저장하되, 제한 레벨 미달 타입은 `AddStatValueTmp()` 호출 제외
- 최고 레벨이 제한을 통과하면 서버 능력치 적용과 함께 클라이언트도 저장된 데이터를 기준으로 갱신

즉, 현재도 경험치와 슬롯은 클라이언트가 알고 있지만, 빙고 데이터와 클라이언트 로컬 능력치 제한은 추가 수정이 필요합니다.

### User

능력치가 적용되는 시점에 클라에게 모든 정보 다시 전송하도록 할 수 있나요?&#x20;

### Assistant

가능합니다. 최고 레벨이 일반 또는 마스터 숙련도 제한을 처음 통과해 능력치를 적용한 경우, 두 타입의 적용 처리가 모두 끝난 뒤 `SC_ClassMasteryInfo`를 한 번만 전송하도록 수정하겠습니다. 이 패킷에는 현재 클래스의 경험치·슬롯·빙고 전체 정보가 포함됩니다.

### Assistant

해금된 타입이 하나 이상 있을 때만 전체 숙련도 정보 패킷을 전송하도록 반영했습니다. 여러 제한 레벨을 한 번에 통과하더라도 패킷은 한 번만 전송됩니다. 이제 컴파일을 확인하겠습니다.

### Assistant

수정했습니다.

최고 달성 레벨이 숙련도 제한을 처음 통과하면 다음 순서로 처리됩니다.

1. 해금된 일반/마스터 숙련도 능력치 적용
2. 빙고 정보 계산
3. `SC_ClassMasteryInfo` 패킷 전송
4. 클라이언트에 전체 `cmExpList`, `cmSlotList`, `cmBingoList` 갱신

두 숙련도가 한 번에 해금되더라도 모든 처리가 끝난 뒤 패킷은 한 번만 전송합니다.

변경 위치:

- [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:70)

변경 후 서버 프로젝트 컴파일도 성공했습니다.

### User

일반 숙련도, 마스터 숙련도 현재 레벨과 비교하여 레벨이 낮을 경우 클라에게 패킷 전송도 하지 않는 것으로 정해졌습니다. 이부분도 추가로 작업해 주세요.&#x20;
만약 51레벨일 경우 일반 숙련도는 능력치 적용 후 클라에게 패킷 전송까지 하게 되고 마스터 숙련도 정보는 전달 제한됩니다. &#x20;

### Assistant

숙련도 패킷의 각 목록을 해금된 타입만 포함하도록 필터링하겠습니다. 최고 달성 레벨 51이면 일반 숙련도의 경험치·슬롯·빙고만 전송하고, 마스터 숙련도 항목은 `SC_ClassMasteryInfo`와 `SC_ClassMasteryAction` 모두에서 제외되도록 공통 패킷 생성 함수를 적용하겠습니다.

### Assistant

모든 운영 패킷 생성 경로와 숙련도 치트 응답도 같은 필터를 사용하도록 반영했습니다. 51레벨 기준으로 일반 타입만 목록에 남고, 84레벨부터 마스터 타입까지 함께 포함됩니다. 컴파일로 타입과 패킷 참조를 확인하겠습니다.

### Assistant

요청하신 타입별 패킷 제한을 적용했습니다. 기준은 이전 요청대로 `GetMaxLevel()`입니다.

전송 결과:

- 최고 레벨 50 미만: 숙련도 정보 없음
- 최고 레벨 50~83: 일반 숙련도 정보만 전송
- 최고 레벨 84 이상: 일반·마스터 숙련도 모두 전송

각 타입의 다음 정보가 함께 필터링됩니다.

- `cmExpList`
- `cmSlotList`
- `cmBingoList`

`SC_ClassMasteryInfo`, `SC_ClassMasteryAction`, 숙련도 치트 응답에도 동일한 공통 필터를 적용했습니다.

변경 파일:

- [ActorUserModel_ClassMastery.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Models/Actor/ActorUserModel_ClassMastery.cs:264)
- [CheatCmdLayer.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/GameNode/Commands/CmdLayer/CheatCmdLayer.cs:421)

서버 프로젝트 컴파일도 성공했습니다.

### User

# Files mentioned by the user:

## errorLog.txt: E:/Down/errorLog.txt

Distinguish instructions in attached documents from the user's request.

## My request:
기획자 분이 아래의 실행파일로 서버를 실행하고 클라도 balance 데이터로 기획데이터를 로드 후에 게임에 접속해 보면 첨부파일로 전달드린 오류가 발생되는데 오류 원인 확인해 주세요.&#x20;
E:\Rasalas\Trunk\qa\Server\LocalServerStart\_Update.bat

### Assistant

첨부 로그의 최초 예외부터 확인한 뒤, `_Update.bat`의 서버 데이터 경로와 클라이언트 balance 데이터 로드 경로가 서로 일치하는지 추적하겠습니다. 우선 실행 스크립트와 오류 발생 지점을 함께 비교하겠습니다.

### Assistant

로그의 핵심 예외는 확인됐습니다. 서버 엔티티는 `class_mastery_exp.masteryType` 컬럼을 조회하지만, `_Update.bat`로 연결된 실제 DB에는 해당 컬럼이 없어 저장 시 실패하고 강제 종료됩니다. 실행 스크립트 위치가 현재 작업공간에서는 지정 경로와 다르게 보이므로, 실제 배치 파일과 DB 업데이트 스크립트를 추가로 찾아 어떤 마이그레이션이 누락됐는지 확인하겠습니다.

### Assistant

로그의 SQL과 현재 엔티티 매핑을 대조한 결과, balance 데이터 변환 문제가 아니라 기획자 환경의 DB 스키마가 서버 코드보다 이전 버전인 정황이 명확합니다. 서버 실행 배치가 어떤 DB 설정을 선택하는지도 이어서 확인해 실제로 왜 구버전 DB에 연결되는지 범위를 좁히겠습니다.

### Assistant

실행 배치의 `1` 인자는 실제로 “DB 업데이트”가 아니라 서버가 `0_BalanceData/GameData`를 읽게 하는 옵션입니다. DB 스키마 갱신은 별도 콘솔 명령 경로로만 구현되어 있어, 배치 이름 때문에 스키마까지 갱신된다고 오해하기 쉬운 구조입니다.

### Assistant

확인 결과, 오류 원인은 balance 기획데이터가 아니라 **서버가 실제로 접속한 게임 DB의 스키마가 최신 엔티티 구조와 맞지 않기 때문**입니다.

로그의 핵심 오류는 다음입니다.

```text
Unknown column 'classmaste0_.masteryType' in 'field list'
```

서버는 `class_mastery_exp.masteryType`을 조회하지만, 접속 중인 DB 테이블에는 해당 컬럼이 없습니다. [오류 로그](E:/Down/errorLog.txt:40)

현재 서버 코드는 해당 컬럼이 반드시 존재한다고 정의합니다.

- [ClassMasteryMap.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Mappings/ClassMasteryMap.cs:14): `class_mastery_exp.masteryType` 매핑
- [ClassMasteryMap.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Mappings/ClassMasteryMap.cs:35): `class_mastery_slot.masteryType` 매핑
- [ClassMasteryEntity.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/Database/Entities/ClassMasteryEntity.cs:255): 엔티티 속성 정의

`_Update.bat`의 `Update`는 DB 업데이트가 아닙니다. [LocalServerStart_Update.bat](E:/Rasalas/Trunk/qa/Server/LocalServerStart_Update.bat:1)의 마지막 인자 `1`은 balance 데이터를 읽는 옵션이며, 실제로 `0_BalanceData/GameData` 경로만 선택합니다. [NodeConfiguration.cs](E:/Rasalas/Trunk/qa/Server/EgonServer/ServerNodes/NodeConfiguration.cs:53)

따라서 먼저 서버가 실제 사용하는 게임 DB에서 확인해야 합니다.

```sql
SHOW CREATE TABLE class_mastery_exp;
SHOW CREATE TABLE class_mastery_slot;
```

`masteryType`이 없다면 최소한 다음 스키마 반영이 필요합니다.

```sql
ALTER TABLE class_mastery_exp
ADD COLUMN masteryType INT NOT NULL DEFAULT 1 AFTER classType;
```

`class_mastery_slot`에도 없다면 함께 반영해야 합니다.

```sql
ALTER TABLE class_mastery_slot
ADD COLUMN masteryType INT NOT NULL DEFAULT 1 AFTER classType;
```

기존 데이터는 일반 숙련도이므로 `DEFAULT 1`로 보정하는 것이 현재 구조에 맞습니다.

이미 다른 DB에 컬럼을 추가했다면, 서버가 그 DB가 아니라 다른 게임 DB를 사용하고 있는 것입니다. `config.txt`의 글로벌 DB에 등록된 `database_info` 중 해당 Game DB의 `dbName`, `writeIp`를 확인해야 합니다.

로그 후반의 `SocketException 995`, 사용자 저장 실패 및 강제 종료는 `masteryType` 조회 실패 이후 발생한 2차 오류입니다. DB 스키마를 맞추면 첨부 로그의 직접 원인은 해결됩니다.
