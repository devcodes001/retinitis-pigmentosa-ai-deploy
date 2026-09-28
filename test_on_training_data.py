"""
Comprehensive validation on real training dataset.
Tests model on actual Normal and RP images from training set.
"""

import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os
from pathlib import Path
import random
from collections import defaultdict

# Model setup
import sys
sys.path.insert(0, r'C:\Users\djlga\Downloads\retina_ai_deployment')
from app import load_model, process_image, CFG

def load_training_data():
    """Load paths to training images"""
    dataset_path = Path(r'C:\Users\djlga\Downloads\archive\kaggle\working\augmented_dataset1\images')
    
    normal_images = list(dataset_path.glob('Normal*.png'))
    rp_images = list(dataset_path.glob('Retina_Pigmentosa*.png'))
    
    return normal_images, rp_images

def test_batch(model, image_paths, class_name, num_samples=50):
    """Test a batch of images from one class"""
    
    if len(image_paths) < num_samples:
        num_samples = len(image_paths)
    
    sample_paths = random.sample(image_paths, num_samples)
    
    results = {
        'class': class_name,
        'num_tested': 0,
        'correct': 0,
        'incorrect': 0,
        'probabilities': [],
        'predictions': [],
        'errors': []
    }
    
    for img_path in sample_paths:
        try:
            # Load and process image
            img = Image.open(img_path).convert('RGB')
            img_tensor = process_image(img)
            
            # Get prediction
            with torch.no_grad():
                output = model(img_tensor.unsqueeze(0))
                prob = output.squeeze().item()
            
            results['num_tested'] += 1
            results['probabilities'].append(prob)
            
            # Determine prediction
            if prob >= CFG.THRESHOLD:
                prediction = 'RP'
            else:
                prediction = 'Normal'
            
            results['predictions'].append(prediction)
            
            # Check if correct
            if (class_name == 'Normal' and prediction == 'Normal') or \
               (class_name == 'RP' and prediction == 'RP'):
                results['correct'] += 1
            else:
                results['incorrect'] += 1
                results['errors'].append({
                    'image': str(img_path.name),
                    'prob': prob,
                    'predicted': prediction,
                    'actual': class_name
                })
        
        except Exception as e:
            results['errors'].append({
                'image': str(img_path.name),
                'error': str(e)
            })
    
    return results

def print_results(normal_results, rp_results):
    """Print comprehensive results"""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE VALIDATION ON TRAINING DATA".center(80))
    print("="*80)
    
    # Normal results
    print("\n[NORMAL CLASS]")
    print(f"  Tested: {normal_results['num_tested']}")
    print(f"  Correct: {normal_results['correct']}")
    print(f"  Incorrect: {normal_results['incorrect']}")
    if normal_results['num_tested'] > 0:
        accuracy = (normal_results['correct'] / normal_results['num_tested']) * 100
        print(f"  Accuracy: {accuracy:.1f}%")
        
        probs = normal_results['probabilities']
        print(f"  Avg Probability: {np.mean(probs):.4f}")
        print(f"  Min Probability: {np.min(probs):.4f}")
        print(f"  Max Probability: {np.max(probs):.4f}")
        print(f"  Std Probability: {np.std(probs):.4f}")
    
    # RP results
    print("\n[RP CLASS (Disease)]")
    print(f"  Tested: {rp_results['num_tested']}")
    print(f"  Correct: {rp_results['correct']}")
    print(f"  Incorrect: {rp_results['incorrect']}")
    if rp_results['num_tested'] > 0:
        accuracy = (rp_results['correct'] / rp_results['num_tested']) * 100
        print(f"  Accuracy: {accuracy:.1f}%")
        
        probs = rp_results['probabilities']
        print(f"  Avg Probability: {np.mean(probs):.4f}")
        print(f"  Min Probability: {np.min(probs):.4f}")
        print(f"  Max Probability: {np.max(probs):.4f}")
        print(f"  Std Probability: {np.std(probs):.4f}")
    
    # Overall
    print("\n[OVERALL]")
    total_correct = normal_results['correct'] + rp_results['correct']
    total_tested = normal_results['num_tested'] + rp_results['num_tested']
    overall_accuracy = (total_correct / total_tested) * 100 if total_tested > 0 else 0
    print(f"  Total Tested: {total_tested}")
    print(f"  Total Correct: {total_correct}")
    print(f"  Overall Accuracy: {overall_accuracy:.1f}%")
    
    # Show misclassifications
    all_errors = normal_results['errors'] + rp_results['errors']
    if all_errors:
        print(f"\n[MISCLASSIFICATIONS] ({len(all_errors)} total)")
        print("-" * 80)
        for i, error in enumerate(all_errors[:10], 1):  # Show first 10
            if 'error' in error:
                print(f"  {i}. {error['image']}: ERROR - {error['error']}")
            else:
                print(f"  {i}. {error['image']}")
                print(f"     Predicted: {error['predicted']} | Actual: {error['actual']} | Prob: {error['prob']:.4f}")
        
        if len(all_errors) > 10:
            print(f"  ... and {len(all_errors) - 10} more")
    
    # Classification boundary analysis
    print(f"\n[CLASSIFICATION BOUNDARY]")
    print(f"  Threshold: {CFG.THRESHOLD:.4f}")
    
    normal_probs = normal_results['probabilities']
    rp_probs = rp_results['probabilities']
    
    if normal_probs and rp_probs:
        normal_max = max(normal_probs)
        rp_min = min(rp_probs)
        
        print(f"  Normal max prob: {normal_max:.4f}")
        print(f"  RP min prob: {rp_min:.4f}")
        
        if normal_max < CFG.THRESHOLD < rp_min:
            gap = rp_min - normal_max
            print(f"  ✓ Clean separation! Gap = {gap:.4f}")
        else:
            print(f"  ⚠ Overlap detected in classification range")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("Loading model...")
    model = load_model()
    model.eval()
    
    print("Loading training dataset paths...")
    normal_images, rp_images = load_training_data()
    
    print(f"Found {len(normal_images)} Normal images")
    print(f"Found {len(rp_images)} RP images")
    
    print("\nTesting on Normal images (50 samples)...")
    normal_results = test_batch(model, normal_images, 'Normal', num_samples=50)
    
    print("Testing on RP images (50 samples)...")
    rp_results = test_batch(model, rp_images, 'RP', num_samples=50)
    
    # Print results
    print_results(normal_results, rp_results)
    
    # Save detailed results
    results_file = 'training_data_validation_results.txt'
    with open(results_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("COMPREHENSIVE VALIDATION ON TRAINING DATA\n")
        f.write("="*80 + "\n\n")
        
        f.write("NORMAL CLASS RESULTS:\n")
        f.write(f"  Tested: {normal_results['num_tested']}\n")
        f.write(f"  Correct: {normal_results['correct']}\n")
        f.write(f"  Incorrect: {normal_results['incorrect']}\n")
        f.write(f"  Probabilities: {normal_results['probabilities']}\n\n")
        
        f.write("RP CLASS RESULTS:\n")
        f.write(f"  Tested: {rp_results['num_tested']}\n")
        f.write(f"  Correct: {rp_results['correct']}\n")
        f.write(f"  Incorrect: {rp_results['incorrect']}\n")
        f.write(f"  Probabilities: {rp_results['probabilities']}\n\n")
        
        f.write("MISCLASSIFICATIONS:\n")
        for error in normal_results['errors'] + rp_results['errors']:
            f.write(f"  {error}\n")
    
    print(f"\nDetailed results saved to: {results_file}")
