from aiogram import Router, F
from aiogram.types import Message
from config import MY_TELEGRAM_ID, BOT_TOKEN
from utils.ocr import extract_text_with_line_grouping
from aiogram import Bot
from utils.gpt import ask_gpt, ask_gpt_with_image
from utils.preprocess_image import preprocess_image_for_openai
import os


router = Router()
bot = Bot(token=BOT_TOKEN)


@router.message()
async def handle_message(message: Message):
    
    # if message.from_user.id != MY_TELEGRAM_ID:
    #     await message.answer("Извини, доступ только для владельца.")
    #     return

    # Поддержка обычного фото
    photo = message.photo[-1] if message.photo else None
    # Поддержка документа-изображения
    document = message.document if message.document and message.document.mime_type.startswith("image/") else None

    caption = message.caption
    text = message.text

    if photo or document:

        await message.answer("Обрабатываю изображение...")

        file_id = photo.file_id if photo else document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        unique_id = photo.file_unique_id if photo else document.file_unique_id
        local_path = f"temp_{unique_id}.jpg"

        with open(local_path, "wb") as f:
            file = await bot.download_file(file_path)
            f.write(file.read())

        cropped_path = preprocess_image_for_openai(local_path, output_path=f"cropped_{unique_id}.jpg")

        prompt = caption or "Нужен ответ:"

        gpt_reply = await ask_gpt_with_image(cropped_path, prompt=prompt)
        await message.answer(f"🤖 GPT-4 Vision:\n\n{gpt_reply}")

        os.remove(local_path)
        os.remove(cropped_path)

    elif text:

        gpt_reply = await ask_gpt(text)
        await message.answer(f"🤖 Ответ:\n\n{gpt_reply}")

    else:
        await message.answer("Пожалуйста, отправь изображение или текст.")