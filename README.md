# YouTube RAG System

A Retrieval-Augmented Generation (RAG) system for YouTube channel content with a Gradio chat interface. Index any YouTube channel and chat with its content using AI.

## Features

- **YouTube Integration**: Fetch channel videos and transcripts using YouTube Data API v3
- **Vector Database**: Store embeddings in ChromaDB for semantic search
- **Interactive UI**: Chat interface powered by Gradio
- **Multiple LLM Providers**: Support for OpenAI (GPT-4) and Anthropic (Claude)
- **Flexible Embeddings**: Choose between OpenAI embeddings or local sentence transformers
- **Smart Chunking**: Recursive and sentence-based text splitting strategies
- **Auto-skip**: Automatically skips videos without transcripts
- **VSCode Integration**: Debug configurations included

## Prerequisites

- Python 3.10 or higher
- YouTube Data API v3 key ([Get one here](https://console.cloud.google.com/apis/credentials))
- OpenAI API key (if using OpenAI for embeddings/LLM) or Anthropic API key (if using Claude)

## Quick Start

### Using Makefile (Recommended)

```bash
# One-command setup: creates venv, installs deps, creates .env
make setup

# Activate the virtual environment
source venv/bin/activate

# Edit .env with your API keys
nano .env

# Index a YouTube channel
make index CHANNEL=@veritasium

# Run the Gradio app
make run
```

### Manual Setup

1. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -e .
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:

```bash
python -m src.app
```

## Project Structure

```
youtube-rag/
├── src/
│   ├── app.py              # Gradio UI entry point
│   ├── youtube/            # YouTube data fetching
│   ├── rag/                # RAG components
│   ├── core/               # Core configuration
│   └── services/           # Business logic
├── data/                   # Data storage
├── tests/                  # Test suite
└── scripts/                # Utility scripts
```

## Available Make Commands

```bash
make help          # Show all available commands
make setup         # Complete setup (venv + deps + .env)
make install       # Install/update dependencies
make run           # Start Gradio web interface
make index         # Index a channel (usage: make index CHANNEL=@name)
make clean         # Remove temporary files
make clean-data    # Remove vector database data only
make clean-all     # Remove everything including venv
make test          # Run tests
make format        # Format code with black
make lint          # Run linting checks
```

## Configuration

Edit your `.env` file to configure the system:

### Required Settings

```bash
# YouTube API (Required)
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### LLM Provider Settings

Choose either OpenAI or Anthropic:

```bash
# For OpenAI (GPT-4)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=your_openai_key_here

# OR for Anthropic (Claude)
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Embedding Settings

Choose between local embeddings (free, runs on CPU) or OpenAI embeddings (paid, higher quality):

```bash
# Use local sentence transformers (free, no API key needed)
SHOULD_LOCAL_EMBED=true
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# OR use OpenAI embeddings (requires OpenAI API key)
SHOULD_LOCAL_EMBED=false
OPENAI_API_KEY=your_openai_key_here
```

### Optional Settings

```bash
# Vector Database
CHROMA_DB_PATH=./data/chroma_db

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval
RETRIEVAL_K=5

# Logging
LOG_LEVEL=INFO
```

## Usage Examples

### Using the Web Interface

1. Start the Gradio app:

```bash
make run
```

2. Open your browser to `http://localhost:7860`
3. Go to "Index Channel" tab and enter a channel handle
4. Once indexed, use the "Chat" tab to ask questions

### Using the CLI Script

```bash
# Index a channel with default settings (50 videos)
make index CHANNEL=@veritasium

# Index more videos
python scripts/seed_channel.py @veritasium --max-videos 100

# Clear and re-index
python scripts/seed_channel.py @veritasium --clear
```

### Programmatic Usage

```python
from src.services.indexing import IndexingService
from src.services.chat import ChatService

# Index a channel
indexing = IndexingService()
stats = indexing.index_channel("@channelname", max_videos=50)
print(f"Indexed {stats['videos_indexed']} videos")

# Query the system
chat = ChatService()
result = chat.ask("What topics does this channel cover?")
print(result["answer"])
print(f"Sources: {result['sources']}")
```

## Troubleshooting

### "Channel not found" Error

Make sure you're using the correct channel handle format:

- ✅ Correct: `@mkbhd` or `mkbhd`
- ❌ Wrong: `https://www.youtube.com/@mkbhd` (don't use full URL)

### "Transcript not available" for all videos

Some channels disable transcripts. The system will skip these videos automatically. Check the stats:

```
Videos Indexed: 45   ← Successfully indexed
Videos Skipped: 5    ← No transcripts available
```

### Config validation error with LLM_PROVIDER

Make sure your `.env` file has NO inline comments:

```bash
# ❌ Wrong
LLM_PROVIDER=openai  # this is a comment

# ✅ Correct
LLM_PROVIDER=openai
```

### Import errors when debugging

Make sure `PYTHONPATH` is set correctly. The `.vscode/launch.json` already includes this, but if running manually:

```bash
export PYTHONPATH="${PWD}"
python scripts/run.py
```

### Out of API quota

- **YouTube API**: Free tier has 10,000 units/day. Each video fetch costs ~3-5 units.
- **OpenAI API**: Check your billing at https://platform.openai.com/usage
- **Anthropic API**: Check usage at https://console.anthropic.com

## Project Structure Details

```
youtube-rag/
├── src/
│   ├── app.py                    # Gradio web interface
│   │
│   ├── youtube/                  # YouTube API integration
│   │   ├── base.py              # Abstract base class
│   │   ├── client.py            # Main YouTube client
│   │   ├── channel.py           # Channel lookup (handle → ID)
│   │   ├── videos.py            # Fetch channel videos
│   │   └── transcripts.py       # Fetch video transcripts
│   │
│   ├── rag/                      # RAG pipeline components
│   │   ├── base.py              # Abstract base classes
│   │   ├── chunker.py           # Text chunking strategies
│   │   ├── embeddings.py        # OpenAI & local embedders
│   │   ├── vectorstore.py       # ChromaDB integration
│   │   ├── retriever.py         # Document retrieval
│   │   └── generator.py         # LLM response generation
│   │
│   ├── core/                     # Core utilities
│   │   ├── config.py            # Pydantic settings
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── logging.py           # Logging setup
│   │
│   └── services/                 # Business logic
│       ├── base.py              # Base service class
│       ├── indexing.py          # Channel indexing service
│       └── chat.py              # Chat/query service
│
├── scripts/
│   └── seed_channel.py          # CLI indexing tool
│
├── data/
│   ├── chroma_db/               # Vector database storage
│   └── cache/                   # Cache directory
│
├── tests/                        # Test suite
├── .vscode/                      # VSCode configurations
├── Makefile                      # Development commands
└── pyproject.toml               # Dependencies
```

## License

MIT
