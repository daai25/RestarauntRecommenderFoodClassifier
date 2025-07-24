from pathlib import Path
from sklearn.model_selection import train_test_split
import shutil

# Adjust these paths
raw_data = Path(__file__).parent.parent / "data" / "raw_data"
output = Path(__file__).parent.parent / "data" / "dataset"
splits = {"train": 0.8, "validation": 0.1, "test": 0.1}

# Make sure output directories exist
for split in splits:
    (output / split).mkdir(parents=True, exist_ok=True)


counter = 0

for class_dir in sorted(raw_data.iterdir()):
    if not class_dir.is_dir():
        continue
    class_name = class_dir.name
    files = list(class_dir.glob("*"))
    if not files:
        continue

    # initial train+temp split (80% train, 20% temp)
    train_files, temp_files = train_test_split(
        files, test_size=splits["validation"] + splits["test"], random_state=42
    )
    # split temp into validation and test equally
    val_size = splits["validation"] / (splits["validation"] + splits["test"])
    val_files, test_files = train_test_split(
        temp_files, test_size=1 - val_size, random_state=42
    )

    for split, split_files in [("train", train_files),
                               ("validation",   val_files),
                               ("test",  test_files)]:
        # create class subfolder
        target_dir = output / split / class_name
        target_dir.mkdir(parents=True, exist_ok=True)

        for src_path in split_files:
            counter += 1
            dst = target_dir / src_path.name
            # Option A: Copy (takes space/time)
            shutil.copy2(src_path, dst)
            # Option B: Symlink (fast, space‑saving)
            # dst.symlink_to(src_path.resolve())

            if counter % 1000 == 0:
                print(f"Processed {counter} processed files...")
