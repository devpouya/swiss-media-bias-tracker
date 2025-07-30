# News Sentiment Analyzer

A web application that allows users to analyze sentiment of news articles from multiple sources on any given topic.

## Features

- **User-driven analysis**: Users select news sources, topic, and analysis type
- **Real-time processing**: Articles are scraped and analyzed on-demand
- **Multiple news sources**: Support for BBC, CNN, Reuters, and custom sources
- **Sentiment analysis**: Uses OpenAI GPT to analyze article sentiment
- **Simple dashboard**: Shows sentiment statistics and article summaries

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**:
   ```bash
   createdb news_agg
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and OpenAI API key
   ```

4. **Run the application**:
   ```bash
   cd app
   python -m uvicorn main:app --reload
   ```

5. **Access the application**:
   Open http://localhost:8000 in your browser

## Usage

1. Select one or more news sources
2. Enter a topic to analyze (e.g., "climate change", "Israel")
3. Click "Analyze" and wait for processing to complete
4. View sentiment statistics and individual article analyses

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL
- **Scraping**: newspaper3k with custom scrapers for major news sites
- **AI**: OpenAI GPT-3.5-turbo for sentiment analysis
- **Frontend**: Simple HTML/CSS/JavaScript

## API Endpoints

- `GET /` - Main application interface
- `POST /api/analyze` - Start new analysis
- `GET /api/results/{request_id}` - Get analysis results

## Bias Research Framework

### Overview
This project is evolving from simple sentiment analysis to sophisticated bias research using comparative analysis and Chain of Thought (CoT) reasoning.

### Research Goals
Instead of binary "biased/unbiased" classification, we aim to:

1. **Rank articles relatively** on contentious topics (e.g., Israel/Palestine, climate change, immigration)
2. **Identify bias direction** - which side of an issue the bias favors
3. **Provide reasoning** - why the LLM classified bias in a particular direction
4. **Create bias spectrums** - position articles from "Strongly Pro-Side A" to "Neutral" to "Strongly Pro-Side B"

### Example Research Topics
- **Israel/Palestine Conflict**: Compare how different sources frame the same events
- **Climate Change**: Analyze scientific vs skeptical framing of environmental data
- **Economic Policy**: Compare progressive vs conservative framing of economic policies
- **Healthcare**: Analyze public vs private healthcare system coverage

### Key Research Questions
1. Can LLMs consistently identify which direction bias leans when comparing articles?
2. What specific language patterns and framing techniques indicate bias direction?
3. How do different news sources systematically bias coverage of the same events?
4. Can we establish reliable "neutral baselines" for controversial topics?

### Chain of Thought Approach
Rather than simple classification, the system will:
1. **Extract factual claims** from articles using LLM parsing
2. **Verify facts** against authoritative sources (Wikipedia, government data)
3. **Identify main claims** and distinguish facts from interpretation
4. **Analyze language choices** and emotional framing
5. **Compare source selection** and quote attribution
6. **Explain reasoning** with specific text evidence and fact-check results
7. **Rank relatively** against other articles, weighted by factual accuracy

### Fact-Checking Integration
A key innovation is layering factual verification onto bias analysis:

**Fact Extraction**: LLMs identify verifiable claims (statistics, dates, events, quotes)
**Source Verification**: Cross-reference against Wikipedia API, government databases, academic sources
**Accuracy Scoring**: Rate articles on factual reliability alongside bias assessment
**Context Analysis**: Identify when facts are accurate but presented without necessary context
**Error-Bias Correlation**: Research how factual inaccuracies correlate with bias direction

**Example Research Questions:**
- Do pro-Israeli articles contain more factual errors than pro-Palestinian ones?
- How do climate change articles selectively present accurate but misleading statistics?
- Which types of factual claims are most susceptible to biased framing?

This approach transforms bias detection from a classification task into a comprehensive research tool for understanding how media shapes public discourse through both interpretive bias and factual manipulation.