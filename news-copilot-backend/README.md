# News Copilot Backend

A Flask-based backend API for the News Copilot Reader application with integrated AI-powered text generation capabilities.

## Features

### Core Functionality
- **User Management**: Authentication, authorization, and user profiles
- **Article Management**: CRUD operations for news articles
- **Category System**: News categorization and filtering
- **Comment System**: User comments and interactions
- **Bookmark System**: Save and manage favorite articles
- **View Tracking**: Article view statistics and analytics
- **Report System**: Content moderation and reporting

### AI-Powered Features
- **Advanced Text Generation**: Custom transformer model integration
- **Smart Article Completion**: Context-aware news article completion
- **Headline Generation**: Automated headline creation
- **Story Continuation**: Coherent narrative flow extension
- **Multi-Context Support**: News, sports, technology, politics, business, health
- **Intelligent Caching**: Performance-optimized generation with Redis

## New AI Generation Endpoints

### Basic Text Generation
```http
POST /api/generate-text
Content-Type: application/json

{
  "prompt": "Breaking news: New AI breakthrough",
  "maxLength": 100,
  "temperature": 0.7,
  "topK": 20,
  "topP": 0.9
}
```

### Advanced Article Completion
```http
POST /api/complete-article
Content-Type: application/json

{
  "content": "The technology sector experienced significant...",
  "context": "technology",
  "maxTokens": 150,
  "temperature": 0.7,
  "style": "formal",
  "generateHeadline": true
}
```

### Headline Generation
```http
POST /api/generate-headline
Content-Type: application/json

{
  "content": "Scientists have discovered a new method for...",
  "style": "breaking",
  "maxLength": 100
}
```

### Story Continuation
```http
POST /api/continue-story
Content-Type: application/json

{
  "previousParagraphs": [
    "The conference began with opening remarks...",
    "Speakers from various industries presented..."
  ],
  "context": "business",
  "targetLength": "medium",
  "tone": "analytical"
}
```

### Service Health Check
```http
GET /api/service-status
```

## Architecture

### Backend Components

1. **Flask Application**: Core web framework
2. **SQLAlchemy**: Database ORM with PostgreSQL/SQLite support
3. **JWT Authentication**: Secure token-based authentication
4. **Redis Caching**: High-performance caching layer
5. **Transformer Integration**: Custom AI model integration

### AI Generation Service

```
app/services/generation/
├── text_generation.py           # Legacy pipeline interface
├── news_completion_service.py   # Advanced completion service
└── __init__.py
```

### New Route Structure

```
app/routes/
├── generation.py               # Basic generation endpoints
├── advanced_generation.py     # Advanced AI features
└── ...
```

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL or SQLite
- Redis (for caching)
- CUDA-compatible GPU (optional, for faster inference)

### Setup

1. **Clone and navigate to backend directory**:
```bash
cd news-copilot-backend
```

2. **Create virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up transformer model** (if available):
```bash
# Ensure the transformer model is trained and available
# Default path: ../news-copilot-models/checkpoints/final_model
```

5. **Configure environment variables**:
```bash
# Create .env file
DATABASE_URL=postgresql://user:password@localhost/newscopilot
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
REDIS_URL=redis://localhost:6379
```

6. **Initialize database**:
```bash
flask db upgrade
```

7. **Run the application**:
```bash
flask run --debug
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///site.db  # or PostgreSQL URL
SQLALCHEMY_DATABASE_URI=sqlite:///site.db

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=1  # hours
JWT_REFRESH_TOKEN_EXPIRES=30  # days

# AI Model
TRANSFORMER_MODEL_PATH=../news-copilot-models/checkpoints/final_model
ENABLE_AI_FEATURES=true
GENERATION_CACHE_TIMEOUT=300  # seconds

# Cache
REDIS_URL=redis://localhost:6379
CACHE_TYPE=redis  # or 'simple' for in-memory

# Mail (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### AI Generation Settings

The AI generation service automatically detects and loads the transformer model:

1. **Model Path**: `../news-copilot-models/checkpoints/final_model`
2. **Fallback Mode**: Graceful degradation to rule-based generation
3. **Context Optimization**: Different parameters for each content type
4. **Caching**: Intelligent caching with Redis for performance

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - User logout

### Article Endpoints
- `GET /api/articles` - List articles
- `POST /api/articles` - Create article
- `GET /api/articles/{id}` - Get article
- `PUT /api/articles/{id}` - Update article
- `DELETE /api/articles/{id}` - Delete article

### AI Generation Endpoints
- `POST /api/generate-text` - Basic text generation
- `POST /api/complete-article` - Advanced article completion
- `POST /api/generate-headline` - Headline generation
- `POST /api/continue-story` - Story continuation
- `GET /api/service-status` - AI service health check

## Usage Examples

### Frontend Integration

```typescript
import generateService from '$lib/services/generate.service';

// Complete an article
const result = await generateService.completeArticle({
  content: "The new technology promises to revolutionize...",
  context: "technology",
  maxTokens: 100,
  temperature: 0.7,
  generateHeadline: true
});

// Generate a headline
const headline = await generateService.generateHeadline({
  content: "Scientists discover breakthrough method...",
  style: "breaking"
});
```

### Editor Integration

The editor widget now supports:
- **Smart inline completions** with AI
- **Context-aware suggestions** based on article category
- **Real-time generation** with debouncing
- **Fallback handling** when AI service is unavailable

## Performance

### Optimization Features
- **Redis caching** for repeated generations
- **Debounced requests** to prevent API spam
- **Intelligent fallbacks** for service reliability
- **Context-specific parameters** for better results

### Expected Performance
- **Cached responses**: < 50ms
- **New generations**: 1-5 seconds (depending on hardware)
- **Fallback mode**: < 100ms

## Deployment

### Production Setup

1. **Use PostgreSQL** for the database
2. **Configure Redis** for caching
3. **Set environment variables** appropriately
4. **Use WSGI server** like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the News Copilot Reader application.
