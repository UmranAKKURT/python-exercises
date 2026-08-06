import json
import os
from datetime import datetime
from PIL import Image, ImageTk

# Proje ana dizinini ve data klasörünü otomatik belirle
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "compression_history.json")

# Data klasörü yoksa oluştur
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def readable_size(size):
    if size < 1024:
        return f"{size} B"
    size /= 1024
    if size < 1024:
        return f"{size:.2f} KB"
    size /= 1024
    return f"{size:.2f} MB"


def file_size(path):
    return os.path.getsize(path)


def image_resolution(path):
    with Image.open(path) as img:
        return img.size


def create_thumbnail(path, size=(250, 250)):
    img = Image.open(path)
    img.thumbnail(size)
    return ImageTk.PhotoImage(img)


def validate_image(path):
    allowed = (".jpg", ".jpeg", ".png", ".webp")
    extension = os.path.splitext(path)[1].lower()
    return extension in allowed


def save_history(data):
    history = load_history()
    history.append(data)
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def clear_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump([], file)


def history_statistics():
    history = load_history()
    if len(history) == 0:
        return {"count": 0, "saved_bytes": 0, "average_ratio": 0}

    total_saved = 0
    total_ratio = 0
    for item in history:
        total_saved += item["saved"]
        total_ratio += item["ratio"]

    return {
        "count": len(history),
        "saved_bytes": total_saved,
        "average_ratio": total_ratio / len(history)
    }


def create_history_item(filename, original_size, compressed_size, ratio):
    return {
        "filename": filename,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "original": original_size,
        "compressed": compressed_size,
        "saved": original_size - compressed_size,
        "ratio": round(ratio, 2)
    }


def estimate_size(original_size, quality):
    estimated = original_size * (quality / 100)
    return int(estimated)


def unique_filename(path):
    if not os.path.exists(path):
        return path

    directory = os.path.dirname(path)
    name = os.path.splitext(os.path.basename(path))[0]
    extension = os.path.splitext(path)[1]

    i = 1
    while True:
        new_path = os.path.join(directory, f"{name}({i}){extension}")
        if not os.path.exists(new_path):
            return new_path
        i += 1