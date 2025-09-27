"""
Language detection and management utilities for Browser4All
"""
import json
import locale
import os
from typing import Dict, Optional, Any
from pathlib import Path

# Supported languages with their configurations
SUPPORTED_LANGUAGES = {
    'en': {
        'name': 'English',
        'speech_code': 'en-US',
        'elevenlabs_voice': '21m00Tcm4TlvDq8ikWAM',  # Rachel
        'locale_codes': ['en_US', 'en_GB', 'en_CA', 'en_AU']
    },
    'es': {
        'name': 'Español',
        'speech_code': 'es-ES',
        'elevenlabs_voice': 'VR6AewLTigWG4xSOukaG',  # Pablo
        'locale_codes': ['es_ES', 'es_MX', 'es_AR', 'es_CO']
    },
    'fr': {
        'name': 'Français',
        'speech_code': 'fr-FR',
        'elevenlabs_voice': 'Xb7hH8MSUJpSbSDYk0k2',  # Alice
        'locale_codes': ['fr_FR', 'fr_CA', 'fr_BE', 'fr_CH']
    },
    'de': {
        'name': 'Deutsch',
        'speech_code': 'de-DE',
        'elevenlabs_voice': 'TxGEqnHWrfWFTfGW9XjX',  # Klaus
        'locale_codes': ['de_DE', 'de_AT', 'de_CH']
    },
    'zh': {
        'name': '中文',
        'speech_code': 'zh-CN',
        'elevenlabs_voice': 'pNInz6obpgDQGcFmaJgB',  # Wei
        'locale_codes': ['zh_CN', 'zh_TW', 'zh_HK']
    }
}

class LanguageManager:
    """Manages language detection, loading, and switching"""
    
    def __init__(self, language: Optional[str] = None):
        self.current_language = language or self.detect_system_language()
        self.translations = {}
        self.translations_dir = Path(__file__).parent / 'translations'
        self._load_translations()
    
    def detect_system_language(self) -> str:
        """Detect the system default language"""
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Extract language code (first 2 characters)
                lang_code = system_locale[:2].lower()
                
                # Check if we support this language
                if lang_code in SUPPORTED_LANGUAGES:
                    return lang_code
                    
                # Check locale-specific matches
                for lang, config in SUPPORTED_LANGUAGES.items():
                    if any(system_locale.startswith(lc.replace('_', '-')) for lc in config['locale_codes']):
                        return lang
        except Exception:
            pass
        
        # Default to English if detection fails
        return 'en'
    
    def _load_translations(self):
        """Load translation files for all supported languages"""
        for lang_code in SUPPORTED_LANGUAGES.keys():
            translation_file = self.translations_dir / f'{lang_code}.json'
            if translation_file.exists():
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to load {lang_code} translations: {e}")
                    # Fallback to English if available
                    if lang_code != 'en' and 'en' in self.translations:
                        self.translations[lang_code] = self.translations['en']
    
    def get_text(self, key_path: str, **kwargs) -> str:
        """
        Get translated text for the current language
        
        Args:
            key_path: Dot-separated path to the text (e.g., 'ui.title', 'agent.greeting')
            **kwargs: Variables to format into the text
        """
        # Try current language first
        text = self._get_text_from_lang(self.current_language, key_path)
        
        # Fallback to English if not found
        if text is None and self.current_language != 'en':
            text = self._get_text_from_lang('en', key_path)
        
        # Final fallback to the key itself
        if text is None:
            text = key_path
        
        # Format with provided variables
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    def _get_text_from_lang(self, lang_code: str, key_path: str) -> Optional[str]:
        """Get text from a specific language's translations"""
        if lang_code not in self.translations:
            return None
            
        keys = key_path.split('.')
        data = self.translations[lang_code]
        
        try:
            for key in keys:
                data = data[key]
            return str(data)
        except (KeyError, TypeError):
            return None
    
    def set_language(self, language: str) -> bool:
        """
        Switch to a different language
        
        Returns:
            bool: True if successful, False if language not supported
        """
        if language in SUPPORTED_LANGUAGES:
            self.current_language = language
            return True
        return False
    
    def get_language_config(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a language (speech codes, voice IDs, etc.)"""
        lang = language or self.current_language
        return SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES['en'])
    
    def get_speech_config(self, language: Optional[str] = None) -> Dict[str, str]:
        """Get speech recognition and TTS configuration"""
        config = self.get_language_config(language)
        return {
            'speech_recognition_language': config['speech_code'],
            'elevenlabs_voice_id': config['elevenlabs_voice'],
            'language_code': language or self.current_language,
            'language_name': config['name']
        }
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get all available languages with their display names"""
        return {code: config['name'] for code, config in SUPPORTED_LANGUAGES.items()}
    
    def detect_text_language(self, text: str) -> str:
        """
        Attempt to detect language from text
        Note: This is a simple heuristic-based detection
        For production use, consider using langdetect library
        """
        text_lower = text.lower()
        
        # Simple keyword-based detection
        language_keywords = {
            'es': ['hola', 'gracias', 'por favor', 'sí', 'no', 'que', 'como', 'donde'],
            'fr': ['bonjour', 'merci', 'oui', 'non', 'que', 'comment', 'où', 's\'il vous plaît'],
            'de': ['hallo', 'danke', 'bitte', 'ja', 'nein', 'wie', 'was', 'wo'],
            'zh': ['你好', '谢谢', '请', '是', '不', '什么', '怎么', '哪里']
        }
        
        # Count keyword matches for each language
        scores = {}
        for lang, keywords in language_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[lang] = score
        
        # Return language with highest score, or current language if no matches
        if scores:
            return max(scores, key=scores.get)
        
        return self.current_language

# Global language manager instance
_language_manager: Optional[LanguageManager] = None

def initialize_language_manager(language: Optional[str] = None) -> LanguageManager:
    """Initialize the global language manager"""
    global _language_manager
    _language_manager = LanguageManager(language)
    return _language_manager

def get_language_manager() -> LanguageManager:
    """Get the global language manager instance"""
    if _language_manager is None:
        return initialize_language_manager()
    return _language_manager

def get_text(key_path: str, **kwargs) -> str:
    """Convenience function to get translated text"""
    return get_language_manager().get_text(key_path, **kwargs)

def set_language(language: str) -> bool:
    """Convenience function to set language"""
    return get_language_manager().set_language(language)

def get_speech_config(language: Optional[str] = None) -> Dict[str, str]:
    """Convenience function to get speech configuration"""
    return get_language_manager().get_speech_config(language)

def get_available_languages() -> Dict[str, str]:
    """Convenience function to get available languages"""
    return get_language_manager().get_available_languages()