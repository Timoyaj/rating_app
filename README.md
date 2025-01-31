# Content Rating System

A sophisticated content evaluation platform that combines a FastAPI backend with a Streamlit frontend to provide comprehensive content rating capabilities. The system evaluates content across multiple dimensions while offering high-performance processing through caching and batch operations.

## System Architecture

```
content-rating-system/
├── api/                    # FastAPI Backend
│   ├── main.py            # API entry point
│   ├── models/            # Data models and schemas
│   └── routers/           # API endpoints
├── core/                  # Core Business Logic
│   ├── rating_calculator.py   # Rating algorithms
│   ├── metrics_collector.py   # Metrics processing
│   ├── data_processor.py      # Data validation
│   └── rating_service.py      # Service orchestration
├── models/                # Shared data models
│   └── resource.py        # Resource definitions
├── streamlit_app/         # Frontend Application
│   └── app.py            # Streamlit UI
├── utils/                 # Utilities
│   └── cache_manager.py   # Caching system
├── tests/                 # Test Suite
│   ├── conftest.py       # Test configuration
│   ├── test_*.py         # Unit tests
│   └── integration/      # Integration tests
└── run.py                # Application runner
```

## Features

### Backend (FastAPI)
- **RESTful API endpoints** for content rating
- **Batch processing** support for multiple resources
- **Caching system** for improved performance
- **Health monitoring** endpoints
- **Error handling** and validation
- **CORS support** for cross-origin requests
- **API documentation** (Swagger/OpenAPI)

### Frontend (Streamlit)
- **Interactive UI** for content submission
- **Real-time rating visualization**
- **Batch upload** capability
- **Analytics dashboard**
- **Radar charts** for score visualization
- **Downloadable reports**
- **Responsive design**

### Rating System
- **Multi-dimensional Rating** (100% total):
  - Relevance (25%)
  - Authority (20%)
  - Engagement (20%)
  - Clarity & Usability (15%)
  - Impact & Results (20%)

### Performance Features
- In-memory and disk-based caching
- Batch processing optimization
- Multi-worker processing
- Resource monitoring
- Configurable cache sizes

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

## Running the Application

The system can be started using the integrated runner:

```bash
python run.py
```

This will start:
- FastAPI backend on http://localhost:8000
- Streamlit frontend on http://localhost:8501
- API documentation at http://localhost:8000/api/docs

## Development Setup

### Backend Development
```bash
# Run FastAPI with auto-reload
uvicorn api.main:app --reload --port 8000
```

### Frontend Development
```bash
# Run Streamlit with auto-reload
streamlit run streamlit_app/app.py
```

## API Documentation

### Key Endpoints

1. Rate Single Content
```
POST /api/v1/rate
Content-Type: application/json

{
    "title": "Example Content",
    "content": "Content text...",
    "author": "Author Name",
    "url": "https://example.com",
    "metadata": {
        "keywords": ["keyword1", "keyword2"],
        "category": "technology",
        ...
    }
}
```

2. Batch Rating
```
POST /api/v1/rate-batch
Content-Type: application/json

{
    "resources": [
        {
            "title": "Content 1",
            ...
        },
        {
            "title": "Content 2",
            ...
        }
    ]
}
```

3. System Statistics
```
GET /api/v1/stats
```

## Testing

Run the test suite:
```bash
pytest
```

Run specific test categories:
```bash
pytest tests/unit          # Unit tests
pytest tests/integration   # Integration tests
```

## Deployment

### Docker Deployment
```bash
# Build the image
docker build -t content-rating-system .

# Run the container
docker run -p 8000:8000 -p 8501:8501 content-rating-system
```

### Environment Variables
- `PORT`: API port (default: 8000)
- `STREAMLIT_PORT`: Frontend port (default: 8501)
- `CACHE_SIZE`: Maximum cache size in MB (default: 100)
- `WORKERS`: Number of API workers (default: 4)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Performance Optimization

### Caching Strategy
- Default cache size: 100MB
- Cache invalidation: 24 hours
- Memory monitoring
- Disk persistence

### Batch Processing
- Concurrent processing
- Memory-efficient chunking
- Progress tracking
- Error handling with partial success

## Error Handling

The system implements comprehensive error handling:
- Input validation
- Processing errors
- Cache management
- Resource access
- API endpoint errors
- Batch processing failures

## License

This project is licensed under the MIT License - see the LICENSE file for details.
