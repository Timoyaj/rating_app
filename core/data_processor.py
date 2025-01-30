"""
Data processor for handling input validation, cleaning, and preparation.
"""
from typing import Dict, List, Union, Optional
import re
from datetime import datetime

class DataProcessor:
    """Handles data validation, cleaning, and preparation for rating calculations."""

    def __init__(self):
        """Initialize data processor with validation rules."""
        self.url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )

    def validate_resource_data(self, data: Dict[str, any]) -> Dict[str, List[str]]:
        """
        Validate input resource data for required fields and data types.
        
        Args:
            data: Dictionary containing resource data
            
        Returns:
            Dict containing any validation errors
        """
        errors = {}
        
        # Required fields and their types
        required_fields = {
            'title': str,
            'content': str,
            'author': str,
            'publication_date': str,
            'url': str,
            'metadata': dict
        }
        
        # Check required fields
        for field, field_type in required_fields.items():
            if field not in data:
                errors.setdefault('missing_fields', []).append(field)
            elif not isinstance(data[field], field_type):
                errors.setdefault('invalid_types', []).append(
                    f"{field}: expected {field_type.__name__}, got {type(data[field]).__name__}"
                )

        # Validate specific fields
        if 'url' in data and not self._validate_url(data['url']):
            errors.setdefault('invalid_values', []).append('Invalid URL format')

        if 'publication_date' in data and not self._validate_date(data['publication_date']):
            errors.setdefault('invalid_values', []).append('Invalid date format')

        if 'metadata' in data:
            metadata_errors = self._validate_metadata(data['metadata'])
            if metadata_errors:
                errors['metadata'] = metadata_errors

        return errors

    def _validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return bool(self.url_pattern.match(url))

    def _validate_date(self, date_str: str) -> bool:
        """
        Validate date string format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False

    def _validate_metadata(self, metadata: Dict[str, any]) -> List[str]:
        """
        Validate metadata fields.
        
        Args:
            metadata: Dictionary containing metadata
            
        Returns:
            List of validation errors
        """
        errors = []
        required_metadata = {
            'keywords': list,
            'category': str,
            'language': str
        }
        
        for field, field_type in required_metadata.items():
            if field not in metadata:
                errors.append(f"Missing required metadata field: {field}")
            elif not isinstance(metadata[field], field_type):
                errors.append(
                    f"Invalid metadata type for {field}: expected {field_type.__name__}, "
                    f"got {type(metadata[field]).__name__}"
                )
                
        return errors

    def clean_text_content(self, content: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            content: Raw text content
            
        Returns:
            str: Cleaned text content
        """
        if not content:
            return ""
            
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        # Remove special characters but keep basic punctuation
        content = re.sub(r'[^\w\s.,!?-]', '', content)
        
        # Normalize whitespace around punctuation
        content = re.sub(r'\s*([.,!?])\s*', r'\1 ', content)
        
        # Remove multiple periods
        content = re.sub(r'\.{2,}', '.', content)
        
        # Ensure single space after punctuation
        content = re.sub(r'([.,!?])\s*', r'\1 ', content)
        
        return content.strip()

    def prepare_resource_data(self, data: Dict[str, any]) -> Dict[str, any]:
        """
        Prepare resource data for processing.
        
        Args:
            data: Raw resource data
            
        Returns:
            Dict containing processed resource data
        """
        processed_data = data.copy()
        
        # Clean text content
        if 'content' in processed_data:
            processed_data['content'] = self.clean_text_content(processed_data['content'])
            
        # Normalize metadata
        if 'metadata' in processed_data:
            processed_data['metadata'] = self._normalize_metadata(processed_data['metadata'])
            
        # Format dates
        if 'publication_date' in processed_data:
            processed_data['publication_date'] = self._normalize_date(
                processed_data['publication_date']
            )
            
        # Normalize URLs
        if 'url' in processed_data:
            processed_data['url'] = processed_data['url'].lower()
            
        return processed_data

    def _normalize_metadata(self, metadata: Dict[str, any]) -> Dict[str, any]:
        """
        Normalize metadata values.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Dict containing normalized metadata
        """
        normalized = {}
        
        if 'keywords' in metadata:
            # Normalize and deduplicate keywords
            normalized['keywords'] = list(set(
                keyword.lower().strip() for keyword in metadata['keywords']
                if keyword.strip()
            ))
            
        if 'category' in metadata:
            # Normalize category
            normalized['category'] = metadata['category'].lower().strip()
            
        if 'language' in metadata:
            # Normalize language code
            normalized['language'] = metadata['language'].lower().strip()
            
        return {**metadata, **normalized}

    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date string to ISO format.
        
        Args:
            date_str: Input date string
            
        Returns:
            str: Normalized ISO date string
        """
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.isoformat()
        except ValueError:
            # Return original if can't parse
            return date_str
