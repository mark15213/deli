# Generator Service for creating Quizzes
import json
import logging
from typing import List
from uuid import UUID
import uuid


from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.models import Card, CardStatus, Deck, User, SourceMaterial

logger = logging.getLogger(__name__)
settings = get_settings()

class QuizOutput(BaseModel):
    question: str = Field(..., description="The question text.")
    options: List[str] = Field(..., description="List of possible answers (for MCQ).")
    answer: str = Field(..., description="The correct answer text. Must be one of the options.")
    explanation: str = Field(..., description="Explanation of why the answer is correct.")
    difficulty: str = Field(..., description="Difficulty level: 'Easy', 'Medium', or 'Hard'.")
    tags: List[str] = Field(..., description="Relevant tags for the quiz.")

class QuizList(BaseModel):
    quizzes: List[QuizOutput]


class GeneratorService:
    """Service for generating quizzes from text using LLM."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # Initialize Google GenAI Client
        # Priority: GEMINI_API_KEY -> OPENAI_API_KEY (fallback)
        settings = get_settings()
        api_key = settings.gemini_api_key
        if not api_key:
            api_key = settings.openai_api_key # Fallback
            
        from google import genai
        self.client = genai.Client(api_key=api_key)
        
    async def generate_quizzes_from_chunk(self, text_chunk: str, source_metadata: dict) -> List[Card]:
        """
        Generate quizzes from a text chunk and save them to DB.
        """
        try:
            # 1. Call LLM
            quiz_list_obj = await self._call_llm(text_chunk)
            
            if not quiz_list_obj or not quiz_list_obj.quizzes:
                return []

            generated_cards = []
            
            user_id = UUID(source_metadata["user_id"])
            source_mat_id = UUID(source_metadata.get("source_material_id"))
            
            # 2. Get or Create Inbox/Default Deck
            deck_id = await self._get_or_create_default_deck(user_id)
            
            # 3. Parse and Create DB Models (Card)
            for q_out in quiz_list_obj.quizzes:
                card_content = {
                    "question": q_out.question,
                    "options": q_out.options,
                    "answer": q_out.answer,
                    "explanation": q_out.explanation
                }
                
                card = Card(
                    deck_id=deck_id,
                    source_material_id=source_mat_id,
                    type="mcq",
                    content=card_content,
                    # embedding=... 
                    status=CardStatus.PENDING,
                    tags=q_out.tags
                )
                self.db.add(card)
                generated_cards.append(card)
            
            await self.db.commit()
            return generated_cards
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            return []

    async def _get_or_create_default_deck(self, user_id: UUID) -> UUID:
        """Get or create 'Inbox' deck."""
        stmt = select(Deck).where(
            Deck.owner_id == user_id, 
            Deck.title == "Inbox"
        )
        result = await self.db.execute(stmt)
        deck = result.scalar_one_or_none()
        
        if not deck:
            deck = Deck(
                id=uuid.uuid4(),
                owner_id=user_id,
                title="Inbox",
                description="Default deck for new cards."
            )
            self.db.add(deck)
            await self.db.flush()
        
        return deck.id

    async def _call_llm(self, text: str) -> QuizList:
        """Invoke LLM to generate structured quiz data."""
        from google.genai import types
        
        prompt = f"""
        You are an expert tutor. Create 1-3 high-quality multiple-choice questions (MCQs) based on the following text.
        
        Text content:
        "{text}"
        
        Requirements:
        1. Questions should test understanding, not just recall.
        2. Provide 3-4 plausible options for each question.
        3. Clearly mark the correct answer.
        4. Provide a brief explanation for the answer.
        5. Tag the content with relevant keywords.
        """
        
        settings = get_settings()
        model_name = settings.openai_model or "gemini-3-flash"
        
        # Use Pydantic model for schema
        try:
            response = await self.client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=QuizList,
                    system_instruction="You are a helpful assistant that generates quizzes."
                )
            )
            
            # Parse response directly using Pydantic
            # The SDK might return text that we need to parse, or if response_schema is set, it validates structure
            # Typically response.parsed if using high level tooling, but standard generate_content returns text
            # However, with response_schema, the text IS json.
            import json
            data = json.loads(response.text)
            return QuizList(**data)
            
        except Exception as e:
             logger.error(f"LLM Quiz Generation Failed: {e}")
             return QuizList(quizzes=[])
