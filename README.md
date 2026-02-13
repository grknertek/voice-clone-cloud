☁️ Voice Clone Cloud Edition
Bu proje, Resemble AI Chatterbox altyapısını kullanarak profesyonel düzeyde ses klonlama yapmanızı sağlayan bir Streamlit uygulamasıdır. Özellikle Word (DOCX) dosyalarındaki senaryoları, yüklenen bir referans sesin tonu ve duygusuyla saniyeler içinde sesli slaytlara dönüştürür.

🛠️ Teknik Özellikler ve Mimari
Proje, Python 3.14+ ve Mac M serisi işlemcilerdeki uyumluluk sorunlarını aşmak için özel yamalar (patching) ve hibrit bir mimari ile inşa edilmiştir:

Zırhlı AI Motoru: Transformers kütüphanesi çekirdek seviyesinde yamalanarak SDPA (Hızlı Mod) hataları giderilmiştir.

Akıllı Audio Pipeline: Sesler numpy dizileri olarak işlenip tek bir WAV başlığı (header) altında birleştirilir, böylece kesintisiz bir dinleme deneyimi sunar.

Gated Model Erişimi: Hugging Face üzerinden kimlik doğrulama katmanı ile güvenli model indirme protokolü.

Dinamik Dil Tespiti: Metin içindeki Türkçe ve İngilizce cümleleri otomatik ayırt ederek uygun model ağırlıklarıyla işleme.

📂 Dosya Yapısı
VOICECLONEPROJECT/
├── _vendor/                # Chatterbox kaynak kodları
├── src/
│   ├── services/
│   │   └── tts_engine.py   # AI Motoru ve Model Yükleme
│   ├── utils/
│   │   ├── audio_utils.py  # Ses Onarımı (FFmpeg Bypass)
│   │   └── text_parser.py  # Word Dosyası Ayrıştırıcı
├── requirements.txt        # Gerekli Kütüphaneler
└── streamlit_app.py        # Ana Kullanıcı Arayüzü
🚀 Kurulum ve Başlatma
1. Hazırlık

Sistemde FFmpeg kurulu olduğundan emin olun ve bir Python sanal ortamı oluşturun:

Bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
2. Model Erişimi

src/services/tts_engine.py içindeki HF_TOKEN değişkenine kendi Access Token'ınızı yapıştırın.

3. Çalıştırma

Bash
streamlit run streamlit_app.py
🎙️ Kullanım Kılavuzu
Referans Ses Yükle: Klonlamak istediğiniz kişinin yaklaşık 10-30 saniyelik, temiz ve arka plan gürültüsü olmayan bir WAV kaydını yükleyin.

Senaryoları Yükle: İçinde "Slayt 1:", "Slayt 2:" gibi başlıklar bulunan Word (DOCX) dosyalarınızı yükleyin.

Klonlamayı Başlat: Butona bastığınızda sistem metni parçalara ayıracak ve her birini referans sesle sentezleyecektir.

İndir: İşlem bitince tüm slaytları içeren bir ZIP dosyası otomatik olarak hazırlanacaktır.

⚠️ Önemli Notlar
Hız: İlk çalıştırmada model ağırlıkları (1.5 GB) indirileceği için internet hızınıza bağlı olarak bir süre beklemeniz gerekebilir.

Boşluklar: Cümleler arası geçişler çok hızlı gelirse tts_engine.py içindeki birleştirme kısmına "silence" (sessizlik) tamponu eklenebilir.

Geliştirici Notu: Bu yazılım, karmaşık kütüphane çakışmalarını (SDPA/Eager/TorchCodec) baypas eden özel bir mimariyle Mac OS için optimize edilmiştir.

🗺️ Yol Haritası (Roadmap)

Projenin gelecek sürümleri için planlanan ve üzerinde çalışılan geliştirmeler:

[ ] Otomatik Gürültü Temizleme (Noise Reduction): Referans ses dosyası yüklenirken, yapay zeka algoritmalarıyla arka plan gürültüsünü temizleyen bir ön işleme katmanı.

[ ] Akıllı Fon Müziği Miksajı: Seslendirilen slaytların arkasına, sesin tonuna uygun bir şekilde otomatik olarak fon müziği ekleme ve ses seviyelerini (ducking) dengeleme.

[ ] Duygu ve Vurgu Kontrolü: Metin içerisine yerleştirilecek özel etiketler (örn: [mutlu], [heyecanlı], [ciddi]) aracılığıyla sesin duygu tonunu kontrol etme yeteneği.

[ ] Genişletilmiş Dosya Desteği: Sadece DOCX değil; PDF, TXT ve doğrudan URL üzerinden içerik çekerek seslendirme yapabilme desteği.

[ ] Gerçek Zamanlı Önizleme (Live Preview): Tüm senaryoyu işlemeden önce, seçilen tek bir cümleyi anlık olarak sentezleyip dinleyebilme özelliği.

[ ] Web API Entegrasyonu: Oluşturulan ses motorunun diğer uygulamalar tarafından kullanılabilmesi için bir REST API katmanı.

[ ] Google Colab & GPU Optimizasyonu: Uygulamanın bulut tabanlı GPU'larda (T4, A100) 10 kat daha hızlı çalışmasını sağlayacak tek tıkla kurulum (One-Click Setup) desteği.