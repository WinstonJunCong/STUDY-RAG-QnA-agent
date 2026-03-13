# ingest/html_loader.py
# Scrapes one or more URLs and converts them to plain text Documents.

import requests
from bs4 import BeautifulSoup
from llama_index.core import Document


def load_html(url: str) -> Document | None:
    """
    Fetches a URL, strips HTML tags, and returns a Document.
    Returns None if the request fails.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; QnA-Agent/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise: scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Get page title for metadata
        title = soup.title.string.strip() if soup.title else url

        print(f"[html_loader] Loaded: {title} ({url})")
        return Document(
            text=text,
            metadata={
                "source": url,
                "type": "html",
                "title": title,
            }
        )

    except Exception as e:
        print(f"[html_loader] Error loading {url}: {e}")
        return None


def load_html_urls(urls: list[str]) -> list[Document]:
    """Load multiple URLs, skipping any that fail."""
    docs = []
    for url in urls:
        doc = load_html(url)
        if doc:
            docs.append(doc)
    return docs
