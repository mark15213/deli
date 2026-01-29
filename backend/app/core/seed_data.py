# Seed data for development - resets on each server restart
# Structure: User -> Source -> SourceMaterial -> Card -> Deck
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text

from app.models import (
    User, Source, SourceMaterial, Card, Deck, 
    CardStatus, DeckSubscription, StudyProgress, FSRSState
)

logger = logging.getLogger(__name__)

# ============================================================================
# Fixed UUIDs for consistent data
# ============================================================================

MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Decks
DECK_IDS = {
    "inbox": uuid.UUID("11111111-0000-0000-0000-000000000001"),
    "ai_research": uuid.UUID("11111111-0000-0000-0000-000000000002"),
    "web_dev": uuid.UUID("11111111-0000-0000-0000-000000000003"),
    "wisdom": uuid.UUID("11111111-0000-0000-0000-000000000004"),
}

# Sources
SOURCE_IDS = {
    "arxiv": uuid.UUID("22222222-0000-0000-0000-000000000001"),
    "notion_kb": uuid.UUID("22222222-0000-0000-0000-000000000002"),
    "twitter_naval": uuid.UUID("22222222-0000-0000-0000-000000000003"),
    "github_react": uuid.UUID("22222222-0000-0000-0000-000000000004"),
}

# SourceMaterials
SOURCE_MATERIAL_IDS = {
    "paper_llm_agents": uuid.UUID("33333333-0000-0000-0000-000000000001"),
    "paper_rag_survey": uuid.UUID("33333333-0000-0000-0000-000000000002"),
    "paper_moe": uuid.UUID("33333333-0000-0000-0000-000000000003"),
    "notion_react_hooks": uuid.UUID("33333333-0000-0000-0000-000000000004"),
    "notion_typescript": uuid.UUID("33333333-0000-0000-0000-000000000005"),
    "naval_thread_1": uuid.UUID("33333333-0000-0000-0000-000000000006"),
    "naval_thread_2": uuid.UUID("33333333-0000-0000-0000-000000000007"),
}

# Card UUIDs - using batch concept for paper reading notes
BATCH_IDS = {
    "llm_agents_notes": uuid.UUID("44444444-0000-0000-0000-000000000001"),
    "rag_notes": uuid.UUID("44444444-0000-0000-0000-000000000002"),
}


# ============================================================================
# Data Generators
# ============================================================================

def get_test_sources() -> List[Dict[str, Any]]:
    """Generate Source (top-level sync configs) data."""
    return [
        {
            "id": SOURCE_IDS["arxiv"],
            "user_id": MOCK_USER_ID,
            "name": "AI Research (arXiv)",
            "type": "ARXIV_PAPER",
            "connection_config": {
                "base_url": "http://export.arxiv.org/api/query",
                "category_filter": ["cs.AI", "cs.CL", "cs.LG"],
            },
            "ingestion_rules": {
                "search_query": "LLM agents OR RAG",
                "parsing_depth": "FULL_TEXT",
                "translate_to": None,
                "math_handling": "LATEX",
            },
            "status": "ACTIVE",
        },
        {
            "id": SOURCE_IDS["notion_kb"],
            "user_id": MOCK_USER_ID,
            "name": "My Knowledge Base (Notion)",
            "type": "NOTION_KB",
            "connection_config": {
                "workspace_id": "ws_dev_12345",
                "integration_token": "mock_notion_token",
                "target_database_id": "db_notes",
            },
            "ingestion_rules": {
                "sync_mode": "INCREMENTAL",
                "import_nested_pages": True,
                "generate_flashcards": True,
            },
            "status": "ACTIVE",
        },
        {
            "id": SOURCE_IDS["twitter_naval"],
            "user_id": MOCK_USER_ID,
            "name": "Naval (X/Twitter)",
            "type": "X_SOCIAL",
            "connection_config": {
                "target_username": "naval",
                "auth_mode": "API_KEY",
                "api_token": "mock_twitter_token",
            },
            "ingestion_rules": {
                "scope": "USER_FEED",
                "include_replies": False,
                "min_likes_threshold": 1000,
                "fetch_frequency": "DAILY",
            },
            "status": "ACTIVE",
        },
        {
            "id": SOURCE_IDS["github_react"],
            "user_id": MOCK_USER_ID,
            "name": "React Docs (GitHub)",
            "type": "GITHUB_REPO",
            "connection_config": {
                "repo_url": "https://github.com/facebook/react",
                "branch": "main",
            },
            "ingestion_rules": {
                "file_extensions": [".md"],
                "focus_on": "ARCHITECTURE",
            },
            "status": "PAUSED",
        },
    ]


