import streamlit as st
import os
import csv
import requests
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from PIL import Image, ImageOps
import io
import time

# === Streamlit UI ===
st.title("📸 Bulk Image Downloader, Resizer & Zipper")
st.write("Upload a CSV with image URLs and SKUs. Images are resized to your dimensions with optional padding color and saved as `.jpg`.")

# === Upload CSV ===
uploaded_file = st.file_uploader("📄 Upload your CSV file", type=["csv"])

if uploaded_file:
    image_column = st.text_input("🔗 Column name for image URL", value="Image")
    sku_column = st.text_input("🔑 Column name for SKU (used as filename)", value="sku")

    # === Resize settings ===
    col1, col2 = st.columns(2)
    with col1:
        width = st.number_input("📐 Width (px)", min_value=1, value=1200)
    with col2:
        height = st.number_input("📐 Height (px)", min_value=1, value=1200)

    # === Background color ===
    bg_color = st.color_picker("🎨 Background color (used for padding)", "#FFFFFF")

    if st.button("📥 Start Download"):
        with TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "input.csv")
            with open(csv_path, "wb") as f:
                f.write(uploaded_file.read())

            image_dir = os.path.join(tmpdir, "images")
            os.makedirs(image_dir, exist_ok=True)

            # === Read CSV ===
            with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = list(csv.DictReader(csvfile))
                total = len(reader)
                if total == 0:
                    st.error("❌ CSV file is empty or incorrectly formatted.")
                    st.stop()

                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Download & resize
                start_time = time.time()

                for idx, row in enumerate(reader, start=1):
                    url = row.get(image_column)
                    sku = row.get(sku_column)
                    if url and sku:
                        try:
                            response = requests.get(url, timeout=10)
                            response.raise_for_status()
                            img = Image.open(io.BytesIO(response.content)).convert("RGB")

                            # Resize and pad
                            resized = ImageOps.pad(
                                img,
                                size=(width, height),
                                color=bg_color,
                                method=Image.LANCZOS
                            )

                            # Save as .jpg
                            output_path = os.path.join(image_dir, f"{sku}.jpg")
                            resized.save(output_path, format="JPEG", quality=90)

                        except Exception:
                            pass  # silently skip

                    # Update progress
                    elapsed = time.time() - start_time
                    avg_time = elapsed / idx
                    remaining = avg_time * (total - idx)
                    status_text.text(f"Processing {idx}/{total} | ⏳ Est. {int(remaining)}s left")
                    progress_bar.progress(idx / total)

            # === Create ZIP ===
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, 'w') as zipf:
                for root, _, files in os.walk(image_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)

            st.success("🎉 All images processed and zipped!")
            st.download_button(
                label="📦 Download ZIP of Images",
                data=zip_buffer.getvalue(),
                file_name="resized_images.zip",
                mime="application/zip"
            )
