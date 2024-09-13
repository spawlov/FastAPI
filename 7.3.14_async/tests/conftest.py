import os
from dotenv import find_dotenv, load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app, Base, get_db

load_dotenv(find_dotenv())

TestEngine = create_async_engine(os.getenv("TEST_DB_URL"), echo=True)
TestSessionLocal = sessionmaker(bind=TestEngine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function")
def test_db():
    engine = create_async_engine(os.getenv("TEST_DB_URL"), future=True)
    return engine

@pytest.fixture(scope="function")
async def session():
    async with test_db.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        session = TestSessionLocal(bind=conn)
        yield session
        await session.close()
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")

def client(session):
    def _get_db_override():
        yield session
    app.dependency_overrides[test_db] = _get_db_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()