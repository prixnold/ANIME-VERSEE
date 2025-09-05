## VantaMind AI & CodeCraft CLI

VantaMind AI is a local-first AI assistant with offline support via Ollama, plus CodeCraft CLI for AI-powered codebase generation from natural language.

### Features
- Image generation, code assistance, and text chat via `vantamind "your request"`
- Offline support using Ollama local models (e.g., `mistral`, `llama3`)
- Intent detection routes tasks: image, code generation, or general chat
- CodeCraft CLI: `codecraft "Build a to-do app #lang:python #framework:flask"`
- Optional image generation via Diffusers (install with `pip install .[image]`)

### Quickstart
1) Install Python 3.9+

2) Install package (editable recommended during development):
```bash
pip install -e .
```

3) Ensure Ollama is running locally (default http://localhost:11434) and models are pulled:
```bash
ollama pull mistral
```

4) Use the assistant:
```bash
vantamind "Write a short haiku about the sea"
```

5) Generate a project with CodeCraft:
```bash
codecraft "Build a workout tracker app #lang:python #framework:flask" -o ./workout-tracker
```

6) Optional: Image generation (Diffusers)
```bash
pip install .[image]
vantamind "generate an image of a serene mountain lake at sunrise" --image-out mountain.png
```

### Tags for CodeCraft
- `#lang:python|node|js|ts`
- `#framework:flask|fastapi|express|vanilla`
- `#type:web|api|cli`
- `#license:mit|apache-2.0`

### Environment
- `OLLAMA_BASE_URL` (default `http://localhost:11434`)
- `VANTAMIND_MODEL` (default `mistral`)

### License
MIT

## VantaMind AI & CodeCraft CLI

VantaMind AI is a versatile, locally-first AI assistant accessible via the `vantamind` command. It can help with text tasks, code assistance, and (best-effort) image generation. Offline support is provided via [Ollama](https://ollama.com/) when available.

CodeCraft CLI is an AI-powered app generator. Describe your desired application in plain English and it produces a project scaffold and files. It integrates with VantaMind's LLM backends and supports tags such as `#lang:python` and `#mobile_friendly` to influence output.

### Quick Start

1. Install in editable mode:

```bash
python -m pip install -e .
```

2. Ensure Ollama is running locally (for offline mode):

```bash
ollama serve &
```

3. Use VantaMind:

```bash
vantamind "Generate a poem about the ocean"
vantamind --code "Write a Python function that sums a list"
vantamind --image "Generate a minimalist rocket logo in neon style" --out rocket.png
```

4. Use CodeCraft:

```bash
codecraft "Build a to-do list web app" #lang:python #framework:flask
```

### Environment

- Offline default is Ollama (http://localhost:11434). Set `OLLAMA_HOST` to override.
- Optional cloud fallback: set `OPENAI_API_KEY` to enable OpenAI for text/code tasks.

### Notes on Image Generation

Image generation via Ollama requires a compatible model (e.g., `flux`, `sdxl`) which may not be available by default. The command will guide you to pull a model if needed. If no local backend is available, the tool will safely no-op with instructions.

# ANIME-VERSE
THE BEST ANIME DUBBING APP IN THE WORLD
