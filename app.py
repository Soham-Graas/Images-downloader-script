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
st.write("Upload a CSV with image URLs and SKUs. Images will be resized to 1200×1200 and saved as .jpg using SKU.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    image_column = st.text_input("🔗 Column name for image URL", value="Image")
    sku_column = st.text_input("🔑 Column name for SKU (used as filename)", value="sku")

    if st.button("📥 Download & Resize Images"):
        with TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "input.csv")
            with open(csv_path, "wb") as f:
                f.write(uploaded_file.read())

            image_dir = os.path.join(tmpdir, "images")
            os.makedirs(image_dir, exist_ok=True)

            def download_and_resize_image(url, sku, save_dir):
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                    resized_img = img.resize((1200, 1200), Image.LANCZOS)

                    file_path = os.path.join(save_dir, f"{sku}.jpg")
                    resized_img.save(file_path, format="JPEG", quality=90)
                    st.success(f"✅ Saved: {sku}.jpg")
                except Exception as e:
                    st.error(f"❌ Failed for SKU {sku}: {e}")

            # Read CSV and process images
            with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    url = row.get(image_column)
                    sku = row.get(sku_column)
                    if url and sku:
                        download_and_resize_image(url, sku, image_dir)

            # Zip the images
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, 'w') as zipf:
                for root, _, files in os.walk(image_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)

            st.success("🎉 All images resized and zipped!")

            # Download button
            st.download_button(
                label="📦 Download ZIP of Images",
                data=zip_buffer.getvalue(),
                file_name="resized_images.zip",
                mime="application/zip"
            )
