# Seed data for development - resets on each server restart
import uuid
from datetime import datetime, timezone, timedelta
from typing import List
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models import User, Deck, Card, CardStatus, DeckSubscription, SourceMaterial

logger = logging.getLogger(__name__)

# Fixed UUIDs for consistent data
MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

DECK_IDS = {
    "naval": uuid.UUID("11111111-1111-1111-1111-111111111111"),
    "react": uuid.UUID("22222222-2222-2222-2222-222222222222"),
    "startup": uuid.UUID("33333333-3333-3333-3333-333333333333"),
}

SOURCE_IDS = {
    "naval_twitter": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    "paul_essay": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    "huberman": uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
}


def get_test_decks() -> List[dict]:
    """Generate test deck data."""
    return [
        {
            "id": DECK_IDS["naval"],
            "owner_id": MOCK_USER_ID,
            "title": "Naval's Wisdom",
            "description": "Insights on wealth, happiness, and living a meaningful life from Naval Ravikant.",
            "is_public": False,
            "cover_image_url": None,
        },
        {
            "id": DECK_IDS["react"],
            "owner_id": MOCK_USER_ID,
            "title": "React Hooks Deep Dive",
            "description": "Master React hooks with practical examples and advanced patterns.",
            "is_public": False,
            "cover_image_url": None,
        },
        {
            "id": DECK_IDS["startup"],
            "owner_id": MOCK_USER_ID,
            "title": "Startup Mindset",
            "description": "Key lessons from Y Combinator, Paul Graham essays, and successful founders.",
            "is_public": True,
            "cover_image_url": None,
        },
    ]


def get_test_sources() -> List[dict]:
    """Generate test source material data."""
    return [
        {
            "id": SOURCE_IDS["naval_twitter"],
            "user_id": MOCK_USER_ID,
            "external_id": "naval_twitter_123",
            "external_url": "https://twitter.com/naval",
            "title": "Naval Ravikant on X",
            "content_hash": "abc123",
            "rich_data": {"source_type": "twitter"},
        },
        {
            "id": SOURCE_IDS["paul_essay"],
            "user_id": MOCK_USER_ID,
            "external_id": "pg_essay_456",
            "external_url": "https://paulgraham.com/superlinear.html",
            "title": "Paul Graham Essay",
            "content_hash": "def456",
            "rich_data": {"source_type": "article"},
        },
        {
            "id": SOURCE_IDS["huberman"],
            "user_id": MOCK_USER_ID,
            "external_id": "huberman_789",
            "external_url": "https://hubermanlab.com",
            "title": "Huberman Lab #85",
            "content_hash": "ghi789",
            "rich_data": {"source_type": "podcast"},
        },
    ]


