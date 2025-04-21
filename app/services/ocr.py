import os
import re
import easyocr
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from app.utils.file import fuzzy_correct_name


# Windows users: set poppler_path to your poppler bin folder
POPPLE_PATH = r"F:\1Development Work\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

def auto_rotate(pil_image):
    try:
        exif = pil_image._getexif()
        orientation_key = 274
        if exif and orientation_key in exif:
            orientation = exif[orientation_key]
            if orientation == 3:
                pil_image = pil_image.rotate(180, expand=True)
            elif orientation == 6:
                pil_image = pil_image.rotate(270, expand=True)
            elif orientation == 8:
                pil_image = pil_image.rotate(90, expand=True)
    except Exception:
        pass
    return pil_image

def convert_pdf_to_image(pdf_path: str) -> str:
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLE_PATH)
    output_path = f"{pdf_path}.jpg"
    images[0].save(output_path, "JPEG")
    return output_path

def extract_text_with_easyocr(image_path: str) -> str:
    # Validate
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    if os.path.getsize(image_path) < 1024:
        raise ValueError("File too small or empty.")

    # Open image
    try:
        pil_img = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Corrupted image: {e}")

    # Rotate if needed
    rotated_img = auto_rotate(pil_img)
    image_np = np.array(rotated_img)

    # OCR
    results = reader.readtext(image_np, detail=0, paragraph=True)
    return "\n".join(results)

def extract_pan_details(text: str) -> dict:
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    dob_pattern = r"\d{2}/\d{2}/\d{4}"
    pan_pattern = r"[A-Z]{5}[0-9O]{4}[A-Z]"
    
    dob = next((re.search(dob_pattern, line).group() for line in lines if re.search(dob_pattern, line)), None)
    pan_number = next((re.search(pan_pattern, line).group() for line in lines if re.search(pan_pattern, line)), None)

    name = fathers_name = None

    # Search for lines that mention name and father's name
    for i, line in enumerate(lines):
        lower_line = line.lower()
        if not name and ("name" in lower_line and "father" not in lower_line):
            # Try to get next non-empty line as name
            if i + 1 < len(lines):
                name = lines[i + 1]
        elif not fathers_name and ("father" in lower_line and "name" in lower_line):
            if i + 1 < len(lines):
                fathers_name = lines[i + 1]

    return {
        "name": fuzzy_correct_name(name),
        "fathersName": fuzzy_correct_name(fathers_name),
        "dob": dob,
        "panNumber": pan_number,
        "rawText": text
    }


def process_pan_card(file_path: str) -> dict:
    ext = file_path.split('.')[-1].lower()
    
    # Convert PDF to image if needed
    if ext == "pdf":
        file_path = convert_pdf_to_image(file_path)

    text = extract_text_with_easyocr(file_path)

    # Optionally remove temporary .jpg if created from PDF
    if file_path.endswith(".pdf.jpg") and os.path.exists(file_path):
        os.remove(file_path)

    return extract_pan_details(text)
