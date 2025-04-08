from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import openai
import os
import io

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        extracted_text = pytesseract.image_to_string(image, lang="rus+eng")

        if not extracted_text.strip():
            return {"reply": "❌ Не удалось распознать текст на изображении."}

        # Отправляем распознанный текст в GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — финансовый помощник. Анализируй текст из документов и объясняй простым языком, что важно."},
                {"role": "user", "content": extracted_text}
            ],
            temperature=0.6
        )

        gpt_reply = response.choices[0].message.content
        return {"reply": gpt_reply}

    except Exception as e:
        return {"reply": f"Ошибка при обработке файла: {str(e)}"}