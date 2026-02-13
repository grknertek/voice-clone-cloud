import torch
import numpy as np
from chatterbox import Chatterbox
from src.utils.text_parser import split_text_by_language

class TTSEngine:
    def __init__(self):
        # GPU kontrolü
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Modeli yükle (Hız için FP16 ve GPU optimizasyonu eklendi)
        self.model = Chatterbox.from_pretrained(
            "resemble-ai/chatterbox",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map=self.device
        )
        print(f"🚀 AI Motoru {self.device} üzerinde başarıyla başlatıldı.")

    def generate(self, text, reference_audio_path):
        """
        Gelen metni dillerine ayırır ve klonlanmış ses üretir.
        """
        # 1. Metni dillerine göre parçala (text_parser'daki fonksiyonu kullanır)
        text_segments = split_text_by_language(text)
        
        combined_audio = []
        
        # 2. Her segmenti işle
        for segment, lang in text_segments:
            # Chatterbox tahmini (inference)
            # lang: 'tr' veya 'en' olarak text_parser'dan gelir
            audio_segment = self.model.predict(
                text=segment,
                reference_audio=reference_audio_path,
                language=lang
            )
            combined_audio.append(audio_segment)
            
        # 3. Tüm parçaları uç uca ekle
        if len(combined_audio) > 1:
            return np.concatenate(combined_audio)
        return combined_audio[0]