import os
import shutil
import uuid
import subprocess
from runpod import serverless
from download_model import ensure_model

TEMP_DIR = "/tmp"


def clean_temp_files(input_path: str, output_path: str):
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)


def process_file(event):
    ensure_model()

    input_file = event.get("input_file")

    if not input_file:
        return {"error": "No input file provided"}

    uid = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{uid}_input.nii.gz")
    output_path = os.path.join(TEMP_DIR, f"{uid}_output.nii.gz")

    with open(input_path, "wb") as f:
        f.write(input_file)

    try:
        subprocess.run([
            "python", "scripts/commands/SynthSeg_predict.py",
            "--i", input_path,
            "--o", output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Prediction failed: {e}"}

    clean_temp_files(input_path, output_path)

    with open(output_path, "rb") as result_file:
        result_data = result_file.read()

    return {"output_file": result_data, "content_type": "application/gzip"}


if __name__ == "__main__":
    serverless.start({"handler": process_file})
