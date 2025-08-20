import json
import os
import sys
from typing import Optional

import requests
import typer
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(add_completion=False, no_args_is_help=True, help="VantaMind AI – versatile assistant with offline Ollama support.")
console = Console()


def _ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def _ollama_model(default: str = "mistral") -> str:
    return os.environ.get("OLLAMA_MODEL", default)


def _ollama_generate(prompt: str, model: Optional[str] = None, stream: bool = False) -> str:
    model_name = model or _ollama_model()
    url = f"{_ollama_host().rstrip('/')}/api/generate"
    payload = {"model": model_name, "prompt": prompt, "stream": stream}
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    if stream:
        text_parts = []
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            chunk = data.get("response", "")
            if chunk:
                console.print(chunk, end="")
                text_parts.append(chunk)
        console.print()
        return "".join(text_parts)
    else:
        data = response.json()
        return data.get("response", "")


def _ollama_embed(text: str, model: Optional[str] = None) -> list[float]:
    model_name = model or os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    url = f"{_ollama_host().rstrip('/')}/api/embeddings"
    payload = {"model": model_name, "prompt": text}
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json().get("embedding", [])


@app.command("text")
def cmd_text(prompt: str = typer.Argument(..., help="Prompt to generate text for"),
             model: Optional[str] = typer.Option(None, "--model", "-m", help="Ollama model to use"),
             stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream output")):
    """Generate text using Ollama locally (default: mistral)."""
    try:
        _ollama_generate(prompt, model=model, stream=stream)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("poem")
def cmd_poem(topic: str = typer.Argument(..., help="Topic for the poem")):
    prompt = f"Write a concise, vivid poem about {topic}."
    try:
        result = _ollama_generate(prompt, stream=True)
        if not result:
            console.print("No output produced.")
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("code")
def cmd_code(task: str = typer.Argument(..., help="Describe the code you need")):
    prompt = (
        "You are a helpful coding assistant. Write clear, runnable code.\n"
        f"Task: {task}\n"
        "Return only code blocks and minimal comments."
    )
    try:
        _ollama_generate(prompt, stream=True)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("image")
def cmd_image(prompt: str = typer.Argument(..., help="Describe the image to generate"),
              out: str = typer.Option("image.png", "--out", "-o", help="Output file path")):
    """Proxy to remote image generation if configured; otherwise print guidance."""
    api_url = os.environ.get("VANTAMIND_IMAGE_API")
    if not api_url:
        console.print("[yellow]No image API configured. Set VANTAMIND_IMAGE_API to enable remote generation.[/yellow]")
        console.print("For local-only use, integrate with an image model provider or Stable Diffusion API.")
        raise typer.Exit(code=2)
    try:
        response = requests.post(api_url, json={"prompt": prompt}, timeout=120)
        response.raise_for_status()
        content = response.content
        with open(out, "wb") as f:
            f.write(content)
        console.print(f"Saved image to {out}")
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("detect")
def cmd_detect(task: str = typer.Argument(..., help="Natural language task")):
    """Intent detection and auto-routing for common verbs like generate, write, summarize."""
    lowered = task.lower()
    if lowered.startswith("generate ") or lowered.startswith("write "):
        return cmd_text(task)
    if lowered.startswith("poem "):
        return cmd_poem(task.split(" ", 1)[1])
    if lowered.startswith("code "):
        return cmd_code(task.split(" ", 1)[1])
    return cmd_text(task)


def main():
    app()


if __name__ == "__main__":
    main()

