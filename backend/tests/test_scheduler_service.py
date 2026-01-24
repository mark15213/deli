# Tests for Scheduler Service
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.services.scheduler_service import SchedulerService
from app.models import Card, CardStatus, StudyProgress, ReviewLog, Deck

@pytest_asyncio.fixture
async def test_deck(db_session, test_user):
    deck = Deck(id=uuid4(), owner_id=test_user.id, title="Test Deck")
    db_session.add(deck)
    await db_session.commit()
    return deck

@pytest_asyncio.fixture
async def test_card(db_session, test_user, test_deck):
    card = Card(
        id=uuid4(),
        deck_id=test_deck.id,
        type="mcq",
        content={"question": "Q", "answer": "A"},
        status=CardStatus.ACTIVE
    )
    db_session.add(card)
    
    # Also create a default StudyProgress for it? 
    # Or test assumes new card has no progress.
    # Service implementation: get_due_cards queries StudyProgress table.
    
    # If we want it to be "Due", and implementation requires StudyProgress to exist:
    # Service implementation says: "If we want NEW cards... tricky... Improved approach: Query StudyProgress directly".
    # And "Fetch cards with StudyProgress where due_date <= now".
    # So if there is no StudyProgress, it might not be returned depending on implementation.
    # Let's check service logic: "select(StudyProgress)..."
    # So yes, card must have progress to be "started".
    # Or we need a way to fetch "New" cards.
    # For this test, let's assume we test "Due Review" scenario.
    
    progress = StudyProgress(
        id=uuid4(),
        user_id=test_user.id,
        card_id=card.id,
        due_date=datetime.now(timezone.utc) - timedelta(days=1), # Yesterday, so it is due
        state="new"
    )
    db_session.add(progress)
    await db_session.commit()
    
    return card

@pytest.mark.asyncio
async def test_get_due_cards(db_session, test_user, test_card):
    """Test fetching due cards."""
    service = SchedulerService(db_session)
    
    # Card is set to be due yesterday
    due = await service.get_due_cards(test_user.id)
    assert len(due) == 1
    assert due[0].id == test_card.id
    
    # Now set updated due date to future
    stmt = (
        patch("app.models.StudyProgress.due_date")
    ) 
    # Just update DB
    from sqlalchemy import update
    stmt = update(StudyProgress).where(StudyProgress.card_id == test_card.id).values(
        due_date=datetime.now(timezone.utc) + timedelta(days=1)
    )
    await db_session.execute(stmt)
    await db_session.commit()
    
    due_after = await service.get_due_cards(test_user.id)
    assert len(due_after) == 0

@pytest.mark.asyncio
async def test_calculate_review(db_session, test_user, test_card):
    """Test FSRS review calculation."""
    # Mock FSRS to avoid dependency issue locally if not installed
    with patch("app.services.scheduler_service.FSRS") as MockFSRS:
        
        mock_fsrs_instance = MockFSRS.return_value
        # Mock repeat return
        mock_card = MagicMock()
        mock_card.due = datetime.now(timezone.utc) + timedelta(days=3)
        mock_card.stability = 1.0
        mock_card.difficulty = 5.0
        mock_card.elapsed_days = 1
        mock_card.scheduled_days = 3
        mock_card.reps = 1
        mock_card.lapses = 0
        mock_card.state = MagicMock()
        mock_card.state.value = 2 # Review
        
        # Structure of fsrs.repeat result: dict[Rating, SchedulingInfo]
        mock_sched_info = MagicMock()
        mock_sched_info.card = mock_card
        
        # Mock the dictionary lookup
        from fsrs import Rating
        mock_fsrs_instance.repeat.return_value = {
            Rating.Good: mock_sched_info
        }

        service = SchedulerService(db_session)
        
        progress = await service.calculate_review(test_user.id, test_card.id, 3)  # 3 = Good
        
        assert progress.card_id == test_card.id
        
        # Check ReviewLog created
        from sqlalchemy import select
        l_stmt = select(ReviewLog).where(ReviewLog.card_id == test_card.id)
        result = await db_session.execute(l_stmt)
        log = result.scalar_one_or_none()
        assert log is not None
        assert log.grade == 3
