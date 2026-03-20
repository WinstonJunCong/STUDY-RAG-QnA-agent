#!/usr/bin/env python3
# query.py — Interactive Q&A loop. Run after ingest.py.

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

sys.path.insert(0, str(Path(__file__).parent))

from pipeline.index_builder import load_index, configure_settings
from agent.qa import ask

console = Console()


def main():
    console.print(Panel.fit(
        "[bold cyan]📚 Document Q&A Agent[/bold cyan]\n"
        "[dim]Free stack: HuggingFace embeddings + Ollama LLM + ChromaDB[/dim]",
        border_style="cyan"
    ))

    console.print("\n[dim]Loading index from ChromaDB...[/dim]")
    try:
        configure_settings()
        index = load_index()
        console.print("[green]✓ Index loaded successfully[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Failed to load index: {e}[/red]")
        console.print("[yellow]Tip: Run `python ingestion.py` first to build the index.[/yellow]")
        return

    console.print("\n[dim]Type your question and press Enter. Type 'quit' to exit.[/dim]\n")

    while True:
        try:
            question = console.input("[bold yellow]🔍 Question:[/bold yellow] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            break

        console.print("\n[dim]Retrieving relevant chunks...[/dim]")

        try:
            result = ask(question, index)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")
            continue

        # Print answer
        # console.print(Panel(
        #     result["answer"],
        #     title="[bold green]💬 Answer[/bold green]",
        #     border_style="green",
        #     padding=(1, 2)
        # ))
        console.print(result["answer"] + "\n")

        # Print sources
        if result["sources"]:
            sources_text = Text()
            for i, src in enumerate(result["sources"], 1):
                # We use markup=True here because qa.py is returning rich [link=...] syntax
                sources_text.append(Text.from_markup(f"  {i}. {src}\n", style="dim"))
            console.print(Panel(
                sources_text,
                title="[bold blue]📎 Sources[/bold blue]",
                border_style="blue",
                padding=(0, 1)
            ))

        console.print()


    console.print("\n[dim]Bye! 👋[/dim]\n")


if __name__ == "__main__":
    main()
