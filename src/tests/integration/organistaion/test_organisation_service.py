from pydantic import ValidationError
import pytest
from sqlalchemy.orm import Session

from app.common.exceptions import ModelNotFoundError
from app.db.models import Building as BuildingModel
from app.db.models import Organization as OrganizationModel
from app.db.repositories.organization import SQLAlchemyOrganizationRepository
from app.domain.organization.schemas import OrganizationCreate
from app.domain.organization.services import OrganizationService


@pytest.fixture
def organization_service(db_session: Session) -> OrganizationService:
    repository = SQLAlchemyOrganizationRepository(db_session)
    return OrganizationService(repository)


def test_get_organization_by_id(
    organization_service: OrganizationService,
    test_organization: OrganizationModel,
):
    org_id = test_organization.id
    result = organization_service.get_organization_by_id(org_id)

    assert result is not None
    assert result.id == org_id
    assert result.name == 'ООО Рога и Копыта'
    assert result.building_id == test_organization.building_id
    assert result.building.address == 'ул. Ленина, 1, Новосибирск'
    assert result.building.geolocation is not None
    assert result.building.geolocation.longitude == pytest.approx(82.920430)
    assert result.building.geolocation.latitude == pytest.approx(55.030204)


def test_get_organization_by_id_with_phones(
    organization_service: OrganizationService, test_organization_with_phones: OrganizationModel
):
    """✅ Получение организации с телефонами"""
    # Act
    result = organization_service.get_organization_by_id(test_organization_with_phones.id)

    # Assert
    assert len(result.phones) == 2
    assert '+79991234567' in result.phones
    assert '+79991234568' in result.phones


def test_get_organization_by_id_not_found(organization_service: OrganizationService):
    """Организация не найдена - ошибка"""
    # Act & Assert
    with pytest.raises(ModelNotFoundError) as exc_info:
        organization_service.get_organization_by_id(999999)


def test_create_organization_success(
    organization_service: OrganizationService, test_building_1: BuildingModel
):
    """Создание организации - успех"""
    # Arrange
    org_data = OrganizationCreate(
        name='ООО Новая Компания', building_id=test_building_1.id, phones=[], activities=[]
    )

    # Act
    result = organization_service.create_organization(org_data)

    # Assert
    assert result.id is not None
    assert result.name == 'ООО Новая Компания'
    assert result.building_id == test_building_1.id


def test_create_organization_with_empty_name(
    organization_service: OrganizationService, test_building_1: BuildingModel
):
    """Создание с пустым именем - ошибка валидации"""
    with pytest.raises(ValidationError) as exc_info:
        OrganizationCreate(name='', building_id=1, phones=[], activities=[])

    assert 'name' in str(exc_info.value)


def test_create_organization_with_invalid_building(organization_service: OrganizationService):
    """Создание с несуществующим зданием - FK ошибка"""
    # Arrange
    org_data = OrganizationCreate(name='ООО Тест', building_id=999999, phones=[], activities=[])

    # Act & Assert
    with pytest.raises(ModelNotFoundError):  # Foreign key constraint
        organization_service.create_organization(org_data)


def test_get_organizations_by_name_single_result(
    organization_service: OrganizationService, multiple_test_organizations: list[OrganizationModel]
):
    """Поиск по имени - один результат"""
    # Act
    results = organization_service.get_organizations_by_name('Альфа')

    # Assert
    assert len(results) == 1
    assert results[0].name == 'ООО Альфа Трейд'


def test_get_organizations_by_name_multiple_results(
    organization_service: OrganizationService, multiple_test_organizations: list[OrganizationModel]
):
    """Поиск по имени - множественные результаты"""
    # Act
    results = organization_service.get_organizations_by_name('ООО')

    # Assert
    assert len(results) >= 3
    org_names = [org.name for org in results]
    assert 'ООО Альфа Трейд' in org_names
    assert 'ООО Бета Групп' in org_names
    assert 'ООО Гамма Сервис' in org_names


def test_get_organizations_by_name_case_insensitive(
    organization_service: OrganizationService, multiple_test_organizations: list[OrganizationModel]
):
    """Поиск без учёта регистра"""
    # Act
    results_lower = organization_service.get_organizations_by_name('альфа')
    results_upper = organization_service.get_organizations_by_name('АЛЬФА')
    results_mixed = organization_service.get_organizations_by_name('АлЬфА')

    # Assert
    assert len(results_lower) == 1
    assert len(results_upper) == 1
    assert len(results_mixed) == 1
    assert results_lower[0].id == results_upper[0].id == results_mixed[0].id


