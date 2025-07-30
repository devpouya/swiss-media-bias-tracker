from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from .database import get_db, engine
from .models import Base, Topic, TopicArticle
from .topic_collector import TopicNewsCollector
from .swiss_bias_analyzer import SwissBiasAnalyzer
from .translation_service import translation_service

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Swiss Media Bias Tracker")

# Initialize Swiss-focused services
topic_collector = TopicNewsCollector()
bias_analyzer = SwissBiasAnalyzer()

@app.get("/")
async def root():
    """Redirect to English homepage by default"""
    return RedirectResponse(url="/en/", status_code=302)

@app.get("/{lang}/", response_class=HTMLResponse)
async def homepage(lang: str, db: Session = Depends(get_db)):
    """Multilingual Swiss homepage - simplified version"""
    
    # Validate language
    if lang not in translation_service.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    # Get translation function for this language
    def t(key_path: str) -> str:
        return translation_service.get_translation(key_path, lang)
    
    # Get data
    topics = db.query(Topic).all()
    if not topics:
        initialize_topics(db)
        topics = db.query(Topic).all()
    
    recent_articles = db.query(TopicArticle).order_by(TopicArticle.analyzed_date.desc()).limit(8).all()
    
    # Generate article cards HTML
    article_cards_html = ""
    for article in recent_articles:
        # Get translated data
        topic_key = f"topics.{article.topic_id.replace('-', '_')}"
        topic_name = t(topic_key)
        bias_key = f"bias_categories.{article.bias_category or 'neutral'}"
        bias_display = t(bias_key)
        
        # Detect language and source
        original_lang = translation_service.detect_article_language(article.source).upper()
        source_name = article.source.split('(')[0].strip()
        confidence_pct = int((article.confidence or 0) * 100)
        
        # Format date
        date_str = article.published_date.strftime('%b %d') if article.published_date else t('common.never')
        
        # Truncate title
        title = article.headline[:85] + "..." if len(article.headline) > 85 else article.headline
        
        article_cards_html += f"""
        <div class="article-card" onclick="window.open('{article.url}', '_blank')">
            <div class="article-header">
                <span class="bias-badge {article.bias_category or 'neutral'}">{bias_display}</span>
                <div class="article-tags">
                    <span class="language-tag">{original_lang}</span>
                    <span class="source-tag">{source_name}</span>
                    <div class="confidence-meter">
                        <span>{confidence_pct}%</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {confidence_pct}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            <h3 class="article-title">{title}</h3>
            <div class="article-meta">
                <span>{date_str}</span> • <span>{topic_name}</span>
            </div>
        </div>
        """
    
    # Generate topic cards HTML
    topic_cards_html = ""
    for topic in topics:
        topic_key = f"topics.{topic.id.replace('-', '_')}"  
        topic_name = t(topic_key)
        last_updated = topic.last_processed.strftime('%B %d, %Y') if topic.last_processed else t('common.never')
        
        topic_cards_html += f"""
        <div class="topic-card" onclick="location.href='/{lang}/topic/{topic.id}'">
            <h3>{topic_name}</h3>
            <div class="topic-stats">
                <strong>{topic.total_articles}</strong> {t('common.articles_analyzed')}<br>
                {t('common.last_updated')}: {last_updated}
            </div>
        </div>
        """
    
    # Build complete HTML (using double braces for CSS to avoid f-string conflicts)
    html = f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t('site_title')}</title>
        <style>
            body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; padding: 40px; background: rgba(255,255,255,0.95); border-radius: 20px; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .header h1 {{ color: #d52b1e; font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }}
            .language-switcher {{ position: fixed; top: 20px; right: 20px; background: rgba(255,255,255,0.9); border-radius: 10px; padding: 8px; z-index: 1000; }}
            .lang-button {{ padding: 8px 12px; margin: 2px; text-decoration: none; color: #666; border-radius: 6px; display: inline-block; font-weight: 600; transition: all 0.2s; }}
            .lang-button.active {{ background: #d52b1e; color: white; }}
            .lang-button:hover {{ background: #d52b1e; color: white; }}
            .main-content {{ display: grid; grid-template-columns: 2fr 1fr; gap: 40px; }}
            .recent-articles, .topic-overview {{ background: rgba(255,255,255,0.95); border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .section-title {{ font-size: 1.8rem; margin-bottom: 20px; color: #333; font-weight: 700; }}
            .article-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 15px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: all 0.3s; }}
            .article-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
            .article-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
            .article-tags {{ display: flex; align-items: center; gap: 8px; }}
            .bias-badge {{ padding: 6px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; color: white; }}
            .restrictive {{ background: linear-gradient(135deg, #d32f2f, #f44336); }} 
            .liberal {{ background: linear-gradient(135deg, #1976d2, #2196f3); }} 
            .neutral {{ background: linear-gradient(135deg, #757575, #9e9e9e); }}
            .pro_eu {{ background: linear-gradient(135deg, #004494, #1565c0); }} 
            .eu_skeptical {{ background: linear-gradient(135deg, #d52b1e, #f44336); }} 
            .green_progressive {{ background: linear-gradient(135deg, #388e3c, #4caf50); }}
            .conservative_business {{ background: linear-gradient(135deg, #6a4c93, #9c27b0); }} 
            .left_center {{ background: linear-gradient(135deg, #e91e63, #f06292); }} 
            .right_center {{ background: linear-gradient(135deg, #ff5722, #ff7043); }}
            .language-tag {{ background: #e3f2fd; color: #1565c0; padding: 4px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: bold; }}
            .source-tag {{ background: #f3e5f5; color: #7b1fa2; padding: 4px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: bold; }}
            .confidence-meter {{ display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #666; }}
            .confidence-bar {{ width: 50px; height: 4px; background: #eee; border-radius: 2px; overflow: hidden; }}
            .confidence-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s; }}
            .article-title {{ font-size: 1.1rem; margin-bottom: 8px; color: #333; font-weight: 600; line-height: 1.4; }}
            .article-meta {{ font-size: 0.9rem; color: #666; }}
            .topic-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 15px; cursor: pointer; border-left: 4px solid #d52b1e; transition: all 0.3s; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
            .topic-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
            .topic-stats {{ color: #666; font-size: 0.9rem; }}
            .footer-info {{ margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 12px; text-align: center; }}
            @media (max-width: 768px) {{ 
                .main-content {{ grid-template-columns: 1fr; }} 
                .language-switcher {{ position: static; margin-bottom: 20px; text-align: center; }}
                .header {{ padding: 30px 20px; }}
                .header h1 {{ font-size: 2rem; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="language-switcher">
                <a href="/de/" class="lang-button {'active' if lang == 'de' else ''}">🇩🇪 DE</a>
                <a href="/fr/" class="lang-button {'active' if lang == 'fr' else ''}">🇫🇷 FR</a>
                <a href="/it/" class="lang-button {'active' if lang == 'it' else ''}">🇮🇹 IT</a>
                <a href="/en/" class="lang-button {'active' if lang == 'en' else ''}">🇬🇧 EN</a>
            </div>
            
            <div class="header">
                <h1>{t('site_title')}</h1>
                <p style="font-size: 1.2rem; color: #666; margin-bottom: 10px;">{t('tagline')}</p>
                <p style="font-style: italic; color: #888;">{t('subtitle')}</p>
            </div>
            
            <div class="main-content">
                <div class="recent-articles">
                    <h2 class="section-title">📰 {t('nav.recent_analysis')}</h2>
                    {article_cards_html or '<p style="color: #666; text-align: center; padding: 40px;">No recent articles available</p>'}
                </div>
                
                <div class="topic-overview">
                    <h2 class="section-title">📋 {t('nav.topics')}</h2>
                    {topic_cards_html}
                    
                    <div class="footer-info">
                        <h4 style="color: #333; margin-bottom: 15px;">{t('footer.swiss_media_sources')}</h4>
                        <p style="font-size: 0.85rem; color: #666; line-height: 1.6;">
                            🇩🇪 <strong>{t('footer.german_speaking')}:</strong> Tages-Anzeiger, NZZ, SRF<br>
                            🇫🇷 <strong>{t('footer.french_speaking')}:</strong> Le Matin, Le Temps, RTS<br>
                            🇮🇹 <strong>{t('footer.italian_speaking')}:</strong> Corriere del Ticino, RSI<br>
                            🇬🇧 <strong>{t('footer.international')}:</strong> SWI swissinfo.ch
                        </p>
                        <p style="font-size: 0.8rem; color: #888; margin-top: 15px; font-style: italic;">
                            {t('footer.powered_by')}<br>
                            {t('footer.analyzing_regions')}
                        </p>
                        <div style="margin-top: 15px;">
                            <a href="/{lang}/admin" style="color: #d52b1e; text-decoration: none; font-weight: 600;">{t('nav.admin_dashboard')}</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

# New topic-based endpoints

@app.get("/api/topics")
async def get_topics(db: Session = Depends(get_db)):
    """Get all available topics with their statistics"""
    topics = db.query(Topic).all()
    
    if not topics:
        # Initialize topics if they don't exist
        initialize_topics(db)
        topics = db.query(Topic).all()
    
    topic_data = []
    for topic in topics:
        topic_data.append({
            "id": topic.id,
            "display_name": topic.display_name,
            "total_articles": topic.total_articles,
            "last_processed": topic.last_processed.isoformat() if topic.last_processed else None,
            "distribution": {
                "pro_side_a": topic.pro_side_a_count,
                "neutral": topic.neutral_count,
                "pro_side_b": topic.pro_side_b_count
            }
        })
    
    return topic_data

@app.get("/api/topic/{topic_id}")
async def get_topic_articles(
    topic_id: str, 
    category: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get articles for a specific topic, optionally filtered by bias category"""
    
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Build query
    query = db.query(TopicArticle).filter(TopicArticle.topic_id == topic_id)
    
    if category:
        valid_categories = bias_analyzer.get_bias_categories_for_topic(topic_id)
        if category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Valid options: {valid_categories}")
        query = query.filter(TopicArticle.bias_category == category)
    
    # Order by most recent first
    articles = query.order_by(TopicArticle.published_date.desc()).limit(limit).all()
    
    # Format response
    article_data = []
    for article in articles:
        article_data.append({
            "id": article.id,
            "headline": article.headline,
            "url": article.url,
            "source": article.source,
            "published_date": article.published_date.isoformat(),
            "bias_category": article.bias_category,
            "bias_category_display": bias_analyzer.get_category_display_name(article.bias_category, topic_id) if article.bias_category else None,
            "confidence": article.confidence,
            "analysis_reasons": article.analysis_reasons,
            "key_indicators": article.key_indicators
        })
    
    return {
        "topic": {
            "id": topic.id,
            "display_name": topic.display_name,
            "total_articles": topic.total_articles
        },
        "articles": article_data,
        "total_returned": len(article_data)
    }

@app.post("/admin/trigger-analysis")
async def trigger_manual_analysis(
    background_tasks: BackgroundTasks,
    topic_id: str = "swiss-politics",
    days_back: int = 7,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Manual trigger for testing - analyze a topic immediately
    
    Args:
        topic_id: Topic to analyze
        days_back: Days back from current date (ignored if start_date/end_date provided)
        start_date: Start date in format "21.7.25" (optional)
        end_date: End date in format "29.7.25" (optional)
    """
    
    # Verify topic exists
    valid_topics = topic_collector.get_all_topics()
    if topic_id not in valid_topics:
        raise HTTPException(status_code=400, detail=f"Invalid topic. Valid options: {list(valid_topics.keys())}")
    
    # Start background processing with date range if provided
    background_tasks.add_task(process_topic_analysis, topic_id, days_back, start_date, end_date, db)
    
    # Generate appropriate message
    if start_date and end_date:
        message = f"Started analysis for {topic_id} from {start_date} to {end_date}"
    else:
        message = f"Started analysis for {topic_id} (last {days_back} days)"
    
    return {
        "status": "analysis_started",
        "topic_id": topic_id,
        "days_back": days_back,
        "start_date": start_date,
        "end_date": end_date,
        "message": message
    }

@app.get("/topic/{topic_id}")
async def topic_page(topic_id: str, db: Session = Depends(get_db)):
    """Basic topic page with article listing"""
    
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get recent articles
    articles = db.query(TopicArticle).filter(TopicArticle.topic_id == topic_id).order_by(TopicArticle.published_date.desc()).limit(20).all()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{topic.display_name} - News Bias Tracker</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
            .topic-header {{ margin-bottom: 30px; }}
            .topic-stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat-box {{ padding: 15px; border: 1px solid #ddd; border-radius: 5px; text-align: center; flex: 1; }}
            .pro-palestine {{ background: #e3f2fd; }}
            .neutral {{ background: #f3f4f6; }}
            .pro-israel {{ background: #fff3e0; }}
            .pro-russia {{ background: #ffebee; }}
            .pro-ukraine {{ background: #e8f5e8; }}
            .article-card {{ margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .bias-badge {{ display: inline-block; padding: 4px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
            .article-meta {{ color: #666; font-size: 14px; margin: 5px 0; }}
            .analysis {{ margin-top: 10px; font-size: 14px; }}
            .filter-buttons {{ margin: 20px 0; }}
            .filter-btn {{ padding: 8px 16px; margin: 5px; border: 1px solid #ddd; background: white; cursor: pointer; }}
            .filter-btn.active {{ background: #007bff; color: white; }}
        </style>
    </head>
    <body>
        <div class="topic-header">
            <h1>{topic.display_name} Coverage Analysis</h1>
            <p>{topic.total_articles} articles analyzed • Last updated: {topic.last_processed.strftime('%B %d, %Y') if topic.last_processed else 'Never'}</p>
        </div>
        
        <div class="topic-stats">
            <div class="stat-box {'pro-palestine' if topic_id == 'israel-palestine' else 'pro-russia'}">
                <h3>{topic.pro_side_a_count}</h3>
                <p>{'Pro-Palestine' if topic_id == 'israel-palestine' else 'Pro-Russia'}</p>
            </div>
            <div class="stat-box neutral">
                <h3>{topic.neutral_count}</h3>
                <p>Neutral</p>
            </div>
            <div class="stat-box {'pro-israel' if topic_id == 'israel-palestine' else 'pro-ukraine'}">
                <h3>{topic.pro_side_b_count}</h3>
                <p>{'Pro-Israel' if topic_id == 'israel-palestine' else 'Pro-Ukraine'}</p>
            </div>
        </div>
        
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterArticles('all')">All Articles</button>
            <button class="filter-btn" onclick="filterArticles('{'pro_palestine' if topic_id == 'israel-palestine' else 'pro_russia'}')">{'Pro-Palestine' if topic_id == 'israel-palestine' else 'Pro-Russia'}</button>
            <button class="filter-btn" onclick="filterArticles('neutral')">Neutral</button>
            <button class="filter-btn" onclick="filterArticles('{'pro_israel' if topic_id == 'israel-palestine' else 'pro_ukraine'}')">{'Pro-Israel' if topic_id == 'israel-palestine' else 'Pro-Ukraine'}</button>
        </div>
        
        <div id="articles-container">
    """
    
    # Add articles to HTML
    for article in articles:
        bias_class = article.bias_category or 'neutral'
        confidence_text = f"({int(article.confidence * 100)}% confidence)" if article.confidence else ""
        
        reasons_html = ""
        if article.analysis_reasons:
            reasons_html = "<ul>" + "".join([f"<li>{reason}</li>" for reason in article.analysis_reasons[:3]]) + "</ul>"
        
        html_content += f"""
            <div class="article-card" data-category="{bias_class}">
                <div class="bias-badge {bias_class}">{bias_analyzer.get_category_display_name(bias_class, topic_id)} {confidence_text}</div>
                <h3>{article.headline}</h3>
                <div class="article-meta">
                    <strong>{article.source}</strong> • {article.published_date.strftime('%B %d, %Y')}
                </div>
                <div class="analysis">
                    <strong>Analysis:</strong>
                    {reasons_html}
                </div>
                <a href="{article.url}" target="_blank">Read Original Article →</a>
            </div>
        """
    
    html_content += """
        </div>
        
        <script>
            function filterArticles(category) {
                const articles = document.querySelectorAll('.article-card');
                const buttons = document.querySelectorAll('.filter-btn');
                
                // Update button states
                buttons.forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                // Show/hide articles
                articles.forEach(article => {
                    if (category === 'all' || article.dataset.category === category) {
                        article.style.display = 'block';
                    } else {
                        article.style.display = 'none';
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/admin")
async def admin_dashboard():
    """Swiss admin interface for manual testing"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swiss Media Admin Dashboard</title>
        <style>
            body { 
                font-family: 'Helvetica Neue', Arial, sans-serif; 
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .header h1 { color: #d52b1e; font-size: 2.5em; margin-bottom: 10px; }
            .header h1::before { content: "🇨🇭 "; }
            .topic-section { 
                margin: 30px 0; 
                padding: 25px; 
                background: white;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                border-left: 5px solid #d52b1e;
            }
            .topic-section h2 {
                color: #333;
                font-size: 1.8em;
                margin-bottom: 20px;
                font-weight: 400;
            }
            button { 
                background: #d52b1e; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                margin: 8px; 
                font-size: 1em;
                transition: all 0.3s;
            }
            button:hover { 
                background: #b71c1c; 
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .status { 
                margin: 15px 0; 
                padding: 15px; 
                background: #f8f9fa; 
                border-radius: 8px; 
                border-left: 4px solid #28a745;
                font-family: monospace;
            }
            .home-link {
                text-align: center;
                margin-bottom: 30px;
            }
            .home-link a {
                color: #d52b1e;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.1em;
            }
        </style>
    </head>
    <body>
        <div class="home-link">
            <a href="/">← Back to Swiss Media Tracker</a>
        </div>
        
        <div class="header">
            <h1>Swiss Media Admin Dashboard</h1>
            <p>Manually trigger analysis for Swiss topics</p>
        </div>
        
        <div class="topic-section">
            <h2>🏛️ Immigration & Integration</h2>
            <button onclick="triggerAnalysis('immigration-integration', 7)">Analyze Last 7 Days</button>
            <button onclick="triggerAnalysis('immigration-integration', 1)">Analyze Last 24 Hours</button>
            <div id="status-immigration-integration" class="status"></div>
        </div>
        
        <div class="topic-section">
            <h2>🇪🇺 EU Relations & Bilateral Agreements</h2>
            <button onclick="triggerAnalysis('eu-relations', 7)">Analyze Last 7 Days</button>
            <button onclick="triggerAnalysis('eu-relations', 1)">Analyze Last 24 Hours</button>
            <div id="status-eu-relations" class="status"></div>
        </div>
        
        <div class="topic-section">
            <h2>🌿 Climate & Energy Policy</h2>
            <button onclick="triggerAnalysis('climate-energy', 7)">Analyze Last 7 Days</button>
            <button onclick="triggerAnalysis('climate-energy', 1)">Analyze Last 24 Hours</button>
            <div id="status-climate-energy" class="status"></div>
        </div>
        
        <div class="topic-section">
            <h2>🗳️ Swiss Politics & Elections</h2>
            <button onclick="triggerAnalysis('swiss-politics', 7)">Analyze Last 7 Days</button>
            <button onclick="triggerAnalysis('swiss-politics', 1)">Analyze Last 24 Hours</button>
            <div id="status-swiss-politics" class="status"></div>
        </div>
        
        <div class="topic-section">
            <h2>📊 View Results</h2>
            <button onclick="viewTopic('immigration-integration')">Immigration & Integration</button>
            <button onclick="viewTopic('eu-relations')">EU Relations</button>
            <button onclick="viewTopic('climate-energy')">Climate & Energy</button>
            <button onclick="viewTopic('swiss-politics')">Swiss Politics</button>
        </div>

        <script>
            async function triggerAnalysis(topicId, daysBack) {
                const statusDiv = document.getElementById(`status-${topicId}`);
                statusDiv.innerHTML = `Starting analysis for ${topicId}...`;
                
                try {
                    const response = await fetch('/admin/trigger-analysis', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `topic_id=${topicId}&days_back=${daysBack}`
                    });
                    
                    const data = await response.json();
                    statusDiv.innerHTML = `✓ ${data.message}`;
                } catch (error) {
                    statusDiv.innerHTML = `✗ Error: ${error.message}`;
                }
            }
            
            function viewTopic(topicId) {
                window.open(`/topic/${topicId}`, '_blank');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def initialize_topics(db: Session):
    """Initialize topics in database if they don't exist"""
    topics_config = topic_collector.get_all_topics()
    
    for topic_id, config in topics_config.items():
        existing_topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not existing_topic:
            topic = Topic(
                id=topic_id,
                display_name=config['display_name'],
                keywords=config['keywords'],
                sides=config['sides']
            )
            db.add(topic)
    
    db.commit()

async def process_topic_analysis(topic_id: str, days_back: int, start_date: Optional[str] = None, end_date: Optional[str] = None, db: Session = None):
    """Background task to analyze a topic"""
    try:
        if start_date and end_date:
            print(f"Starting topic analysis: {topic_id} from {start_date} to {end_date}")
        else:
            print(f"Starting topic analysis: {topic_id} (last {days_back} days)")
        
        # Get or create topic
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            initialize_topics(db)
            topic = db.query(Topic).filter(Topic.id == topic_id).first()
        
        # Collect articles with custom date range if provided
        print("Collecting articles...")
        articles = topic_collector.collect_articles_for_topic(topic_id, days_back, start_date, end_date)
        
        if not articles:
            print("No articles found")
            return
        
        print(f"Processing {len(articles)} articles...")
        
        # Process each article
        processed_count = 0
        for article_data in articles:
            try:
                # Check if article already exists (by content hash)
                existing = db.query(TopicArticle).filter_by(content_hash=article_data['content_hash']).first()
                if existing:
                    continue  # Skip duplicates
                
                # Analyze bias
                print(f"Analyzing: {article_data['headline'][:50]}...")
                bias_result = bias_analyzer.analyze_article_bias(article_data, topic_id)
                
                # Save to database
                topic_article = TopicArticle(
                    topic_id=topic_id,
                    headline=article_data['headline'],
                    content=article_data['content'],
                    url=article_data['url'],
                    source=article_data['source'],
                    published_date=article_data['published_date'],
                    content_hash=article_data['content_hash'],
                    bias_category=bias_result['category'],
                    confidence=bias_result['confidence'],
                    analysis_reasons=bias_result['main_reasons'],
                    key_indicators=bias_result['key_indicators'],
                    analyzed_date=datetime.now(),
                    gemini_raw_response=bias_result,
                    processing_status="completed"
                )
                
                db.add(topic_article)
                processed_count += 1
                
                # Commit every 5 articles to avoid losing progress
                if processed_count % 5 == 0:
                    db.commit()
                
            except Exception as e:
                print(f"Error processing article {article_data['headline'][:30]}: {e}")
                continue
        
        # Final commit
        db.commit()
        
        # Update topic statistics
        update_topic_statistics(topic_id, db)
        
        print(f"Completed analysis: {processed_count} articles processed for {topic_id}")
        
    except Exception as e:
        print(f"Error in topic analysis {topic_id}: {e}")
        import traceback
        traceback.print_exc()

def update_topic_statistics(topic_id: str, db: Session):
    """Update Swiss topic statistics after processing"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return
    
    # Count articles by category
    articles = db.query(TopicArticle).filter(TopicArticle.topic_id == topic_id).all()
    
    category_counts = {"pro_side_a": 0, "neutral": 0, "pro_side_b": 0}
    
    # Swiss topic mappings
    topic_mappings = {
        "immigration-integration": {"side_a": "restrictive", "side_b": "liberal"},
        "eu-relations": {"side_a": "pro_eu", "side_b": "eu_skeptical"},
        "climate-energy": {"side_a": "green_progressive", "side_b": "conservative_business"},
        "swiss-politics": {"side_a": "left_center", "side_b": "right_center"}
    }
    
    mapping = topic_mappings.get(topic_id, {"side_a": "side_a", "side_b": "side_b"})
    
    for article in articles:
        if not article.bias_category:
            continue
            
        if article.bias_category == mapping["side_a"]:
            category_counts["pro_side_a"] += 1
        elif article.bias_category == "neutral":
            category_counts["neutral"] += 1
        elif article.bias_category == mapping["side_b"]:
            category_counts["pro_side_b"] += 1
    
    # Update topic
    topic.total_articles = len(articles)
    topic.pro_side_a_count = category_counts["pro_side_a"]
    topic.neutral_count = category_counts["neutral"]
    topic.pro_side_b_count = category_counts["pro_side_b"]
    topic.last_processed = datetime.now()
    
    db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)