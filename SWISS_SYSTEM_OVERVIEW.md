# Swiss News Bias Analysis System

## 🇨🇭 System Overview

The system has been completely redesigned to focus on Swiss media bias analysis with multilingual support for Switzerland's four official languages.

## 📰 Swiss News Sources (9 total)

### German-speaking Switzerland (Deutschschweiz)
- **Tages-Anzeiger** (Center-Left, Zurich) - 2 RSS feeds
- **Neue Zürcher Zeitung (NZZ)** (Center-Right, Zurich) - 2 RSS feeds  
- **SRF** (Center, National) - 2 RSS feeds

### French-speaking Switzerland (Romandy)
- **Le Matin** (Center-Left, Romandy) - 1 RSS feed
- **Le Temps** (Center, Romandy) - 1 RSS feed
- **RTS** (Center, Romandy) - 1 RSS feed

### Italian-speaking Switzerland (Ticino)
- **Corriere del Ticino** (Center, Ticino) - 1 RSS feed
- **RSI** (Center, Ticino) - 1 RSS feed

### English (International/Expats)
- **SWI swissinfo.ch** (Center, National) - 1 RSS feed

## 🏛️ Swiss Political Topics (4 total)

### 1. Immigration & Integration
- **Positions**: Restrictive ↔ Liberal
- **Keywords**: 
  - DE: immigration, integration, ausländer, migration, asyl, flüchtling, svp
  - FR: immigration, intégration, étranger, migration, asile, réfugié
  - IT: immigrazione, integrazione, straniero, migrazione, asilo

### 2. EU Relations & Bilateral Agreements  
- **Positions**: Pro-EU ↔ EU-Skeptical
- **Keywords**:
  - DE: eu, europa, bilaterale, rahmenabkommen, personenfreizügigkeit
  - FR: ue, europe, bilatéral, accord-cadre, libre-circulation
  - IT: ue, europa, bilaterale, accordo-quadro, libera-circolazione

### 3. Climate & Energy Policy
- **Positions**: Green/Progressive ↔ Conservative/Business
- **Keywords**:
  - DE: klima, energie, co2, klimawandel, energiewende, erneuerbare
  - FR: climat, énergie, changement-climatique, transition-énergétique
  - IT: clima, energia, cambiamento-climatico, transizione-energetica

### 4. Swiss Politics & Elections
- **Positions**: Left/Center ↔ Right/Center
- **Keywords**:
  - DE: bundesrat, wahlen, abstimmung, svp, sp, fdp, parlament
  - FR: conseil-fédéral, élections, votation, udc, ps, plr, parlement
  - IT: consiglio-federale, elezioni, votazione, udc, ps, plr
  - EN: federal-council, elections, referendum, politics, parliament

## 🔍 Swiss Bias Analysis

### Specialized Swiss Context Analysis
- **Political party representation** (SVP, SP, FDP, Mitte, Grüne)
- **Regional perspectives** (Zurich vs Romandy vs Ticino)
- **Swiss institutional context** (direct democracy, federalism)
- **Language-specific loaded terms** ("Überfremdung", "Rahmenabkommen")

### Multilingual Bias Detection
- **German**: Recognizes Swiss German political terminology
- **French**: Swiss French political and media language
- **Italian**: Ticino-specific political discourse
- **English**: International/expat perspective on Swiss issues

## 🗄️ Database Schema Updates

### Enhanced TopicArticle Model
```sql
- language: "de", "fr", "it", "en"
- source_region: "zurich", "romandy", "ticino", "national"  
- bias_category: Topic-specific categories
- analysis_reasons: Swiss context-aware reasoning
```

### Swiss Author Bias Tracking
```sql
- immigration_restrictive/neutral/liberal
- eu_relations_pro_eu/neutral/eu_skeptical  
- climate_green_progressive/neutral/conservative_business
- politics_left_center/neutral/right_center
```

## 🚀 Key Features

✅ **Multilingual keyword matching** across 4 languages  
✅ **Swiss political context awareness** (parties, institutions)  
✅ **Regional bias detection** (German/French/Italian Switzerland)  
✅ **Rate-limiting with retry logic** for API calls  
✅ **Author tracking** across Swiss media landscape  
✅ **Topic-specific bias categories** for Swiss issues  

## 📊 Usage Examples

### Collect Immigration Articles
```python
collector = TopicNewsCollector()
articles = collector.collect_articles_for_topic("immigration-integration")
# Returns articles in DE/FR/IT from Swiss sources
```

### Analyze Swiss Political Bias
```python  
analyzer = SwissBiasAnalyzer()
result = analyzer.analyze_article_bias(article, "swiss-politics")
# Returns: "left_center", "neutral", or "right_center"
```

### Track Author Bias Patterns
```python
# Author bias across Swiss topics automatically tracked
# Shows if NZZ journalists lean right, Tages-Anzeiger left, etc.
```

## 🎯 Next Steps

1. **Website UI Update** - Swiss-themed interface
2. **Language Detection** - Automatic language identification  
3. **Regional Analysis** - Compare Zurich vs Romandy vs Ticino coverage
4. **Swiss Author Profiles** - Track journalist bias patterns
5. **Swiss Political Calendar** - Sync with elections, referendums

The system is now completely focused on Swiss media landscape with sophisticated multilingual bias detection! 🇨🇭