---
title: "Flux LoRA Training on RunPod: Complete Setup Guide"
description: "Step-by-step guide to fine-tuning Flux image models with LoRA on cloud GPUs. From dataset prep to deployment."
pubDate: 2024-11-30
updatedDate: 2024-11-30
heroImage: /images/placeholder.jpg
tags:
  - "flux"
  - "lora"
  - "image-generation"
  - "runpod"
  - "fine-tuning"
affiliateLinks:
  - text: "Get RunPod Credits"
    url: "https://runpod.io?ref=voidsignal&utm_source=voidsignal&utm_medium=affiliate&utm_campaign=flux-lora"
  - text: "Try Replicate"
    url: "https://replicate.com?utm_source=voidsignal&utm_medium=affiliate&utm_campaign=ai-api"
---

## The Signal

Flux has become the go-to open-source image model for quality that rivals Midjourney. But the real power unlocks when you fine-tune it on your own concepts—characters, styles, products, faces. LoRA (Low-Rank Adaptation) makes this practical without needing 80GB of VRAM or days of training time.

This guide walks through the complete workflow: dataset preparation, cloud GPU setup on [RunPod](https://runpod.io?ref=voidsignal&utm_source=voidsignal&utm_medium=affiliate&utm_campaign=flux-lora), training configuration, and deploying your custom model.

## Key Features of Flux LoRA Training

- **24GB VRAM minimum** for Flux.1-dev LoRA training (RTX 4090 or A100)
- **500-1500 training steps** for most concepts
- **10-30 images** typically sufficient for style/character LoRAs
- **~30 minutes to 2 hours** training time depending on dataset size
- **Output size**: 50-200MB LoRA files (vs 12GB+ full model)

## Prerequisites

Before starting, you'll need:

- [RunPod account](https://runpod.io?ref=voidsignal&utm_source=voidsignal&utm_medium=affiliate&utm_campaign=flux-lora) with credits ($10-25 for experimentation)
- 10-30 high-quality training images
- Basic command line familiarity
- Optional: [Hugging Face account](https://huggingface.co?utm_source=voidsignal&utm_medium=affiliate&utm_campaign=hf-models) for model hosting

## Step 1: Prepare Your Dataset

Quality beats quantity. For character/face LoRAs:

- **10-20 images** showing varied angles, lighting, expressions
- **Consistent subject** across all images
- **512x512 or 1024x1024** resolution minimum
- **Clean backgrounds** help but aren't required

For style LoRAs:

- **20-30 images** demonstrating the style consistently
- **Varied subjects** rendered in the target style
- **Similar aspect ratios** across the dataset

### Captioning Your Images

Each image needs a text caption. The format matters:

```
# For a character named "ohwx"
ohwx person, portrait photo, natural lighting, looking at camera
ohwx person, full body shot, standing outdoors, casual clothing
ohwx person, close-up, dramatic lighting, serious expression
```

Use a **unique trigger word** (like `ohwx`) that doesn't exist in the base model's vocabulary. This prevents concept bleeding.

**Automated captioning** with BLIP or CogVLM can bootstrap captions, but manual review improves results significantly.

## Step 2: Launch RunPod Instance

1. Log into [RunPod](https://runpod.io?ref=voidsignal&utm_source=voidsignal&utm_medium=affiliate&utm_campaign=flux-lora)
2. Click "Deploy" → "GPU Pods"
3. Select GPU:
   - **Budget**: RTX 4090 (24GB) ~$0.40/hr
   - **Recommended**: A100 40GB ~$1.50/hr
   - **Fast**: A100 80GB ~$2.00/hr
4. Choose template: `runpod/pytorch:2.1.0-py3.10-cuda12.1.0`
5. Set volume size: 50GB minimum
6. Deploy and wait for "Running" status

### Connect to Your Pod

```bash
# Via SSH (recommended)
ssh root@your-pod-ip -i ~/.ssh/your_key

# Or use RunPod's web terminal
```

## Step 3: Install Training Environment

```bash
# Clone the ai-toolkit (SimpleTuner alternative)
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Login to Hugging Face (for model access)
huggingface-cli login
```

## Step 4: Upload Your Dataset

```bash
# Create dataset directory
mkdir -p /workspace/datasets/my_concept

# Upload via SCP from your local machine
scp -r ./my_images/* root@your-pod-ip:/workspace/datasets/my_concept/
```

Organize files:

```
/workspace/datasets/my_concept/
├── image_001.png
├── image_001.txt  # caption file
├── image_002.png
├── image_002.txt
└── ...
```

## Step 5: Configure Training

Create a training config file:

```yaml
# /workspace/ai-toolkit/config/my_lora.yaml
job: extension
config:
  name: "my_concept_lora"
  process:
    - type: sd_trainer
      training_folder: "/workspace/output"
      device: cuda:0
      network:
        type: lora
        linear: 16
        linear_alpha: 16
      save:
        dtype: float16
        save_every: 250
      datasets:
        - folder_path: "/workspace/datasets/my_concept"
          caption_ext: txt
          caption_dropout_rate: 0.05
          shuffle_tokens: false
          cache_latents_to_disk: true
          resolution: [1024, 1024]
      train:
        batch_size: 1
        steps: 1000
        gradient_accumulation_steps: 1
        train_unet: true
        train_text_encoder: false
        gradient_checkpointing: true
        noise_scheduler: flowmatch
        optimizer: adamw8bit
        lr: 4e-4
        ema_config:
          use_ema: true
          ema_decay: 0.99
      model:
        name_or_path: "black-forest-labs/FLUX.1-dev"
        is_flux: true
        quantize: true
      sample:
        sampler: flowmatch
        sample_every: 250
        width: 1024
        height: 1024
        prompts:
          - "ohwx person, portrait photo, studio lighting"
          - "ohwx person, outdoor scene, natural lighting"
        seed: 42
        walk_seed: true
        guidance_scale: 3.5
        sample_steps: 20
```

## Step 6: Start Training

```bash
cd /workspace/ai-toolkit
python run.py config/my_lora.yaml
```

Monitor progress:

- **Loss curve** should trend downward
- **Sample images** generated every 250 steps show quality progression
- **Training time**: ~1-2 hours for 1000 steps on A100

### Common Issues

**OOM (Out of Memory)**:
- Reduce batch_size to 1
- Enable gradient_checkpointing
- Use quantize: true
- Reduce resolution to 768x768

**Overfitting** (samples look identical to training images):
- Reduce steps (try 500-750)
- Increase caption_dropout_rate to 0.1
- Add more diverse training images

## Step 7: Test Your LoRA

```python
from diffusers import FluxPipeline
import torch

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16
)
pipe.load_lora_weights("/workspace/output/my_concept_lora.safetensors")
pipe.to("cuda")

image = pipe(
    "ohwx person, cyberpunk portrait, neon lighting",
    num_inference_steps=20,
    guidance_scale=3.5
).images[0]

image.save("test_output.png")
```

## Step 8: Deploy Your Model

### Option A: Replicate (Recommended)

[Replicate](https://replicate.com?utm_source=voidsignal&utm_medium=affiliate&utm_campaign=ai-api) handles scaling and infrastructure:

```bash
# Install Cog
pip install cog

# Push your model
cog push r8.im/your-username/your-model
```

Then call via API:

```python
import replicate

output = replicate.run(
    "your-username/your-model:latest",
    input={
        "prompt": "ohwx person, portrait",
        "lora_scale": 0.8
    }
)
```

### Option B: RunPod Serverless

Keep it in the [RunPod ecosystem](https://runpod.io?ref=voidsignal&utm_source=voidsignal&utm_medium=affiliate&utm_campaign=flux-lora):

1. Create a serverless endpoint
2. Upload your LoRA to the endpoint's storage
3. Configure the handler to load your LoRA on cold start

### Option C: Hugging Face Spaces

Free hosting for demos:

```bash
# Upload to Hugging Face
huggingface-cli upload your-username/my-flux-lora ./my_concept_lora.safetensors
```

## Limitations & Trade-offs

**Flux LoRA limitations**:
- Requires 24GB+ VRAM (no consumer GPU under RTX 4090)
- Slower inference than SDXL
- Larger file sizes than SD 1.5 LoRAs

**Training gotchas**:
- Captions significantly impact quality—garbage in, garbage out
- Overfitting happens fast with small datasets
- Style LoRAs need more diverse training data than character LoRAs

**Cost considerations**:
- Budget ~$5-15 per successful LoRA (including failed experiments)
- [RunPod spot instances](https://runpod.io?ref=voidsignal&utm_source=voidsignal&utm_medium=affiliate&utm_campaign=flux-lora) can cut costs 50%+ for interruptible training

## The Verdict

Flux LoRA training is accessible to anyone willing to spend a few hours learning the workflow and $10-20 on cloud compute. The results rival commercial fine-tuning services at a fraction of the cost.

**Start here**:
1. [RunPod](https://runpod.io?ref=voidsignal&utm_source=voidsignal&utm_medium=affiliate&utm_campaign=flux-lora) for training compute
2. [Replicate](https://replicate.com?utm_source=voidsignal&utm_medium=affiliate&utm_campaign=ai-api) for deployment
3. [Hugging Face](https://huggingface.co?utm_source=voidsignal&utm_medium=affiliate&utm_campaign=hf-models) for model hosting and community

For those wanting to learn the fundamentals before diving in, [Codecademy's Python and ML courses](https://www.codecademy.com?utm_source=voidsignal&utm_medium=affiliate&utm_campaign=learn-code) provide solid foundations for understanding the underlying concepts.

The barrier to custom image generation has never been lower. Your unique concepts, styles, and characters are now trainable in an afternoon.
