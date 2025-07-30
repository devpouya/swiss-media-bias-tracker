# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Start the application:**
```bash
cd app
python -m uvicorn main:app --reload
```

**Database setup:**
```bash
createdb news_agg
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Environment setup:**
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY
```

## Architecture Overview

This is a **FastAPI-based news sentiment analysis application** with the following key components:

### Core Data Flow
1. **User Request** → Analysis request created in database with status "processing"
2. **Background Task** → Scrapes articles from news sources using custom scrapers
3. **Article Processing** → Articles stored in `ArticleTemp` table with content hashing for deduplication
4. **Sentiment Analysis** → OpenAI GPT-3.5-turbo analyzes each article, results stored in `SentimentResult`
5. **Results** → Frontend polls `/api/results/{request_id}` until status changes to "completed"

### Key Components

**Database Models (`models.py`):**
- `AnalysisRequest`: Tracks analysis jobs with sources, topic, status
- `ArticleTemp`: Temporary storage for scraped articles with content hashing
- `SentimentResult`: Stores sentiment scores (-1 to 1), confidence, and summaries

**News Scraping (`scraper.py`):**
- Custom scrapers for BBC, CNN, Reuters using BeautifulSoup
- Generic scraper using newspaper3k for other sources
- Content deduplication via MD5 hashing
- Respectful scraping with 1-second delays between sources

**Sentiment Analysis (`sentiment_analyzer.py`):**
- OpenAI GPT-3.5-turbo integration with structured JSON responses
- Sentiment scores normalized to -1 (negative) to 1 (positive) range
- Confidence scoring and article summarization
- Batch processing capabilities with error handling

**API Structure (`main.py`):**
- Single-page application with embedded HTML/CSS/JavaScript
- Async background task processing using FastAPI BackgroundTasks
- Real-time status polling for long-running analysis jobs
- RESTful endpoints: `/api/analyze` (POST), `/api/results/{id}` (GET)

### Database Schema
- Uses PostgreSQL with SQLAlchemy ORM
- UUID primary keys for all tables
- Foreign key relationships between requests, articles, and sentiment results
- ARRAY column type for storing multiple news sources per request

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (defaults to SQLite for development)
- `GOOGLE_API_KEY`: Required for Gemini 2.0 Flash sentiment analysis (falls back to dummy analyzer if not provided)

The application handles long-running analysis jobs through background processing, allowing users to submit requests and poll for results without blocking the main thread.

## Bias Research Framework

### Research Objectives
This system aims to develop sophisticated bias detection that goes beyond binary "biased/unbiased" classification to provide:

1. **Comparative Bias Analysis**: Rank articles relative to each other on contentious topics
2. **Directional Bias Detection**: Identify which side of an issue the bias leans toward
3. **Reasoning Transparency**: Use Chain of Thought (CoT) prompting to explain bias assessment
4. **Context-Aware Evaluation**: Assess bias within the context of a specific topic/conflict
5. **Fact-Based Verification**: Cross-reference article claims against authoritative sources

### Methodology

**Step 1: Topic-Focused Collection**
- Gather articles on a specific contentious topic (e.g., Israel/Palestine conflict)
- Ensure diverse source representation across the bias spectrum
- Create article clusters by sub-topics within the main issue

**Step 2: Relative Bias Ranking**
- Compare articles pairwise: "Is Article A more biased toward Side X than Article B?"
- Build a relative ranking system rather than absolute scores
- Use multiple LLM evaluations for consensus scoring

**Step 3: Chain of Thought Analysis**
- Prompt LLM to explain its reasoning step-by-step
- Identify specific text passages that indicate bias
- Analyze language choices, source selection, and framing decisions
- Generate explanations for why bias leans in a particular direction

**Step 4: Fact Verification Layer**
- Extract factual claims from articles using LLM parsing
- Cross-reference claims against authoritative sources (Wikipedia, government data, academic sources)
- Identify factual inaccuracies, omissions, or misrepresentations
- Distinguish between factual errors and interpretive bias

