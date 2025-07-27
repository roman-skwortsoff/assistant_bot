import cv2
import os

def preprocess_image_for_openai(
    image_path,
    output_path="resized.jpg",
    target_width=640,
    quality=90,
    grayscale=True,
    return_stats=True
):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Не удалось загрузить изображение: {image_path}")
        return None

    original_height, original_width = image.shape[:2]

    # Пропорциональное уменьшение
    scale = target_width / original_width
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    if grayscale:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # JPEG качество влияет только на размер файла, но не на стоимость запроса
    cv2.imwrite(output_path, resized, [cv2.IMWRITE_JPEG_QUALITY, quality])

    if return_stats:
        megapixels = (new_width * new_height) / 1_000_000
        estimated_cost = round(megapixels * 0.00765, 6)
        stats = {
            "original_size": f"{original_width}x{original_height}",
            "new_size": f"{new_width}x{new_height}",
            "megapixels": round(megapixels, 4),
            "estimated_cost_usd": estimated_cost,
            "output_path": output_path
        }
        print(stats)

    return output_path
