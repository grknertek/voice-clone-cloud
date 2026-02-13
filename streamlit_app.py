import streamlit as st
import sys
import os
import tempfile
import zipfile
import io
import numpy as np
import soundfile as sf

# Path Ayarları
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, 'src'))
vendor_path = os.path.join(base_dir, '_vendor', 'src')
if os.path.exists(vendor_path): sys.path.append(vendor_path)

from services.tts_engine import TTSEngine
from utils.audio_utils import repair_audio
from utils.text_parser import parse_docx, split_text_by_language

st.set_page_config(page_title="Voice Clone Cloud", layout="wide")

def main():
    st.title("☁️ Voice Clone Cloud Edition")
    
    @st.cache_resource
    def get_engine(): return TTSEngine.get_instance()
    
    engine = get_engine()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        ref_audio = st.file_uploader("Referans Ses (WAV)", type=["wav"])
    with col2:
        scripts = st.file_uploader("Senaryolar (DOCX)", type=["docx"], accept_multiple_files=True)

    if st.button("🎙️ Klonlamayı Başlat", type="primary", use_container_width=True):
        if not ref_audio or not scripts:
            st.warning("Dosyaları yükleyin!"); return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(ref_audio.getbuffer())
            raw_path = tmp.name
        fixed_path = raw_path.replace(".wav", "_fix.wav")

        try:
            if repair_audio(raw_path, fixed_path):
                zip_buffer = io.BytesIO()
                files_created = 0
                
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for script_file in scripts:
                        sections = parse_docx(script_file)
                        for title, content in sections:
                            st.write(f"⏳ İşleniyor: {title}")
                            segments = split_text_by_language(content)
                            
                            # --- SES BİRLEŞTİRME MANTIĞI ---
                            combined_samples = []
                            for txt, lang in segments:
                                st.caption(f"  🎙️ Okunuyor: {txt[:40]}...")
                                sample_array = engine.generate_audio(txt, lang, fixed_path)
                                if sample_array is not None:
                                    combined_samples.append(sample_array)
                            
                            if combined_samples:
                                # Tüm numpy dizilerini uç uca ekle
                                final_audio_array = np.concatenate(combined_samples)
                                
                                # Tek bir WAV dosyası olarak belleğe yaz
                                wav_io = io.BytesIO()
                                sf.write(wav_io, final_audio_array, 22050, format='WAV')
                                
                                filename = f"{os.path.splitext(script_file.name)[0]}_{title}.wav"
                                zf.writestr(filename, wav_io.getvalue())
                                files_created += 1
                
                if files_created > 0:
                    st.success("✅ Tüm cümleler birleştirildi!")
                    st.download_button("📥 ZIP İNDİR", zip_buffer.getvalue(), "voice_clones.zip")
        finally:
            if os.path.exists(raw_path): os.unlink(raw_path)
            if os.path.exists(fixed_path): os.unlink(fixed_path)

if __name__ == "__main__": main()