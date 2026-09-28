#!/usr/bin/env python3
"""Upload images to HuggingFace Dataset in batches"""

from huggingface_hub import HfApi, create_repo
import os
import glob
import time

def main():
    # User's new token
    token = 'YOUR_HF_TOKEN_HERE'  # Replace with your actual HF token
    
    # Dataset repository ID
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
    image_files = sorted(glob.glob('images/*.png') + glob.glob('images/*.jpg') + glob.glob('images/*.jpeg'))
    total_images = len(image_files)
    print(f'Found {total_images} images to upload')
    
    # Upload in batches of 100
    batch_size = 100
    for i in range(0, total_images, batch_size):
        batch = image_files[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_images + batch_size - 1) // batch_size
        
        print(f'\nUploading batch {batch_num}/{total_batches} ({len(batch)} images)...')
        
        try:
            # Upload each file in the batch
            for img_file in batch:
                api.upload_file(
                    path_or_fileobj=img_file,
                    path_in_repo=f"images/{os.path.basename(img_file)}",
                    repo_id=dataset_id,
                    repo_type='dataset',
                    token=token
                )
            print(f'Batch {batch_num} completed!')
        except Exception as e:
            print(f'Error uploading batch {batch_num}: {e}')
        
        # Small delay between batches
        time.sleep(1)
    
    print('\n' + '='*50)
    print('DONE!')
    print(f'Your dataset is live at: https://huggingface.co/datasets/{dataset_id}')
    print('='*50)

if __name__ == "__main__":
    main()