def test_get_organizations_by_name_partial_match(
    organization_service: OrganizationService, multiple_test_organizations: list[OrganizationModel]
):
    """Частичное совпадение имени"""
    # Act
    results = organization_service.get_organizations_by_name('Трей')

    # Assert
    assert len(results) == 1
    assert 'Трейд' in results[0].name


def test_get_organizations_by_name_not_found(
    organization_service: OrganizationService, multiple_test_organizations: list[OrganizationModel]
):
    """Поиск не дал результатов"""
    # Act
    results = organization_service.get_organizations_by_name('НесуществующаяКомпания123')

    # Assert
    assert len(results) == 0
    assert isinstance(results, list)


def test_get_organizations_by_name_empty_query(
    organization_service: OrganizationService, multiple_test_organizations: list[OrganizationModel]
):
    """✅ Пустой поисковый запрос - возвращает всё"""
    # Act
    results = organization_service.get_organizations_by_name('')

    # Assert
    assert len(results) >= 4  # Все созданные организации


def test_get_organizations_by_building(
    organization_service: OrganizationService,
    test_building_1: BuildingModel,
    test_building_2: BuildingModel,
    multiple_test_organizations: list[OrganizationModel],
):
    """✅ Разные здания возвращают разные организации"""
    # Act
    results_building_1 = organization_service.get_organizations_by_building(test_building_1.id)
    results_building_2 = organization_service.get_organizations_by_building(test_building_2.id)

    # Assert
    assert len(results_building_1) >= 3
    assert len(results_building_2) >= 1

    # ID организаций не пересекаются
    ids_1 = {org.id for org in results_building_1}
    ids_2 = {org.id for org in results_building_2}
    assert ids_1.isdisjoint(ids_2)


def test_get_organizations_by_building_empty(organization_service: OrganizationService):
    """✅ Здание без организаций - пустой список"""
    # Act
    results = organization_service.get_organizations_by_building(999999)

    # Assert
    assert len(results) == 0
    assert isinstance(results, list)


def test_get_organizations_by_activity_recursive_parent(
    organization_service: OrganizationService, organizations_with_activities_hierarchy: dict
):
    """
    РЕКУРСИВНЫЙ ПОИСК: поиск по родительской activity
    должен вернуть все организации с дочерними activities!

    Иерархия:
    Торговля (parent) ← ищем по этой
    ├── Торговля продуктами (child_1)
    │   └── Торговля овощами (grandchild)
    └── Торговля одеждой (child_2)

    Должны вернуться ВСЕ 4 организации:
    - ООО ТоргХолдинг (имеет parent)
    - ООО Продукты Плюс (имеет child_1)
    - ООО Модный Дом (имеет child_2)
    - ИП Овощной Рай (имеет grandchild)
    """
    data = organizations_with_activities_hierarchy

    # Act - ищем по РОДИТЕЛЬСКОЙ activity "Торговля"
    results = organization_service.get_organizations_by_activity(data['activity_parent'].id)

    # Assert - должны вернуться ВСЕ организации
    assert len(results) == 4, 'Должны вернуться все 4 организации в иерархии'

    org_ids = {org.id for org in results}
    assert data['parent'].id in org_ids, 'Организация с parent activity'
    assert data['child_1'].id in org_ids, 'Организация с child_1 activity'
    assert data['child_2'].id in org_ids, 'Организация с child_2 activity'
    assert data['grandchild'].id in org_ids, 'Организация с grandchild activity'


def test_get_organizations_by_activity_recursive_middle_level(
    organization_service: OrganizationService, organizations_with_activities_hierarchy: dict
):
    """
    ✅ РЕКУРСИВНЫЙ ПОИСК: поиск по средней activity

    Иерархия:
    Торговля (parent)
    ├── Торговля продуктами (child_1) ← ищем по этой
    │   └── Торговля овощами (grandchild)
    └── Торговля одеждой (child_2)

    Должны вернуться 2 организации:
    - ООО Продукты Плюс (имеет child_1)
    - ИП Овощной Рай (имеет grandchild - потомок child_1)
    """
    data = organizations_with_activities_hierarchy

    # Act - ищем по "Торговля продуктами"
    results = organization_service.get_organizations_by_activity(data['activity_child_1'].id)

    # Assert
    assert len(results) == 2, 'Должны вернуться 2 организации'

    org_ids = {org.id for org in results}
    assert data['child_1'].id in org_ids
    assert data['grandchild'].id in org_ids

    # НЕ должны вернуться другие
    assert data['parent'].id not in org_ids
    assert data['child_2'].id not in org_ids


