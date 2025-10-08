import os
import uuid
import subprocess
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse
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

# Mount static folders
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    # Save input file
    input_filename = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Prepare output file
    output_filename = f"enhanced_{input_filename}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Run RealSR NCNN Vulkan
    try:
        result = subprocess.run(
            ["realsr-ncnn-vulkan", "-i", input_path, "-o", output_path, "-s", "4"],
            capture_output=True,
            text=True,
            check=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("ERROR:", e.stderr)
        return {"error": f"Enhancement failed:\n{e.stderr}"}
    except Exception as e:
        print("GENERAL ERROR:", str(e))
        return {"error": str(e)}

    if not os.path.exists(output_path):
        return {"error": "Output file not created — enhancement may have failed."}

    return FileResponse(output_path, media_type="image/png", filename=output_filename)