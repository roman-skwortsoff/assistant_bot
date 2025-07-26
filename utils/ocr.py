import cv2
import numpy as np
from PIL import Image, ImageEnhance
import easyocr
import re
from typing import List, Optional, Tuple


def enhance_code_image(image_path):
    """Чуть улучшает спецсимволы, сохраняя оригинальное изображение"""
    # 1. Загрузка и увеличение 2x
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Изображение не загружено")
    
    resized = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # 2. Создаем маску ТОЛЬКО для нужных символов
    symbol_mask = np.zeros_like(resized)
    
    # 3. Очень мягкое выделение символов (=, _, *, и т.д.)
    symbols = [
        np.array([[0,0,0], [1,1,1], [0,0,0]], np.uint8),  # Горизонтальные
        np.array([[0,1,0], [0,1,0], [0,1,0]], np.uint8),  # Вертикальные
        np.array([[0,1,0], [1,1,1], [0,1,0]], np.uint8)   # Крестообразные
    ]
    
    for kernel in symbols:
        filtered = cv2.morphologyEx(resized, cv2.MORPH_HITMISS, kernel)
        symbol_mask = cv2.bitwise_or(symbol_mask, filtered)
    
    # 4. Слегка усиливаем символы
    enhanced = cv2.addWeighted(resized, 0.9, symbol_mask, 0.25, 0)
    
    return enhanced


def group_text_by_lines(detections: List[Tuple[List[List[int]], str, float]], threshold_y: int = 10) -> List[str]:
    """
    Группирует распознанные текстовые блоки по строкам, учитывая их координаты.
    
    Args:
        detections: Результат EasyOCR в формате [([[x1,y1],[x2,y2],[x3,y3],[x4,y4]], text, confidence).
        threshold_y: Максимальное вертикальное расстояние между строками (пиксели).
    
    Returns:
        Список строк, объединенных по горизонтали.
    """
    if not detections:
        return []
    
    # Сортируем блоки по вертикальной позиции (y-координата верхнего левого угла)
    detections_sorted = sorted(detections, key=lambda det: det[0][0][1])
    
    lines = []
    current_line = []
    prev_y = detections_sorted[0][0][0][1]  # y-координата первого блока
    
    for detection in detections_sorted:
        (bbox, text, _) = detection
        current_y = bbox[0][1]
        
        # Если блок находится на той же строке (с учетом погрешности threshold_y)
        if abs(current_y - prev_y) <= threshold_y:
            current_line.append((bbox[0][0], text))  # (x-координата, текст)
        else:
            # Сортируем слова в строке по x-координате (слева направо)
            current_line_sorted = sorted(current_line, key=lambda x: x[0])
            line_text = " ".join([text for (_, text) in current_line_sorted])
            lines.append(line_text)
            
            # Начинаем новую строку
            current_line = [(bbox[0][0], text)]
            prev_y = current_y
    
    # Добавляем последнюю строку
    if current_line:
        current_line_sorted = sorted(current_line, key=lambda x: x[0])
        line_text = " ".join([text for (_, text) in current_line_sorted])
        lines.append(line_text)
    
    return lines

def extract_text_with_line_grouping(
    image_path: str,
    languages: List[str] = ["ru", "en"],
    detail: bool = True,  # Обязательно True, чтобы получить координаты
) -> Optional[str]:
    """
    Распознает текст с помощью EasyOCR, сохраняя оригинальную структуру строк.
    
    Args:
        image_path: Путь к изображению.
        languages: Языки для распознавания.
        detail: Должен быть True, чтобы получить координаты блоков.
    
    Returns:
        Текст с сохранением структуры строк или None в случае ошибки.
    """
    image = image_path
    try:
        reader = easyocr.Reader(languages)
        detections = reader.readtext(image, detail=detail, paragraph=False)
        
        if not detections:
            return None
        
        lines = group_text_by_lines(detections)
        return "\n".join(lines)
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return None