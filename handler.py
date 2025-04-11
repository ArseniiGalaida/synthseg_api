import os
import uuid
import subprocess
import base64
import runpod
from download_model import ensure_model


def run(job):

    ensure_model()

    uid = str(uuid.uuid4())
    temp_dir = "/tmp"
    input_path = os.path.join(temp_dir, f"{uid}_input.nii.gz")
    output_path = os.path.join(temp_dir, f"{uid}_output.nii.gz")

    with open(input_path, "wb") as f:
        f.write(base64.b64decode(job["input"]["file_data"]))

    try:
        subprocess.run([
            "python", "scripts/commands/SynthSeg_predict.py",
            "--i", input_path,
            "--o", output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Prediction failed: {str(e)}"}

    with open(output_path, "rb") as f:
        result_data = base64.b64encode(f.read()).decode("utf-8")

    os.remove(input_path)
    os.remove(output_path)

    return {
        "file_name": "segmented.nii.gz",
        "file_data": result_data
    }


if __name__ == '__main__':
    runpod.serverless.start({'handler': run})