def get_test_source_materials() -> List[Dict[str, Any]]:
    """Generate SourceMaterial (individual content items) data."""
    return [
        # --- arXiv Papers ---
        {
            "id": SOURCE_MATERIAL_IDS["paper_llm_agents"],
            "user_id": MOCK_USER_ID,
            "source_id": SOURCE_IDS["arxiv"],
            "external_id": "2308.11432",
            "external_url": "https://arxiv.org/abs/2308.11432",
            "title": "A Survey on Large Language Model based Autonomous Agents",
            "content_hash": "hash_llm_agents_v1",
            "raw_snippet": "LLM-based autonomous agents represent a paradigm shift...",
            "rich_data": {
                "summary": "This comprehensive survey reviews the rapidly evolving field of Large Language Model (LLM)-based autonomous agents. It provides a systematic framework to categorize agent architectures, covering brain (reasoning), perception, action, and memory components. The survey analyzes key techniques including chain-of-thought reasoning, tool use, and multi-agent collaboration.",
                "authors": ["Lei Wang", "Chen Ma", "Xueyang Feng"],
                "published_date": "2023-08-22",
                "categories": ["cs.AI", "cs.CL"],
                "suggestions": [
                    {
                        "key": "reading_notes",
                        "name": "Reading Notes",
                        "description": "Generate reading notes for this paper",
                        "reason": "Helps understand the paper's key contributions",
                    },
                ],
            },
        },
        {
            "id": SOURCE_MATERIAL_IDS["paper_rag_survey"],
            "user_id": MOCK_USER_ID,
            "source_id": SOURCE_IDS["arxiv"],
            "external_id": "2312.10997",
            "external_url": "https://arxiv.org/abs/2312.10997",
            "title": "Retrieval-Augmented Generation for Large Language Models: A Survey",
            "content_hash": "hash_rag_survey_v1",
            "raw_snippet": "RAG has emerged as a promising solution to address knowledge limitations...",
            "rich_data": {
                "summary": "This survey provides a comprehensive review of Retrieval-Augmented Generation (RAG) for LLMs. It organizes the RAG paradigm into three stages: pre-retrieval, retrieval, and post-retrieval. The paper covers techniques like query rewriting, dense retrieval, and fusion methods.",
                "authors": ["Yunfan Gao", "Yun Xiong", "Xinyu Gao"],
                "published_date": "2023-12-18",
                "categories": ["cs.CL", "cs.IR"],
                "suggestions": [
                    {
                        "key": "reading_notes",
                        "name": "Reading Notes",
                        "description": "Generate structured reading notes",
                        "reason": "Master the RAG pipeline",
                    },
                ],
            },
        },
        {
            "id": SOURCE_MATERIAL_IDS["paper_moe"],
            "user_id": MOCK_USER_ID,
            "source_id": SOURCE_IDS["arxiv"],
            "external_id": "2401.04088",
            "external_url": "https://arxiv.org/abs/2401.04088",
            "title": "Mixtral of Experts",
            "content_hash": "hash_moe_v1",
            "raw_snippet": "We introduce Mixtral 8x7B, a Sparse Mixture of Experts (SMoE)...",
            "rich_data": {
                "summary": "Mixtral 8x7B is a Sparse Mixture of Experts language model that outperforms Llama 2 70B and GPT-3.5 on most benchmarks. It uses a router network to select 2 experts out of 8 for each token, achieving high performance with efficient inference.",
                "authors": ["Mistral AI Team"],
                "published_date": "2024-01-08",
                "categories": ["cs.LG", "cs.CL"],
            },
        },
        # --- Notion Pages ---
        {
            "id": SOURCE_MATERIAL_IDS["notion_react_hooks"],
            "user_id": MOCK_USER_ID,
            "source_id": SOURCE_IDS["notion_kb"],
            "external_id": "notion_page_react_hooks",
            "external_url": "https://notion.so/React-Hooks-abc123",
            "title": "React Hooks Deep Dive",
            "content_hash": "hash_react_hooks_v1",
            "rich_data": {
                "summary": "Personal notes on React hooks including useState, useEffect, useMemo, useCallback, and custom hooks patterns.",
            },
        },
        {
            "id": SOURCE_MATERIAL_IDS["notion_typescript"],
            "user_id": MOCK_USER_ID,
            "source_id": SOURCE_IDS["notion_kb"],
            "external_id": "notion_page_typescript",
            "external_url": "https://notion.so/TypeScript-Tips-def456",
            "title": "TypeScript Advanced Patterns",
            "content_hash": "hash_typescript_v1",
            "rich_data": {
                "summary": "Collection of advanced TypeScript patterns including conditional types, mapped types, and template literal types.",
            },
        },
        # --- Twitter Threads ---
        {
            "id": SOURCE_MATERIAL_IDS["naval_thread_1"],
            "user_id": MOCK_USER_ID,
            "source_id": SOURCE_IDS["twitter_naval"],
            "external_id": "twitter_naval_wealth",
            "external_url": "https://twitter.com/naval/status/1002103360646823936",
            "title": "How to Get Rich (Without Getting Lucky)",
            "content_hash": "hash_naval_wealth_v1",
            "rich_data": {
                "summary": "Naval's famous thread on building wealth through leverage, specific knowledge, and long-term thinking.",
                "thread_length": 40,
            },
        },
        {
            "id": SOURCE_MATERIAL_IDS["naval_thread_2"],
            "user_id": MOCK_USER_ID,
            "source_id": SOURCE_IDS["twitter_naval"],
            "external_id": "twitter_naval_happiness",
            "external_url": "https://twitter.com/naval/status/1261481222359801856",
            "title": "Happiness is a Skill",
            "content_hash": "hash_naval_happiness_v1",
            "rich_data": {
                "summary": "Thread on how happiness is a skill that can be trained, not a destination.",
            },
        },
    ]


