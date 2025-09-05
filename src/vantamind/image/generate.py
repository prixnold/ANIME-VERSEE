from __future__ import annotations

from pathlib import Path
from typing import Optional


def generate_image(prompt: str, output_path: Path, model: Optional[str] = None, steps: int = 30) -> None:
    """Generate an image using Diffusers Stable Diffusion pipeline.

    This function requires the optional [image] extras to be installed.
    """
    # Imported lazily to keep base install light
    from diffusers import StableDiffusionPipeline
    import torch

    model_id = model or "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    image = pipe(prompt, num_inference_steps=steps).images[0]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

