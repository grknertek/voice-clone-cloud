import streamlit as st
import os, shutil, io, zipfile
from datetime import datetime
import soundfile as sf
from src.services.tts_engine import TTSEngine
from src.utils.text_parser import parse_docx

st.set_page_config(page_title="Voice Clone Cloud", page_icon="🎙️")
st.title("🎙️ Voice Clone Cloud")

@st.cache_resource
def load_engine():
    return TTSEngine()

engine = load_engine()
if engine: st.success("✅ AI Motoru Hazır")

ref_audio = st.file_uploader("Referans Ses", type=["wav", "mp3"])
docx_file = st.file_uploader("Senaryo", type=["docx"])

if ref_audio and docx_file and st.button("Klonlamayı Başlat"):
    with open("temp_ref.wav", "wb") as f:
        f.write(ref_audio.getbuffer())
    
    slides = parse_docx(docx_file) # Bu bir liste döndürüyor
    output_files = []
    
    st.info(f"{len(slides)} slayt işleniyor...")
    for title, text in slides:
        st.write(f"⏳ İşleniyor: {title}")
        audio = engine.generate(text, "temp_ref.wav")
        filename = f"{title.replace(' ', '_')}.wav"
        sf.write(filename, audio, 22050)
        output_files.append(filename)
    
    zip_name = "output.zip"
    with zipfile.ZipFile(zip_name, "w") as zf:
        for f in output_files: zf.write(f)
    
    if os.path.exists("/content/drive/MyDrive"):
        path = "/content/drive/MyDrive/VoiceClone_Outputs"
        os.makedirs(path, exist_ok=True)
        drive_path = f"{path}/ses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        shutil.copy(zip_name, drive_path)
        st.success(f"🚀 Drive'a kaydedildi: {drive_path}")
    
    with open(zip_name, "rb") as f:
        st.download_button("📥 ZIP İndir", f, zip_name)