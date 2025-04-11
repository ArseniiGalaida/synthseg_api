import os
import shutil
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from .download_model import ensure_model


ensure_model()

TEMP_DIR = "../temp"
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_temp_files(input_path: str, output_path: str):
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)


@app.get("/")
def index():
    return {"Extravision": "SynthSegApp"}


@app.post("/segment/")
async def segment_nii(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    ensure_model()

    uid = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{uid}_input.nii.gz")
    output_path = os.path.join(TEMP_DIR, f"{uid}_output.nii.gz")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        subprocess.run([
            "python", "scripts/commands/SynthSeg_predict.py",
            "--i", input_path,
            "--o", output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Prediction failed: {e}"}

    background_tasks.add_task(clean_temp_files, input_path, output_path)

    return FileResponse(output_path, media_type="application/gzip", filename="segmented.nii.gz")
