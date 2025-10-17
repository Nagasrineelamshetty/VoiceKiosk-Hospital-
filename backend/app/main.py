from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from app.utils import speech_to_text, find_best_match, text_to_speech, translate_text
import os
import uuid

app = FastAPI()

# ✅ Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Ensure folders exist
os.makedirs("app/uploads", exist_ok=True)
os.makedirs("app/responses", exist_ok=True)


@app.post("/api/query")
async def handle_query(file: UploadFile = File(...), language: str = Form("auto")):
    """
    language: "auto", "hi", "te", or "en"
    """
    try:
        # 1️⃣ Save uploaded audio
        temp_filename = f"temp_{uuid.uuid4()}.wav"
        temp_path = os.path.join("app/uploads", temp_filename)
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        print(f"📁 Saved audio: {temp_path}")

        # 2️⃣ Speech → Text
        user_text, detected_lang = await speech_to_text(temp_path, language)
        print(f"🗣 User said ({detected_lang}): {user_text}")

        # 3️⃣ Translate to English for DB querying
        query_in_english = await translate_text(user_text, target_lang="en")
        print(f"🌐 Query in English: {query_in_english}")

        # 4️⃣ Query database
        answer_in_english = await find_best_match(query_in_english)
        print(f"💬 Answer in English: {answer_in_english}")

        # 5️⃣ Translate back to user language
        if language == "auto":
            tts_lang = detected_lang if detected_lang in ["en", "hi", "te"] else "en"
        else:
            tts_lang = language

        translated_answer = await translate_text(answer_in_english, target_lang=tts_lang)
        print(f"🌍 Translated answer ({tts_lang}): {translated_answer}")

        # 6️⃣ Text → Speech
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = await text_to_speech(translated_answer, lang=tts_lang, filename=audio_filename)
        print(f"🔊 Audio generated at: {audio_path}")

        # 7️⃣ Return response
        return JSONResponse({
            "query_original": user_text,
            "detected_language": detected_lang,
            "query_translated": query_in_english,
            "answer_en": answer_in_english,
            "answer_translated": translated_answer,
            "audio_url": f"/audio/{audio_filename}"
        })

    except Exception as e:
        print(f"⚠️ Error in handle_query: {e}")
        fallback_text = "Sorry, I couldn’t fetch the response."
        audio_filename = f"{uuid.uuid4()}.mp3"
        await text_to_speech(fallback_text, lang="en", filename=audio_filename)
        return JSONResponse({
            "query_original": "",
            "detected_language": "en",
            "query_translated": "",
            "answer_en": fallback_text,
            "answer_translated": fallback_text,
            "audio_url": f"/audio/{audio_filename}"
        }, status_code=500)


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    filepath = os.path.join("app/responses", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="audio/mpeg")
    return JSONResponse({"error": "Audio not found"}, status_code=404)
