"""
Metrics collector for gathering and analyzing content metrics.
"""
from typing import Dict, List, Tuple, Optional
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from collections import Counter

class MetricsCollector:
    """Handles collection and analysis of content metrics."""

    def __init__(self):
        """Initialize the metrics collector with required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))

    def analyze_text_content(self, content: str) -> Dict[str, any]:
        """
        Analyze text content for various metrics.
        
        Args:
            content: The text content to analyze
            
        Returns:
            Dict containing various text metrics
        """
        if not content:
            return {
                'word_count': 0,
                'keywords': [],
                'readability_score': 0.0,
                'sentence_count': 0
            }

        # Tokenize content
        words = word_tokenize(content.lower())
        sentences = nltk.sent_tokenize(content)
        
        # Remove stop words and get keywords
        keywords = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        # Calculate metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(1, sentence_count)
        
        # Calculate Flesch Reading Score
        readability_score = self._calculate_flesch_score(word_count, sentence_count, content)
        
        # Get keyword frequency
        keyword_freq = Counter(keywords)
        top_keywords = keyword_freq.most_common(10)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': avg_sentence_length,
            'readability_score': readability_score,
            'keywords': top_keywords,
            'keyword_density': {word: count/word_count for word, count in top_keywords}
        }

    def _calculate_flesch_score(self, word_count: int, sentence_count: int, 
                              content: str) -> float:
        """
        Calculate Flesch Reading Ease score.
        
        Args:
            word_count: Total number of words
            sentence_count: Total number of sentences
            content: Original text content
            
        Returns:
            float: Flesch Reading Ease score (0-100)
        """
        if word_count == 0 or sentence_count == 0:
            return 0.0
            
        # Count syllables (basic implementation)
        def count_syllables(word: str) -> int:
            word = word.lower()
            count = 0
            vowels = 'aeiouy'
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index-1] not in vowels:
                    count += 1
            if word.endswith('e'):
                count -= 1
            if count == 0:
                count += 1
            return count
            
        syllable_count = sum(count_syllables(word) for word in content.split())
        
        # Flesch Reading Ease = 206.835 - 1.015(total words/total sentences) - 84.6(total syllables/total words)
        score = 206.835 - 1.015 * (word_count/sentence_count) - 84.6 * (syllable_count/word_count)
        
        return max(0.0, min(100.0, score))

    def analyze_engagement_metrics(self, metrics: Dict[str, any]) -> Dict[str, float]:
        """
        Analyze engagement related metrics.
        
        Args:
            metrics: Dictionary containing raw engagement metrics
            
        Returns:
            Dict containing processed engagement scores
        """
        required_fields = ['view_count', 'interaction_time', 'social_shares']
        if not all(field in metrics for field in required_fields):
            raise ValueError(f"Missing required engagement metrics: {required_fields}")
            
        total_views = metrics['view_count']
        avg_interaction_time = metrics['interaction_time']
        social_shares = metrics['social_shares']
        
        engagement_score = {
            'interaction_rate': min(10.0, (metrics.get('interactions', 0) / max(1, total_views)) * 10),
            'avg_session_time': min(10.0, avg_interaction_time / 5),  # Normalize to 10-point scale
            'social_impact': min(10.0, (social_shares / max(1, total_views)) * 20)
        }
        
        return engagement_score

    def analyze_authority_metrics(self, metrics: Dict[str, any]) -> Dict[str, float]:
        """
        Analyze authority related metrics.
        
        Args:
            metrics: Dictionary containing authority metrics
            
        Returns:
            Dict containing processed authority scores
        """
        required_fields = ['citations', 'author_credentials', 'domain_authority']
        if not all(field in metrics for field in required_fields):
            raise ValueError(f"Missing required authority metrics: {required_fields}")
            
        citation_score = min(10.0, metrics['citations'] / 10)  # Normalize citations to 10-point scale
        credentials_score = min(10.0, metrics['author_credentials'])
        domain_score = min(10.0, metrics['domain_authority'])
        
        return {
            'citation_impact': citation_score,
            'author_expertise': credentials_score,
            'domain_authority': domain_score,
            'overall_authority': (citation_score + credentials_score + domain_score) / 3
        }

    def calculate_impact_metrics(self, metrics: Dict[str, any]) -> Dict[str, float]:
        """
        Calculate impact metrics based on outcomes and results.
        
        Args:
            metrics: Dictionary containing impact-related metrics
            
        Returns:
            Dict containing processed impact scores
        """
        required_fields = ['positive_outcomes', 'conversion_rate', 'user_satisfaction']
        if not all(field in metrics for field in required_fields):
            raise ValueError(f"Missing required impact metrics: {required_fields}")
            
        outcomes_score = min(10.0, metrics['positive_outcomes'])
        conversion_score = min(10.0, metrics['conversion_rate'] * 10)
        satisfaction_score = min(10.0, metrics['user_satisfaction'])
        
        return {
            'outcome_effectiveness': outcomes_score,
            'conversion_impact': conversion_score,
            'user_satisfaction': satisfaction_score,
            'overall_impact': (outcomes_score + conversion_score + satisfaction_score) / 3
        }
