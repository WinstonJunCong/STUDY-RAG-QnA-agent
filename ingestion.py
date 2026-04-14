#!/usr/bin/env python3
# ingest.py — Run this once to load all your documents into ChromaDB.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from ingest.text_loader import load_text_files
from ingest.html_loader import load_html_urls
from ingest.video_loader import load_videos
from pipeline.index_builder import build_index

HTML_URLS = []

VIDEO_FILES = []

WHISPER_MODEL = "base"

def main():
    all_docs = []

    print("\n>> Loading text/markdown files...")
    for folder in config.TEXT_FOLDERS:
        docs = load_text_files(folder)
        all_docs.extend(docs)
        print(f"   {len(docs)} docs from {folder}")

    print("\n>> Loading HTML pages...")
    if HTML_URLS:
        docs = load_html_urls(HTML_URLS)
        all_docs.extend(docs)
        print(f"   {len(docs)} pages loaded")
    else:
        print("   (no URLs configured)")

    print("\n>> Transcribing videos...")
    if VIDEO_FILES:
        docs = load_videos(VIDEO_FILES, model_size=WHISPER_MODEL)
        all_docs.extend(docs)
        print(f"   {len(docs)} segments transcribed")
    else:
        print("   (no video files configured)")

    if not all_docs:
        print("\nWARNING: No documents loaded! Check your TEXT_FOLDERS in config.py")
        return

    print(f"\n>> Building index from {len(all_docs)} total documents...")
    build_index(all_docs)

    print("\nDone! Run `python query.py` to start asking questions.\n")


if __name__ == "__main__":
    main()
