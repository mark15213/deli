
import asyncio
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models import SourceMaterial, Card

async def check_data():
    async with async_session_maker() as session:
        # Find the source material
        stmt = select(SourceMaterial).where(SourceMaterial.title.ilike("%AdaReasoner%"))
        result = await session.execute(stmt)
        sources = result.scalars().all()
        
        print(f"Found {len(sources)} sources matching 'AdaReasoner'")
        
        for source in sources:
            print(f"Source: {source.title} (ID: {source.id})")
            print(f"  Rich Data Keys: {source.rich_data.keys() if source.rich_data else 'None'}")
            if source.rich_data:
                 print(f"  Summary: {source.rich_data.get('summary')[:50]}...")
                 print(f"  Suggestions: {len(source.rich_data.get('suggestions', []))}")
            
            # Check logs if we have source_id
            if source.source_id:
                from app.models import SourceLog
                stmt = select(SourceLog).where(SourceLog.source_id == source.source_id).order_by(SourceLog.created_at.desc()).limit(5)
                result = await session.execute(stmt)
                logs = result.scalars().all()
                print(f"  Recent Logs ({len(logs)}):")
                for log in logs:
                     print(f"    - [{log.created_at}] {log.event_type} ({log.status}): {log.message} | Lens: {log.lens_key}")

            # Find cards for this source
            stmt = select(Card).where(Card.source_material_id == source.id)
            result = await session.execute(stmt)
            cards = result.scalars().all()
            
            print(f"  Found {len(cards)} cards for this source:")
            for card in cards:
                print(f"    - Card ID: {card.id}, Type: {card.type}, Status: {card.status}")

if __name__ == "__main__":
    asyncio.run(check_data())
