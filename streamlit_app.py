import streamlit as st
import os
import shutil
import io
import numpy as np
import zipfile
from datetime import datetime
import soundfile as sf
from src.services.tts_engine import TTSEngine
from src.utils.text_parser import parse_docx

# Sayfa Yapılandırması
st.set_page_config(page_title="Voice Clone Cloud Edition", page_icon="☁️")
st.title("☁️ Voice Clone Cloud Edition")

# Google Drive Ayarları
DRIVE_BASE_PATH = "/content/drive/MyDrive/VoiceClone_Outputs"

# AI Motorunu Başlat (Önbelleğe alarak hızı artırıyoruz)
@st.cache_resource
def load_engine():
    try:
        return TTSEngine()
    except Exception as e:
        st.error(f"AI Motoru yüklenirken hata oluştu: {e}")
        return None

engine = load_engine()

if engine:
    st.success("✅ AI Motoru Hazır (GPU Aktif)")

# --- ARAYÜZ ---
st.header("1. Giriş Dosyalarını Yükle")
col1, col2 = st.columns(2)

with col1:
    ref_audio = st.file_uploader("Referans Ses (WAV/MP3)", type=["wav", "mp3"])
with col2:
    docx_file = st.file_uploader("Senaryo Dosyası (DOCX)", type=["docx"])

if ref_audio and docx_file:
    st.header("2. İşleme ve Seslendirme")
    
    if st.button("🎙️ Klonlamayı Başlat ve Drive'a Kaydet"):
        try:
            # Geçici dosyaları hazırla
            with open("temp_ref.wav", "wb") as f:
                f.write(ref_audio.getbuffer())
            
            # Senaryoyu parçala
            slides = parse_docx(docx_file)
            st.info(f"Toplam {len(slides)} slayt tespit edildi. İşleniyor...")
            
            output_files = []
            progress_bar = st.progress(0)
            
            # Sentezleme Döngüsü
            for i, (slide_title, slide_text) in enumerate(slides.items()):
                st.write(f"⏳ İşleniyor: {slide_title}")
                
                # AI Sentezleme
                audio_data = engine.generate(slide_text, "temp_ref.wav")
                
                # Geçici dosya olarak kaydet
                filename = f"{slide_title.replace(' ', '_')}.wav"
                sf.write(filename, audio_data, 22050)
                output_files.append((filename, audio_data))
                
                # Progress güncelle
                progress_bar.progress((i + 1) / len(slides))
            
            # --- ZIP OLUŞTURMA ---
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for filename, _ in output_files:
                    zf.write(filename)
            
            with open("output_slaytlar.zip", "wb") as f:
                f.write(zip_buffer.getvalue())

            st.success("✅ Tüm slaytlar başarıyla seslendirildi!")

            # --- GOOGLE DRIVE ENTEGRASYONU ---
            if os.path.exists("/content/drive/MyDrive"):
                if not os.path.exists(DRIVE_BASE_PATH):
                    os.makedirs(DRIVE_BASE_PATH)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                drive_filename = f"ses_slaytlari_{timestamp}.zip"
                drive_full_path = os.path.join(DRIVE_BASE_PATH, drive_filename)
                
                shutil.copy("output_slaytlar.zip", drive_full_path)
                st.balloons()
                st.info(f"🚀 Drive Senkronizasyonu Başarılı! Dosya şuraya kaydedildi: \n`MyDrive/VoiceClone_Outputs/{drive_filename}`")
            else:
                st.warning("⚠️ Drive bağlı değil, dosya sadece yerel indirilebilir.")

            # İndirme Butonu
            st.download_button(
                label="📥 ZIP Dosyasını Bilgisayara İndir",
                data=zip_buffer.getvalue(),
                file_name="output_slaytlar.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

else:
    st.info("Lütfen devam etmek için referans ses ve senaryo dosyasını yükleyin.")