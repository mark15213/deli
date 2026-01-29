import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.api import deps
from app.models.models import Source, User

# We need to ensure the DB sessions are handled correctly in tests
# Assuming existing conftest.py handles basic async setup, 
# but I'll make this self-contained or rely on what's likely there.
# To be safe, I will mock the session or use the existing override mechanism if I knew it.
# Since I'm adding a new test file, I should try to align with the project's testing pattern.
# For now, I'll write a test that uses the app's dependency overrides to ensure we are hitting the DB.

@pytest.mark.asyncio
async def test_debug_seeding_and_list(client, db_session):
    # This test assumes:
    # 1. 'async_client' fixture provides an httpx client for the app
    # 2. 'db_session' fixture provides a database session
    # 3. The app lifespan is triggered or we can trigger the seeding manually if needed.
    # Note: TestClient (sync) triggers lifespan. AsyncClient might not unless managed.
    # If the project uses AsyncClient, we need to check how they handle lifespan.
    # But for "Restart" simulation, calling the seeding function directly might be easier/cleaner 
    # if we can't easily restart the app in tests.
    
    # However, the user wants to ensure it happens on *restarts*.
    # So I should verify the `reseed_debug_sources` logic itself effectively.

    from app.core.debug_data import reseed_debug_sources
    
    # 1. Run seeding
    await reseed_debug_sources(db_session)
    
    # 2. Verify data exists via DB
    stmt = select(Source)
    result = await db_session.execute(stmt)
    sources = result.scalars().all()
    assert len(sources) >= 5, "Should have seeded at least 5 sources"
    
    types = {s.type for s in sources}
    assert "X_SOCIAL" in types
    assert "NOTION_KB" in types
    
    # 3. Verify via API
    # We need to make sure the API uses the same DB session or can access the data.
    # If using dependency overrides, we typically override get_db.
    # Assuming the `async_client` fixture sets this up.
    
    response = await client.get("/api/v1/sources/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    
    # 4. Simulate Restart (Run seeding again)
    # This should verify that it doesn't duplicate indefinitely or crash, 
    # but rather resets or handles it (my implementation deletes and recreates).
    
    # Capture IDs from first run
    ids_run_1 = {s["id"] for s in data}
    
    await reseed_debug_sources(db_session)
    
    response_2 = await client.get("/api/v1/sources/")
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert len(data_2) >= 5
    
    ids_run_2 = {s["id"] for s in data_2}
    
    # Since my implementation deletes and recreates, IDs should be DIFFERENT.
    # This proves it refreshed the data.
    assert ids_run_1.isdisjoint(ids_run_2), "IDs should change after reseed (refresh)"

