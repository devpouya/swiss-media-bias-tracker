"""Swiss-focused bias analyzer with multilingual support"""

import google.generativeai as genai
import os
from typing import Dict, List
import json
import time
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SwissBiasAnalyzer:
    """Swiss media bias analyzer with multilingual support"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
            
        genai.configure(api_key=api_key)
        # Use Gemini 1.5 Flash for better multilingual support
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("Using Gemini 1.5 Flash for Swiss bias analysis")
        except:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("Using Gemini 2.0 Flash for Swiss bias analysis")
        
        self.last_request_time = 0
        self.min_delay = 6  # 6 seconds between requests to stay under 10/minute
    
    def analyze_article_bias(self, article: Dict, topic_id: str) -> Dict:
        """
        Analyze Swiss article bias for specific topic
        """
        if topic_id == "immigration-integration":
            return self._analyze_immigration_bias(article)
        elif topic_id == "eu-relations":
            return self._analyze_eu_relations_bias(article)
        elif topic_id == "climate-energy":
            return self._analyze_climate_energy_bias(article)
        elif topic_id == "swiss-politics":
            return self._analyze_swiss_politics_bias(article)
        else:
            raise ValueError(f"Unknown Swiss topic: {topic_id}")
    
    def _analyze_immigration_bias(self, article: Dict) -> Dict:
        """Analyze Immigration & Integration article for bias"""
        prompt = f"""
- You are a Swiss media bias expert. 
- You have a very important job. You read an article, and find out the bias of the article AS ACCURATELY AS POSSIBLE.
- You analyze the article for bias in the context of Swiss media, considering cultural and political nuances
- You use the following criteria to determine bias:
For 1. consider who is quoted, who is not quoted, and what perspectives are included or excluded. Who has written the article? What is their background?
For 2. consider the language used, especially loaded terms or euphemisms. Are there any terms that are particularly loaded or biased in the Swiss context?
Is the language neutral, or does it suggest a particular viewpoint? Does it explicitly mention the racial or citizenship background of individuals involved?
For 3. consider how statistics are presented, whether they are contextualized, and if they support a particular narrative. Are statistics cherry-picked to support a specific viewpoint?
For 4. consider the political context, including how different parties are represented and whether there is a balance between nationalist and internationalist viewpoints. Are the positions of different political parties represented fairly?
1. PERSPECTIVE BALANCE:
   - Are immigrant/refugee voices included alongside Swiss citizens?
   - How are political parties (SVP, SP, FDP) represented?
   - Balance between security concerns vs humanitarian aspects?

2. LANGUAGE CHOICES:
   - "Asylsuchende" vs "Asylanten" vs "Flüchtlinge"
   - "Ausländerkriminalität" vs "Kriminalität"
   - "Überfremdung" vs "Vielfalt" vs "Integration"
   - "Wirtschaftsflüchtlinge" vs "Migranten"

3. STATISTICAL FRAMING:
   - Are immigration statistics contextualized properly?
   - Focus on crime statistics vs economic contributions?
   - Cherry-picking data to support a narrative?

4. POLITICAL CONTEXT:
   - How are SVP positions presented vs other parties?
   - Balance between nationalist and internationalist viewpoints?
   - Discussion of Swiss humanitarian tradition?

After having gone through the article, and analyzing it, you will classify the article into one of the following categories:
Classify as:
- "restrictive": Favors tighter immigration controls, security concerns
- "neutral": Balanced presentation of immigration issues
- "liberal": Favors open immigration, integration support
Article Title: {article['headline']}
Article Content: {article['content'][:3000]}...
Return ONLY valid JSON:
{{
    "category": "restrictive|neutral|liberal",
    "confidence": 0.8,
    "main_reasons": ["Quotes only SVP politicians", "Uses loaded term 'Überfremdung'"],
    "key_indicators": ["source_imbalance", "loaded_language", "context_omission"]
}}
"""
        
        return self._get_gemini_analysis(prompt, article['headline'])
    
    def _analyze_eu_relations_bias(self, article: Dict) -> Dict:
        """Analyze EU Relations article for bias"""
        prompt = f"""
Analyze this Swiss article about EU relations and bilateral agreements for bias:

1. PERSPECTIVE BALANCE:
   - Pro-EU vs EU-skeptical viewpoints represented?
   - Business interests vs sovereignty concerns?
   - Urban vs rural perspectives on EU integration?

2. LANGUAGE CHOICES:
   - "Rahmenabkommen" vs "Unterwerfung" vs "Partnerschaft"
   - "Souveränität" vs "Isolation"
   - "Bilaterale Verträge" vs "Rosinenpickerei"
   - "Personenfreizügigkeit" vs "Masseneinwanderung"

3. ECONOMIC FRAMING:
   - Focus on benefits vs costs of EU relationship?
   - Swiss banking/finance interests represented?
   - Impact on different economic sectors?

4. POLITICAL CONTEXT:
   - How are different party positions presented?
   - Swiss neutrality and independence emphasized?
   - Historical context of Swiss-EU relations?

Article Title: {article['headline']}
Article Content: {article['content'][:3000]}...

Classify as:
- "pro_eu": Favors closer EU integration, bilateral agreements
- "neutral": Balanced analysis of EU relations
- "eu_skeptical": Emphasizes sovereignty, independence from EU

Return ONLY valid JSON:
{{
    "category": "pro_eu|neutral|eu_skeptical",
    "confidence": 0.8,
    "main_reasons": ["Emphasizes economic benefits of EU access", "Quotes mainly business leaders"],
    "key_indicators": ["source_selection", "economic_framing", "political_context"]
}}
"""
        
        return self._get_gemini_analysis(prompt, article['headline'])
    
    def _analyze_climate_energy_bias(self, article: Dict) -> Dict:
        """Analyze Climate & Energy Policy article for bias"""
        prompt = f"""
Analyze this Swiss article about climate and energy policy for bias:

1. PERSPECTIVE BALANCE:
   - Environmental groups vs business interests represented?
   - Rural vs urban energy perspectives?
   - Different cantonal approaches discussed?

2. LANGUAGE CHOICES:
   - "Klimawandel" vs "Klimahysterie" vs "Klimakrise"
   - "Energiewende" vs "Energiechaos" vs "Energieumbau"
   - "Erneuerbare Energien" vs "ineffiziente Technologien"
   - "CO2-Steuer" vs "Energieabgabe"

3. SCIENTIFIC FRAMING:
   - Are climate science facts presented accurately?
   - Economic costs vs environmental benefits balanced?
   - Swiss Alpine/hydroelectric context considered?

4. POLITICAL CONTEXT:
   - Green Party vs SVP/FDP positions on energy?
   - Federal vs cantonal energy competencies?
   - Swiss energy independence considerations?

Article Title: {article['headline']}
Article Content: {article['content'][:3000]}...

Classify as:
- "green_progressive": Favors aggressive climate action, renewable energy
- "neutral": Balanced analysis of climate/energy trade-offs  
- "conservative_business": Emphasizes economic costs, business concerns

Return ONLY valid JSON:
{{
    "category": "green_progressive|neutral|conservative_business",
    "confidence": 0.8,
    "main_reasons": ["Emphasizes economic costs of carbon tax", "Quotes business leaders extensively"],
    "key_indicators": ["economic_focus", "source_selection", "language_framing"]
}}
"""
        
        return self._get_gemini_analysis(prompt, article['headline'])
    
    def _analyze_swiss_politics_bias(self, article: Dict) -> Dict:
        """Analyze Swiss Politics article for bias"""
        prompt = f"""
Analyze this Swiss political article for bias:

1. PARTY REPRESENTATION:
   - Are all major parties (SVP, SP, FDP, Mitte, Grüne) fairly represented?
   - Government vs opposition balance?
   - Federal vs cantonal political perspectives?

2. LANGUAGE CHOICES:
   - Neutral political terminology vs loaded language?
   - "Populismus" vs "Bürgernähe"
   - "Kompromiss" vs "Verwässerung" vs "Ausgleich"
   - "Mitte-Politik" vs "Stillstand"

3. ELECTORAL FRAMING:
   - Urban vs rural voting patterns contextualized?
   - Swiss direct democracy (referendums) properly explained?
   - Historical voting trends vs current shifts?

4. INSTITUTIONAL CONTEXT:
   - Swiss consensus democracy principles respected?
   - Federal Council's collegial system explained?
   - Cantonal diversity and federalism considered?

