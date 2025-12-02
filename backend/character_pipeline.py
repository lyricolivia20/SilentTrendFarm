"""
Character Generation Pipeline with SDXL, Theme Analysis, and Rigging
"""
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Literal
import base64
import httpx
import re
from gradio_client import Client
import tempfile
import os
import json

class CharacterGenerationRequest(BaseModel):
    prompt: str
    enhance_prompt: Optional[bool] = True
    generate_t_pose: Optional[bool] = True
    analyze_theme: Optional[bool] = True

class RigModelRequest(BaseModel):
    glb_base64: str
    rigging_method: Optional[Literal["mixamo", "auto"]] = "auto"

class ThemeAnalysis(BaseModel):
    primary_theme: str
    environment_params: Dict
    suggested_enhancements: List[str]

# Theme keywords for analysis
THEME_KEYWORDS = {
    "cyberpunk": {
        "keywords": ["cyber", "punk", "neon", "tech", "futuristic", "robot", "android", "synthetic", "chrome", "hologram"],
        "environment": {
            "skybox_color": "#1a0033",
            "ground_color": "#0a0a0a",
            "fog_color": "#ff00ff",
            "fog_density": 0.02,
            "lights": [
                {"type": "point", "color": "#ff00ff", "intensity": 2, "position": [5, 5, 5]},
                {"type": "point", "color": "#00ffff", "intensity": 2, "position": [-5, 5, -5]},
                {"type": "ambient", "color": "#220044", "intensity": 0.3}
            ],
            "particles": True,
            "grid_color": "#ff00ff"
        }
    },
    "fantasy": {
        "keywords": ["wizard", "mage", "elf", "dwarf", "orc", "dragon", "knight", "magic", "sword", "armor", "medieval"],
        "environment": {
            "skybox_color": "#87CEEB",
            "ground_color": "#3a5f3a",
            "fog_color": "#e6f3ff",
            "fog_density": 0.01,
            "lights": [
                {"type": "point", "color": "#ffd700", "intensity": 1.5, "position": [10, 10, 10]},
                {"type": "point", "color": "#9370db", "intensity": 1, "position": [-5, 3, 5]},
                {"type": "ambient", "color": "#f0e68c", "intensity": 0.4}
            ],
            "particles": False,
            "grid_color": "#8b7355"
        }
    },
    "scifi": {
        "keywords": ["space", "alien", "astronaut", "spaceship", "laser", "plasma", "quantum", "galactic"],
        "environment": {
            "skybox_color": "#000033",
            "ground_color": "#1a1a2e",
            "fog_color": "#0066cc",
            "fog_density": 0.015,
            "lights": [
                {"type": "point", "color": "#00ccff", "intensity": 2, "position": [0, 10, 0]},
                {"type": "point", "color": "#ff6600", "intensity": 1.5, "position": [8, 5, -8]},
                {"type": "ambient", "color": "#001133", "intensity": 0.2}
            ],
            "particles": True,
            "grid_color": "#0066cc"
        }
    },
    "horror": {
        "keywords": ["zombie", "vampire", "monster", "demon", "ghost", "undead", "dark", "evil", "creepy"],
        "environment": {
            "skybox_color": "#0a0a0a",
            "ground_color": "#1a0000",
            "fog_color": "#660000",
            "fog_density": 0.03,
            "lights": [
                {"type": "point", "color": "#ff0000", "intensity": 1, "position": [0, 2, 5]},
                {"type": "point", "color": "#800080", "intensity": 0.5, "position": [-3, 1, -3]},
                {"type": "ambient", "color": "#1a0000", "intensity": 0.2}
            ],
            "particles": False,
            "grid_color": "#330000"
        }
    },
    "default": {
        "keywords": [],
        "environment": {
            "skybox_color": "#ffffff",
            "ground_color": "#f0f0f0",
            "fog_color": "#ffffff",
            "fog_density": 0.005,
            "lights": [
                {"type": "directional", "color": "#ffffff", "intensity": 0.8, "position": [10, 20, 10]},
                {"type": "ambient", "color": "#ffffff", "intensity": 0.3}
            ],
            "particles": False,
            "grid_color": "#cccccc"
        }
    }
}

def analyze_theme(prompt: str) -> ThemeAnalysis:
    """Analyze prompt to determine theme and environment parameters"""
    prompt_lower = prompt.lower()
    detected_theme = "default"
    confidence_scores = {}
    
    for theme, config in THEME_KEYWORDS.items():
        if theme == "default":
            continue
        score = sum(1 for keyword in config["keywords"] if keyword in prompt_lower)
        confidence_scores[theme] = score
        
    if confidence_scores:
        best_theme = max(confidence_scores, key=confidence_scores.get)
        if confidence_scores[best_theme] > 0:
            detected_theme = best_theme
    
    # Get environment parameters
    env_params = THEME_KEYWORDS[detected_theme]["environment"]
    
    # Suggest enhancements based on theme
    enhancements = []
    if detected_theme == "cyberpunk":
        enhancements = ["glowing neon accents", "metallic textures", "holographic effects"]
    elif detected_theme == "fantasy":
        enhancements = ["magical aura", "ancient runes", "mystical glow"]
    elif detected_theme == "scifi":
        enhancements = ["energy shields", "plasma effects", "advanced technology"]
    elif detected_theme == "horror":
        enhancements = ["dark shadows", "eerie atmosphere", "weathered textures"]
    
    return ThemeAnalysis(
        primary_theme=detected_theme,
        environment_params=env_params,
        suggested_enhancements=enhancements
    )