def get_test_cards() -> List[dict]:
    """Generate test card data with various types."""
    cards = []
    
    # Naval deck - active cards
    naval_cards = [
        {
            "type": "note",
            "content": {
                "question": "Seek wealth, not money or status. Wealth is having assets that earn while you sleep. Money is how we transfer time and wealth. Status is your place in the social hierarchy.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_IDS["naval_twitter"],
        },
        {
            "type": "flashcard",
            "content": {
                "question": "What is the 'Lindy Effect'?",
                "answer": "The Lindy Effect is a theorized phenomenon by which the future life expectancy of some non-perishable things like a technology or an idea is proportional to their current age.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_IDS["naval_twitter"],
        },
        {
            "type": "mcq",
            "content": {
                "question": "Which of the following best describes 'specific knowledge'?",
                "options": [
                    "Knowledge that can be learned in school",
                    "Knowledge that is found through pursuing your genuine curiosity",
                    "Knowledge that everyone has access to",
                    "Knowledge from textbooks and courses",
                ],
                "answer": "Knowledge that is found through pursuing your genuine curiosity",
                "explanation": "Specific knowledge is knowledge that you cannot be trained for. It's found by pursuing your genuine curiosity and passion.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_IDS["naval_twitter"],
        },
        {
            "type": "flashcard",
            "content": {
                "question": "What are the three forms of leverage according to Naval?",
                "answer": "1. Labor (people working for you), 2. Capital (money working for you), 3. Products with no marginal cost of replication (code and media).",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_IDS["naval_twitter"],
        },
        {
            "type": "cloze",
            "content": {
                "question": "Code and media are called ______ leverage.",
                "answer": "permissionless",
                "explanation": "Code and media are permissionless leverage because you don't need anyone's permission to use them.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_IDS["naval_twitter"],
        },
    ]
    
    for card in naval_cards:
        card["id"] = uuid.uuid4()
        card["deck_id"] = DECK_IDS["naval"]
        card["tags"] = ["naval", "wealth"]
        cards.append(card)
    
    # React deck - active cards
    react_cards = [
        {
            "type": "flashcard",
            "content": {
                "question": "What is the difference between useState and useRef?",
                "answer": "useState triggers a re-render when the value changes. useRef does not trigger a re-render and persists across renders.",
            },
            "status": CardStatus.ACTIVE,
        },
        {
            "type": "mcq",
            "content": {
                "question": "When should you use useCallback?",
                "options": [
                    "For every function in a component",
                    "When passing callbacks to optimized child components",
                    "Never, it's deprecated",
                    "Only in class components",
                ],
                "answer": "When passing callbacks to optimized child components",
                "explanation": "useCallback memoizes functions to prevent unnecessary re-renders of child components that rely on referential equality.",
            },
            "status": CardStatus.ACTIVE,
        },
    ]
    
    for card in react_cards:
        card["id"] = uuid.uuid4()
        card["deck_id"] = DECK_IDS["react"]
        card["tags"] = ["react", "hooks"]
        card["source_material_id"] = None
        cards.append(card)
    
    # Pending cards (for inbox)
    pending_cards = [
        {
            "type": "note",
            "content": {
                "question": "The returns for performance are superlinear. Teachers and coaches implicitly tell us returns are linear. But in the real world you get paid for performance, not effort.",
            },
            "source_material_id": SOURCE_IDS["paul_essay"],
            "tags": ["paul_graham", "performance"],
        },
        {
            "type": "flashcard",
            "content": {
                "question": "What does 'superlinear returns' mean?",
                "answer": "When the reward for performance grows faster than the effort put in. Small differences in performance can lead to huge differences in outcomes.",
            },
            "source_material_id": SOURCE_IDS["paul_essay"],
            "tags": ["paul_graham"],
        },
        {
            "type": "mcq",
            "content": {
                "question": "According to Paul Graham, which field has the most superlinear returns?",
                "options": [
                    "Teaching",
                    "Medicine",
                    "Technology startups",
                    "Government work",
                ],
                "answer": "Technology startups",
                "explanation": "Startups have extreme superlinear returns because successful ones can scale infinitely with minimal additional effort.",
            },
            "source_material_id": SOURCE_IDS["paul_essay"],
            "tags": ["paul_graham", "startup"],
        },
        {
            "type": "note",
            "content": {
                "question": "Morning sunlight exposure within 30-60 minutes of waking sets your circadian rhythm and improves sleep quality that night.",
            },
            "source_material_id": SOURCE_IDS["huberman"],
            "tags": ["health", "sleep"],
        },
        {
            "type": "flashcard",
            "content": {
                "question": "How does morning light affect dopamine?",
                "answer": "Morning light exposure triggers a cortisol spike that increases dopamine baseline for 12-14 hours, improving motivation and mood.",
            },
            "source_material_id": SOURCE_IDS["huberman"],
            "tags": ["health", "dopamine"],
        },
        {
            "type": "cloze",
            "content": {
                "question": "The optimal time for morning light exposure is within ______ minutes of waking.",
                "answer": "30-60",
                "explanation": "Getting light within the first hour maximizes the cortisol awakening response.",
            },
            "source_material_id": SOURCE_IDS["huberman"],
            "tags": ["health"],
        },
    ]
    
    for card in pending_cards:
        card["id"] = uuid.uuid4()
        card["deck_id"] = DECK_IDS["startup"]  # Default pending deck
        card["status"] = CardStatus.PENDING
        cards.append(card)
    
    return cards


async def clear_test_data(db: AsyncSession):
    """Clear all test data from the database."""
    logger.info("Clearing existing test data...")
    
    # Delete in order to respect foreign keys
    await db.execute(delete(DeckSubscription).where(DeckSubscription.user_id == MOCK_USER_ID))
    await db.execute(delete(Card).where(Card.deck_id.in_(list(DECK_IDS.values()))))
    await db.execute(delete(Deck).where(Deck.owner_id == MOCK_USER_ID))
    await db.execute(delete(SourceMaterial).where(SourceMaterial.user_id == MOCK_USER_ID))
    
    await db.commit()
    logger.info("Test data cleared.")


async def seed_test_data(db: AsyncSession):
    """Seed the database with test data."""
    logger.info("Seeding test data...")
    
    # Ensure mock user exists
    user_stmt = select(User).where(User.id == MOCK_USER_ID)
    result = await db.execute(user_stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            id=MOCK_USER_ID,
            email="debug@deli.app",
            username="Debug User",
        )
        db.add(user)
        await db.flush()
    
    # Create source materials
    for source_data in get_test_sources():
        source = SourceMaterial(**source_data)
        db.add(source)
    
    await db.flush()
    
    # Create decks
    for deck_data in get_test_decks():
        deck = Deck(**deck_data)
        db.add(deck)
    
    await db.flush()
    
    # Create cards
    for card_data in get_test_cards():
        card = Card(**card_data)
        db.add(card)
    
    # Subscribe user to Naval's Wisdom and React decks
    sub1 = DeckSubscription(user_id=MOCK_USER_ID, deck_id=DECK_IDS["naval"])
    sub2 = DeckSubscription(user_id=MOCK_USER_ID, deck_id=DECK_IDS["react"])
    db.add(sub1)
    db.add(sub2)
    
    await db.commit()
    logger.info(f"Seeded {len(get_test_decks())} decks, {len(get_test_cards())} cards, {len(get_test_sources())} sources.")


async def reset_seed_data(db: AsyncSession):
    """Clear and reseed test data - call on startup."""
    await clear_test_data(db)
    await seed_test_data(db)
