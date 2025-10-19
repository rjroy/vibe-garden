# Replicate API Reference

## Overview

Replicate is a platform for running machine learning models in the cloud. This server uses the Replicate API to generate images using various AI models.

## Getting Started

1. Sign up at [replicate.com](https://replicate.com)
2. Get your API token from [account settings](https://replicate.com/account/api-tokens)
3. Set the `REPLICATE_API_TOKEN` environment variable

## Popular Image Models

### Flux Schnell (Recommended for Quick Generation)
- **Model ID**: `black-forest-labs/flux-schnell`
- **Speed**: Very fast (~2-3 seconds)
- **Quality**: Good
- **Best for**: Rapid prototyping, iterations

### Flux Dev (Recommended for Quality)
- **Model ID**: `black-forest-labs/flux-dev`
- **Speed**: Moderate (~10-15 seconds)
- **Quality**: Excellent
- **Best for**: Production images

### SDXL (Stable Diffusion XL)
- **Model ID**: `stability-ai/sdxl`
- **Speed**: Moderate
- **Quality**: Very good
- **Best for**: General purpose

### Stable Diffusion
- **Model ID**: `stability-ai/stable-diffusion`
- **Speed**: Fast
- **Quality**: Good
- **Best for**: Classic SD workflows

## API Usage

### Running a Prediction

```python
output = replicate_client.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "a cat wearing a space suit",
        "width": 1024,
        "height": 1024,
        "num_outputs": 1
    }
)
```

### Common Parameters

- `prompt` (string, required): Text description of desired image
- `width` (number): Image width in pixels (default: 1024)
- `height` (number): Image height in pixels (default: 1024)
- `num_outputs` (number): Number of images to generate (default: 1)
- `guidance_scale` (number): How closely to follow the prompt (model dependent)
- `num_inference_steps` (number): Quality vs speed tradeoff (model dependent)

## Output Format

The API returns an array of URLs pointing to the generated images:

```json
[
  "https://replicate.delivery/pbxt/..../output.png"
]
```

## Rate Limits and Costs

- Rate limits vary by account tier
- Each generation consumes credits based on model and parameters
- Check [Replicate pricing](https://replicate.com/pricing) for current rates

## Resources

- [Replicate Documentation](https://replicate.com/docs)
- [Python Client](https://github.com/replicate/replicate-python)
- [Model Explorer](https://replicate.com/explore)