def enhance_prompt_for_character(prompt: str, generate_t_pose: bool = True) -> str:
    """Enhance prompt for better character generation"""
    # Analyze theme first
    theme_analysis = analyze_theme(prompt)
    
    # Base enhancements for character generation
    enhancements = [
        "full body character",
        "centered composition",
        "detailed textures",
        "high quality 3D render style"
    ]
    
    # Add T-pose if requested
    if generate_t_pose:
        enhancements.append("T-pose stance")
        enhancements.append("arms extended horizontally")
        enhancements.append("standing upright")
    
    # Add theme-specific enhancements
    enhancements.extend(theme_analysis.suggested_enhancements)
    
    # Clean the original prompt
    clean_prompt = prompt.strip()
    
    # Build enhanced prompt
    enhanced = f"{clean_prompt}, {', '.join(enhancements)}, white background, studio lighting"
    
    return enhanced

async def generate_image_sdxl(prompt: str, enhance: bool = True, t_pose: bool = True) -> Dict:
    """Generate image using various AI services"""
    # Enhance prompt if requested
    final_prompt = enhance_prompt_for_character(prompt, t_pose) if enhance else prompt
    
    # Try multiple services in order of preference
    methods_to_try = [
        ("prodia_sdxl", generate_with_prodia),
        ("stable_diffusion_xl", generate_with_stable_diffusion_xl),
        ("pollinations", generate_with_pollinations),
        ("playground_v2", generate_with_playground)
    ]
    
    last_error = None
    for method_name, method_func in methods_to_try:
        try:
            result = await method_func(final_prompt)
            if result:
                return {
                    "success": True,
                    "image_base64": result,
                    "enhanced_prompt": final_prompt,
                    "original_prompt": prompt,
                    "method": method_name
                }
        except Exception as e:
            last_error = e
            continue
    
    # If all methods fail, raise the last error
    raise HTTPException(status_code=500, detail=f"Image generation failed: {str(last_error)}")

async def generate_with_prodia(prompt: str) -> str:
    """Generate using Prodia's SDXL API (free tier)"""
    try:
        # Prodia offers free SDXL generation
        client = Client("prodia/sdxl-stable-diffusion-xl")
        result = client.predict(
            prompt,  # prompt
            "blurry, low quality, distorted",  # negative prompt
            20,  # steps
            7,  # cfg scale
            512,  # width
            512,  # height
            -1,  # seed
            api_name="/predict"
        )
        
        if result and isinstance(result, str):
            with open(result, "rb") as f:
                img_bytes = f.read()
            if os.path.exists(result):
                os.unlink(result)
            return base64.b64encode(img_bytes).decode('utf-8')
    except:
        raise

async def generate_with_stable_diffusion_xl(prompt: str) -> str:
    """Try alternative SDXL spaces"""
    try:
        # Try alternative SDXL space
        client = Client("hysts/SDXL")
        result = client.predict(
            prompt,
            "blurry, low quality",
            7.5,  # guidance
            25,  # steps
            api_name="/run"
        )
        
        if result and len(result) > 0:
            img_path = result[0] if isinstance(result, tuple) else result
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            if os.path.exists(img_path):
                os.unlink(img_path)
            return base64.b64encode(img_bytes).decode('utf-8')
    except:
        raise

async def generate_with_pollinations(prompt: str) -> str:
    """Use Pollinations AI as fallback"""
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try with different model parameters
        urls_to_try = [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&model=flux&nologo=true",
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true",
            f"https://pollinations.ai/p/{encoded_prompt}?width=512&height=512"
        ]
        
        for url in urls_to_try:
            try:
                response = await client.get(url)
                if response.status_code == 200 and response.content:
                    return base64.b64encode(response.content).decode('utf-8')
            except:
                continue
    
    raise Exception("Pollinations generation failed")

async def generate_with_playground(prompt: str) -> str:
    """Try Playground v2 model"""
    try:
        client = Client("playgroundai/playground-v2.5-1024px-aesthetic")
        result = client.predict(
            prompt,
            "ugly, blurry, low quality",
            True,  # randomize seed
            512,  # width
            512,  # height
            3,  # guidance scale
            api_name="/predict"
        )
        
        if result:
            img_path = result[0] if isinstance(result, tuple) else result
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            if os.path.exists(img_path):
                os.unlink(img_path)
            return base64.b64encode(img_bytes).decode('utf-8')
    except:
        raise

