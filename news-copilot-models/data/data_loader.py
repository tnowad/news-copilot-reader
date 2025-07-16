"""Data loader for news articles and related data."""

import json
import os
import pandas as pd
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Data class for news articles."""
    id: str
    title: str
    content: str
    category: str
    author: Optional[str] = None
    published_date: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "author": self.author,
            "published_date": self.published_date,
            "url": self.url,
            "summary": self.summary,
            "tags": self.tags or []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NewsArticle":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            category=data.get("category", ""),
            author=data.get("author"),
            published_date=data.get("published_date"),
            url=data.get("url"),
            summary=data.get("summary"),
            tags=data.get("tags", [])
        )


class NewsDataLoader:
    """Data loader for news articles."""
    
    def __init__(self, data_dir: str = "./data"):
        """Initialize the data loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_from_json(self, file_path: str) -> List[NewsArticle]:
        """Load news articles from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of NewsArticle objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            articles = []
            if isinstance(data, list):
                for item in data:
                    articles.append(NewsArticle.from_dict(item))
            elif isinstance(data, dict) and "articles" in data:
                for item in data["articles"]:
                    articles.append(NewsArticle.from_dict(item))
            
            logger.info(f"Loaded {len(articles)} articles from {file_path}")
            return articles
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return []
    
    def load_from_csv(self, file_path: str) -> List[NewsArticle]:
        """Load news articles from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of NewsArticle objects
        """
        try:
            df = pd.read_csv(file_path)
            articles = []
            
            for _, row in df.iterrows():
                article = NewsArticle(
                    id=str(row.get("id", "")),
                    title=str(row.get("title", "")),
                    content=str(row.get("content", "")),
                    category=str(row.get("category", "")),
                    author=row.get("author"),
                    published_date=row.get("published_date"),
                    url=row.get("url"),
                    summary=row.get("summary"),
                    tags=row.get("tags", "").split(",") if row.get("tags") else None
                )
                articles.append(article)
            
            logger.info(f"Loaded {len(articles)} articles from {file_path}")
            return articles
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return []
    
    def save_to_json(self, articles: List[NewsArticle], file_path: str) -> bool:
        """Save news articles to JSON file.
        
        Args:
            articles: List of NewsArticle objects
            file_path: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "articles": [article.to_dict() for article in articles],
                "count": len(articles)
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(articles)} articles to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
            return False
    
    def save_to_csv(self, articles: List[NewsArticle], file_path: str) -> bool:
        """Save news articles to CSV file.
        
        Args:
            articles: List of NewsArticle objects
            file_path: Path to save the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = []
            for article in articles:
                article_dict = article.to_dict()
                if article_dict["tags"]:
                    article_dict["tags"] = ",".join(article_dict["tags"])
                data.append(article_dict)
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
            logger.info(f"Saved {len(articles)} articles to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
            return False
    
    def load_training_data(self) -> Tuple[List[NewsArticle], List[NewsArticle]]:
        """Load training and validation data.
        
        Returns:
            Tuple of (training_articles, validation_articles)
        """
        train_file = self.data_dir / "train.json"
        val_file = self.data_dir / "validation.json"
        
        train_articles = []
        val_articles = []
        
        if train_file.exists():
            train_articles = self.load_from_json(str(train_file))
        
        if val_file.exists():
            val_articles = self.load_from_json(str(val_file))
        
        return train_articles, val_articles
    
    def split_data(self, articles: List[NewsArticle], 
                   train_ratio: float = 0.8, 
                   val_ratio: float = 0.1) -> Tuple[List[NewsArticle], List[NewsArticle], List[NewsArticle]]:
        """Split articles into train, validation, and test sets.
        
        Args:
            articles: List of articles to split
            train_ratio: Ratio for training set
            val_ratio: Ratio for validation set
            
        Returns:
            Tuple of (train_articles, val_articles, test_articles)
        """
        import random
        
        # Shuffle articles
        articles_copy = articles.copy()
        random.shuffle(articles_copy)
        
        total = len(articles_copy)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        train_articles = articles_copy[:train_end]
        val_articles = articles_copy[train_end:val_end]
        test_articles = articles_copy[val_end:]
        
        logger.info(f"Data split: Train={len(train_articles)}, "
                   f"Val={len(val_articles)}, Test={len(test_articles)}")
        
        return train_articles, val_articles, test_articles
    
    def get_category_distribution(self, articles: List[NewsArticle]) -> Dict[str, int]:
        """Get distribution of categories in the articles.
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary with category counts
        """
        category_counts = {}
        for article in articles:
            category = article.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
