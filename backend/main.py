"""
FastAPI Backend for SilentTrendFarm
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import requests
from pytrends.request import TrendReq
from datetime import datetime
import json
import base64
import io
import time
import httpx
from gradio_client import Client
from character_pipeline import (
    CharacterGenerationRequest,
    RigModelRequest,
    generate_image_sdxl,
    convert_to_3d_hunyuan,
    auto_rig_model,
    analyze_theme,
    full_character_pipeline
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SilentTrendFarm API",
    description="Backend API for SilentTrendFarm blog",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "https://lyricodes.dev", "*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TrendRequest(BaseModel):
    keywords: List[str]
    timeframe: Optional[str] = "today 3-m"
    geo: Optional[str] = ""

class BlogPostIdea(BaseModel):
    title: str
    description: str
    keywords: List[str]
    category: str

class ContentAnalysis(BaseModel):
    url: str
    extract_meta: Optional[bool] = True

class Image3DRequest(BaseModel):
    image_url: str

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "SilentTrendFarm API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Google Trends endpoint
@app.post("/api/trends")
async def get_trends(request: TrendRequest):
    """
    Fetch trending topics from Google Trends
    """
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(request.keywords, timeframe=request.timeframe, geo=request.geo)
        
        # Get interest over time
        interest_over_time = pytrends.interest_over_time()
        
        # Get related queries
        related_queries = pytrends.related_queries()
        
        return {
            "keywords": request.keywords,
            "interest_over_time": interest_over_time.to_dict() if not interest_over_time.empty else {},
            "related_queries": related_queries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Blog post idea generator
@app.post("/api/generate-ideas")
async def generate_blog_ideas(category: str = "tech"):
    """
    Generate blog post ideas based on current trends
    """
    try:
        # Get trending topics
        pytrends = TrendReq(hl='en-US', tz=360)
        trending = pytrends.trending_searches(pn='united_states')
        
        ideas = []
        for trend in trending[0][:5]:  # Get top 5 trends
            ideas.append({
                "title": f"Understanding {trend}: A Deep Dive",
                "description": f"Explore the latest developments and insights about {trend}",
                "keywords": [trend, category],
                "category": category
            })
        
        return {"ideas": ideas, "generated_at": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content scraper endpoint (for research)
@app.post("/api/analyze-content")
async def analyze_content(request: ContentAnalysis):
    """
    Analyze content from a URL for SEO insights
    """
    try:
        from bs4 import BeautifulSoup
        
        response = requests.get(request.url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract meta information
        meta_data = {}
        if request.extract_meta:
            meta_data = {
                "title": soup.find('title').text if soup.find('title') else "",
                "description": soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else "",
                "keywords": soup.find('meta', {'name': 'keywords'})['content'] if soup.find('meta', {'name': 'keywords'}) else "",
                "h1_tags": [h1.text for h1 in soup.find_all('h1')],
                "h2_tags": [h2.text for h2 in soup.find_all('h2')][:5]  # Limit to 5
            }
        
        # Count words
        text = soup.get_text()
        word_count = len(text.split())
        
        return {
            "url": request.url,
            "meta_data": meta_data,
            "word_count": word_count,
            "analyzed_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI content assistant endpoint (if OpenAI key is available)
@app.post("/api/ai-assistant")
async def ai_assistant(prompt: str, max_tokens: int = 150):
    """
    AI-powered content assistant using OpenAI
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful blog writing assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        
        return {
            "response": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image to 3D using Hugging Face Spaces (TripoSR or InstantMesh)
@app.post("/api/image-to-3d")
async def image_to_3d(request: Image3DRequest):
    """
    Convert an image to a 3D model using Hugging Face Spaces
    Uses TripoSR for fast image-to-3D conversion
    Returns a URL to download the GLB file
    """
    try:
        image_path = None
        
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            response = await http_client.get(request.image_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch image")
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(response.content)
            image_path = tmp.name
        
        # Use TripoSR for 3D generation
        # TripoSR is fast and produces good results
        tripo_client = Client("stabilityai/TripoSR")
        
        result = tripo_client.predict(
            image_path,  # Input image
            True,        # Remove background (already done but let it handle edge cases)
            0.5,         # Foreground ratio
            api_name="/run"
        )
        
        # Clean up temp file
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        
        # Result should be a path to the GLB file
        # Read and return as base64 or provide download
        if result and len(result) > 1:
            glb_path = result[1]  # GLB file path
            
            with open(glb_path, "rb") as f:
                glb_bytes = f.read()
            
            glb_base64 = base64.b64encode(glb_bytes).decode('utf-8')
            
            return {
                "success": True,
                "glb_base64": glb_base64,
                "message": "3D model generated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="3D generation returned no result")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"3D generation failed: {str(e)}")


# Combined pipeline endpoint
@app.post("/api/pipeline/image-to-3d")
async def full_pipeline(request: Image3DRequest):
    """
    Full pipeline: Image -> Background Removal -> 3D Model
    """
    try:
        return await image_to_3d(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Character Generation with SDXL and prompt enhancement
@app.post("/api/generate-image")
async def generate_character_image(request: CharacterGenerationRequest):
    """
    Generate a character image using SDXL with automatic prompt enhancement
    and T-pose generation for 3D conversion
    """
    try:
        # Analyze theme if requested
        theme_data = None
        if request.analyze_theme:
            theme_analysis = analyze_theme(request.prompt)
            theme_data = {
                "primary_theme": theme_analysis.primary_theme,
                "environment_params": theme_analysis.environment_params,
                "suggested_enhancements": theme_analysis.suggested_enhancements
            }
        
        # Generate image
        result = await generate_image_sdxl(
            request.prompt,
            enhance=request.enhance_prompt,
            t_pose=request.generate_t_pose
        )
        
        return {
            "success": result["success"],
            "image_base64": result["image_base64"],
            "enhanced_prompt": result["enhanced_prompt"],
            "original_prompt": result["original_prompt"],
            "theme_analysis": theme_data,
            "method": result.get("method", "sdxl")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Convert to 3D using Hunyuan3D or alternatives
@app.post("/api/convert-to-3d")
async def convert_image_to_3d(image_base64: str):
    """
    Convert a 2D image to 3D model using Hunyuan3D or fallback services
    """
    try:
        result = await convert_to_3d_hunyuan(image_base64)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Auto-rig 3D model
@app.post("/api/rig-model")
async def rig_3d_model(request: RigModelRequest):
    """
    Auto-rig a 3D model for animation using Mixamo or procedural rigging
    """
    try:
        result = await auto_rig_model(
            request.glb_base64,
            method=request.rigging_method
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Full character generation pipeline
@app.post("/api/character-pipeline")
async def character_generation_pipeline(prompt: str):
    """
    Complete pipeline: Text → Enhanced Image → 3D Model → Rigged Character
    with theme analysis for environment customization
    """
    try:
        result = await full_character_pipeline(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stats endpoint
@app.get("/api/stats")
async def get_stats():
    """
    Get blog statistics
    """
    # This would typically query a database
    # For now, returning mock data
    return {
        "total_posts": 42,
        "total_views": 15234,
        "categories": {
            "indie-dev": 15,
            "ai-ml": 12,
            "it-tech": 15
        },
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
