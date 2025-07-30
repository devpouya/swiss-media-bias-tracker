"""Author extraction utilities for news articles"""

import re
from typing import Optional, List, Dict
from datetime import datetime
from app.models import Author
from sqlalchemy.orm import Session

class AuthorExtractor:
    """Extract and normalize author information from news articles"""
    
    # Common author patterns in different news sources
    AUTHOR_PATTERNS = [
        r"By\s+([A-Z][a-z]+ [A-Z][a-z]+)",  # "By John Smith"
        r"By\s+([A-Z]\. [A-Z][a-z]+)",      # "By J. Smith"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+CNN", # "John Smith, CNN"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+BBC", # "John Smith, BBC"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+Reuters", # "John Smith, Reuters"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+Associated Press", # "John Smith, Associated Press"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+Guardian", # "John Smith, Guardian"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+Al Jazeera", # "John Smith, Al Jazeera"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+New York Times", # "John Smith, New York Times"
        r"([A-Z][a-z]+ [A-Z][a-z]+),?\s+Wall Street Journal", # "John Smith, Wall Street Journal"
    ]
    
    # Staff/generic bylines to ignore
    IGNORE_BYLINES = {
        "staff", "editor", "correspondent", "reporter", "news desk", 
        "editorial board", "opinion", "wire services", "associated press",
        "reuters", "bloomberg", "news service", "staff writer"
    }
    
    def __init__(self):
        pass
    
    def extract_author_from_content(self, content: str, source: str) -> Optional[str]:
        """Extract author name from article content"""
        
        # Take first few paragraphs where bylines usually appear
        search_text = content[:1000]
        
        for pattern in self.AUTHOR_PATTERNS:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                author_name = match.group(1).strip()
                if self._is_valid_author_name(author_name):
                    return author_name
        
        return None
    
    def extract_author_from_headline(self, headline: str) -> Optional[str]:
        """Extract author from headline if present"""
        
        # Some headlines include author like "Analysis by John Smith: ..."
        analysis_pattern = r"Analysis by ([A-Z][a-z]+ [A-Z][a-z]+):"
        match = re.search(analysis_pattern, headline)
        if match:
            author_name = match.group(1).strip()
            if self._is_valid_author_name(author_name):
                return author_name
        
        return None
    
    def _is_valid_author_name(self, name: str) -> bool:
        """Check if extracted name is a valid author name"""
        name_lower = name.lower()
        
        # Skip generic bylines
        if name_lower in self.IGNORE_BYLINES:
            return False
        
        # Must have at least first and last name
        name_parts = name.split()
        if len(name_parts) < 2:
            return False
        
        # Check if it looks like a real name (not all caps, etc.)
        if name.isupper() or name.islower():
            return False
        
        return True
    
    def normalize_author_name(self, name: str) -> str:
        """Normalize author name for database storage and matching"""
        # Remove extra whitespace and standardize format
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Handle initials: "J. Smith" -> "j smith"
        name = re.sub(r'([A-Z])\.', r'\1', name)
        
        # Lowercase for matching
        return name.lower()
    
    def find_or_create_author(self, byline: str, source: str, db: Session) -> Optional[Author]:
        """Find existing author or create new one"""
        
        if not byline:
            return None
        
        normalized_name = self.normalize_author_name(byline)
        
        # Try to find existing author
        author = db.query(Author).filter(Author.normalized_name == normalized_name).first()
        
        if author:
            # Update existing author
            if source not in (author.sources or []):
                sources = author.sources or []
                sources.append(source)
                author.sources = sources
            
            # Add byline variation if not seen before
            variations = author.byline_variations or []
            if byline not in variations:
                variations.append(byline)
                author.byline_variations = variations
            
            author.last_seen = datetime.now()
            
        else:
            # Create new author
            author = Author(
                name=byline,
                normalized_name=normalized_name,
                byline_variations=[byline],
                sources=[source],
                first_seen=datetime.now(),
                last_seen=datetime.now()
            )
            db.add(author)
        
        return author
    
    def update_author_bias_stats(self, author: Author, topic_id: str, bias_category: str, confidence: float):
        """Update author's bias statistics"""
        
        # Update total articles
        author.total_articles = (author.total_articles or 0) + 1
        
        # Update average confidence
        if author.average_bias_confidence:
            # Running average
            total_confidence = author.average_bias_confidence * (author.total_articles - 1) + confidence
            author.average_bias_confidence = total_confidence / author.total_articles
        else:
            author.average_bias_confidence = confidence
        
        # Update topic-specific bias counts
        if topic_id == "israel-palestine":
            if bias_category == "pro_palestine":
                author.israel_palestine_pro_palestine = (author.israel_palestine_pro_palestine or 0) + 1
            elif bias_category == "neutral":
                author.israel_palestine_neutral = (author.israel_palestine_neutral or 0) + 1  
            elif bias_category == "pro_israel":
                author.israel_palestine_pro_israel = (author.israel_palestine_pro_israel or 0) + 1
        
        elif topic_id == "russia-ukraine":
            if bias_category == "pro_russia":
                author.russia_ukraine_pro_russia = (author.russia_ukraine_pro_russia or 0) + 1
            elif bias_category == "neutral":
                author.russia_ukraine_neutral = (author.russia_ukraine_neutral or 0) + 1
            elif bias_category == "pro_ukraine":
                author.russia_ukraine_pro_ukraine = (author.russia_ukraine_pro_ukraine or 0) + 1
    
    def get_author_bias_summary(self, author: Author, topic_id: str) -> Dict:
        """Get bias summary for an author on a specific topic"""
        
        if topic_id == "israel-palestine":
            pro_a = author.israel_palestine_pro_palestine or 0
            neutral = author.israel_palestine_neutral or 0
            pro_b = author.israel_palestine_pro_israel or 0
            labels = ["Pro-Palestine", "Neutral", "Pro-Israel"]
        elif topic_id == "russia-ukraine":
            pro_a = author.russia_ukraine_pro_russia or 0
            neutral = author.russia_ukraine_neutral or 0
            pro_b = author.russia_ukraine_pro_ukraine or 0
            labels = ["Pro-Russia", "Neutral", "Pro-Ukraine"]
        else:
            return {}
        
        total = pro_a + neutral + pro_b
        if total == 0:
            return {}
        
        return {
            "total_articles": total,
            "distribution": {
                labels[0].lower().replace("-", "_"): pro_a,
                "neutral": neutral,
                labels[1].lower().replace("-", "_"): pro_b
            },
            "percentages": {
                labels[0].lower().replace("-", "_"): (pro_a / total) * 100,
                "neutral": (neutral / total) * 100,
                labels[1].lower().replace("-", "_"): (pro_b / total) * 100
            },
            "labels": labels
        }