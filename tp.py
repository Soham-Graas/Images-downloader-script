import pandas as pd
import os

def split_excel(file_path, chunk_size=2500):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    # Create output directory
    output_dir = f"{base_name}_split"
    os.makedirs(output_dir, exist_ok=True)

    # Split and save chunks
    total_rows = len(df)
    for i in range(0, total_rows, chunk_size):
        part_df = df[i:i+chunk_size]
        part_num = i // chunk_size + 1
        part_filename = os.path.join(output_dir, f"{base_name}_part{part_num}.xlsx")
        part_df.to_excel(part_filename, index=False)
        print(f"Saved: {part_filename}")

# Example usage
split_excel(r"C:\Users\Soham Hardas\Documents\KSA product creation\seller_product_import_assign.xlsx")  # Replace with your actual file
