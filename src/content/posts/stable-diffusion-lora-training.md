---
title: "Getting Started with Stable Diffusion - Training a LoRA on Your Likeness"
description: "Fine-tune Stable Diffusion with your own face using LoRA. A practical guide to personalizing AI image generation models."
pubDate: 2024-11-11
heroImage: /images/stable-diffusion-lora.jpg
tags:
  - "ai"
  - "stable-diffusion"
  - "machine-learning"
  - "image-generation"
category: "ai-ml"
---

The real power of generative AI models like Stable Diffusion is unlocked through personalization. Fine-tuning allows you to teach the model a new concept, style, or in this case, a specific person's likeness. While this once required massive datasets and powerful hardware, methods like LoRA (Low-Rank Adaptation) have made it incredibly accessible. A LoRA is a small file that acts as a "patch" for a base model, modifying its output without altering the original. Here is a step-by-step guide to training a LoRA on your own face.

## Base Model Selection

For training a likeness, the stable-diffusion-v1-5 model is the recommended base. It is widely supported, performs well for this task, and is compatible with the vast majority of community tools and other LoRAs, ensuring you won't run into compatibility issues.

## Prepare Your Dataset

A high-quality dataset is the most critical component. Gather 50 to 100 high-quality images of your face from various angles, with different lighting and expressions. To prepare them for training, crop and resize all images to a consistent resolution, either 512x512 or 768x768 pixels.

## Set Up Training in KohyaSS

KohyaSS is a popular graphical interface for training Stable Diffusion models. Within KohyaSS, configure the following key settings:

- **Method**: Select LoRA.
- **Training Steps**: A range of 2000 to 5000 steps is a good starting point. Fewer steps may result in underfitting (the model doesn't learn enough), while too many can lead to overfitting (the model only generates exact copies of your training images).
- **Optimizer**: Choose the AdamW optimizer for stable and effective learning.

## Train and Test

If you don't have a powerful local GPU, you can run the training process on a cloud service like Google Colab. The process can take several hours to complete. Once finished, you will have a LoRA file (usually a .safetensors file). Load this into your Stable Diffusion interface (like Automatic1111) and test it with prompts. If the results are too rigid or not accurate enough, you may need to adjust the training steps and retrain.

Creating a personalized LoRA gives you the power to place yourself in any scene or style imaginable. But to get the best results, you need to master the language of the AI: the prompt.
