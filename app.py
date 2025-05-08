import streamlit as st
import os
import csv
import requests
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from PIL import Image
import io

# === Streamlit UI ===
st.title("📸 Image Downloader & Resizer from CSV")
st.write("Upload a CSV with image URLs and SKUs. Images will be resized and saved as .jpg using SKU values.")

# === CSV Upload ===
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    image_column = st.text_input("🔗 Column name for image URL", value="Image")
    sku_column = st.text_input("🔑 Column name for SKU (used as filename)", value="sku")

    # === Dimension Inputs ===
    col1, col2 = st.columns(2)
    with col1:
        width = st.number_input("Image Width (px)", min_value=1, value=1200)
    with col2:
        height = st.number_input("Image Height (px)", min_value=1, value=1200)

    if st.button("📥 Download & Resize Images"):
        with TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "input.csv")
            with open(csv_path, "wb") as f:
                f.write(uploaded_file.read())

            image_dir = os.path.join(tmpdir, "images")
            os.makedirs(image_dir, exist_ok=True)

            def download_and_resize_image(url, sku, save_dir, size):
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                    resized_img = img.resize(size, Image.LANCZOS)
                    file_path = os.path.join(save_dir, f"{sku}.jpg")
                    resized_img.save(file_path, format="JPEG", quality=90)
                except:
                    pass  # Silently skip errors

            # Process CSV
            with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    url = row.get(image_column)
                    sku = row.get(sku_column)
                    if url and sku:
                        download_and_resize_image(url, sku, image_dir, (width, height))

            # Create ZIP
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, 'w') as zipf:
                for root, _, files in os.walk(image_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)

            st.success("🎉 All images resized and zipped!")
            st.download_button(
                label="📦 Download ZIP of Images",
                data=zip_buffer.getvalue(),
                file_name="resized_images.zip",
                mime="application/zip"
            )
