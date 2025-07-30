import requests
from bs4 import BeautifulSoup
import feedparser
import hashlib
from typing import List, Dict
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
import re

class TopicNewsCollector:
    """Enhanced news collector for topic-based analysis"""
    
    # Swiss-focused topic configurations
    TOPICS = {
        "immigration-integration": {
            "display_name": "Immigration & Integration",
            "keywords": ["immigration", "integration", "ausländer", "migration", "asyl", "flüchtling", "einbürgerung", "svp", "fremdenfeindlichkeit", "zuwanderung"],
            "keywords_fr": ["immigration", "intégration", "étranger", "migration", "asile", "réfugié", "naturalisation"],
            "keywords_it": ["immigrazione", "integrazione", "straniero", "migrazione", "asilo", "rifugiato", "naturalizzazione"],
            "sides": ["restrictive", "liberal"]
        },
        "eu-relations": {
            "display_name": "EU Relations & Bilateral Agreements",
            "keywords": ["eu", "europa", "bilaterale", "rahmenabkommen", "personenfreizügigkeit", "brexit", "europapolitik", "neutralität"],
            "keywords_fr": ["ue", "europe", "bilatéral", "accord-cadre", "libre-circulation", "neutralité"],
            "keywords_it": ["ue", "europa", "bilaterale", "accordo-quadro", "libera-circolazione", "neutralità"],
            "sides": ["pro_eu", "eu_skeptical"]
        },
        "climate-energy": {
            "display_name": "Climate & Energy Policy",
            "keywords": ["klima", "energie", "co2", "klimawandel", "energiewende", "atomausstieg", "erneuerbare", "wasserkraft", "solar"],
            "keywords_fr": ["climat", "énergie", "changement-climatique", "transition-énergétique", "renouvelable", "hydraulique", "solaire"],
            "keywords_it": ["clima", "energia", "cambiamento-climatico", "transizione", "energetica", "rinnovabile", "idroelettrico", "solare", "svizzera"],
            "sides": ["green_progressive", "conservative_business"]
        },
        "swiss-politics": {
            "display_name": "Swiss Politics & Elections",
            "keywords": ["bundesrat", "wahlen", "abstimmung", "svp", "sp", "fdp", "cvp", "grüne", "parlament", "bundesversammlung"],
            "keywords_fr": ["conseil-fédéral", "élections", "votation", "udc", "ps", "plr", "pdc", "verts", "parlement"],
            "keywords_it": ["consiglio-federale", "elezioni", "votazione", "udc", "ps", "plr", "pdc", "verdi", "parlamento"],
            "keywords_en": ["federal-council", "elections", "referendum", "swiss-people-party", "social-democratic", "parliament", "politics", "voting"],
            "sides": ["left_center", "right_center"]
        }
    }
    
    # Swiss news source configurations
    NEWS_SOURCES = {
        "tagesanzeiger": {
            "name": "Tages-Anzeiger",
            "language": "de",
            "rss_feeds": [
                "https://www.tagesanzeiger.ch/rss.html",
                "https://www.tagesanzeiger.ch/schweiz/rss.html"
            ],
            "scrape_urls": ["https://www.tagesanzeiger.ch/schweiz"],
            "known_bias": "center_left",
            "region": "zurich"
        },
        "nzz": {
            "name": "Neue Zürcher Zeitung",
            "language": "de", 
            "rss_feeds": [
                "https://www.nzz.ch/recent.rss",
                "https://www.nzz.ch/schweiz.rss"
            ],
            "scrape_urls": ["https://www.nzz.ch/schweiz"],
            "known_bias": "center_right",
            "region": "zurich"
        },
        "srf": {
            "name": "SRF (Schweizer Radio und Fernsehen)",
            "language": "de",
            "rss_feeds": [
                "https://www.srf.ch/news/bnf/rss/1646",
                "https://www.srf.ch/news/bnf/rss/1890"
            ],
            "scrape_urls": ["https://www.srf.ch/news/schweiz"],
            "known_bias": "center",
            "region": "national"
        },
        "lematin": {
            "name": "Le Matin",
            "language": "fr",
            "rss_feeds": ["https://www.lematin.ch/rss"],
            "scrape_urls": ["https://www.lematin.ch/suisse"],
            "known_bias": "center_left",
            "region": "romandy"
        },
        "letemps": {
            "name": "Le Temps",
            "language": "fr",
            "rss_feeds": ["https://www.letemps.ch/rss"],
            "scrape_urls": ["https://www.letemps.ch/suisse"],
            "known_bias": "center",
            "region": "romandy"
        },
        "rts": {
            "name": "RTS (Radio Télévision Suisse)",
            "language": "fr",
            "rss_feeds": ["https://www.rts.ch/info/rss/info-rss.xml"],
            "scrape_urls": ["https://www.rts.ch/info/suisse/"],
            "known_bias": "center",
            "region": "romandy"
        },
        "corriere": {
            "name": "Corriere del Ticino",
            "language": "it",
            "rss_feeds": ["https://www.cdt.ch/rss"],
            "scrape_urls": ["https://www.cdt.ch/svizzera"],
            "known_bias": "center",
            "region": "ticino"
        },
        "rsi": {
            "name": "RSI (Radiotelevisione Svizzera)",
            "language": "it",
            "rss_feeds": ["https://www.rsi.ch/rss/notizie.xml"],
            "scrape_urls": ["https://www.rsi.ch/news/svizzera"],
            "known_bias": "center",
            "region": "ticino"
        },
        "swissinfo": {
            "name": "SWI swissinfo.ch",
            "language": "en",
            "rss_feeds": ["https://www.swissinfo.ch/eng/rss"],
            "scrape_urls": ["https://www.swissinfo.ch/eng"],
            "known_bias": "center",
            "region": "national"
        }
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def collect_articles_for_topic(self, topic_id: str, days_back: int = 7, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Collect articles for a specific topic from all sources
        If start_date and end_date are provided (format: "21.7.25"), use custom date range
        Otherwise use days_back from current date
        """
        if topic_id not in self.TOPICS:
            raise ValueError(f"Unknown topic: {topic_id}")
        
        topic_config = self.TOPICS[topic_id]
        all_articles = []
        
        # Parse custom date range if provided
        date_filter = None
        if start_date and end_date:
            try:
                # Parse dates in format "21.7.25" -> "21.07.2025"
                start_parts = start_date.split('.')
                end_parts = end_date.split('.')
                
                start_dt = datetime(2000 + int(start_parts[2]), int(start_parts[1]), int(start_parts[0]))
                end_dt = datetime(2000 + int(end_parts[2]), int(end_parts[1]), int(end_parts[0]))
                
                date_filter = (start_dt, end_dt)
                print(f"Collecting articles for topic: {topic_config['display_name']} from {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
            except Exception as e:
                print(f"Error parsing dates, using days_back instead: {e}")
                date_filter = None
        
        if not date_filter:
            print(f"Collecting articles for topic: {topic_config['display_name']} (last {days_back} days)")
        
        for source_id, source_config in self.NEWS_SOURCES.items():
            print(f"  Collecting from {source_config['name']}...")
            
            # Try RSS feeds first
            articles_from_rss = self._collect_from_rss(source_id, source_config, topic_config, days_back, date_filter)
            all_articles.extend(articles_from_rss)
            
            # If RSS didn't yield enough, try scraping
            if len(articles_from_rss) < 3:  # Threshold for trying scraping
                articles_from_scraping = self._collect_from_scraping(source_id, source_config, topic_config, days_back, date_filter)
                all_articles.extend(articles_from_scraping)
            
            time.sleep(1)  # Be respectful to servers
        
        # Remove duplicates based on content hash
        unique_articles = self._deduplicate_articles(all_articles)
        
        # Filter for topic relevance
        relevant_articles = self._filter_for_topic_relevance(unique_articles, topic_config)
        
        print(f"Collected {len(relevant_articles)} relevant articles for {topic_config['display_name']}")
        return relevant_articles
    
    def _collect_from_rss(self, source_id: str, source_config: Dict, topic_config: Dict, days_back: int, date_filter: tuple = None) -> List[Dict]:
        """Collect articles from RSS feeds"""
        articles = []
        
        # Set date filtering
        if date_filter:
            start_date, end_date = date_filter
        else:
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now()
        
        for rss_url in source_config.get('rss_feeds', []):
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries:
                    # Check if article is within date range
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    if pub_date:
                        if date_filter:
                            # Custom date range
                            if not (start_date <= pub_date <= end_date):
                                continue
                        else:
                            # Days back from now
                            if pub_date < start_date:
                                continue
                    
                    # Check if article is relevant to topic
                    title = entry.get('title', '')
                    description = entry.get('description', '')
                    
                    if self._matches_topic_keywords(title + ' ' + description, topic_config):
                        # Extract full article content
                        full_content = self._extract_full_article(entry.link)
                        if full_content:
                            articles.append({
                                'headline': title,
                                'url': entry.link,
                                'content': full_content,
                                'source': source_config['name'],
                                'published_date': pub_date if hasattr(entry, 'published_parsed') else datetime.now(),
                                'content_hash': hashlib.md5(full_content.encode()).hexdigest()
                            })
                        
            except Exception as e:
                print(f"Error collecting from RSS {rss_url}: {e}")
                continue
        
        return articles
    
    def _collect_from_scraping(self, source_id: str, source_config: Dict, topic_config: Dict, days_back: int, date_filter: tuple = None) -> List[Dict]:
        """Fallback: scrape articles from website"""
        articles = []
        
        # Set date filtering for comparison
        if date_filter:
            start_date, end_date = date_filter
        else:
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now()
        
        for scrape_url in source_config.get('scrape_urls', []):
            try:
                response = self.session.get(scrape_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Generic link extraction (this could be improved per-site)
                links = soup.find_all('a', href=True)
                article_urls = []
                
                for link in links:
                    href = link.get('href')
                    text = link.get_text().strip()
                    
                    # Check if link text is relevant to topic
                    if (href and len(text) > 20 and 
                        self._matches_topic_keywords(text, topic_config)):
                        full_url = urljoin(scrape_url, href)
                        article_urls.append((full_url, text))
                
                # Extract content from promising URLs
                for url, title in article_urls[:5]:  # Limit to prevent overload
                    content = self._extract_full_article(url)
                    if content and len(content) > 200:
                        # For scraped articles, we can't easily determine the exact publish date
                        # So we'll accept articles as long as they're topic-relevant
                        # In a production system, you'd want better date extraction per source
                        articles.append({
                            'headline': title,
                            'url': url,
                            'content': content,
                            'source': source_config['name'],
                            'published_date': datetime.now(),  # Approximate - could be improved with per-site date extraction
                            'content_hash': hashlib.md5(content.encode()).hexdigest()
                        })
                        
            except Exception as e:
                print(f"Error scraping from {scrape_url}: {e}")
                continue
        
        return articles
    
    def _extract_full_article(self, url: str) -> str:
        """Extract full article content from URL"""
        try:
            # Import here to avoid issues if newspaper3k isn't installed
            from newspaper import Article
            
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 100:
                return article.text
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting article from {url}: {e}")
            return None
    
    def _matches_topic_keywords(self, text: str, topic_config: Dict) -> bool:
        """Check if text contains topic-relevant keywords (multilingual)"""
        text_lower = text.lower()
        
        # Collect all keywords from all languages
        all_keywords = topic_config.get('keywords', [])
        all_keywords.extend(topic_config.get('keywords_fr', []))
        all_keywords.extend(topic_config.get('keywords_it', []))
        all_keywords.extend(topic_config.get('keywords_en', []))
        
        # Must contain at least one keyword
        matches = sum(1 for keyword in all_keywords if keyword.lower() in text_lower)
        return matches >= 1  # At least one keyword match
    
    def _filter_for_topic_relevance(self, articles: List[Dict], topic_config: Dict) -> List[Dict]:
        """Filter articles for strong topic relevance"""
        relevant_articles = []
        
        for article in articles:
            # Check both headline and content for keyword density
            full_text = f"{article['headline']} {article['content']}"
            
            # Collect all keywords from all languages
            all_keywords = topic_config.get('keywords', [])
            all_keywords.extend(topic_config.get('keywords_fr', []))
            all_keywords.extend(topic_config.get('keywords_it', []))
            all_keywords.extend(topic_config.get('keywords_en', []))
            
            keyword_matches = sum(1 for keyword in all_keywords 
                                if keyword.lower() in full_text.lower())
            
            # Require multiple keyword matches or strong presence in headline
            headline_matches = sum(1 for keyword in all_keywords 
                                 if keyword.lower() in article['headline'].lower())
            
            if keyword_matches >= 2 or headline_matches >= 1:
                relevant_articles.append(article)
        
        return relevant_articles
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on content hash"""
        seen_hashes = set()
        unique_articles = []
        
        for article in articles:
            content_hash = article['content_hash']
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_articles.append(article)
        
        return unique_articles
    
    def get_topic_config(self, topic_id: str) -> Dict:
        """Get configuration for a topic"""
        return self.TOPICS.get(topic_id)
    
    def get_all_topics(self) -> Dict:
        """Get all available topics"""
        return self.TOPICS