import os
import sys

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from geoalchemy2.shape import from_shape
from shapely import Point
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

TEST_DATABASE_URL = 'postgresql://postgres:postgres@localhost:5433/test_secunda_thp'

os.environ.update(
    {
        'DATABASE_URL': TEST_DATABASE_URL,
    },
)

if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db.db import create_database_engine, create_session_factory
from app.db.models import Activity as ActivityModel
from app.db.models import Building as BuildingModel
from app.db.models import Organization as OrganizationModel
from app.db.models import OrganizationPhone as OrganizationPhoneModel


@pytest.fixture(scope='session', autouse=True)
def apply_migrations():
    cfg = Config('alembic.ini')
    cfg.set_main_option('sqlalchemy_url', TEST_DATABASE_URL)
    command.upgrade(cfg, 'head')
    yield
    command.downgrade(cfg, 'base')


@pytest_asyncio.fixture
async def test_engine():
    engine = create_database_engine(pool_pre_ping=False)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(test_engine: AsyncEngine):
    return create_session_factory(test_engine)


@pytest_asyncio.fixture
async def db_session(session_factory: async_sessionmaker[AsyncSession]):
    """Создаёт асинхронную сессию с автоматическим откатом после теста."""
    async with session_factory() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_building_1(db_session: AsyncSession) -> BuildingModel:
    """Создаёт тестовое здание 1."""
    point = Point(82.920430, 55.030204)  # lon, lat

    building = BuildingModel(
        address='ул. Ленина, 1, Новосибирск',
        geolocation=from_shape(point, srid=4326)
    )

    db_session.add(building)
    await db_session.flush()
    await db_session.refresh(building)

    return building


@pytest_asyncio.fixture
async def test_building_2(db_session: AsyncSession) -> BuildingModel:
    """Создаёт тестовое здание 2."""
    point = Point(82.925430, 55.035204)

    building = BuildingModel(
        address='ул. Ленина, 2, Новосибирск',
        geolocation=from_shape(point, srid=4326)
    )

    db_session.add(building)
    await db_session.flush()
    await db_session.refresh(building)

    return building


@pytest_asyncio.fixture
async def test_building_3(db_session: AsyncSession) -> BuildingModel:
    """Создаёт тестовое здание 3 (Томск)."""
    point = Point(80.0, 53.0)  # Далеко от Новосибирска

    building = BuildingModel(
        address='г. Томск, ул. Тестовая, 1',
        geolocation=from_shape(point, srid=4326)
    )

    db_session.add(building)
    await db_session.flush()
    await db_session.refresh(building)

    return building


@pytest_asyncio.fixture
async def test_activity_parent(db_session: AsyncSession) -> ActivityModel:
    activity = ActivityModel(
        name='Торговля',
        parent_id=None,
    )

    db_session.add(activity)
    await db_session.flush()
    await db_session.refresh(activity)

    return activity


@pytest_asyncio.fixture
async def test_activity_child_1(
    db_session: AsyncSession,
    test_activity_parent: ActivityModel,
) -> ActivityModel:
    activity = ActivityModel(
        name='Торговля продуктами',
        parent_id=test_activity_parent.id,
    )

    db_session.add(activity)
    await db_session.flush()
    await db_session.refresh(activity)

    return activity


@pytest_asyncio.fixture
async def test_activity_child_2(
    db_session: AsyncSession,
    test_activity_parent: ActivityModel,
) -> ActivityModel:
    activity = ActivityModel(
        name='Торговля одеждой',
        parent_id=test_activity_parent.id,
    )

    db_session.add(activity)
    await db_session.flush()
    await db_session.refresh(activity)

    return activity


@pytest_asyncio.fixture
async def test_activity_grandchild(
    db_session: AsyncSession,
    test_activity_child_1: ActivityModel,
) -> ActivityModel:
    activity = ActivityModel(
        name='Торговля овощами',
        parent_id=test_activity_child_1.id,
    )

    db_session.add(activity)
    await db_session.flush()
    await db_session.refresh(activity)

    return activity


@pytest_asyncio.fixture
async def test_organization(
    db_session: AsyncSession,
    test_building_1: BuildingModel,
) -> OrganizationModel:
    """Создаёт тестовую организацию."""
    org = OrganizationModel(
        name='ООО Рога и Копыта',
        building_id=test_building_1.id,
    )

    db_session.add(org)
    await db_session.flush()
    await db_session.refresh(org)

    return org


@pytest_asyncio.fixture
async def test_organization_with_phones(
    db_session: AsyncSession,
    test_organization: OrganizationModel,
) -> OrganizationModel:
    """Создаёт организацию с телефонами."""
    phones = [
        OrganizationPhoneModel(
            organization_id=test_organization.id,
            phone_number='+79991234567'
        ),
        OrganizationPhoneModel(
            organization_id=test_organization.id,
            phone_number='+79991234568'
        ),
    ]

    db_session.add_all(phones)
    await db_session.flush()
    await db_session.refresh(test_organization)

    return test_organization


@pytest_asyncio.fixture
async def multiple_test_organizations(
    db_session: AsyncSession,
    test_building_1: BuildingModel,
    test_building_2: BuildingModel,
) -> list[OrganizationModel]:
    """Создаёт несколько тестовых организаций."""
    orgs = [
        OrganizationModel(name='ООО Альфа Трейд', building_id=test_building_1.id),
        OrganizationModel(name='ООО Бета Групп', building_id=test_building_1.id),
        OrganizationModel(name='ООО Гамма Сервис', building_id=test_building_2.id),
        OrganizationModel(name='ИП Иванов', building_id=test_building_1.id),
    ]

    db_session.add_all(orgs)
    await db_session.flush()

    for org in orgs:
        await db_session.refresh(org)

    return orgs


@pytest_asyncio.fixture
async def organizations_with_activities_hierarchy(
    db_session: AsyncSession,
    test_building_1: BuildingModel,
    test_activity_parent: ActivityModel,
    test_activity_child_1: ActivityModel,
    test_activity_child_2: ActivityModel,
    test_activity_grandchild: ActivityModel,
) -> dict:
    """Создаёт организации с иерархией активностей."""
    # Org с родительской activity
    org_parent = OrganizationModel(
        name='ООО ТоргХолдинг',
        building_id=test_building_1.id,
    )
    org_parent.activities.append(test_activity_parent)

    # Org с child activity 1
    org_child_1 = OrganizationModel(
        name='ООО Продукты Плюс',
        building_id=test_building_1.id,
    )
    org_child_1.activities.append(test_activity_child_1)

    # Org с child activity 2
    org_child_2 = OrganizationModel(
        name='ООО Модный Дом',
        building_id=test_building_1.id,
    )
    org_child_2.activities.append(test_activity_child_2)

    # Org с grandchild activity
    org_grandchild = OrganizationModel(
        name='ИП Овощной Рай',
        building_id=test_building_1.id,
    )
    org_grandchild.activities.append(test_activity_grandchild)

    db_session.add_all([org_parent, org_child_1, org_child_2, org_grandchild])
    await db_session.flush()

    for org in [org_parent, org_child_1, org_child_2, org_grandchild]:
        await db_session.refresh(org, ['activities'])

    return {
        'parent': org_parent,
        'child_1': org_child_1,
        'child_2': org_child_2,
        'grandchild': org_grandchild,
        'activity_parent': test_activity_parent,
        'activity_child_1': test_activity_child_1,
        'activity_child_2': test_activity_child_2,
        'activity_grandchild': test_activity_grandchild,
    }