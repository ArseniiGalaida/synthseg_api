import os
import gdown
from dotenv import load_dotenv

load_dotenv()


def ensure_model():
    model_path = os.path.join(os.path.dirname(__file__), "../models", "synthseg_2.0.h5")
    file_id = os.getenv("MODEL_FILE_ID")

    if not os.path.exists(model_path):
        print("Downloading model from Google Drive...")

        url = f"https://drive.google.com/uc?id={file_id}"

        gdown.download(url, model_path, quiet=False)

        print("Model downloaded!")
    else:
        print("Model already exists!")
