from app.services.ocr import process_pan_card

if __name__ == "__main__":
    path = "sample-image.png"
    result = process_pan_card(path)
    print(result)
