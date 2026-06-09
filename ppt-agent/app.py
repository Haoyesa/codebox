from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from generator.pptx import build_pptx
from generator.content import generate_content
from generator.style import get_style
from generator.image import search_image

app = FastAPI(title="PPT Generator Agent")

app.mount("/static", StaticFiles(directory="static"), name="static")


class GenerateRequest(BaseModel):
    keywords: str
    background: str
    scene: str


@app.post("/generate")
async def generate(req: GenerateRequest):
    style = get_style(req.scene)
    content = await generate_content(req.keywords, req.background, req.scene, style)

    # 为每页内容搜索配图
    images = {}
    for slide in content.get("slides", []):
        if slide.get("type") == "content" and slide.get("title"):
            img_url = search_image(slide.get("title", ""))
            if img_url:
                images[slide["title"]] = img_url

    output = build_pptx(content, style, images)

    return {
        "scene": req.scene,
        "style": style["name"],
        "slides": len(content.get("slides", [])),
        "output": output
    }


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}