import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_tables_exist(db_session: AsyncSession):
    """Проверяет наличие всех необходимых таблиц в базе данных."""
    result = await db_session.execute(
        text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
    )
    tables = [row[0] for row in result]
    
    # Проверяем наличие основных таблиц
    expected_tables = [
        'organizations',
        'buildings',
        'activities',
        'organization_phones',
        'organization_activity',
        'alembic_version',  # Alembic служебная таблица
    ]
    
    for table in expected_tables:
        assert table in tables, f"Table {table} not found!"
    
    print(f"✅ Все таблицы найдены: {tables}")


@pytest.mark.asyncio
async def test_alembic_version_exists(db_session: AsyncSession):
    """Проверяет наличие версии Alembic в базе данных."""
    result = await db_session.execute(
        text("SELECT version_num FROM alembic_version")
    )
    version = result.scalar()
    
    assert version is not None, "No Alembic version found!"
    print(f'✅ Alembic version: {version}')
