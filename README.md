# Content Rating System

A Python-based content rating system that evaluates and scores content resources based on multiple criteria including relevance, authority, engagement, clarity, and impact. The system provides a comprehensive, data-driven approach to content evaluation while maintaining high performance through caching and batch processing capabilities.

## Features

- **Multi-dimensional Rating**: Evaluates content across 5 core criteria
  - Relevance (25%)
  - Authority (20%)
  - Engagement (20%)
  - Clarity & Usability (15%)
  - Impact & Results (20%)

- **Advanced Metrics Collection**
  - Text analysis using NLTK
  - Engagement metrics processing
  - Authority and impact evaluation
  - Automated readability scoring

- **Performance Optimization**
  - In-memory and disk-based caching
  - Batch processing capabilities
  - Resource usage monitoring
  - Configurable cache sizes

- **Data Validation & Processing**
  - Input validation
  - Data normalization
  - Error handling
  - Consistent data formatting

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd content-rating-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
content-rating-system/
├── core/
│   ├── rating_calculator.py   # Core rating calculations
│   ├── metrics_collector.py   # Metrics collection and analysis
│   ├── data_processor.py      # Data validation and processing
│   └── rating_service.py      # Main service orchestration
├── models/
│   └── resource.py           # Resource data model
├── utils/
│   └── cache_manager.py      # Caching functionality
├── requirements.txt          # Project dependencies
├── example.py               # Usage example
└── README.md               # Documentation
```

## Usage

Here's a basic example of how to use the rating system:

```python
from core.rating_service import RatingService

# Initialize the rating service
rating_service = RatingService()

# Example resource data
resource_data = {
    'title': 'Example Article',
    'content': 'Article content here...',
    'author': 'John Doe',
    'url': 'https://example.com/article',
    'publication_date': '2024-01-30T00:00:00Z',
    'metadata': {
        'keywords': ['example', 'article'],
        'category': 'technology',
        'language': 'en',
        'view_count': 1000,
        'social_shares': 150,
        # ... other metadata
    }
}

# Rate the resource
rated_resource = rating_service.rate_resource(resource_data)

# Access the results
print(f"Final Score: {rated_resource.final_score}")
print("Individual Scores:")
for criterion, score in rated_resource.scores.items():
    print(f"{criterion}: {score}")
```

For more detailed examples, see `example.py`.

## Components

### RatingCalculator

Handles core rating calculations and score computations:
- Individual criterion scoring
- Weight application
- Final score calculation with modifiers

### MetricsCollector

Collects and analyzes various metrics:
- Text content analysis
- Engagement metrics processing
- Authority metrics evaluation
- Impact metrics calculation

### DataProcessor

Manages data validation and preparation:
- Input validation
- Data cleaning
- Format standardization
- Error checking

### Resource

Data model representing content resources:
- Content metadata
- Rating scores
- Caching information
- Serialization methods

### CacheManager

Handles caching operations:
- In-memory caching
- Disk-based persistence
- Cache invalidation
- Size management

### RatingService

Main service orchestrating the rating process:
- Component coordination
- Process management
- Error handling
- Result caching

## Performance Considerations

- Caching is enabled by default with a 100MB limit
- Batch processing is available for multiple resources
- Cache invalidation occurs after 24 hours
- Memory usage is monitored and managed

## Error Handling

The system includes comprehensive error handling:
- Input validation errors
- Processing errors
- Cache-related errors
- Resource access errors

## Extending the System

To add new rating criteria or modify existing ones:

1. Update the `WEIGHTS` dictionary in `RatingCalculator`
2. Add corresponding calculation methods
3. Modify the `_calculate_rating` method in `RatingService`
4. Update the resource model if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
