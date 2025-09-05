from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .llm.ollama_client import OllamaClient
from .router.intent import detect_intent, Intent


app = typer.Typer(add_completion=False, help="VantaMind AI assistant")
console = Console()


def _default_model() -> str:
    return os.getenv("VANTAMIND_MODEL", "mistral")


def _write_output(text: str, output_path: Optional[Path]) -> None:
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


@app.command()
def run(
    prompt: str = typer.Argument(..., help="Your request, e.g., 'Write a poem' or 'Generate an image...'"),
    model: str = typer.Option(None, help="Ollama model name (default from VANTAMIND_MODEL)"),
    temperature: float = typer.Option(0.2, help="Sampling temperature"),
    top_p: float = typer.Option(1.0, help="Top-p nucleus sampling (1.0 = disabled)"),
    repeat_penalty: float = typer.Option(1.0, help="Penalty for repeated tokens (>=1.0)"),
    num_predict: int = typer.Option(-1, help="Max tokens to generate (-1 = unlimited)"),
    num_ctx: int = typer.Option(4096, help="Context window size if supported by model"),
    raw: bool = typer.Option(False, help="Disable system prompt and safety/formatting (raw completion)"),
    image_out: Optional[Path] = typer.Option(None, help="If set, attempts image generation to this file"),
) -> None:
    """Run VantaMind AI for a single-shot request."""
    model_name = model or _default_model()
    client = OllamaClient()

    if not client.is_available():
        console.print("[red]Ollama is not reachable. Please start it and try again.[/red]")
        raise typer.Exit(code=1)

    intent = detect_intent(prompt)

    if intent == Intent.IMAGE or image_out is not None:
        try:
            from .image.generate import generate_image
        except Exception as exc:  # pragma: no cover - optional dependency
            console.print("[yellow]Image generation not available. Install extras: pip install .[image][/yellow]")
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=2)

        if image_out is None:
            image_out = Path("image.png")
        console.print(Panel.fit(f"Generating image -> {image_out}", title="VantaMind"))
        generate_image(prompt, output_path=image_out)
        console.print(f"Saved: {image_out}")
        return

    # Default to chat/generation
    messages = [] if raw else [
        {"role": "system", "content": "You are VantaMind, a helpful, concise assistant."},
    ]
    messages.append({"role": "user", "content": prompt})
    console.print(Panel.fit(f"Model: {model_name}", title="VantaMind"))
    opts = {
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "num_predict": num_predict,
        "num_ctx": num_ctx,
    }
    result = client.chat(model=model_name, messages=messages, temperature=temperature, options=opts)
    console.print(result)


def main() -> None:  # entrypoint
    app()


if __name__ == "__main__":
    main()

 

