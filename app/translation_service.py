"""
Swiss Translation Service with caching and Gemini integration
"""

import json
import os
import hashlib
from typing import Dict, Optional
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class SwissTranslationService:
    """Translation service for Swiss Media Bias Tracker"""
    
    SUPPORTED_LANGUAGES = ["en", "de", "fr", "it"]
    DEFAULT_LANGUAGE = "en"
    
    def __init__(self):
        self.static_cache = {}  # Pre-loaded UI translations
        self.dynamic_cache = {} # Article title translations
        self.max_dynamic_entries = 1000  # LRU cache limit
        
        # Initialize Gemini for dynamic translations
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
            print("⚠️ No GOOGLE_API_KEY found - dynamic translations disabled")
        
        # Load static translations
        self.load_static_translations()
    
    def load_static_translations(self):
        """Load all static translations from JSON files"""
        translations_dir = Path(__file__).parent.parent / "translations"
        
        for lang in self.SUPPORTED_LANGUAGES:
            file_path = translations_dir / f"{lang}.json"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.static_cache[lang] = json.load(f)
                print(f"✓ Loaded {lang.upper()} translations ({len(self.static_cache[lang])} keys)")
            except FileNotFoundError:
                print(f"❌ Translation file not found: {file_path}")
                self.static_cache[lang] = {}
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in {file_path}: {e}")
                self.static_cache[lang] = {}
    
    def get_translation(self, key_path: str, lang: str, fallback: str = None) -> str:
        """
        Get static translation by dot-notation key path
        
        Args:
            key_path: Dot notation path like 'nav.recent_analysis' or 'topics.immigration_integration'
            lang: Target language code
            fallback: Fallback text if translation not found
        
        Returns:
            Translated text or fallback
        """
        if lang not in self.SUPPORTED_LANGUAGES:
            lang = self.DEFAULT_LANGUAGE
        
        # Navigate through nested dictionary
        try:
            translation_dict = self.static_cache.get(lang, {})
            keys = key_path.split('.')
            
            for key in keys:
                translation_dict = translation_dict[key]
            
            return translation_dict
        except (KeyError, TypeError):
            # Try fallback to English if not default language
            if lang != self.DEFAULT_LANGUAGE:
                try:
                    en_dict = self.static_cache.get(self.DEFAULT_LANGUAGE, {})
                    keys = key_path.split('.')
                    for key in keys:
                        en_dict = en_dict[key]
                    return en_dict
                except (KeyError, TypeError):
                    pass
            
            # Return fallback or key path
            return fallback or key_path
    
    def t(self, key_path: str, lang: str = DEFAULT_LANGUAGE) -> str:
        """Shorthand for get_translation"""
        return self.get_translation(key_path, lang)
    
    def detect_article_language(self, source: str) -> str:
        """Detect original language from Swiss news source"""
        source_languages = {
            "Tages-Anzeiger": "de",
            "Neue Zürcher Zeitung": "de", 
            "SRF (Schweizer Radio und Fernsehen)": "de",
            "Le Matin": "fr",
            "Le Temps": "fr",
            "RTS (Radio Télévision Suisse)": "fr",
            "Corriere del Ticino": "it",
            "RSI (Radiotelevisione Svizzera)": "it",
            "SWI swissinfo.ch": "en"
        }
        return source_languages.get(source, "de")  # Default to German
    
    async def translate_article_title(self, title: str, source_lang: str, target_lang: str) -> str:
        """
        Translate article title with caching
        
        Args:
            title: Original article title
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated title or original if translation fails
        """
        # Return original if same language
        if source_lang == target_lang:
            return title
        
        # Check cache first
        cache_key = self._generate_cache_key(title, source_lang, target_lang)
        if cache_key in self.dynamic_cache:
            return self.dynamic_cache[cache_key]
        
        # Translate using Gemini if available
        if self.gemini_model:
            try:
                translated = await self._gemini_translate_title(title, source_lang, target_lang)
                self._add_to_dynamic_cache(cache_key, translated)
                return translated
            except Exception as e:
                print(f"Translation failed for '{title[:50]}...': {e}")
        
        # Return original title if translation fails
        return title
    
    async def _gemini_translate_title(self, title: str, source_lang: str, target_lang: str) -> str:
        """Use Gemini to translate article title"""
        language_map = {
            "de": "German", "fr": "French", "it": "Italian", "en": "English"
        }
        
        source_lang_name = language_map.get(source_lang, source_lang)
        target_lang_name = language_map.get(target_lang, target_lang)
        
        prompt = f"""
Translate this Swiss news article title from {source_lang_name} to {target_lang_name}.
Keep the meaning accurate and preserve Swiss political/geographic terms.
Return ONLY the translated title, no explanation.

Title: {title}
"""
        
        response = self.gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=200,
            )
        )
        
        return response.text.strip() if response.text else title
    
    def _generate_cache_key(self, title: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        content = f"{source_lang}_{target_lang}_{title}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _add_to_dynamic_cache(self, key: str, value: str):
        """Add translation to dynamic cache with LRU eviction"""
        if len(self.dynamic_cache) >= self.max_dynamic_entries:
            # Remove oldest entry (first inserted)
            oldest_key = next(iter(self.dynamic_cache))
            del self.dynamic_cache[oldest_key]
        
        self.dynamic_cache[key] = value
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        return {
            "static_languages": len(self.static_cache),
            "dynamic_entries": len(self.dynamic_cache),
            "max_dynamic_entries": self.max_dynamic_entries,
            "gemini_available": self.gemini_model is not None
        }

# Global translation service instance
translation_service = SwissTranslationService()