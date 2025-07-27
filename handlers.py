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

    if message.photo:
        await message.answer("Обрабатываю изображение...")

        photo = message.photo[-1]  # самое большое фото
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path

        local_path = f"temp_{photo.file_unique_id}.jpg"

        # Сохраняем файл локально
        with open(local_path, "wb") as f:
            file = await bot.download_file(file_path)
            f.write(file.read())

        # Обрезаем изображение (если удалось) и сохраняем
        cropped_path = preprocess_image_for_openai(local_path, output_path=f"cropped_{photo.file_unique_id}.jpg")

        gpt_reply = await ask_gpt_with_image(cropped_path)
        await message.answer(f"🤖 GPT-4 Vision:\n\n{gpt_reply}")

        # Выбираем файл для OCR
        # image_for_ocr = cropped_path if cropped_path else local_path

        # Обрабатываем OCR
        # text = extract_text_with_line_grouping(image_for_ocr)
        # print(text)

        # Удалим временный файл
        os.remove(local_path)
        os.remove(cropped_path)

        # if text:
            # await message.answer(f"Текст на изображении:\n\n{text}")
            # gpt_reply = await ask_gpt(text)
            # await message.answer(f"🤖 Ответ:\n\n{gpt_reply}")
        # else:
        #     await message.answer("Не удалось распознать текст.")
    else:
        await message.answer("Отправлен текст:  " + message.text[:10] + "...")
        gpt_reply = await ask_gpt(message.text)
        await message.answer(f"🤖 Ответ:\n\n{gpt_reply}")
        # pass

