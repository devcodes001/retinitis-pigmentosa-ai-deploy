#!/usr/bin/env python3
"""Upload images to HuggingFace Dataset"""

from huggingface_hub import HfApi, create_repo
import os
import glob

def main():
    # User's new token
    token = 'YOUR_HF_TOKEN_HERE'  # Replace with your actual HF token
    
    # Dataset repository ID (you can change this to your preferred name)
    dataset_id = 'jayalakshmii0811/retina-images-dataset'
    
    api = HfApi()
    
    # Create dataset repository
    try:
        create_repo(token=token, repo_id=dataset_id, repo_type='dataset', exist_ok=True)
        print(f'Created/access dataset repo: {dataset_id}')
    except Exception as e:
        print(f'Error creating repo: {e}')
        return
    
    # Get all image files
    image_files = glob.glob('images/*.png') + glob.glob('images/*.jpg') + glob.glob('images/*.jpeg')
    print(f'Found {len(image_files)} images to upload')
    
    # Upload images folder
    print('Uploading images folder...')
    try:
        api.upload_folder(
            folder_path='images',
            repo_id=dataset_id,
            repo_type='dataset',
            token=token
        )
        print('Images uploaded successfully!')
    except Exception as e:
        print(f'Error uploading images: {e}')
    
    print('\n' + '='*50)
    print('DONE!')
    print(f'Your dataset is live at: https://huggingface.co/datasets/{dataset_id}')
    print('='*50)

if __name__ == "__main__":
    main()
