import streamlit as st
import os
import shutil
import io
import zipfile
from datetime import datetime
import soundfile as sf
from src.services.tts_engine import TTSEngine
from src.utils.text_parser import parse_docx

# --- Sayfa Yapılandırması ---
st.set_page_config(page_title="Voice Clone Cloud Edition", page_icon="☁️")
st.title("☁️ Voice Clone Cloud Edition")

# Google Drive Çıktı Yolu
DRIVE_BASE_PATH = "/content/drive/MyDrive/VoiceClone_Outputs"

# AI Motorunu Önbelleğe Alarak Yükle
@st.cache_resource
def load_engine():
    try:
        return TTSEngine()
    except Exception as e:
        st.error(f"AI Motoru yüklenirken hata oluştu: {e}")
        return None

engine = load_engine()

if engine:
    st.success("✅ AI Motoru Hazır (GPU Aktif)")

# --- ARAYÜZ ---
st.header("1. Giriş Dosyalarını Yükle")
col1, col2 = st.columns(2)

with col1:
    ref_audio = st.file_uploader("Referans Ses (WAV/MP3)", type=["wav", "mp3"])
with col2:
    docx_file = st.file_uploader("Senaryo Dosyası (DOCX)", type=["docx"])

if ref_audio and docx_file:
    st.header("2. İşleme ve Seslendirme")
    
    if st.button("🎙️ Klonlamayı Başlat ve Drive'a Kaydet"):
        try:
            # Geçici referans ses dosyasını kaydet
            with open("temp_ref.wav", "wb") as f:
                f.write(ref_audio.getbuffer())
            
            # Word dosyasını parçala (Bu fonksiyon bir LISTE döndürür)
            slides = parse_docx(docx_file)
            st.info(f"Toplam {len(slides)} slayt tespit edildi. İşleniyor...")
            
            output_files = []
            progress_bar = st.progress(0)
            
            # --- DÜZELTİLMİŞ DÖNGÜ (LISTE İÇİN) ---
            for i, slide_tuple in enumerate(slides):
                # parse_docx list(zip(...)) döndürdüğü için (başlık, metin) şeklinde ayırıyoruz
                slide_title, slide_text = slide_tuple
                
                st.write(f"⏳ İşleniyor: {slide_title}")
                
                # AI Sentezleme
                audio_data = engine.generate(slide_text, "temp_ref.wav")
                
                # Dosya ismini temizle ve kaydet
                clean_title = str(slide_title).replace(' ', '_').replace(':', '')
                filename = f"{clean_title}.wav"
                sf.write(filename, audio_data, 22050)
                output_files.append(filename)
                
                # Progress çubuğunu güncelle
                progress_bar.progress((i + 1) / len(slides))
            
            # --- ZIP OLUŞTURMA ---
            zip_filename = "output_slaytlar.zip"
            with zipfile.ZipFile(zip_filename, "w") as zf:
                for filename in output_files:
                    zf.write(filename)
                    os.remove(filename) # ZIP'e ekledikten sonra yerel kopyayı sil (temizlik)
            
            st.success("✅ Tüm slaytlar başarıyla seslendirildi!")

            # --- GOOGLE DRIVE ENTEGRASYONU ---
            if os.path.exists("/content/drive/MyDrive"):
                if not os.path.exists(DRIVE_BASE_PATH):
                    os.makedirs(DRIVE_BASE_PATH)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                drive_zip_name = f"ses_slaytlari_{timestamp}.zip"
                drive_full_path = os.path.join(DRIVE_BASE_PATH, drive_zip_name)
                
                shutil.copy(zip_filename, drive_full_path)
                st.balloons()
                st.info(f"🚀 Drive Senkronizasyonu Başarılı! \n`MyDrive/VoiceClone_Outputs/{drive_zip_name}`")
            else:
                st.warning("⚠️ Google Drive bağlı değil. Dosyayı sadece aşağıdan indirebilirsiniz.")

            # Manuel İndirme Butonu
            with open(zip_filename, "rb") as f:
                st.download_button(
                    label="📥 ZIP Dosyasını Bilgisayara İndir",
                    data=f,
                    file_name=zip_filename,
                    mime="application/zip"
                )

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            # Hata detayını teknik analiz için yazdır
            st.exception(e)

else:
    st.info("Lütfen devam etmek için dosyaları yükleyin.")