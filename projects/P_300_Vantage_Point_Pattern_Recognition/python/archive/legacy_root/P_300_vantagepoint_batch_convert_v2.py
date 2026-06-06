import os
import zipfile
import datetime

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

today = datetime.date.today()
month_name = today.strftime("%B")
year = today.strftime("%Y")

zip_name = f"P_300_{month_name}_{year}_MTD.zip"
zip_path = os.path.join(OUTPUT_FOLDER, zip_name)

zip_mode = "a" if os.path.exists(zip_path) else "w"
monthly_zip = zipfile.ZipFile(zip_path, zip_mode, zipfile.ZIP_DEFLATED)


def convert_file(input_file, output_file):
    with open(input_file, "r") as f_in:
        data = f_in.read()

    with open(output_file, "w") as f_out:
        f_out.write(data)


def process_all_files():
    converted_files = []

    files = [f for f in os.listdir(INPUT_FOLDER)
             if f.lower().endswith(".txt") or f.lower().endswith(".dat")]

    if not files:
        print("No input files found.")
        input("\nPress Enter to exit...")
        return

    for filename in files:
        input_path = os.path.join(INPUT_FOLDER, filename)

        base, _ = os.path.splitext(filename)
        output_csv = os.path.join(OUTPUT_FOLDER, base + ".csv")

        print(f"Converting: {filename} → {base}.csv")

        convert_file(input_path, output_csv)
        converted_files.append(base + ".csv")

        print(f"Archiving original file into {zip_name}")
        monthly_zip.write(input_path, arcname=filename)

        os.remove(input_path)

    print("\nAll files processed successfully.")
    print(f"Monthly archive updated: {zip_path}")

    print("\n-----------------------------------------")
    print(" Conversion Summary")
    print("-----------------------------------------")
    for f in converted_files:
        print(f"  ✔ {f}")
    print("-----------------------------------------")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    process_all_files()
    monthly_zip.close()
