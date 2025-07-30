# Swiss Media Bias Tracker

A multilingual web application that analyzes bias in Swiss news coverage across Switzerland's four official languages (German, French, Italian, and English).

## Features

- **Swiss-focused analysis**: Tracks bias in Swiss news sources across linguistic regions
- **Multilingual interface**: Full support for DE/FR/IT/EN with automatic URL routing
- **Real-time processing**: Articles are collected and analyzed on-demand  
- **Swiss news sources**: Tages-Anzeiger, NZZ, SRF, Le Temps, Le Matin, RTS, Corriere del Ticino, RSI, SWI swissinfo.ch
- **AI-powered bias analysis**: Uses Google Gemini to analyze bias with Swiss political context
- **Modern responsive UI**: Clean design with language switching and article cards

## Swiss Topics Analyzed

1. **Immigration & Integration** - Analysis of restrictive vs liberal perspectives
2. **EU Relations & Bilateral Agreements** - Pro-EU vs EU-skeptical coverage  
3. **Climate & Energy Policy** - Green/progressive vs conservative/business framing
4. **Swiss Politics & Elections** - Left-center vs right-center political coverage

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Add your Google API key for Gemini
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

3. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access the application**:
   - English: http://localhost:8000/en/
   - German: http://localhost:8000/de/  
   - French: http://localhost:8000/fr/
   - Italian: http://localhost:8000/it/

## Usage

1. **Browse recent analysis**: View latest analyzed articles on the homepage
2. **Language switching**: Use the top-right language switcher to change interface language
3. **Topic exploration**: Click on topic cards to view detailed analysis by category
4. **Manual analysis**: Use `/admin` endpoint to trigger analysis for specific topics and date ranges
5. **View results**: Articles are categorized by bias direction with confidence scores and reasoning

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM and SQLite database
- **Translation**: JSON-based translation system with memory caching
- **News Collection**: RSS feeds and web scraping from 9 Swiss sources
- **AI Analysis**: Google Gemini 1.5 Flash for multilingual bias analysis
- **Frontend**: Responsive HTML/CSS with Swiss-themed design
- **Language Detection**: Automatic source language detection for article tagging

## API Endpoints

- `GET /{lang}/` - Multilingual homepage (lang: en/de/fr/it)
- `GET /api/topics` - Get all topics with statistics
- `GET /api/topic/{topic_id}` - Get articles for specific topic
- `POST /admin/trigger-analysis` - Manually trigger bias analysis
- `GET /{lang}/admin` - Admin dashboard for manual testing

## Swiss News Sources

**German-speaking Switzerland:**
- Tages-Anzeiger (Zurich, center-left)
- Neue Zürcher Zeitung (NZZ, center-right)
- Schweizer Radio und Fernsehen (SRF, public media)

**French-speaking Switzerland (Romandy):**
- Le Matin (popular daily)
- Le Temps (quality daily)
- Radio Télévision Suisse (RTS, public media)

**Italian-speaking Switzerland (Ticino):**
- Corriere del Ticino (regional daily)
- Radiotelevisione Svizzera (RSI, public media)

**International/English:**
- SWI swissinfo.ch (Swiss international service)

## Bias Analysis Framework

### Approach
Rather than simple "biased/unbiased" classification, the system:

1. **Context-aware analysis**: Considers Swiss political landscape (SVP, SP, FDP parties)
2. **Topic-specific categories**: Each topic has relevant bias dimensions
3. **Multilingual understanding**: Analyzes articles in their original language
4. **Evidence-based reasoning**: Provides specific examples of bias indicators
5. **Confidence scoring**: Rates analysis confidence based on evidence strength

### Bias Categories by Topic

**Immigration & Integration:**
- Restrictive (emphasizes concerns, limits)
- Liberal (emphasizes benefits, openness)  
- Neutral (balanced presentation)

**EU Relations:**
- Pro-EU (favors closer ties)
- EU-skeptical (favors independence)
- Neutral (balanced analysis)

**Climate & Energy:**
- Green/Progressive (pro-climate action)
- Conservative/Business (economic concerns)
- Neutral (balanced coverage)

**Swiss Politics:**
- Left-center (SP, Green perspectives)
- Right-center (SVP, FDP perspectives)
- Neutral (balanced political coverage)

### Analysis Factors

1. **Source Selection**: Who is quoted and given voice
2. **Language Choices**: Loaded terms vs neutral language
3. **Context Provision**: What background information is included/omitted
4. **Framing**: How issues are presented and prioritized
5. **Swiss Context**: Understanding of Swiss political and cultural nuances

This system provides researchers and citizens with tools to understand how Swiss media across different linguistic regions covers important political topics, revealing potential bias patterns in Switzerland's diverse media landscape.