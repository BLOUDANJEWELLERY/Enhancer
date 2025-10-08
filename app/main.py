import os
import uuid
import subprocess
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AI Image Enhancer")

# Directories for uploads and outputs
UPLOAD_DIR = "/app/uploads"
OUTPUT_DIR = "/app/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup templates
templates = Jinja2Templates(directory="/app/templates")

# Mount static folder if you later add styles/scripts
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page UI"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    """Handle image upload and enhancement using RealSR"""
    # Save input
    input_filename = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Prepare output path
    output_filename = f"enhanced_{input_filename}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # RealSR binary + model paths
    realsr_bin = "/usr/local/bin/realsr-ncnn-vulkan"
    model_dir = "/usr/local/bin/models-DF2K_JPEG"

    # Run enhancement
    try:
        subprocess.run(
            [
                realsr_bin,
                "-i", input_path,
                "-o", output_path,
                "-s", "4",        # upscale factor
                "-m", model_dir   # model directory
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            {"error": f"RealSR failed: {e.stderr.decode('utf-8')}"},
            status_code=500
        )

    return FileResponse(output_path, media_type="image/png", filename=output_filename)