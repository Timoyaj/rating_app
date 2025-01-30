"""
Resource model representing content to be rated.
"""
from typing import Dict, List, Optional
from datetime import datetime

class Resource:
    """Represents a content resource that can be rated."""

    def __init__(
        self,
        title: str,
        content: str,
        author: str,
        url: str,
        publication_date: str,
        metadata: Dict[str, any],
        resource_id: Optional[str] = None
    ):
        """
        Initialize a resource.
        
        Args:
            title: Resource title
            content: Main content text
            author: Content author
            url: Resource URL
            publication_date: ISO format date string
            metadata: Dictionary of metadata
            resource_id: Optional unique identifier
        """
        self.title = title
        self.content = content
        self.author = author
        self.url = url
        self.publication_date = publication_date
        self.metadata = metadata
        self.resource_id = resource_id or self._generate_id()
        
        # Rating related attributes
        self.scores: Dict[str, float] = {}
        self.final_score: Optional[float] = None
        self.last_rated: Optional[datetime] = None
        self.rating_metadata: Dict[str, any] = {}

    def _generate_id(self) -> str:
        """
        Generate a unique identifier for the resource.
        
        Returns:
            str: Unique identifier
        """
        from hashlib import sha256
        from time import time
        
        # Create a unique string based on content and timestamp
        unique_string = f"{self.title}{self.url}{time()}"
        return sha256(unique_string.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, any]:
        """
        Convert resource to dictionary representation.
        
        Returns:
            Dict containing resource data
        """
        return {
            'resource_id': self.resource_id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'url': self.url,
            'publication_date': self.publication_date,
            'metadata': self.metadata,
            'scores': self.scores,
            'final_score': self.final_score,
            'last_rated': self.last_rated.isoformat() if self.last_rated else None,
            'rating_metadata': self.rating_metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'Resource':
        """
        Create resource instance from dictionary data.
        
        Args:
            data: Dictionary containing resource data
            
        Returns:
            Resource instance
        """
        # Create base resource
        resource = cls(
            title=data['title'],
            content=data['content'],
            author=data['author'],
            url=data['url'],
            publication_date=data['publication_date'],
            metadata=data['metadata'],
            resource_id=data.get('resource_id')
        )
        
        # Add rating data if present
        if 'scores' in data:
            resource.scores = data['scores']
        if 'final_score' in data:
            resource.final_score = data['final_score']
        if 'last_rated' in data and data['last_rated']:
            resource.last_rated = datetime.fromisoformat(
                data['last_rated'].replace('Z', '+00:00')
            )
        if 'rating_metadata' in data:
            resource.rating_metadata = data['rating_metadata']
            
        return resource

    def update_score(self, criterion: str, score: float) -> None:
        """
        Update individual criterion score.
        
        Args:
            criterion: Name of criterion
            score: Score value (0-10)
        """
        self.scores[criterion] = max(0.0, min(10.0, score))
        self.last_rated = datetime.now()

    def set_final_score(self, score: float, metadata: Optional[Dict[str, any]] = None) -> None:
        """
        Set final calculated score and optional metadata.
        
        Args:
            score: Final score value (0-10)
            metadata: Optional dictionary of score metadata
        """
        self.final_score = max(0.0, min(10.0, score))
        if metadata:
            self.rating_metadata.update(metadata)
        self.last_rated = datetime.now()

    def is_stale(self, max_age_hours: int = 24) -> bool:
        """
        Check if the rating is stale and should be recalculated.
        
        Args:
            max_age_hours: Maximum age in hours before considered stale
            
        Returns:
            bool: True if rating is stale, False otherwise
        """
        if not self.last_rated:
            return True
            
        age = datetime.now() - self.last_rated
        return age.total_seconds() > (max_age_hours * 3600)