**Step 5: Bias Spectrum Mapping**
- Create a spectrum from "Strongly Pro-Side A" to "Neutral" to "Strongly Pro-Side B"
- Position articles along this spectrum based on comparative analysis
- Weight positioning by factual accuracy scores
- Identify neutral baseline articles for calibration

### Research Questions
1. Can LLMs consistently identify directional bias when comparing articles?
2. What linguistic and structural features most reliably indicate bias direction?
3. How does bias manifest differently across news sources and article types?
4. Can we create a reliable "neutrality baseline" for controversial topics?
5. How do factual inaccuracies correlate with bias direction and strength?
6. Can we distinguish between intentional misinformation and interpretive bias?
7. Which types of factual claims are most susceptible to biased presentation?

### Implementation Approach
- **CoT Prompting**: "First, identify the main claims in this article. Then, analyze the language used. Finally, compare this framing to how the opposing side might present the same facts."
- **Comparative Analysis**: Present pairs of articles and ask for relative bias assessment
- **Evidence Extraction**: Require LLM to cite specific text passages supporting its bias assessment
- **Multi-perspective Validation**: Cross-check assessments using different prompt approaches

### Example CoT Prompts

**Fact Extraction Prompt:**
```
Extract all factual claims from this article that can be verified against external sources:

Article: [CONTENT]

For each claim, identify:
1. The specific factual assertion
2. Whether it includes numbers, dates, names, or events
3. The level of specificity (vague vs precise)
4. The source attribution (if any)

Return: {"factual_claims": [{"claim": "text", "type": "statistic|event|quote|date", "source": "attribution", "verifiable": true|false}]}
```

**Fact Verification Prompt:**
```
Compare these article claims against reference information:

Article Claims: [EXTRACTED_CLAIMS]
Reference Source: [WIKIPEDIA/AUTHORITATIVE_SOURCE]

For each claim, determine:
1. Accuracy: correct|incorrect|partially_correct|unverifiable
2. Context: Does the article provide necessary context?
3. Omissions: What relevant information is missing?
4. Framing: How does presentation affect interpretation?

Return: {"fact_check": [{"claim": "text", "accuracy": "status", "reference": "source_text", "context_issues": "explanation"}]}
```

**Enhanced Bias Analysis:**
```
Analyze this article about [TOPIC] for bias using chain of thought reasoning:

Step 1: Identify the main claims and facts presented
Step 2: Verify factual accuracy against reference sources
Step 3: Analyze the language choices (neutral vs loaded terms)
Step 4: Examine source selection and quote attribution
Step 5: Consider what perspectives or context might be missing
Step 6: Determine how factual errors or omissions affect bias direction

Article: [CONTENT]
Reference Facts: [VERIFIED_FACTS]

Respond with your reasoning for each step, then conclude with:
{"bias_direction": "pro_side_a|neutral|pro_side_b", "bias_strength": 0.0-1.0, "factual_accuracy": 0.0-1.0, "evidence": ["quote1", "quote2"], "fact_issues": ["error1", "omission2"], "reasoning": "explanation"}
```

**Comparative Analysis:**
```
Compare these two articles on [TOPIC] and determine which is more biased toward [SIDE A] vs [SIDE B]:

Article A: [CONTENT A]
Article B: [CONTENT B]

Think step by step:
1. What are the key differences in how they frame the issue?
2. Which uses more loaded language or emotional appeals?
3. Which provides more balanced source attribution?
4. Which omits more relevant context?

Conclusion: {"more_biased": "A|B|equal", "direction": "toward_side_a|toward_side_b", "confidence": 0.0-1.0}
```

### Data Structure Planning

**Enhanced Database Models:**
- `BiasAnalysis` table with fields: `bias_direction`, `bias_strength`, `factual_accuracy`, `evidence_quotes`, `reasoning`, `comparison_group`
- `FactualClaim` table: `claim_text`, `claim_type`, `source_attribution`, `verification_status`
- `FactCheck` table: `claim_id`, `reference_source`, `accuracy_status`, `context_issues`
- `ReferenceSource` table: Wikipedia articles, government data, academic papers used for verification
- `ArticleComparison` table for pairwise rankings with factual accuracy weighting
- `BiasSpectrum` table to track relative positioning on controversial topics
- `TopicClusters` table to group related articles for comparative analysis

