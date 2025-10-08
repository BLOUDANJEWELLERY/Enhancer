import os
import uuid
import subprocess
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    # Save input
    input_filename = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Prepare output path
    output_filename = f"enhanced_{input_filename}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Run RealSR
    try:
        subprocess.run(
            ["realsr-ncnn-vulkan", "-i", input_path, "-o", output_path, "-s", "4"],
            check=True
        )
    except Exception as e:
        return {"error": str(e)}

    return FileResponse(output_path, media_type="image/png", filename=output_filename)