# ingest/video_loader.py
# Transcribes video/audio files using OpenAI Whisper (free, runs locally).
# Each segment becomes its own Document with a timestamp in metadata.

from pathlib import Path
from llama_index.core import Document

# Supported file extensions
SUPPORTED_EXTENSIONS = {".mp4", ".mp3", ".wav", ".m4a", ".mkv", ".avi", ".mov", ".flac"}


def load_video(path: str, model_size: str = "base") -> list[Document]:
    """
    Transcribes a video/audio file and returns one Document per segment.
    Each Document's metadata includes the timestamp (in seconds).

    model_size options (tradeoff: speed vs accuracy):
      "tiny"   → fastest, lower accuracy
      "base"   → good balance (default)
      "small"  → better accuracy, slower
      "medium" → high accuracy, needs more RAM
      "large"  → best accuracy, slow, needs GPU
    """
    try:
        import whisper
    except ImportError:
        print("[video_loader] Error: openai-whisper not installed. Run: pip install openai-whisper")
        return []

    file_path = Path(path)
    if not file_path.exists():
        print(f"[video_loader] File not found: {path}")
        return []

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"[video_loader] Unsupported file type: {file_path.suffix}")
        return []

    print(f"[video_loader] Transcribing: {file_path.name} (model={model_size}) ...")
    model = whisper.load_model(model_size)
    result = model.transcribe(str(file_path))

    docs = []
    for seg in result.get("segments", []):
        text = seg["text"].strip()
        if not text:
            continue

        start = seg["start"]
        minutes = int(start // 60)
        seconds = int(start % 60)
        timestamp_label = f"{minutes}:{seconds:02d}"

        docs.append(Document(
            text=text,
            metadata={
                "source": str(file_path),
                "type": "video",
                "filename": file_path.name,
                "timestamp_seconds": start,
                "timestamp_label": timestamp_label,
                "file_path": str(file_path.absolute()),
            }
        ))

    print(f"[video_loader] Transcribed {len(docs)} segments from {file_path.name}")
    return docs


def load_videos(paths: list[str], model_size: str = "base") -> list[Document]:
    """Transcribe multiple video files."""
    docs = []
    for path in paths:
        docs.extend(load_video(path, model_size=model_size))
    return docs
