import os
import shutil
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from download_model import ensure_model

# downloading model
ensure_model()


TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/segment/")
async def segment_nii(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{uid}_input.nii.gz")
    output_path = os.path.join(TEMP_DIR, f"{uid}_output.nii.gz")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        subprocess.run([
            "python", "./scripts/commands/SynthSeg_predict.py",
            "--i", input_path,
            "--o", output_path
        ], check=True, cwd="D:/SynthSeg/SynthSeg")
    except subprocess.CalledProcessError as e:
        return {"error": f"Prediction failed: {e}"}

    return FileResponse(output_path, media_type="application/gzip", filename="segmented.nii.gz")
