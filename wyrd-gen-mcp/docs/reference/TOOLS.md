# Available Tools

## generate_image

Generate an image using AI models via Replicate.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Text prompt describing the image |
| `model` | string | No | `black-forest-labs/flux-schnell` | Replicate model identifier |
| `width` | number | No | 1024 | Image width in pixels |
| `height` | number | No | 1024 | Image height in pixels |
| `num_outputs` | number | No | 1 | Number of images to generate |

### Example Usage

**Simple generation:**
```
Generate an image: "a serene mountain landscape at sunset"
```

**With custom parameters:**
```
Generate an image using flux-dev: "cyberpunk city street, neon lights, rain"
with dimensions 1920x1080
```

### Response Format

```json
{
  "success": true,
  "model": "black-forest-labs/flux-schnell",
  "prompt": "a serene mountain landscape at sunset",
  "images": [
    "https://replicate.delivery/pbxt/.../output.png"
  ],
  "metadata": {
    "width": 1024,
    "height": 1024,
    "num_outputs": 1
  }
}
```

### Error Handling

If generation fails, you'll receive:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common errors:
- Invalid API token
- Model not found
- Invalid parameters
- Rate limit exceeded

---

## list_image_models

List popular image generation models available on Replicate.

### Parameters

None required.

### Example Usage

```
What image models are available?
```

### Response Format

```json
[
  {
    "model": "black-forest-labs/flux-schnell",
    "description": "Fast image generation model from Black Forest Labs",
    "best_for": "Quick iterations and prototyping"
  },
  {
    "model": "black-forest-labs/flux-dev",
    "description": "High-quality image generation with more detail",
    "best_for": "Production-quality images"
  }
]
```

---

## Choosing the Right Model

### For Speed: Flux Schnell
- Fastest generation times
- Good quality
- Great for testing prompts

### For Quality: Flux Dev
- Best output quality
- Slower generation
- Production-ready images

### For Versatility: SDXL
- Wide range of styles
- Good balance of speed/quality
- Large community support

### For Classic Workflows: Stable Diffusion
- Well-documented
- Lots of fine-tuned variants
- Predictable results
