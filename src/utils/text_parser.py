import re
from docx import Document

def parse_docx(file):
    """Word dosyasını slayt slayt ayırır."""
    doc = Document(file)
    content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    # "Slayt X:" veya "Slide X:" başlıklarına göre böl
    sections = re.split(r'(?i)(?:Slayt|Slide)\s*\d+[:\s]*-*', content)
    titles = re.findall(r'(?i)((?:Slayt|Slide)\s*\d+)', content)
    
    # Eğer başlık bulunamazsa tüm metni tek parça al
    if not titles:
        return [("Tam Metin", content)]
    
    # Bölünen parçaları başlıklarla eşleştir (ilk boş parçayı atla)
    clean_sections = [s.strip() for s in sections if s.strip()]
    return list(zip(titles, clean_sections))

def split_text_by_language(text):
    """
    Metni cümlelere böler ve dilleri tespit eder.
    Sondaki cümlelerin kaybolmaması için geliştirilmiş mantık.
    """
    # Basit bir cümle bölücü (nokta, ünlem, soru işaretinden sonra böler)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Eğer split metni tamamen bitiremediyse (noktasız biten son cümle)
    if not sentences[-1].strip():
        sentences = sentences[:-1]

    results = []
    for sentence in sentences:
        if not sentence.strip(): continue
        
        # Basit dil tespiti (Geliştirilebilir)
        # Eğer cümlede yoğun Türkçe karakter varsa 'tr', yoksa 'en'
        tr_chars = len(re.findall(r'[çğıöşüİĞÖŞÜ]', sentence, re.I))
        lang = 'tr' if tr_chars > 0 else 'en'
        
        results.append((sentence, lang))
    
    return results