def test_get_organizations_by_activity_leaf_node(
    organization_service: OrganizationService, organizations_with_activities_hierarchy: dict
):
    """
    ✅ Поиск по листовой activity (без детей)

    Торговля одеждой (child_2) ← ищем по этой (нет детей)

    Должна вернуться только 1 организация
    """
    data = organizations_with_activities_hierarchy

    # Act
    results = organization_service.get_organizations_by_activity(data['activity_child_2'].id)

    # Assert
    assert len(results) == 1
    assert results[0].id == data['child_2'].id


def test_get_organizations_by_activity_not_found(organization_service: OrganizationService):
    """✅ Activity без организаций"""
    # Act
    results = organization_service.get_organizations_by_activity(999999)

    # Assert
    assert len(results) == 0
    assert isinstance(results, list)


def test_get_organizations_by_geolocation_inside_bounds(
    organization_service: OrganizationService,
    test_organization: OrganizationModel,
    test_building_1: BuildingModel,
):
    """✅ Геопоиск - организации внутри bbox"""
    # Arrange - bounding box вокруг Новосибирска
    # test_building: Point(82.920430, 55.030204)
    min_lat = 55.0
    max_lat = 55.1
    min_lon = 82.9
    max_lon = 83.0

    # Act
    results = organization_service.get_organizations_by_geolocation(
        min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon
    )

    # Assert
    assert len(results) >= 1
    org_ids = {org.id for org in results}
    assert test_organization.id in org_ids


def test_get_organizations_by_geolocation_multiple_results(
    organization_service: OrganizationService, multiple_test_organizations: list[OrganizationModel]
):
    """✅ Геопоиск - множественные результаты в одном bbox"""
    # Arrange
    min_lat = 55.0
    max_lat = 55.1
    min_lon = 82.9
    max_lon = 83.0

    # Act
    results = organization_service.get_organizations_by_geolocation(
        min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon
    )

    # Assert
    assert len(results) >= 4  # Все организации в двух зданиях Новосибирска


def test_get_organizations_by_geolocation_outside_bounds(
    organization_service: OrganizationService,
    test_organization: OrganizationModel,
    test_building_3: BuildingModel,
):
    """✅ Геопоиск - bbox не включает организации"""
    # Arrange - bbox вдали от всех зданий
    min_lat = 50.0
    max_lat = 51.0
    min_lon = 70.0
    max_lon = 71.0

    # Act
    results = organization_service.get_organizations_by_geolocation(
        min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon
    )

    # Assert
    assert len(results) == 0


def test_get_organizations_by_geolocation_exact_bounds(
    organization_service: OrganizationService,
    test_building_3: BuildingModel,
    db_session: Session,
):
    """✅ Геопоиск - точные границы вокруг одного здания"""
    # Arrange - создаём организацию в далёком здании
    org = OrganizationModel(name='ООО Далёкая', building_id=test_building_3.id)
    db_session.add(org)
    db_session.flush()

    # Bbox точно вокруг точки (80.0, 53.0)
    min_lat = 52.9
    max_lat = 53.1
    min_lon = 79.9
    max_lon = 80.1

    # Act
    results = organization_service.get_organizations_by_geolocation(
        min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon
    )

    # Assert
    assert len(results) == 1
    assert results[0].name == 'ООО Далёкая'


def test_get_organizations_by_geolocation_empty(organization_service: OrganizationService):
    """✅ Геопоиск - пустой регион"""
    # Arrange - bbox в океане
    min_lat = 0.0
    max_lat = 1.0
    min_lon = 0.0
    max_lon = 1.0

    # Act
    results = organization_service.get_organizations_by_geolocation(
        min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon
    )

    # Assert
    assert len(results) == 0
    assert isinstance(results, list)
