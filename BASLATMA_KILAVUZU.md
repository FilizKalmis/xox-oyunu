# XOX Oyunu - Hızlı Başlatma Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Ana Menüyü Başlat
```bash
python game_launcher.py
```

Ana menüden istediğiniz oyun modunu seçin:
- **Aynı Bilgisayardan Karşılıklı**: İki kişi aynı bilgisayarda oynar
- **Bilgisayara Karşı**: AI ile oynarsınız
- **Network Üzerinden**: İki farklı bilgisayardan oynarsınız

### 2. Network Modu İçin

**Sunucuyu başlat:**
```bash
python server_gui.py
```

**İstemcileri başlat:**
- Her iki oyuncu da `game_launcher.py` çalıştırır
- "Network Üzerinden Karşılıklı" seçeneğini seçer
- İlk bağlanan X, ikinci bağlanan O olur

**Not:** Farklı bilgisayarlardan bağlanıyorsanız, `game_network.py` dosyasındaki `HOST` değişkenini sunucunun IP adresine ayarlayın.

## ⚙️ Zaman Modu

Ana menüde "Zaman Modu (10 saniye bonus)" seçeneğini işaretleyerek:
- Her hamle için 10 saniye bonus süre alırsınız
- Her oyuncuya 30 saniye temel süre verilir
- Süre dolduğunda otomatik sıra değişir

## 🧪 Test Case'leri Çalıştırma

```bash
python test_game.py
```

3 test case çalıştırılır:
1. Kazanan Tespiti
2. Beraberlik Tespiti  
3. Çapraz Kazanma

## 📋 Proje Yapısı

- `game_launcher.py` - Ana menü
- `game_base.py` - Temel oyun sınıfı
- `game_local.py` - Aynı bilgisayar modu
- `game_ai.py` - AI modu
- `game_network.py` - Network client
- `server_gui.py` - Network sunucusu
- `test_game.py` - Test case'leri
- `README.md` - Detaylı dokümantasyon

## ✅ Gereksinimler Karşılandı

- ✅ Aynı bilgisayardan karşılıklı oyun
- ✅ Bilgisayara karşı oyun (AI)
- ✅ Network üzerinden karşılıklı oyun (Socket programlama)
- ✅ Zaman modu (10 saniye bonus)
- ✅ 3 adet test case
- ✅ Dokümantasyon

## 🎮 Oyun Kuralları

- X oyuncusu ilk hamleyi yapar
- Sırayla hamle yapılır
- 3 aynı işaret yatay, dikey veya çapraz olursa o oyuncu kazanır
- Tüm kareler dolarsa berabere olur

## 🔧 Sorun Giderme

**Network bağlantı sorunu:**
- Sunucunun çalıştığından emin olun
- Firewall ayarlarını kontrol edin
- IP adresinin doğru olduğundan emin olun

**Port hatası:**
- Port 55555 kullanımda ise `server_gui.py` ve `game_network.py` dosyalarındaki `PORT` değişkenini değiştirin

---

**İyi Oyunlar! 🎯**


