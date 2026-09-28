"""
Train ResNet50 on Retinitis Pigmentosa dataset
Classes:
  0 = Normal (healthy)
  1 = Retina_Pigmentosa (disease)
"""

import os, torch, torch.nn as nn
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader, random_split
from pathlib import Path
import shutil

# ── Paths ──────────────────────────────────────────────────────────────
IMAGES_DIR  = Path("images")
DATASET_DIR = Path("dataset_structured")
MODEL_DIR   = Path("models")
MODEL_PATH  = MODEL_DIR / "resnet50_retinitis_classifier.pth"

# ── Build a structured folder (ImageFolder expects class subfolders) ───
def build_dataset():
    for cls, prefix in [("Normal", "Normal_"), ("Disease", "Retina_Pigmentosa_")]:
        dst = DATASET_DIR / cls
        dst.mkdir(parents=True, exist_ok=True)
        for f in IMAGES_DIR.glob(f"{prefix}*.png"):
            target = dst / f.name
            if not target.exists():
                shutil.copy2(f, target)
    print(f"Dataset ready: {sum(1 for _ in DATASET_DIR.rglob('*.png'))} images")

# ── Config ─────────────────────────────────────────────────────────────
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")
EPOCHS      = 5
BATCH_SIZE  = 32
LR          = 1e-4
INPUT_SIZE  = 224

print(f"Using device: {DEVICE}")
build_dataset()

# ── Transforms ─────────────────────────────────────────────────────────
train_tf = transforms.Compose([
    transforms.Resize((INPUT_SIZE, INPUT_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])
val_tf = transforms.Compose([
    transforms.Resize((INPUT_SIZE, INPUT_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# ── Dataset split ──────────────────────────────────────────────────────
full_ds = datasets.ImageFolder(DATASET_DIR)
# class_to_idx: {'Disease': 0, 'Normal': 1} — note alphabetical order
print("Class mapping:", full_ds.class_to_idx)

n_val   = int(0.15 * len(full_ds))
n_train = len(full_ds) - n_val
train_ds, val_ds = random_split(full_ds, [n_train, n_val],
                                generator=torch.Generator().manual_seed(42))

# Apply separate transforms
train_ds.dataset.transform = train_tf   # shared ref — ok for this script
val_ds.dataset.transform   = val_tf

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

# ── Model ──────────────────────────────────────────────────────────────
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
for param in model.parameters():           # freeze backbone
    param.requires_grad = False

num_features = model.fc.in_features
model.fc = nn.Sequential(
    nn.Linear(num_features, 512),
    nn.ReLU(inplace=True),
    nn.Dropout(0.3),
    nn.Linear(512, 2)
)
model = model.to(DEVICE)

# ── Training ───────────────────────────────────────────────────────────
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.fc.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)

best_val_acc = 0.0
for epoch in range(EPOCHS):
    # -- Train --
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    for i, (inputs, labels) in enumerate(train_loader):
        inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total   += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        if (i + 1) % 10 == 0:
            print(f"  Epoch {epoch+1}/{EPOCHS} | Batch {i+1}/{len(train_loader)} "
                  f"| Loss: {running_loss/(i+1):.4f} | Acc: {100.*correct/total:.1f}%")

    train_acc = 100. * correct / total

    # -- Validate --
    model.eval()
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            val_total   += labels.size(0)
            val_correct += predicted.eq(labels).sum().item()

    val_acc = 100. * val_correct / val_total
    print(f"\nEpoch {epoch+1}/{EPOCHS} — Train Acc: {train_acc:.1f}%  Val Acc: {val_acc:.1f}%\n")

    scheduler.step()

    # Save best model
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        MODEL_DIR.mkdir(exist_ok=True)
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"  [SAVED] Best model saved ({val_acc:.1f}%) -> {MODEL_PATH}\n")

print(f"\nTraining complete! Best val accuracy: {best_val_acc:.1f}%")
print(f"Model saved to: {MODEL_PATH}")