Article Title: {article['headline']}
Article Content: {article['content'][:3000]}...

Classify as:
- "left_center": Favors SP, Greens, social democratic policies
- "neutral": Balanced coverage of Swiss political spectrum
- "right_center": Favors SVP, FDP, conservative/liberal policies

Return ONLY valid JSON:
{{
    "category": "left_center|neutral|right_center",
    "confidence": 0.8,
    "main_reasons": ["Focuses on SP climate proposals", "Minimal coverage of business concerns"],
    "key_indicators": ["party_balance", "policy_framing", "source_diversity"]
}}
"""
        
        return self._get_gemini_analysis(prompt, article['headline'])
    
    def _get_gemini_analysis(self, prompt: str, article_title: str) -> Dict:
        """Get analysis from Gemini API with rate limiting and retry logic"""
        max_retries = 3
        base_delay = 10  # Base delay for exponential backoff
        
        for attempt in range(max_retries):
            try:
                # Rate limiting: ensure minimum delay between requests
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.min_delay:
                    sleep_time = self.min_delay - time_since_last
                    print(f"Rate limiting: waiting {sleep_time:.1f}s before next request...")
                    time.sleep(sleep_time)
                
                self.last_request_time = time.time()
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=300,
                    )
                )
                
                print(f"Raw Gemini response for '{article_title[:50]}...': '{response.text}'")
                
                if not response.text or not response.text.strip():
                    print("Empty response from Gemini")
                    raise ValueError("Empty response from Gemini")
                
                # Clean the response text
                response_text = response.text.strip()
                
                # Sometimes Gemini wraps JSON in code blocks
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                elif response_text.startswith('```'):
                    response_text = response_text.replace('```', '').strip()
                
                print(f"Cleaned response: '{response_text}'")
                
                result = json.loads(response_text)
                
                # Validate required fields
                required_fields = ['category', 'confidence', 'main_reasons', 'key_indicators']
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                
                # Ensure confidence is within range
                result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))
                
                print(f"Bias analysis for '{article_title[:30]}...': {result['category']} (confidence: {result['confidence']})")
                return result
            
            except Exception as e:
                error_str = str(e)
                print(f"Attempt {attempt + 1}/{max_retries} failed: {error_str}")
                
                # Check if it's a rate limit error
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 5)
                        print(f"Rate limit hit, waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        continue
                
                # Check if it's a JSON parsing error
                elif "json" in error_str.lower():
                    if attempt < max_retries - 1:
                        print(f"JSON parsing failed, retrying in {base_delay}s...")
                        time.sleep(base_delay)
                        continue
                
                # For other errors, don't retry immediately
                if attempt == max_retries - 1:
                    print(f"All attempts failed for article: {article_title[:30]}...")
                    break
        
        # Return fallback result after all retries failed
        return {
            'category': 'neutral',
            'confidence': 0.0,
            'main_reasons': [f'Analysis failed after {max_retries} attempts - likely rate limited'],
            'key_indicators': ['rate_limit_error']
        }
    
    def get_bias_categories_for_topic(self, topic_id: str) -> List[str]:
        """Get valid bias categories for a Swiss topic"""
        categories = {
            "immigration-integration": ["restrictive", "neutral", "liberal"],
            "eu-relations": ["pro_eu", "neutral", "eu_skeptical"],
            "climate-energy": ["green_progressive", "neutral", "conservative_business"],
            "swiss-politics": ["left_center", "neutral", "right_center"]
        }
        
        return categories.get(topic_id, ["neutral"])
    
    def get_category_display_name(self, category: str, topic_id: str) -> str:
        """Get human-readable category name"""
        display_names = {
            "immigration-integration": {
                "restrictive": "Restrictive",
                "neutral": "Neutral", 
                "liberal": "Liberal"
            },
            "eu-relations": {
                "pro_eu": "Pro-EU",
                "neutral": "Neutral",
                "eu_skeptical": "EU-Skeptical"
            },
            "climate-energy": {
                "green_progressive": "Green/Progressive",
                "neutral": "Neutral",
                "conservative_business": "Conservative/Business"
            },
            "swiss-politics": {
                "left_center": "Left/Center",
                "neutral": "Neutral", 
                "right_center": "Right/Center"
            }
        }
        
        return display_names.get(topic_id, {}).get(category, category)