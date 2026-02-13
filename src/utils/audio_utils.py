import torch
import torchaudio
import soundfile as sf
import os

def repair_audio(input_path, output_path, target_hz=22050):
    try:
        data, sr = sf.read(input_path)
        if len(data.shape) == 1:
            waveform = torch.from_numpy(data).float().unsqueeze(0)
        else:
            waveform = torch.from_numpy(data.T).float()
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        if sr != target_hz:
            resampler = torchaudio.transforms.Resample(sr, target_hz)
            waveform = resampler(waveform)
            
        sf.write(output_path, waveform.squeeze().numpy(), target_hz)
        return True
    except Exception as e:
        print(f"⚠️ Audio Repair Hatası: {e}")
        return False