# Document Parser Service - Parse CSV, MD files into flashcards
import csv
import io
import re
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedCard:
    """Represents a parsed flashcard from document."""
    type: str  # 'qa', 'mcq', 'cloze'
    question: str
    answer: Optional[str] = None
    options: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    explanation: Optional[str] = None


class DocumentParser:
    """Parse various document formats into flashcards."""
    
    SUPPORTED_EXTENSIONS = ['.csv', '.md', '.txt']
    
    def parse(self, filename: str, content: bytes) -> List[ParsedCard]:
        """Parse document content into cards based on file extension."""
        ext = self._get_extension(filename).lower()
        
        if ext == '.csv':
            return self._parse_csv(content)
        elif ext in ['.md', '.txt']:
            return self._parse_markdown(content)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _get_extension(self, filename: str) -> str:
        """Extract file extension."""
        if '.' in filename:
            return '.' + filename.rsplit('.', 1)[-1]
        return ''
    
    def _parse_csv(self, content: bytes) -> List[ParsedCard]:
        """
        Parse CSV file into cards.
        Expected columns: question, answer, [type], [tags], [options], [explanation]
        """
        cards = []
        text = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        
        for row in reader:
            # Normalize column names (lowercase, strip)
            row = {k.lower().strip(): v for k, v in row.items()}
            
            question = row.get('question', '').strip()
            answer = row.get('answer', '').strip()
            
            if not question:
                continue
            
            card_type = row.get('type', 'qa').strip().lower()
            if card_type not in ['qa', 'mcq', 'cloze', 'flashcard']:
                card_type = 'qa'
            if card_type == 'flashcard':
                card_type = 'qa'
            
            # Parse tags (comma-separated)
            tags_str = row.get('tags', '')
            tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else None
            
            # Parse options for MCQ (semicolon or comma separated)
            options = None
            if card_type == 'mcq':
                options_str = row.get('options', '')
                if options_str:
                    options = [o.strip() for o in options_str.split(';') if o.strip()]
                    if len(options) < 2:
                        options = [o.strip() for o in options_str.split(',') if o.strip()]
            
            explanation = row.get('explanation', '').strip() or None
            
            cards.append(ParsedCard(
                type=card_type,
                question=question,
                answer=answer if answer else None,
                options=options,
                tags=tags,
                explanation=explanation,
            ))
        
        return cards
    
    def _parse_markdown(self, content: bytes) -> List[ParsedCard]:
        """
        Parse Markdown file into cards.
        
        Supported formats:
        1. Q: ... A: ... blocks
        2. ## Question + Answer under heading
        3. - Q: ... | A: ... (inline)
        """
        cards = []
        text = content.decode('utf-8')
        
        # Strategy 1: Q: / A: blocks
        qa_pattern = re.compile(
            r'(?:^|\n)\s*Q:\s*(.+?)(?:\n\s*A:\s*(.+?))?(?=\n\s*Q:|\n\s*---|\n\s*##|\Z)',
            re.DOTALL | re.IGNORECASE
        )
        
        matches = qa_pattern.findall(text)
        for q, a in matches:
            question = q.strip()
            answer = a.strip() if a else None
            if question:
                cards.append(ParsedCard(
                    type='qa',
                    question=question,
                    answer=answer,
                ))
        
        # If no Q:/A: found, try header-based parsing
        if not cards:
            # Split by ## headers
            sections = re.split(r'\n##\s+', text)
            for section in sections[1:]:  # Skip content before first ##
                lines = section.strip().split('\n', 1)
                if len(lines) >= 1:
                    question = lines[0].strip()
                    answer = lines[1].strip() if len(lines) > 1 else None
                    if question:
                        cards.append(ParsedCard(
                            type='qa',
                            question=question,
                            answer=answer,
                        ))
        
        return cards


# Singleton instance
document_parser = DocumentParser()
