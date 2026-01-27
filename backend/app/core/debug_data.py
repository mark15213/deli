from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid
import logging

from app.models.models import Source, User, SourceMaterial
from app.schemas.source_schemas import SourceType
from app.api import deps

logger = logging.getLogger(__name__)

async def reseed_debug_sources(db: AsyncSession):
    """
    Clears existing sources for the debug user and reseeds with one example of each SourceType.
    Only runs if the debug user exists.
    """
    # 1. Get Debug User
    # We can't use deps.get_mock_user directly because it expects a db session as dependency injection
    # But we can reuse the logic or just query for the known UUID if we want to be safe.
    # Actually, deps.get_mock_user is an async function that takes a session. We can call it directly!
    try:
        debug_user = await deps.get_mock_user(db)
    except Exception as e:
        logger.error(f"Failed to get debug user: {e}")
        return

    logger.info(f"Reseeding sources for debug user: {debug_user.email} ({debug_user.id})")

    # 2. Clear existing sources
    # Note: Cascading delete should handle source_materials
    try:
        await db.execute(delete(Source).where(Source.user_id == debug_user.id))
        # No need to commit yet, we can do it at the end
    except Exception as e:
         logger.error(f"Failed to clear existing sources: {e}")
         return

    # 3. Create Seed Data
    sources_data = [
        {
            "name": "My Twitter Feed",
            "type": "X_SOCIAL",
            "connection_config": {
                "target_username": "elonmusk",
                "auth_mode": "API_KEY",
                "api_token": "mock_encrypted_token"
            },
            "ingestion_rules": {
                "scope": "USER_FEED",
                "include_replies": False,
                "min_likes_threshold": 100,
                "fetch_frequency": "HOURLY"
            }
        },
        {
            "name": "Knowledge Base (Notion)",
            "type": "NOTION_KB",
            "connection_config": {
                "workspace_id": "ws_12345",
                "integration_token": "secret_notion_token",
                "target_database_id": "db_central_knowledge"
            },
            "ingestion_rules": {
                "sync_mode": "INCREMENTAL",
                "import_nested_pages": True,
                "generate_flashcards": True
            }
        },
        {
            "name": "AI Research Papers",
            "type": "ARXIV_PAPER",
            "connection_config": {
                "base_url": "http://export.arxiv.org/api/query",
                "category_filter": ["cs.AI", "cs.CL"]
            },
            "ingestion_rules": {
                "search_query": "LLM agents",
                "parsing_depth": "FULL_TEXT",
                "math_handling": "LATEX"
            }
        },
        {
            "name": "Deli Backend Repo",
            "type": "GITHUB_REPO",
            "connection_config": {
                "repo_url": "https://github.com/deli/backend",
                "branch": "main",
                "access_token": "ghp_mock_token"
            },
            "ingestion_rules": {
                "file_extensions": [".py", ".md"],
                "focus_on": "ARCHITECTURE",
                "readme_priority": "HIGHEST"
            }
        },
        {
            "name": "Tech Crunch RSS",
            "type": "WEB_RSS",
            "connection_config": {
                "url": "https://techcrunch.com/feed/",
                "type": "RSS"
            },
            "ingestion_rules": {
                "clean_mode": "READABILITY",
                "auto_tagging": True,
                "exclude_keywords": ["ads"]
            }
        }
    ]

    for s_data in sources_data:
        source_id = uuid.uuid4()
        source = Source(
            id=source_id,
            user_id=debug_user.id,
            name=s_data["name"],
            type=s_data["type"],
            connection_config=s_data["connection_config"],
            ingestion_rules=s_data["ingestion_rules"],
            status="ACTIVE",
            last_synced_at=None
        )
        db.add(source)
        
        # Add Mock Content for Arxiv Source so summary works in UI
        if s_data["type"] == "ARXIV_PAPER":
            material = SourceMaterial(
                id=uuid.uuid4(),
                user_id=debug_user.id,
                source_id=source_id,
                external_id="mock_paper_1", # Mock external ID
                title="Generative Agents: Interactive Simulacra of Human Behavior",
                rich_data={
                    "summary": "This paper introduces generative agents—computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior.",
                    "suggestions": [
                        {
                            "key": "methodology_lens",
                            "name": "Methodology Analysis",
                            "description": "Deep dive into the architectural implementation.",
                            "reason": "Understand how memory synthesis works."
                        }
                    ]
                }
            )
            db.add(material)
    
    await db.commit()
    logger.info(f"Successfully seeded {len(sources_data)} sources.")
