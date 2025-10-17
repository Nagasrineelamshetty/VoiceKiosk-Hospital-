# app/utils.py
import whisper
from gtts import gTTS
import os
from difflib import get_close_matches
from deep_translator import GoogleTranslator
from typing import Tuple
from app.db import (
    faqs_collection,
    doctors_collection,
    departments_collection,
    services_collection,
    visiting_hours_collection,
    emergency_contacts_collection,
    client
)

# -----------------------------
# 🌍 Language Codes
# -----------------------------
LANG_CODES = {"english": "en", "hindi": "hi", "telugu": "te"}

# -----------------------------
# 🎙️ Load Whisper Model
# -----------------------------
def load_whisper_model(model_name: str = "base"):
    print("🎙️ Loading Whisper model... please wait.")
    try:
        model = whisper.load_model(model_name)
        print("✅ Whisper model loaded successfully!")
        return model
    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        raise

model = load_whisper_model()

# -----------------------------
# 1️⃣ Speech → Text + Language Detection
# -----------------------------
async def speech_to_text(audio_path: str, language: str = "auto") -> Tuple[str, str]:
    try:
        print(f"🎧 Transcribing audio ({language})...")
        result = model.transcribe(audio_path, language=language) if language != "auto" else model.transcribe(audio_path)
        
        # Safe extraction of text
        text = result.get("text")
        if not isinstance(text, str):
            text = ""
        text = text.strip()

        # Safe extraction of language
        detected_lang = result.get("language")
        if not isinstance(detected_lang, str):
            detected_lang = "en"

        if not text:
            return "Sorry, I couldn't understand the audio.", detected_lang

        print(f"🗣️ Detected language: {detected_lang} | Text: {text}")
        return text, detected_lang

    except Exception as e:
        print(f"⚠️ Error in speech_to_text: {e}")
        return "Error processing your audio.", "en"

# -----------------------------
# 2️⃣ Translation
# -----------------------------
async def translate_text(text: str, target_lang: str = "en") -> str:
    try:
        if not text:
            return ""
        translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
        print(f"🌐 Translated ({target_lang}): {translated}")
        return translated
    except Exception as e:
        print(f"⚠️ Error in translate_text: {e}")
        return text

# -----------------------------
# 3️⃣ Text → Speech
# -----------------------------
async def text_to_speech(text: str, lang: str = "en", filename: str = "response.mp3") -> str:
    try:
        if lang not in ["en", "hi", "te"]:
            lang = "en"
        if not text:
            text = "Sorry, I don't have an answer for that."

        output_dir = os.path.join("app", "responses")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

        print(f"🔊 Generating TTS in {lang}...")
        gTTS(text=text, lang=lang).save(output_path)
        print(f"✅ Audio saved at: {output_path}")
        return output_path

    except Exception as e:
        print(f"⚠️ Error in text_to_speech: {e}")
        return ""

# -----------------------------
# 4️⃣ Find Best Match
# -----------------------------
async def find_best_match(query: str) -> str:
    if client is None:
        print("⚠️ Skipping DB query due to connection failure.")
        return "Sorry, I couldn’t fetch information due to a database connection issue."

    query_lower = query.lower().strip()
    print(f"🔍 Searching DB for: {query_lower}")

    # Helper to safely fetch documents from collections
    async def safe_find(collection, length=100):
        try:
            return await collection.find().to_list(length=length)
        except Exception as e:
            print(f"⚠️ Error fetching from {collection.name}: {e}")
            return []

    # ✅ FAQs
    faqs = await safe_find(faqs_collection)
    if faqs:
        faq_questions = [item.get("question", "").lower() for item in faqs]
        faq_match = get_close_matches(query_lower, faq_questions, n=1, cutoff=0.5)
        if faq_match:
            try:
                matched = await faqs_collection.find_one({"question": faq_match[0]})
                if matched and matched.get("answer"):
                    return matched["answer"]
            except Exception as e:
                print(f"⚠️ Error fetching FAQ answer: {e}")

    # ✅ Doctors
    doctors = await safe_find(doctors_collection)
    for doctor in doctors:
        name = doctor.get("name", "").lower()
        if name and name in query_lower:
            dept = doctor.get("department", "unknown")
            return f"{doctor.get('name', 'Unknown')} is in the {dept} department."

    
    # ✅ Departments
    departments = await safe_find(departments_collection, length=50)
    for dept in departments:
        dept_name = dept.get("name", "").lower()
        if dept_name and dept_name in query_lower:
        # Check if user asked about head of department
            if "head" in query_lower or "in charge" in query_lower or "who is the doctor" in query_lower:
                head = dept.get("head_of_department", "Not available")
                return f"The head of the {dept.get('name', 'Unknown')} department is {head}."
        # Otherwise return general description
            desc = dept.get("description", "Handles general cases.")
            location = dept.get("location", "location not specified")
            return f"The {dept.get('name', 'Unknown')} department is located in the {location}. {desc}"


    # ✅ Services
    services = await safe_find(services_collection)
    for svc in services:
        svc_name = svc.get("name", "").lower()
        if svc_name and svc_name in query_lower:
            return f"We provide {svc.get('name', 'this')} service. {svc.get('description', '')}"

    # ✅ Emergency Contacts
    emergency_contacts = await safe_find(emergency_contacts_collection, length=50)
    for contact in emergency_contacts:
        name = contact.get("name", "").lower()
        if name and name in query_lower:
            phone = contact.get("phone", "N/A")
            return f"You can contact {contact.get('name', 'Someone')} at {phone} for immediate help."

    # ✅ Visiting Hours
    visiting_hours = await safe_find(visiting_hours_collection)
    for visit in visiting_hours:
        doc_name = visit.get("doctor_name", "").lower()
        if doc_name and doc_name in query_lower:
            return f"{visit.get('doctor_name', 'Doctor')} is available on {visit.get('day', 'N/A')} from {visit.get('start_time', 'N/A')} to {visit.get('end_time', 'N/A')}."

    print("⚠️ No match found.")
    return "Sorry, I couldn’t find information related to that."