**Research Workflow:**
1. Collect articles on specific controversial topic
2. Extract factual claims using LLM parsing
3. Verify claims against authoritative sources (Wikipedia API, government databases)
4. Perform individual CoT bias analysis incorporating fact-check results
5. Run pairwise comparisons within topic clusters
6. Generate bias spectrum ranking weighted by factual accuracy
7. Analyze correlation between factual errors and bias direction
8. Extract common bias patterns and linguistic markers

**Fact Source Integration:**
- **Wikipedia API**: For historical events, biographical data, basic statistics
- **Government APIs**: Census data, economic indicators, policy details
- **Academic Sources**: Scientific studies, research findings
- **News Archives**: Cross-reference against multiple established sources
- **Primary Sources**: Official statements, documents, transcripts

## Media Literacy Integration Framework

Based on comprehensive media literacy research (BIAS_.md), the system incorporates nine key dimensions of bias detection beyond simple sentiment analysis:

### **1. Source Diversity Analysis**
**Objective**: Detect over-reliance on "official" sources vs. affected communities
**Implementation**:
- Extract and classify all quoted sources (official/unofficial, expert/ordinary, government/corporate/activist)
- Calculate balance ratios and quote length by source type
- Identify demographic diversity gaps in source selection
- Flag articles that exclude perspectives of those most affected by the issue

**Database**: `SourceProfile` table tracking `source_type`, `quote_length`, `demographic_category`, `expertise_level`

**Example Detection**: "31% Afghan sources in US Afghan withdrawal coverage, only 5% Afghan women despite focus on women's rights"

### **2. Media Ownership & Conflict Analysis**
**Objective**: Identify how media ownership creates coverage bias
**Implementation**:
- Maintain comprehensive media ownership database (corporations, billionaires, hedge funds)
- Detect conflicts when coverage topics relate to owner interests
- Track corporate sponsorship influence on content
- Analyze systematic patterns in owner-influenced coverage

**Example Detection**: "Washington Post (Bezos-owned) coverage of wealth taxes and space programs shows systematic pro-owner bias"

### **3. Implicit Assumption & Stereotype Detection**
**Objective**: Identify unstated assumptions that shape narrative framing
**Implementation**:
- Use CoT prompting to extract implicit assumptions: "What does this article assume without stating?"
- Detect systematic treatment patterns for different groups/issues
- Identify missing perspectives and contextual omissions
- Analyze story selection bias (street crime vs. wage theft coverage patterns)

**Example Detection**: "Heavy shoplifting coverage vs. minimal wage theft reporting suggests assumption that street crime is more significant than corporate crime"

### **4. Loaded Language Detection System**
**Objective**: Identify terminology that shapes public opinion through word choice
**Implementation**:
- Build context-aware loaded language dictionary for key topics
- Detect patterns: "government-run" vs "public", "proxy" vs "ally", "divisive" vs "controversial"
- Analyze emotional framing through language choice
- Suggest neutral alternatives for loaded terminology

**Database**: `LoadedTerms` table with `original_term`, `neutral_alternative`, `topic_context`, `bias_direction`

**Example Detection**: "Medicare for All described as 'government-run' (negative framing) rather than 'public' (neutral)"

### **5. False Balance Detection**
**Objective**: Identify when "balanced" coverage gives equal weight to truth and disinformation
**Implementation**:
- Cross-reference competing claims against factual sources
- Detect disproportionate coverage of fringe vs. consensus positions
- Identify missing historical/power context in "balanced" reporting
- Flag articles that normalize disinformation through false equivalence

**Example Detection**: "COVID vaccine article presents 'tough decision' framing despite clear medical consensus favoring vaccination"

### **6. Visual Analysis Integration**
**Objective**: Detect how images and charts manipulate story perception
**Implementation**:
- Computer vision analysis of image content vs. article topic relevance
- Chart data extraction and verification against claims
- Geographic/temporal mismatch detection between visuals and content
- Emotional manipulation scoring for image selection