async def convert_to_3d_hunyuan(image_base64: str) -> Dict:
    """Convert image to 3D using Hunyuan3D or similar free service"""
    try:
        # Try Hunyuan3D-1 space
        client = Client("Tencent/Hunyuan3D-1")
        
        # Save image temporarily
        img_bytes = base64.b64decode(image_base64)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name
        
        # Generate 3D model
        result = client.predict(
            tmp_path,  # input image
            30,  # number of steps
            3,  # seed
            "std",  # guidance type
            api_name="/image_to_3d"
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Result should contain paths to generated files
        if result and len(result) > 0:
            # Find the GLB file
            glb_path = None
            for item in result:
                if isinstance(item, str) and item.endswith('.glb'):
                    glb_path = item
                    break
            
            if glb_path and os.path.exists(glb_path):
                with open(glb_path, "rb") as f:
                    glb_bytes = f.read()
                glb_base64 = base64.b64encode(glb_bytes).decode('utf-8')
                
                return {
                    "success": True,
                    "glb_base64": glb_base64,
                    "method": "hunyuan3d"
                }
        
        raise Exception("Hunyuan3D generation failed")
        
    except Exception as e:
        # Fallback to TripoSR (already implemented)
        try:
            client = Client("stabilityai/TripoSR")
            
            img_bytes = base64.b64decode(image_base64)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            
            result = client.predict(
                tmp_path,
                True,  # remove background
                0.5,  # foreground ratio
                api_name="/run"
            )
            
            os.unlink(tmp_path)
            
            if result and len(result) > 1:
                glb_path = result[1]
                with open(glb_path, "rb") as f:
                    glb_bytes = f.read()
                glb_base64 = base64.b64encode(glb_bytes).decode('utf-8')
                
                return {
                    "success": True,
                    "glb_base64": glb_base64,
                    "method": "triposr_fallback"
                }
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"3D conversion failed: {str(e)}")

async def auto_rig_model(glb_base64: str, method: str = "auto") -> Dict:
    """Auto-rig a 3D model using Mixamo or procedural rigging"""
    try:
        # For now, we'll implement a basic procedural rigging approach
        # In production, you'd integrate with Mixamo API or use Blender Python
        
        # Decode GLB
        glb_bytes = base64.b64decode(glb_base64)
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(suffix=".glb", delete=False) as tmp:
            tmp.write(glb_bytes)
            input_path = tmp.name
        
        # Here you would normally:
        # 1. Upload to Mixamo via their API (requires authentication)
        # 2. Or use Blender Python API for procedural rigging
        # 3. Or use a rigging service API
        
        # For demonstration, we'll add basic metadata indicating rigging is needed
        rigging_metadata = {
            "rigged": False,
            "method_requested": method,
            "bones_needed": [
                "root", "spine", "chest", "neck", "head",
                "shoulder_l", "arm_l", "forearm_l", "hand_l",
                "shoulder_r", "arm_r", "forearm_r", "hand_r",
                "thigh_l", "shin_l", "foot_l",
                "thigh_r", "shin_r", "foot_r"
            ],
            "message": "Model prepared for rigging. Use Mixamo or Blender for actual rigging."
        }
        
        # Clean up
        os.unlink(input_path)
        
        # Return the original model with rigging metadata
        return {
            "success": True,
            "glb_base64": glb_base64,
            "rigging_metadata": rigging_metadata,
            "message": "Model ready for rigging. Upload to Mixamo.com for free auto-rigging."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rigging failed: {str(e)}")

# Full pipeline function
async def full_character_pipeline(prompt: str) -> Dict:
    """Execute the full character generation pipeline"""
    try:
        # Step 1: Analyze theme
        theme_analysis = analyze_theme(prompt)
        
        # Step 2: Generate image with SDXL
        image_result = await generate_image_sdxl(prompt, enhance=True, t_pose=True)
        
        # Step 3: Convert to 3D
        model_result = await convert_to_3d_hunyuan(image_result["image_base64"])
        
        # Step 4: Prepare for rigging
        rig_result = await auto_rig_model(model_result["glb_base64"])
        
        return {
            "success": True,
            "theme_analysis": {
                "primary_theme": theme_analysis.primary_theme,
                "environment_params": theme_analysis.environment_params,
                "suggested_enhancements": theme_analysis.suggested_enhancements
            },
            "image": {
                "base64": image_result["image_base64"],
                "enhanced_prompt": image_result["enhanced_prompt"]
            },
            "model": {
                "glb_base64": model_result["glb_base64"],
                "method": model_result.get("method", "unknown")
            },
            "rigging": rig_result["rigging_metadata"],
            "message": "Character pipeline completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
