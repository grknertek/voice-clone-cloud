import torch
import torchaudio
import io
import sys
import os
import streamlit as st
import huggingface_hub
import transformers

# --- PERTH BYPASS ---
try:
    import perth
    class MockWatermarker:
        def __init__(self, *args, **kwargs): pass
        def apply_watermark(self, audio, *args, **kwargs): return audio
    perth.PerthImplicitWatermarker = MockWatermarker
except Exception:
    from types import ModuleType
    m = ModuleType('perth')
    m.PerthImplicitWatermarker = type('W', (), {'__init__': lambda s, *a, **k: None, 'apply_watermark': lambda s, a, *x, **y: a})
    sys.modules['perth'] = m

# --- TRANSFORMERS PATCH ---
original_config_init = transformers.PretrainedConfig.__init__
def patched_config_init(self, *args, **kwargs):
    kwargs['output_attentions'] = False
    original_config_init(self, *args, **kwargs)
transformers.PretrainedConfig.__init__ = patched_config_init

class TTSEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()

    def _load_model(self):
        HF_TOKEN = "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" # Tokenini buraya yaz

        try:
            if HF_TOKEN and "hf_" in HF_TOKEN:
                huggingface_hub.login(token=HF_TOKEN)
            
            from chatterbox.tts import ChatterboxTTS
            
            orig_load = torch.load
            def smart_load(*args, **kwargs):
                kwargs['map_location'] = torch.device(self.device)
                if 'weights_only' in kwargs: kwargs['weights_only'] = False
                return orig_load(*args, **kwargs)
            
            torch.load = smart_load
            self._model = ChatterboxTTS.from_pretrained(device=self.device)
            torch.load = orig_load
            st.success("✅ AI Motoru Hazır")
            
        except Exception as e:
            st.error(f"❌ Yükleme Hatası: {e}")
            raise e

    def generate_audio(self, text, lang, ref_path):
        if not text.strip() or self._model is None: return None
        try:
            with torch.no_grad():
                audio = self._model.generate(text=text, audio_prompt_path=ref_path)
            
            if audio is None: return None
            
            # --- KRİTİK DEĞİŞİKLİK ---
            # Dosya (WAV) dönmüyoruz, saf numpy dizisi dönüyoruz
            return audio.cpu().squeeze().numpy()
            
        except Exception as e:
            st.warning(f"⚠️ Hata: {e}")
            return None