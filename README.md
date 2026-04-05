# FinSight Backend

A conversational AI financial advisor that understands emotion and intent — not a robotic chatbot, but a friend who knows finance.

## What Makes It Different

- **Emotion-Aware**: Detects anxiety, fear, excitement in messy human language
- **Intent Understanding**: Understands conflicting goals ("I want to invest but I'm scared")
- **RAG-Powered**: Retrieves real financial knowledge so it doesn't hallucinate
- **Memory**: Remembers your conversation history
- **Conversational**: Talks like a smart friend, not a bullet-point robot

## Architecture

```
User: "I got 50k, rent is due, want to invest but scared"
    ↓
┌─────────────────┐  ┌─────────────────┐
│ Emotion Detector│  │ Intent Detector │
│   (fear: 0.82)  │  │ (invest: 0.75)  │
└─────────────────┘  └─────────────────┘
    ↓                      ↓
    └──────────────────────┘
              ↓
    ┌─────────────────────┐
    │    RAG Service      │
    │  (financial docs)   │
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │  Memory Service     │
    │  (conversation)     │
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │   LLM Service       │
    │  (GPT-4 + prompt)   │
    └─────────────────────┘
              ↓
Response: "Hey, that's a lot happening at once..."
```

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

Create `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://localhost:6379/0
```

Optional Redis for persistent memory:
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 3. Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /chat` | Main chat endpoint |
| `GET /health` | Service health & status |
| `POST /conversation/new` | Start new conversation |
| `GET /conversation/{id}/history` | Get conversation history |

### Example Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I got 50k this month, my rent is due, I also want to invest but I'"'"'m scared"
  }'
```

### Example Response

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Hey, that's a lot happening at once! First, take a breath. Having 50k is exciting, but I hear the fear too...",
  "detected_emotion": {
    "emotion": "fear",
    "confidence": 0.82,
    "intensity": 0.9
  },
  "detected_intent": {
    "intent": "investing",
    "confidence": 0.75,
    "sub_intents": ["budgeting"]
  },
  "rag_sources": ["conflict_resolution", "fear_management"]
}
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI |
| Emotion Detection | `j-hartmann/emotion-english-distilroberta-base` (Transformers) |
| Intent Detection | SentenceTransformers + similarity matching |
| Vector DB | ChromaDB |
| Embeddings | `all-MiniLM-L6-v2` |
| Memory | Redis (with in-memory fallback) |
| LLM | OpenAI GPT-4 |

## Project Structure

```
app/
├── core/
│   └── config.py          # Environment & settings
├── models/
│   └── schemas.py         # Pydantic models
├── services/
│   ├── emotion_detector.py    # Emotion analysis
│   ├── intent_detector.py     # Intent classification
│   ├── rag_service.py         # Vector retrieval
│   ├── memory_service.py      # Conversation storage
│   └── llm_service.py         # GPT-4 integration
└── main.py                # FastAPI routes

data/
└── chroma/                # Vector database storage
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection |
| `OPENAI_MODEL` | No | `gpt-4` | LLM model |
| `CHROMA_PERSIST_DIR` | No | `./data/chroma` | Vector DB path |
| `APP_ENV` | No | `development` | Environment |

## Features for Demo

1. **Natural Language**: No structured questions needed
2. **Conflict Resolution**: Handles "rent vs invest vs fear" scenarios
3. **Emotional Intelligence**: Acknowledges anxiety before advice
4. **Transparency**: Returns detected emotion/intent + knowledge sources
5. **Memory**: Multi-turn conversations feel continuous

## Student Project Highlights

- **No existing ML**: Pure neural networks (transformers, embeddings)
- **Novel angle**: Emotion-aware financial advice
- **Live demo ready**: Natural conversation anyone can try
- **Teacher-friendly**: Just talk to it, no setup needed

## License

MIT
