from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import tempfile, uuid, os, subprocess

app = FastAPI()

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    input_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    output_path = input_path.replace(".", "_enhanced.")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Run Real-ESRGAN (CPU mode)
    subprocess.run([
        "realesrgan-ncnn-vulkan",
        "-i", input_path,
        "-o", output_path
    ], check=True)

    return FileResponse(output_path, media_type="image/png")
