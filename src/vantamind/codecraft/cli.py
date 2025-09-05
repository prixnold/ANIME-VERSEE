from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .engine import CodeCraftEngine


app = typer.Typer(add_completion=False, help="CodeCraft CLI: Generate app scaffolds from plain English.")
console = Console()


@app.command()
def main(
    description: Optional[str] = typer.Argument(None, help="App description, e.g. \"Build a Flask API\" with optional tags like #lang:python"),
    out_dir: Path = typer.Option(Path.cwd(), "--out", help="Target directory"),
):
    if not description:
        console.print("Provide a description, e.g. codecraft \"Build a to-do web app\" #lang:python")
        raise typer.Exit(1)
    engine = CodeCraftEngine()
    files = engine.generate_project(description, out_dir)
    table = Table(title="Generated Files")
    table.add_column("Path")
    table.add_column("Size")
    for f in files:
        p = out_dir / f.path
        size = p.stat().st_size if p.exists() else 0
        table.add_row(str(f.path), f"{size} bytes")
    console.print(table)


if __name__ == "__main__":
    app()

