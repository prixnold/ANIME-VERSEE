import json
import os
import subprocess
from pathlib import Path
from typing import Optional

import requests
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(add_completion=False, no_args_is_help=True, help="CodeCraft CLI – generate complete apps from plain English.")
console = Console()


def _ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def _model() -> str:
    return os.environ.get("CODECRAFT_MODEL", os.environ.get("OLLAMA_MODEL", "mistral"))


def _ollama_generate(prompt: str, stream: bool = False) -> str:
    url = f"{_ollama_host().rstrip('/')}/api/generate"
    payload = {"model": _model(), "prompt": prompt, "stream": stream}
    response = requests.post(url, json=payload, timeout=180)
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


SCAFFOLD_PROMPT = """
You are CodeCraft, an expert software generator. The user will describe an app.
Return a JSON with keys: files (list of {path, content}), instructions (string), dependencies (list of strings).
Keep code runnable. Do not include backticks. Use unix newlines. Keep paths relative.
"""


@app.command("new")
def cmd_new(description: str = typer.Argument(..., help="Describe the app to build, in plain English"),
            out_dir: Path = typer.Option(Path("./codecraft_app"), "--out", "-o", help="Output directory"),
            install: bool = typer.Option(False, "--install", help="Attempt to install dependencies after generation")):
    prompt = f"{SCAFFOLD_PROMPT}\nUser description: {description}\nJSON:"
    try:
        text = _ollama_generate(prompt, stream=False)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to salvage JSON if model returned extra prose
            start = text.find("{")
            end = text.rfind("}")
            data = json.loads(text[start:end+1])

        files = data.get("files", [])
        instructions = data.get("instructions", "")
        dependencies = data.get("dependencies", [])

        out_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            path = out_dir / f.get("path", "unknown.txt")
            path.parent.mkdir(parents=True, exist_ok=True)
            content = f.get("content", "")
            path.write_text(content)

        console.print(Panel.fit("Generated files written to " + str(out_dir)))
        if instructions:
            console.print(Panel.fit(instructions, title="Instructions"))
        if dependencies:
            console.print("Dependencies:")
            for dep in dependencies:
                console.print(f" - {dep}")

        if install and dependencies:
            _attempt_install(dependencies, cwd=out_dir)

    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


def _attempt_install(dependencies: list[str], cwd: Path):
    try:
        subprocess.run(["python3", "-m", "pip", "install", *dependencies], cwd=str(cwd), check=True)
        console.print("Dependencies installed.")
    except subprocess.CalledProcessError:
        console.print("[yellow]Dependency install failed. Install manually as needed.[/yellow]")


def main():
    app()


if __name__ == "__main__":
    main()

