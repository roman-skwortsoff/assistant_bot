from PIL import Image
import pytesseract

def extract_text_from_photo(image_path: str) -> str:
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='eng+rus')
        return text.strip()
    except Exception as e:
        print(f"OCR error: {e}")
        return ""
