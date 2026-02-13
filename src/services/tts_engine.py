import torch
import numpy as np
from chatterbox import Chatterbox

class TTSEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # En güvenli yükleme şekli
        self.model = Chatterbox.from_pretrained("resemble-ai/chatterbox")
        print(f"🚀 AI Motoru {self.device} üzerinde hazır.")

    def generate(self, text, reference_audio_path):
        # Hata payı en düşük tahmin fonksiyonu
        return self.model.predict(
            text=text,
            reference_audio=reference_audio_path,
            language="tr"
        )