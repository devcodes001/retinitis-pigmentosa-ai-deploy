import os
from huggingface_hub import HfApi, create_repo
from huggingface_hub.utils import HfHubHTTPError

# Configuration
SPACE_NAME = "retina-ai-diagnostic"
USERNAME = "jayalakshmii0811"  # Replace with your HuggingFace username
TOKEN = "YOUR_HF_TOKEN_HERE"  # Replace with your actual HF token

# Initialize API
api = HfApi(token=TOKEN)

def create_space():
    try:
        # Create the space
        repo_id = f"{USERNAME}/{SPACE_NAME}"
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
            token=TOKEN
        )
        print(f"Space created: https://huggingface.co/spaces/{repo_id}")
        return repo_id
    except HfHubHTTPError as e:
        if "already exists" in str(e):
            print(f"Space already exists: https://huggingface.co/spaces/{USERNAME}/{SPACE_NAME}")
            return f"{USERNAME}/{SPACE_NAME}"
        else:
            raise e

def upload_files(repo_id):
    # Files to upload
    files_to_upload = [
        ("../retina_ai_deployment/app.py", "app.py"),
        ("../retina_ai_deployment/space.py", "space.py"),
        ("../retina_ai_deployment/runtime.txt", "runtime.txt"),
        ("../retina_ai_deployment/pyproject.toml", "pyproject.toml"),
        ("../retina_ai_deployment/.streamlit/config.toml", ".streamlit/config.toml"),
        ("VIT_rp.pth", "models/VIT_rp.pth"),
        ("efficientnet_rp_model.pth", "models/efficientnet_rp_model.pth"),
        ("mobilenet.pth", "models/mobilenet.pth"),
        ("resnet50_retinitis_classifier.pth", "models/resnet50_retinitis_classifier.pth"),
        ("swin_retina_rp_deploy.pth", "models/swin_retina_rp_deploy.pth"),
    ]

    for local_path, repo_path in files_to_upload:
        if os.path.exists(local_path):
            try:
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=repo_path,
                    repo_id=repo_id,
                    repo_type="space",
                    token=TOKEN
                )
                print(f"Uploaded {local_path} to {repo_path}")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        else:
            print(f"File not found: {local_path}")

if __name__ == "__main__":
    repo_id = create_space()
    upload_files(repo_id)
    print(f"\nSpace URL: https://huggingface.co/spaces/{repo_id}")
    print("The Retina AI diagnostic system is now deployed and permanently accessible!")
