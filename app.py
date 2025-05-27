import os
import shutil
import pandas as pd

# === CONFIGURATION ===
source_folder = r"C:\Users\Soham Hardas\Downloads\pak"
target_root_folder = r"C:\Users\Soham Hardas\Documents\Pakistan"
csv_file = r"C:\Users\Soham Hardas\Documents\Pakistan\Pakistan Images.csv"
image_column = 'base_image'  # Column in CSV with image names
images_per_folder = 2000
start_folder_index = 1

# === LOAD IMAGE NAMES FROM CSV ===
df = pd.read_csv(csv_file)
image_names = df[image_column].dropna().astype(str).tolist()

# === FILTER TO ONLY EXISTING FILES ===
existing_images = [img for img in image_names if os.path.exists(os.path.join(source_folder, img))]

print(f"📦 Found {len(existing_images)} images to copy.")

# === SPLIT AND COPY IMAGES ===
for i in range(0, len(existing_images), images_per_folder):
    folder_number = start_folder_index + (i // images_per_folder)
    new_folder_name = f'images{folder_number}'
    new_folder_path = os.path.join(target_root_folder, new_folder_name)

    os.makedirs(new_folder_path, exist_ok=True)

    batch = existing_images[i:i + images_per_folder]
    for img_name in batch:
        src_path = os.path.join(source_folder, img_name)
        dst_path = os.path.join(new_folder_path, img_name)

        shutil.copy2(src_path, dst_path)

    print(f"✅ Copied {len(batch)} images to {new_folder_name}")

print("🎉 All available images have been successfully split and copied.")
