"""Service for analyzing conversation data and extracting insights."""

import json
import re
from typing import Dict, List, Tuple, Optional
from textblob import TextBlob
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class AnalyticsService:
    """Service for analyzing conversation data and extracting insights."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
        
        if sentiment_score > 0.1:
            sentiment_label = "positive"
        elif sentiment_score < -0.1:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return sentiment_score, sentiment_label
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text using TF-IDF.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        try:
            # Clean text
            cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform([cleaned_text])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top keywords
            scores = tfidf_matrix.toarray()[0]
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [keyword for keyword, score in keyword_scores[:max_keywords] if score > 0]
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def extract_topics(self, text: str, num_topics: int = 5) -> List[str]:
        """
        Extract topics from text using simple keyword clustering.
        
        Args:
            text: Text to extract topics from
            num_topics: Number of topics to extract
            
        Returns:
            List of topics
        """
        keywords = self.extract_keywords(text, max_keywords=20)
        
        # Simple topic extraction based on keyword frequency
        # In a production system, you might use LDA or other topic modeling
        topics = []
        
        # Define topic categories based on common keywords
        topic_categories = {
            "technology": ["api", "software", "code", "development", "tech", "system"],
            "business": ["business", "company", "revenue", "profit", "market", "sales"],
            "customer_service": ["customer", "support", "help", "issue", "problem", "service"],
            "product": ["product", "feature", "update", "version", "release", "improvement"],
            "general": ["discussion", "meeting", "call", "conversation", "chat", "talk"]
        }
        
        for category, category_keywords in topic_categories.items():
            if any(keyword in keywords for keyword in category_keywords):
                topics.append(category)
        
        return topics[:num_topics]
    
    def calculate_quality_score(self, conversation_data: Dict) -> float:
        """
        Calculate quality score for a conversation.
        
        Args:
            conversation_data: Dictionary containing conversation data
            
        Returns:
            Quality score between 0 and 1
        """
        try:
            score = 0.0
            
            # Check if summary exists and has content
            summary = conversation_data.get("summary", {})
            if isinstance(summary, dict):
                summary_text = summary.get("text", "") or summary.get("content", "")
            else:
                summary_text = str(summary)
            
            if summary_text and len(summary_text.strip()) > 10:
                score += 0.3
            
            # Check summary length (not too short, not too long)
            if 50 <= len(summary_text) <= 2000:
                score += 0.2
            
            # Check if actions exist
            actions = conversation_data.get("actions", [])
            if actions and len(actions) > 0:
                score += 0.2
            
            # Check if metadata exists
            metadata = conversation_data.get("conversation_metadata", {})
            if metadata and len(metadata) > 0:
                score += 0.1
            
            # Check for meaningful content (not just filler words)
            meaningful_words = ["api", "data", "user", "system", "feature", "problem", "solution"]
            if any(word in summary_text.lower() for word in meaningful_words):
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            print(f"Error calculating quality score: {e}")
            return 0.0
    
    def calculate_engagement_score(self, conversation_data: Dict) -> float:
        """
        Calculate engagement score for a conversation.
        
        Args:
            conversation_data: Dictionary containing conversation data
            
        Returns:
            Engagement score between 0 and 1
        """
        try:
            score = 0.0
            
            # Check number of actions (more actions = more engagement)
            actions = conversation_data.get("actions", [])
            if len(actions) > 5:
                score += 0.3
            elif len(actions) > 2:
                score += 0.2
            elif len(actions) > 0:
                score += 0.1
            
            # Check summary length (longer summaries might indicate more engagement)
            summary = conversation_data.get("summary", {})
            if isinstance(summary, dict):
                summary_text = summary.get("text", "") or summary.get("content", "")
            else:
                summary_text = str(summary)
            
            if len(summary_text) > 500:
                score += 0.3
            elif len(summary_text) > 200:
                score += 0.2
            elif len(summary_text) > 50:
                score += 0.1
            
            # Check for question marks (questions indicate engagement)
            if "?" in summary_text:
                score += 0.2
            
            # Check for exclamation marks (excitement indicates engagement)
            if "!" in summary_text:
                score += 0.1
            
            # Check for specific engagement indicators
            engagement_words = ["discuss", "explore", "analyze", "investigate", "review", "consider"]
            if any(word in summary_text.lower() for word in engagement_words):
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            print(f"Error calculating engagement score: {e}")
            return 0.0
    
    def analyze_conversation(self, conversation_data: Dict) -> Dict:
        """
        Perform complete analysis of a conversation.
        
        Args:
            conversation_data: Dictionary containing conversation data
            
        Returns:
            Dictionary containing all analysis results
        """
        try:
            # Extract summary text
            summary = conversation_data.get("summary", {})
            if isinstance(summary, dict):
                summary_text = summary.get("text", "") or summary.get("content", "")
            else:
                summary_text = str(summary)
            
            # Perform sentiment analysis
            sentiment_score, sentiment_label = self.analyze_sentiment(summary_text)
            
            # Extract keywords and topics
            keywords = self.extract_keywords(summary_text)
            topics = self.extract_topics(summary_text)
            
            # Calculate quality and engagement scores
            quality_score = self.calculate_quality_score(conversation_data)
            engagement_score = self.calculate_engagement_score(conversation_data)
            
            return {
                "sentiment": sentiment_score,
                "sentiment_label": sentiment_label,
                "keywords": keywords,
                "topics": topics,
                "quality_score": quality_score,
                "engagement_score": engagement_score
            }
            
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            return {
                "sentiment": 0.0,
                "sentiment_label": "neutral",
                "keywords": [],
                "topics": [],
                "quality_score": 0.0,
                "engagement_score": 0.0
            }