def get_test_decks() -> List[Dict[str, Any]]:
    """Generate Deck data."""
    return [
        {
            "id": DECK_IDS["inbox"],
            "owner_id": MOCK_USER_ID,
            "title": "📥 Inbox",
            "description": "Pending cards awaiting review and categorization.",
            "is_public": False,
        },
        {
            "id": DECK_IDS["ai_research"],
            "owner_id": MOCK_USER_ID,
            "title": "🤖 AI Research",
            "description": "Notes and flashcards from AI/ML papers and research.",
            "is_public": False,
        },
        {
            "id": DECK_IDS["web_dev"],
            "owner_id": MOCK_USER_ID,
            "title": "💻 Web Development",
            "description": "Frontend frameworks, TypeScript, and web technologies.",
            "is_public": False,
        },
        {
            "id": DECK_IDS["wisdom"],
            "owner_id": MOCK_USER_ID,
            "title": "🧠 Wisdom & Mental Models",
            "description": "Life lessons, mental models, and wisdom from thinkers.",
            "is_public": True,
        },
    ]


def get_test_cards() -> List[Dict[str, Any]]:
    """Generate Card data with proper relationships."""
    cards = []
    
    # =========================================================================
    # AI Research Deck - ACTIVE Cards from Papers
    # =========================================================================
    
    # LLM Agents Paper - Reading Notes (batch)
    llm_agents_notes = [
        {
            "id": uuid.UUID("55555555-0001-0000-0000-000000000001"),
            "type": "note",
            "content": {
                "question": "**Agent Architecture Overview**\n\nLLM-based agents consist of four key components:\n- **Brain**: The LLM core that handles reasoning (CoT, ToT, ReAct)\n- **Perception**: Processing multimodal inputs (text, image, audio)\n- **Action**: Tool use and environment interaction\n- **Memory**: Short-term (context) and long-term (vector stores)",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_llm_agents"],
            "deck_id": DECK_IDS["ai_research"],
            "batch_id": BATCH_IDS["llm_agents_notes"],
            "batch_index": 1,
            "tags": ["llm", "agents", "architecture"],
        },
        {
            "id": uuid.UUID("55555555-0001-0000-0000-000000000002"),
            "type": "note",
            "content": {
                "question": "**Reasoning Techniques**\n\n1. **Chain-of-Thought (CoT)**: Step-by-step reasoning\n2. **Tree-of-Thought (ToT)**: Exploring multiple reasoning paths\n3. **ReAct**: Interleaving reasoning with actions\n4. **Reflexion**: Self-reflection and learning from mistakes",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_llm_agents"],
            "deck_id": DECK_IDS["ai_research"],
            "batch_id": BATCH_IDS["llm_agents_notes"],
            "batch_index": 2,
            "tags": ["llm", "reasoning", "cot"],
        },
        {
            "id": uuid.UUID("55555555-0001-0000-0000-000000000003"),
            "type": "flashcard",
            "content": {
                "question": "What are the four main components of an LLM-based autonomous agent?",
                "answer": "1. Brain (LLM reasoning core)\n2. Perception (multimodal input processing)\n3. Action (tool use and environment interaction)\n4. Memory (short-term context and long-term storage)",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_llm_agents"],
            "deck_id": DECK_IDS["ai_research"],
            "batch_id": BATCH_IDS["llm_agents_notes"],
            "batch_index": 3,
            "tags": ["llm", "agents"],
        },
        {
            "id": uuid.UUID("55555555-0001-0000-0000-000000000004"),
            "type": "mcq",
            "content": {
                "question": "Which reasoning technique interleaves thinking with actions in a loop?",
                "options": [
                    "Chain-of-Thought (CoT)",
                    "Tree-of-Thought (ToT)",
                    "ReAct",
                    "Self-Consistency",
                ],
                "answer": "ReAct",
                "explanation": "ReAct (Reason + Act) combines reasoning traces with actions, allowing the agent to observe results and adjust its approach iteratively.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_llm_agents"],
            "deck_id": DECK_IDS["ai_research"],
            "batch_id": BATCH_IDS["llm_agents_notes"],
            "batch_index": 4,
            "tags": ["llm", "reasoning"],
        },
    ]
    cards.extend(llm_agents_notes)
    
    # RAG Survey - Individual Cards
    rag_cards = [
        {
            "id": uuid.UUID("55555555-0002-0000-0000-000000000001"),
            "type": "flashcard",
            "content": {
                "question": "What are the three stages of the RAG pipeline?",
                "answer": "1. **Pre-retrieval**: Query rewriting, expansion, decomposition\n2. **Retrieval**: Finding relevant documents (sparse/dense retrieval)\n3. **Post-retrieval**: Re-ranking, filtering, fusion with LLM",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_rag_survey"],
            "deck_id": DECK_IDS["ai_research"],
            "tags": ["rag", "retrieval"],
        },
        {
            "id": uuid.UUID("55555555-0002-0000-0000-000000000002"),
            "type": "cloze",
            "content": {
                "question": "In RAG, ______ retrieval uses learned embeddings while ______ retrieval uses term frequency.",
                "answer": "dense, sparse",
                "explanation": "Dense retrieval (e.g., DPR) uses neural embeddings; sparse retrieval (e.g., BM25) uses term frequency-inverse document frequency.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_rag_survey"],
            "deck_id": DECK_IDS["ai_research"],
            "tags": ["rag", "retrieval"],
        },
    ]
    cards.extend(rag_cards)
    
    # =========================================================================
    # Web Dev Deck - ACTIVE Cards from Notion
    # =========================================================================
    
    webdev_cards = [
        {
            "id": uuid.UUID("55555555-0003-0000-0000-000000000001"),
            "type": "flashcard",
            "content": {
                "question": "What is the difference between `useState` and `useRef`?",
                "answer": "- `useState`: Triggers re-render when value changes, used for UI state\n- `useRef`: Does NOT trigger re-render, persists across renders, used for DOM refs or mutable values",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["notion_react_hooks"],
            "deck_id": DECK_IDS["web_dev"],
            "tags": ["react", "hooks"],
        },
        {
            "id": uuid.UUID("55555555-0003-0000-0000-000000000002"),
            "type": "mcq",
            "content": {
                "question": "When should you use `useCallback`?",
                "options": [
                    "For every function in a component",
                    "When passing callbacks to memoized child components",
                    "Only in class components",
                    "To cache API responses",
                ],
                "answer": "When passing callbacks to memoized child components",
                "explanation": "useCallback memoizes functions to maintain referential equality, preventing unnecessary re-renders of React.memo'd children.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["notion_react_hooks"],
            "deck_id": DECK_IDS["web_dev"],
            "tags": ["react", "hooks", "performance"],
        },
        {
            "id": uuid.UUID("55555555-0003-0000-0000-000000000003"),
            "type": "flashcard",
            "content": {
                "question": "What is a TypeScript conditional type and give an example?",
                "answer": "A type that changes based on a condition.\n\nExample:\n```typescript\ntype IsString<T> = T extends string ? true : false;\ntype A = IsString<'hello'>; // true\ntype B = IsString<42>; // false\n```",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["notion_typescript"],
            "deck_id": DECK_IDS["web_dev"],
            "tags": ["typescript", "types"],
        },
    ]
    cards.extend(webdev_cards)
    
    # =========================================================================
    # Wisdom Deck - ACTIVE Cards from Naval
    # =========================================================================
    
    wisdom_cards = [
        {
            "id": uuid.UUID("55555555-0004-0000-0000-000000000001"),
            "type": "note",
            "content": {
                "question": "**Seek Wealth, Not Money or Status**\n\nWealth is having assets that earn while you sleep. Money is how we transfer time and wealth. Status is your place in the social hierarchy.\n\n*Key insight*: Wealth creation is a positive-sum game. Status is zero-sum.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["naval_thread_1"],
            "deck_id": DECK_IDS["wisdom"],
            "tags": ["naval", "wealth"],
        },
        {
            "id": uuid.UUID("55555555-0004-0000-0000-000000000002"),
            "type": "flashcard",
            "content": {
                "question": "What are Naval's three forms of leverage?",
                "answer": "1. **Labor**: People working for you\n2. **Capital**: Money working for you\n3. **Products with zero marginal cost**: Code and media (permissionless leverage)",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["naval_thread_1"],
            "deck_id": DECK_IDS["wisdom"],
            "tags": ["naval", "leverage"],
        },
        {
            "id": uuid.UUID("55555555-0004-0000-0000-000000000003"),
            "type": "cloze",
            "content": {
                "question": "Code and media are called ______ leverage because you don't need permission to use them.",
                "answer": "permissionless",
                "explanation": "Unlike labor (need to convince people) or capital (need money), anyone can write code or create content.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["naval_thread_1"],
            "deck_id": DECK_IDS["wisdom"],
            "tags": ["naval", "leverage"],
        },
        {
            "id": uuid.UUID("55555555-0004-0000-0000-000000000004"),
            "type": "flashcard",
            "content": {
                "question": "According to Naval, what is 'specific knowledge'?",
                "answer": "Specific knowledge is knowledge that cannot be trained for. It is found through pursuing your genuine curiosity and passion, often at the edge of knowledge. It feels like play to you but looks like work to others.",
            },
            "status": CardStatus.ACTIVE,
            "source_material_id": SOURCE_MATERIAL_IDS["naval_thread_1"],
            "deck_id": DECK_IDS["wisdom"],
            "tags": ["naval", "knowledge"],
        },
    ]
    cards.extend(wisdom_cards)
    
    # =========================================================================
    # Inbox - PENDING Cards (awaiting review)
    # =========================================================================
    
    pending_cards = [
        {
            "id": uuid.UUID("55555555-0005-0000-0000-000000000001"),
            "type": "note",
            "content": {
                "question": "**Mixtral 8x7B Architecture**\n\nA Sparse Mixture of Experts model that uses a router to select 2 out of 8 expert networks for each token. This achieves the quality of larger models with the inference cost of smaller ones.",
            },
            "status": CardStatus.PENDING,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_moe"],
            "deck_id": DECK_IDS["inbox"],
            "tags": ["moe", "mixtral"],
        },
        {
            "id": uuid.UUID("55555555-0005-0000-0000-000000000002"),
            "type": "flashcard",
            "content": {
                "question": "What is the key advantage of Sparse Mixture of Experts (SMoE)?",
                "answer": "SMoE achieves high model quality while only activating a subset of parameters per token, giving better performance-to-compute efficiency than dense models.",
            },
            "status": CardStatus.PENDING,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_moe"],
            "deck_id": DECK_IDS["inbox"],
            "tags": ["moe", "efficiency"],
        },
        {
            "id": uuid.UUID("55555555-0005-0000-0000-000000000003"),
            "type": "mcq",
            "content": {
                "question": "In Mixtral 8x7B, how many experts are selected per token?",
                "options": ["1", "2", "4", "8"],
                "answer": "2",
                "explanation": "The router selects the top-2 experts for each token, balancing model capacity with inference efficiency.",
            },
            "status": CardStatus.PENDING,
            "source_material_id": SOURCE_MATERIAL_IDS["paper_moe"],
            "deck_id": DECK_IDS["inbox"],
            "tags": ["moe", "mixtral"],
        },
        {
            "id": uuid.UUID("55555555-0005-0000-0000-000000000004"),
            "type": "note",
            "content": {
                "question": "**Happiness is a Skill**\n\nHappiness is not something that happens to you. It's a skill that you can develop, like fitness. The mind can be trained just like the body.",
            },
            "status": CardStatus.PENDING,
            "source_material_id": SOURCE_MATERIAL_IDS["naval_thread_2"],
            "deck_id": DECK_IDS["inbox"],
            "tags": ["naval", "happiness"],
        },
        {
            "id": uuid.UUID("55555555-0005-0000-0000-000000000005"),
            "type": "flashcard",
            "content": {
                "question": "What is the useReducer hook best used for?",
                "answer": "Complex state logic with multiple sub-values, or when the next state depends on the previous one. It's especially useful for state that involves multiple related updates.",
            },
            "status": CardStatus.PENDING,
            "source_material_id": SOURCE_MATERIAL_IDS["notion_react_hooks"],
            "deck_id": DECK_IDS["inbox"],
            "tags": ["react", "hooks"],
        },
    ]
    cards.extend(pending_cards)
    
    return cards


def get_test_study_progress() -> List[Dict[str, Any]]:
    """Generate StudyProgress data for active cards."""
    now = datetime.now(timezone.utc)
    
    progress = []
    
    # Cards due today
    due_today_ids = [
        uuid.UUID("55555555-0001-0000-0000-000000000001"),  # LLM agents note 1
        uuid.UUID("55555555-0001-0000-0000-000000000003"),  # LLM agents flashcard
        uuid.UUID("55555555-0003-0000-0000-000000000001"),  # React useState
    ]
    
    for i, card_id in enumerate(due_today_ids):
        progress.append({
            "id": uuid.uuid4(),
            "user_id": MOCK_USER_ID,
            "card_id": card_id,
            "stability": 1.0 + i * 0.5,
            "difficulty": 5.0,
            "elapsed_days": 1.0,
            "scheduled_days": 1.0,
            "retrievability": 0.9,
            "state": FSRSState.REVIEW,
            "due_date": now - timedelta(hours=i),  # Due in the past = should study now
            "last_review_at": now - timedelta(days=1),
        })
    
    # Cards due tomorrow
    due_tomorrow_ids = [
        uuid.UUID("55555555-0001-0000-0000-000000000002"),  # LLM agents note 2
        uuid.UUID("55555555-0002-0000-0000-000000000001"),  # RAG flashcard
    ]
    
    for card_id in due_tomorrow_ids:
        progress.append({
            "id": uuid.uuid4(),
            "user_id": MOCK_USER_ID,
            "card_id": card_id,
            "stability": 3.0,
            "difficulty": 4.5,
            "elapsed_days": 2.0,
            "scheduled_days": 3.0,
            "retrievability": 0.85,
            "state": FSRSState.REVIEW,
            "due_date": now + timedelta(days=1),
            "last_review_at": now - timedelta(days=2),
        })
    
    # New cards (never studied)
    new_card_ids = [
        uuid.UUID("55555555-0001-0000-0000-000000000004"),  # LLM agents MCQ
        uuid.UUID("55555555-0002-0000-0000-000000000002"),  # RAG cloze
        uuid.UUID("55555555-0003-0000-0000-000000000002"),  # React useCallback
        uuid.UUID("55555555-0003-0000-0000-000000000003"),  # TypeScript
        uuid.UUID("55555555-0004-0000-0000-000000000001"),  # Naval note
        uuid.UUID("55555555-0004-0000-0000-000000000002"),  # Naval flashcard 1
        uuid.UUID("55555555-0004-0000-0000-000000000003"),  # Naval cloze
        uuid.UUID("55555555-0004-0000-0000-000000000004"),  # Naval flashcard 2
    ]
    
    for card_id in new_card_ids:
        progress.append({
            "id": uuid.uuid4(),
            "user_id": MOCK_USER_ID,
            "card_id": card_id,
            "stability": 0.0,
            "difficulty": 0.0,
            "elapsed_days": 0.0,
            "scheduled_days": 0.0,
            "retrievability": 0.0,
            "state": FSRSState.NEW,
            "due_date": now,
            "last_review_at": None,
        })
    
    return progress


# ============================================================================
# Database Operations
# ============================================================================

async def clear_all_test_data(db: AsyncSession):
    """Clear ALL data for the mock user - complete reset."""
    logger.info("Clearing all test data for mock user...")
    
    # Delete in order to respect foreign keys
    # 1. Delete study progress and review logs first
    await db.execute(text("DELETE FROM study_progress WHERE user_id = :uid"), {"uid": str(MOCK_USER_ID)})
    await db.execute(text("DELETE FROM review_logs WHERE user_id = :uid"), {"uid": str(MOCK_USER_ID)})
    
    # 2. Delete card-deck associations
    await db.execute(text("""
        DELETE FROM card_decks WHERE card_id IN (
            SELECT id FROM cards WHERE owner_id = :uid
        )
    """), {"uid": str(MOCK_USER_ID)})
    
    # 3. Delete cards
    await db.execute(text("DELETE FROM cards WHERE owner_id = :uid"), {"uid": str(MOCK_USER_ID)})
    
    # 4. Delete deck subscriptions and decks
    await db.execute(text("DELETE FROM deck_subscriptions WHERE user_id = :uid"), {"uid": str(MOCK_USER_ID)})
    await db.execute(text("DELETE FROM decks WHERE owner_id = :uid"), {"uid": str(MOCK_USER_ID)})
    
    # 5. Delete source logs
    await db.execute(text("""
        DELETE FROM source_logs WHERE source_id IN (
            SELECT id FROM sources WHERE user_id = :uid
        )
    """), {"uid": str(MOCK_USER_ID)})
    
    # 6. Delete source materials
    await db.execute(text("DELETE FROM source_materials WHERE user_id = :uid"), {"uid": str(MOCK_USER_ID)})
    
    # 7. Delete sources
    await db.execute(text("DELETE FROM sources WHERE user_id = :uid"), {"uid": str(MOCK_USER_ID)})
    
    await db.commit()
    logger.info("Test data cleared.")


async def seed_all_test_data(db: AsyncSession):
    """Seed the database with complete test data."""
    logger.info("Seeding test data...")
    
    # 1. Ensure mock user exists
    result = await db.execute(select(User).where(User.id == MOCK_USER_ID))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            id=MOCK_USER_ID,
            email="debug@deli.app",
            username="Debug User",
            settings={"daily_new_limit": 20, "daily_review_limit": 100},
        )
        db.add(user)
        await db.flush()
    
    # 2. Create Sources
    for source_data in get_test_sources():
        source = Source(**source_data)
        db.add(source)
    await db.flush()
    
    # 3. Create Source Materials
    for material_data in get_test_source_materials():
        material = SourceMaterial(**material_data)
        db.add(material)
    await db.flush()
    
    # 4. Create Decks
    for deck_data in get_test_decks():
        deck = Deck(**deck_data)
        db.add(deck)
    await db.flush()
    
    # 5. Create Cards (with proper deck association)
    for card_data in get_test_cards():
        deck_id = card_data.pop("deck_id")  # Remove deck_id from card data
        card = Card(
            id=card_data["id"],
            owner_id=MOCK_USER_ID,
            source_material_id=card_data.get("source_material_id"),
            type=card_data["type"],
            content=card_data["content"],
            status=card_data["status"],
            tags=card_data.get("tags"),
            batch_id=card_data.get("batch_id"),
            batch_index=card_data.get("batch_index"),
        )
        db.add(card)
        await db.flush()
        
        # Associate card with deck via many-to-many
        await db.execute(
            text("INSERT INTO card_decks (card_id, deck_id) VALUES (:cid, :did)"),
            {"cid": str(card.id), "did": str(deck_id)}
        )
    
    # 6. Create Study Progress for active cards
    for progress_data in get_test_study_progress():
        progress = StudyProgress(**progress_data)
        db.add(progress)
    
    # 7. Subscribe user to all decks
    for deck_id in DECK_IDS.values():
        sub = DeckSubscription(user_id=MOCK_USER_ID, deck_id=deck_id)
        db.add(sub)
    
    await db.commit()
    
    logger.info(
        f"Seeded: {len(get_test_sources())} sources, "
        f"{len(get_test_source_materials())} materials, "
        f"{len(get_test_decks())} decks, "
        f"{len(get_test_cards())} cards, "
        f"{len(get_test_study_progress())} study progress entries"
    )


async def reset_seed_data(db: AsyncSession):
    """Complete reset and reseed of test data - called on every server restart."""
    logger.info("=== Resetting seed data ===")
    await clear_all_test_data(db)
    await seed_all_test_data(db)
    logger.info("=== Seed data reset complete ===")
