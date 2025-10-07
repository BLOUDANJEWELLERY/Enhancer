from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
from realesrgan import RealESRGAN
from gfpgan import GFPGANer
from PIL import Image
import shutil
import uuid

app = FastAPI()

# Model init
model_path = "RealESRGAN_x4.pth"  # we will download automatically if missing
upscaler = RealESRGAN(model_path, scale=4)
face_enhancer = GFPGANer(model_path='GFPGANv1.3.pth', upscale=1)

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    # Save uploaded image
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    upload_path = UPLOAD_DIR / filename
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Open image
    img = Image.open(upload_path).convert("RGB")

    # Optional: Face enhancement
    img, _ = face_enhancer.enhance(img, has_aligned=False)

    # Upscale
    result = upscaler.predict(img)

    # Save output
    out_path = OUTPUT_DIR / filename
    result.save(out_path)

    return FileResponse(out_path)