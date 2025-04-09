from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import pytesseract
from PIL import Image
import os
import io

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

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

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты AI-финансовый помощник из Казахстана. Отвечай кратко и по делу, с учётом казахстанской реальности (ставки, банки, кредиты, долги и т.д.)."
                },
                {
                    "role": "user",
                    "content": extracted_text
                }
            ],
            temperature=0.6,
            max_tokens=500
        )

        return {"reply": response.choices[0].message.content}

    except Exception as e:
        return {"reply": f"Ошибка при обработке файла: {str(e)}"}