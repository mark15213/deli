# Generator Service for creating Quizzes
import json
import logging
from typing import List, Optional
from uuid import UUID

from openai import AsyncOpenAI
import instructor
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Quiz, QuizType, QuizStatus

logger = logging.getLogger(__name__)
settings = get_settings()

# Define the structure for LLM output
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
        # Initialize OpenAI client patched with instructor for structured output
        self.client = instructor.patch(AsyncOpenAI(api_key=settings.openai_api_key))
        
    async def generate_quizzes_from_chunk(self, text_chunk: str, source_metadata: dict) -> List[Quiz]:
        """
        Generate quizzes from a text chunk and save them to DB.
        """
        try:
            # 1. Call LLM
            quiz_outputs = await self._call_llm(text_chunk)
            
            generated_quizzes = []
            
            # 2. Parse and Create DB Models
            for q_out in quiz_outputs.quizzes:
                quiz = Quiz(
                    user_id=UUID(source_metadata["user_id"]),
                    type=QuizType.MCQ,
                    question=q_out.question,
                    options=q_out.options,
                    answer=q_out.answer,
                    explanation=q_out.explanation,
                    difficulty=q_out.difficulty,
                    tags=q_out.tags,
                    status=QuizStatus.PENDING,
                    source_page_id=source_metadata.get("page_id"),
                    source_page_title=source_metadata.get("page_title"),
                    # source_block_id=... (optional if we had granular block tracking)
                )
                self.db.add(quiz)
                generated_quizzes.append(quiz)
            
            await self.db.commit()
            return generated_quizzes
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            # In a real system, we might want to store a 'failed_generation' record
            return []

    async def _call_llm(self, text: str) -> QuizList:
        """Invoke LLM to generate structured quiz data."""
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
        
        return await self.client.chat.completions.create(
            model="gpt-3.5-turbo", # Or gpt-4
            response_model=QuizList,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates quizzes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
