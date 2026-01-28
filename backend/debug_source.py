
import asyncio
import os
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.models import Source, SourceLog, SourceMaterial, Card

async def check_db():
    async with async_session_maker() as db:
        print("--- Latest Source Logs ---")
        stmt = select(SourceLog).order_by(SourceLog.created_at.desc()).limit(10)
        result = await db.execute(stmt)
        logs = result.scalars().all()
        for log in logs:
            print(f"[{log.created_at}] Source: {log.source_id} | Event: {log.event_type} | Status: {log.status} | Msg: {log.message}")

        print("\n--- Checking for 'InternData-A1' Source ---")
        stmt = select(Source).where(Source.name.ilike("%InternData%"))
        result = await db.execute(stmt)
        source = result.scalar_one_or_none()
        
        if source:
            print(f"Source Found: {source.id} | Name: {source.name} | User: {source.user_id}")
            
            # Check Material
            stmt = select(SourceMaterial).where(SourceMaterial.source_id == source.id)
            result = await db.execute(stmt)
            mats = result.scalars().all()
            print(f"Materials count: {len(mats)}")
            for m in mats:
                print(f"  Material: {m.id} | Title: {m.title}")
                
            # Check Cards
            if mats:
                stmt = select(Card).where(Card.source_material_id == mats[0].id)
                result = await db.execute(stmt)
                cards = result.scalars().all()
                print(f"Cards count: {len(cards)}")
                for c in cards:
                     print(f"  Card: {c.type} | Status: {c.status}")
        else:
            print("Source 'InternData-A1' NOT FOUND.")

if __name__ == "__main__":
    asyncio.run(check_db())
