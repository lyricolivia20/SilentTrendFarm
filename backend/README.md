# SilentTrendFarm Backend API

A FastAPI-powered backend for the SilentTrendFarm blog, providing trend analysis, content generation, and blog management capabilities.

## 🚀 Features

- **Trend Analysis**: Fetch and analyze trending topics using Google Trends
- **Content Generation**: AI-powered blog post idea generation
- **SEO Analysis**: Analyze web content for SEO insights
- **Statistics API**: Track blog performance metrics
- **Serverless Ready**: Deploy to Netlify Functions or any cloud platform
- **Auto Documentation**: Interactive API docs at `/docs`

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Optional: Docker for containerized deployment

## 🛠️ Installation

### Local Setup

1. **Install dependencies:**
```bash
pip install -r ../requirements.txt
```

2. **Set up environment variables:**
```bash
cp ../.env.example ../.env
# Edit .env with your API keys
```

3. **Run the development server:**
```bash
python run_server.py
```

The API will be available at `http://localhost:8000`

### Docker Setup

```bash
# Build the image
docker build -t silenttrendfarm-backend .

# Run the container
docker run -p 8000:8000 --env-file ../.env silenttrendfarm-backend
```

## 📚 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API root with version info |
| `/health` | GET | Health check endpoint |
| `/docs` | GET | Interactive API documentation |
| `/redoc` | GET | Alternative API documentation |

### Feature Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trends` | POST | Get Google Trends data |
| `/api/generate-ideas` | POST | Generate blog post ideas |
| `/api/analyze-content` | POST | Analyze URL for SEO |
| `/api/ai-assistant` | POST | AI content assistant |
| `/api/stats` | GET | Blog statistics |

## 🔧 Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=your_key_here

# Optional
BACKEND_ENV=development
PORT=8000
DATABASE_URL=sqlite:///./blog.db
SERPAPI_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

## 🚀 Deployment

### Netlify Functions

The backend includes Netlify Functions for serverless deployment:

```javascript
// Located in /netlify/functions/
- api.js     // Main API handler
- trends.js  // Trends endpoint
```

### Railway

```bash
railway login
railway init
railway up
```

### Render

1. Push code to GitHub
2. Connect repository on render.com
3. Use the generated `render.yaml`

### Fly.io

```bash
flyctl launch --dockerfile backend/Dockerfile
flyctl deploy
```

### Google Cloud Run

```bash
gcloud run deploy silenttrendfarm-backend \
  --source . \
  --port 8000 \
  --allow-unauthenticated
```

## 📝 API Usage Examples

### Get Trending Topics

```python
import requests

response = requests.post('http://localhost:8000/api/trends', json={
    'keywords': ['AI', 'web development'],
    'timeframe': 'today 3-m',
    'geo': 'US'
})

trends = response.json()
```

### Generate Blog Ideas

```python
response = requests.post('http://localhost:8000/api/generate-ideas', 
    params={'category': 'ai-ml'})

ideas = response.json()
```

### Analyze Content

```python
response = requests.post('http://localhost:8000/api/analyze-content', json={
    'url': 'https://example.com/article',
    'extract_meta': True
})

analysis = response.json()
```

## 🧪 Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

## 📊 Monitoring

- Health endpoint: `/health`
- Metrics available at: `/api/stats`
- Logs location: `./logs/`

## 🔒 Security

- CORS configured for production domains
- Environment variables for sensitive data
- Rate limiting ready (configure in production)
- Input validation with Pydantic

## 🤝 Integration with Frontend

The Astro frontend can connect to this backend using the provided API client:

```javascript
// src/lib/api.js
import api from '../lib/api.js';

// Use in Astro components
const trends = await api.getTrends(['keyword1', 'keyword2']);
```

## 📄 License

MIT License - See main project LICENSE file

## 🆘 Support

For issues or questions:
1. Check the API docs at `/docs`
2. Review error messages in logs
3. Open an issue on GitHub

---

Built with ❤️ using FastAPI
