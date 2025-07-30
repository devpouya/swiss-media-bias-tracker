from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


# Swiss topic-based models
class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(String, primary_key=True)  # "immigration-integration", "eu-relations"
    display_name = Column(String, nullable=False)  # "Immigration & Integration"
    keywords = Column(JSON, nullable=False)  # ["immigration", "integration", "ausländer"]
    sides = Column(JSON, nullable=False)  # ["restrictive", "liberal"]
    total_articles = Column(Integer, default=0)
    last_processed = Column(DateTime)
    
    # 3-category distribution
    pro_side_a_count = Column(Integer, default=0)  # e.g., restrictive
    neutral_count = Column(Integer, default=0)
    pro_side_b_count = Column(Integer, default=0)  # e.g., liberal
    
    # Relationships
    articles = relationship("TopicArticle", back_populates="topic")


class Author(Base):
    __tablename__ = "authors"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False)  # lowercase, no punctuation for matching
    byline_variations = Column(JSON)  # Different ways author name appears ["John Smith", "J. Smith"]
    
    # Statistics
    total_articles = Column(Integer, default=0)
    first_seen = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now)
    
    # Bias analysis
    average_bias_confidence = Column(Float, default=0.0)
    
    # Swiss topic bias counts
    immigration_restrictive = Column(Integer, default=0)
    immigration_neutral = Column(Integer, default=0)
    immigration_liberal = Column(Integer, default=0)
    
    eu_relations_pro_eu = Column(Integer, default=0)
    eu_relations_neutral = Column(Integer, default=0)
    eu_relations_eu_skeptical = Column(Integer, default=0)
    
    climate_green_progressive = Column(Integer, default=0)
    climate_neutral = Column(Integer, default=0)
    climate_conservative_business = Column(Integer, default=0)
    
    politics_left_center = Column(Integer, default=0)
    politics_neutral = Column(Integer, default=0)
    politics_right_center = Column(Integer, default=0)
    
    # Source affiliations
    sources = Column(JSON)  # ["CNN", "BBC"] - sources this author writes for
    
    # Relationships
    articles = relationship("TopicArticle", back_populates="author")

class TopicArticle(Base):
    __tablename__ = "topic_articles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    author_id = Column(String, ForeignKey("authors.id"), nullable=True)
    
    # Article data
    headline = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)  # "Tages-Anzeiger", "NZZ", "SRF"
    author_byline = Column(String, nullable=True)
    published_date = Column(DateTime, nullable=False)
    content_hash = Column(String, nullable=False)
    
    # Multilingual support
    language = Column(String, nullable=True)  # "de", "fr", "it", "en"
    source_region = Column(String, nullable=True)  # "zurich", "romandy", "ticino", "national"
    
    # Swiss bias analysis results
    bias_category = Column(String)  # Topic-specific: "restrictive/liberal", "pro_eu/eu_skeptical", etc.
    confidence = Column(Float)  # 0.0-1.0
    analysis_reasons = Column(JSON)  # ["Uses loaded term 'Überfremdung'", "Only quotes SVP"]
    key_indicators = Column(JSON)  # ["loaded_language", "source_imbalance", "political_framing"]
    
    # Processing metadata
    analyzed_date = Column(DateTime)
    gemini_raw_response = Column(JSON)
    processing_status = Column(String, default="pending")
    
    # Relationships
    topic = relationship("Topic", back_populates="articles")
    author = relationship("Author", back_populates="articles")