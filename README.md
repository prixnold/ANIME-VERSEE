# VantaMind AI + CodeCraft CLI

Two CLIs:

- VantaMind AI: versatile assistant for text, code, and optional image gen. Offline via Ollama.
- CodeCraft CLI: generate complete apps from plain English using local models.

## Install (editable)

```bash
python3 -m pip install -e .
```

## VantaMind AI

Examples:

```bash
vantamind text "Summarize the plot of The Odyssey"
vantamind poem "autumn rain"
vantamind code "Python script that counts words in a file"
vantamind detect "write a haiku about the ocean"
```

Environment:

- OLLAMA_HOST: default `http://localhost:11434`
- OLLAMA_MODEL: default `mistral`
- VANTAMIND_IMAGE_API: optional remote image API endpoint

## CodeCraft CLI

Generate a new app:

```bash
codecraft new "Build a to-do list web app" -o ./my_app
```

Optional:

- CODECRAFT_MODEL: override model name (defaults to OLLAMA_MODEL or `mistral`)

Requires Ollama running locally for offline generation.