**Example Detection**: "COVID articles about Africa show corpses/funeral homes despite low infection rates, while East Asia articles show no death imagery despite higher casualties"

### **7. Headline-Content Mismatch Detection**
**Objective**: Identify misleading headlines that don't match article content
**Implementation**:
- Extract main claims from headlines vs. article body
- Detect contradictions between headline and content
- Identify crucial context omitted from headlines
- Score headlines for click-bait sensationalism vs. accuracy

**Example Detection**: "'Hundreds infected despite vaccination' headline buries 0.09% rate deep in article"

### **8. Story Prominence Analysis**
**Objective**: Analyze how story placement shapes perceived importance
**Implementation**:
- Track homepage/front page placement patterns
- Compare coverage volume allocation across different topics
- Analyze timing of story publication (buried vs. highlighted)
- Generate prominence-to-importance ratio scores

**Example Detection**: "Peloton ad receives 10x more coverage than $22 billion military budget increase"

### **9. Newsroom Diversity Impact Tracking**
**Objective**: Correlate newsroom composition with coverage patterns
**Implementation**:
- Maintain newsroom demographic databases for major outlets
- Analyze coverage blind spots related to newsroom composition
- Track decision-maker diversity in editorial choices
- Weight bias assessments by newsroom representation

**Research Finding**: "83% white newsroom staff affects coverage of racial justice issues, reproductive rights, immigration"

### **Enhanced Database Architecture**

```python
class MediaLiteracyAnalysis(Base):
    """Comprehensive media literacy metrics per article"""
    article_id = Column(String, ForeignKey("articles_temp.id"))
    source_diversity_score = Column(Float)  # 0-1 official vs affected sources ratio
    loaded_language_count = Column(Integer)  # number of loaded terms detected
    loaded_terms = Column(JSON)  # specific terms and neutral alternatives
    false_balance_detected = Column(Boolean)  # disinformation given equal weight
    headline_mismatch_score = Column(Float)  # 0-1 headline accuracy to content
    ownership_conflicts = Column(JSON)  # detected owner interest conflicts
    implicit_assumptions = Column(JSON)  # unstated assumptions identified
    stereotype_patterns = Column(JSON)  # systematic bias patterns
    visual_manipulation_score = Column(Float)  # misleading imagery/charts
    prominence_score = Column(Float)  # story placement vs importance

class SourceProfile(Base):
    """Individual source analysis within articles"""
    analysis_id = Column(String, ForeignKey("media_literacy_analysis.id"))
    source_name = Column(String)
    source_type = Column(String)  # official, expert, ordinary, activist, corporate
    quote_length = Column(Integer)
    demographic_category = Column(String)
    expertise_level = Column(String)
    perspective_represented = Column(String)  # which viewpoint this source represents

class MediaOutletProfile(Base):
    """Outlet-level bias patterns and characteristics"""
    outlet_name = Column(String, primary_key=True)
    ownership_structure = Column(JSON)  # parent companies, billionaire owners
    newsroom_diversity = Column(JSON)  # demographic composition data
    funding_sources = Column(JSON)  # advertisers, sponsors, conflicts
    systematic_biases = Column(JSON)  # detected patterns across coverage
    credibility_score = Column(Float)  # overall factual accuracy rating
```

### **Comprehensive Analysis Workflow**

1. **Extract Sources**: Identify all quoted individuals and their classifications
2. **Analyze Language**: Detect loaded terminology and suggest neutral alternatives  
3. **Verify Claims**: Cross-reference factual assertions against authoritative sources
4. **Assess Balance**: Determine if competing perspectives receive proportional, accurate coverage
5. **Check Visuals**: Analyze images/charts for relevance and potential manipulation
6. **Compare Headlines**: Verify headline accuracy against article content
7. **Evaluate Prominence**: Assess story placement relative to importance
8. **Identify Assumptions**: Extract implicit assumptions and missing perspectives
9. **Generate Literacy Score**: Combine all metrics into comprehensive media literacy assessment

This framework transforms the system from simple bias detection into a sophisticated **media literacy research platform** capable of identifying the subtle manipulation techniques documented in contemporary journalism research.