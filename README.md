# 📚 Document Q&A Agent — Free Stack

A fully local, zero-cost document Q&A agent using:
- **LlamaIndex** — RAG framework
- **HuggingFace Sentence Transformers** — free local embeddings
- **Ollama + Llama 3.2** — free local LLM
- **ChromaDB** — free local vector store
- **Whisper** — free local video/audio transcription

No API keys. No cloud. No cost.

---

## Project Structure

```
qna-agent/
├── ingest/
│   ├── text_loader.py      # .txt / .md files
│   ├── html_loader.py      # scrape web pages
│   └── video_loader.py     # Whisper transcription
├── pipeline/
│   └── index_builder.py    # chunk → embed → ChromaDB
├── agent/
│   └── qa.py               # retrieve → answer with citations
├── ingest.py               # ← run this first
├── query.py                # ← run this to ask questions
├── config.py               # tweak models / settings here
└── requirements.txt
```

---

## Setup Plan

### Step 1 — Install Ollama (the free local LLM)

Download from https://ollama.com and run:

```bash
ollama pull llama3.2
```

This downloads the Llama 3.2 model (~2GB). It runs entirely on your machine.

> **Low RAM?** Use `ollama pull phi3` instead, then set `OLLAMA_MODEL = "phi3"` in config.py

---

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

The first run will also download the HuggingFace embedding model (~130MB, cached after first use).

---

### Step 3 — Add your documents

Edit `ingest.py` and fill in your sources:

```python
TEXT_FOLDERS = ["./docs"]          # folder with .txt / .md files
HTML_URLS    = ["https://..."]     # web pages to scrape
VIDEO_FILES  = ["./video.mp4"]     # videos to transcribe
```

Put your text/markdown files inside a `./docs/` folder.

---

### Step 4 — Ingest (one-time)

```bash
python ingest.py
```

This will:
1. Load all your documents
2. Split them into chunks
3. Embed each chunk locally (HuggingFace)
4. Store vectors in `./chroma_db/` on disk

Only needs to run once (or when you add new documents).

---

### Step 5 — Ask questions

```bash
python query.py
```

You'll get an interactive prompt. Every answer includes source citations and video timestamps.

---

## Tweaking Performance

All settings are in `config.py`:

| Setting | Default | Effect |
|---|---|---|
| `EMBED_MODEL` | `bge-small-en-v1.5` | Swap for `bge-large` for better quality |
| `OLLAMA_MODEL` | `llama3.2` | Swap for `mistral` or `phi3` |
| `CHUNK_SIZE` | `512` | Smaller = more precise retrieval |
| `CHUNK_OVERLAP` | `50` | Higher = better context continuity |
| `TOP_K` | `5` | More chunks = more context for LLM |

---

## Cost Breakdown

| Component | Cost |
|---|---|
| Embeddings (HuggingFace) | ✅ Free |
| LLM (Ollama) | ✅ Free |
| Vector DB (ChromaDB) | ✅ Free |
| Video transcription (Whisper) | ✅ Free |
| **Total** | **$0** |

---

## Troubleshooting

**"Connection refused" from Ollama**
→ Make sure Ollama is running: `ollama serve`

**Out of memory with video transcription**
→ Use a smaller Whisper model in config: `WHISPER_MODEL = "tiny"`

**Slow embedding on first run**
→ Normal — HuggingFace downloads the model once, then it's cached.

**Poor answer quality**
→ Try a larger Ollama model (`mistral` or `llama3.2:3b`) or increase `TOP_K` in config.py
