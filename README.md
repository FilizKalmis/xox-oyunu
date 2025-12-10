# XOX (Tic-Tac-Toe) Oyunu - Socket Programlama Projesi

## Proje Hakkında

Bu proje, Python socket programlama kullanılarak geliştirilmiş bir XOX (Tic-Tac-Toe) oyunudur. Oyun, farklı oyun modlarını destekler ve network üzerinden çok oyunculu oyun imkanı sunar.

## Özellikler

### Oyun Modları

1. **Aynı Bilgisayardan Karşılıklı**
   - İki oyuncu aynı bilgisayarda sırayla oynar
   - Basit ve hızlı oyun deneyimi

2. **Bilgisayara Karşı**
   - Kullanıcı bilgisayar AI'ına karşı oynar
   - AI akıllı hamle stratejisi kullanır (kazanma, engelleme, merkez kontrolü)

3. **Network Üzerinden Karşılıklı**
   - İki oyuncu farklı bilgisayarlardan network üzerinden oynar
   - Socket programlama ile gerçek zamanlı iletişim
   - Aynı ağ üzerinden bağlantı yeterlidir

### Zaman Modu (Bonus Özellik)

- Her hamle için 10 saniye bonus süre eklenir
- Her oyuncuya 30 saniye temel süre verilir
- Süre dolduğunda otomatik olarak sıra değişir

## Kurulum

### Gereksinimler

- Python 3.6 veya üzeri
- tkinter (genellikle Python ile birlikte gelir)

### Çalıştırma

1. **Ana Menüyü Başlatma:**
   ```bash
   python game_launcher.py
   ```

2. **Network Modu için Sunucuyu Başlatma:**
   ```bash
   python server_gui.py
   ```

3. **Network Modu için İstemci Başlatma:**
   - Ana menüden "Network Üzerinden Karşılıklı" seçeneğini seçin
   - Açılan pencerede sunucunun IP adresini girin (sunucu ekranında gösterilen IP)

## Dosya Yapısı

```
PythonSocket/
├── game_launcher.py      # Ana menü ve oyun modu seçimi
├── game_base.py          # Temel oyun sınıfı (ortak fonksiyonlar)
├── game_local.py         # Aynı bilgisayar modu
├── game_ai.py            # Bilgisayara karşı modu
├── game_network.py       # Network modu (client)
├── server_gui.py         # Network modu sunucusu
├── test_game.py          # Test case'leri
├── README.md             # Bu dosya
├── client_gui.py         # Eski network client (X oyuncusu)
└── client_gui_0.py       # Eski network client (O oyuncusu)
```

## Kullanım

### 1. Aynı Bilgisayar Modu

1. `game_launcher.py` dosyasını çalıştırın
2. "Aynı Bilgisayardan Karşılıklı" butonuna tıklayın
3. İsteğe bağlı olarak "Zaman Modu" seçeneğini işaretleyin
4. X oyuncusu ilk hamleyi yapar, sırayla oynayın

### 2. Bilgisayara Karşı Modu

1. `game_launcher.py` dosyasını çalıştırın
2. "Bilgisayara Karşı" butonuna tıklayın
3. İsteğe bağlı olarak "Zaman Modu" seçeneğini işaretleyin
4. X oyuncusu olarak oynayın, AI O oyuncusu olarak otomatik hamle yapar

### 3. Network Modu

1. **Sunucu tarafı (Bir bilgisayarda):**
   ```bash
   python server_gui.py
   ```
   - Sunucu penceresi açılır ve **IP adresi otomatik olarak gösterilir**
   - Bu IP adresini not edin (örnek: 192.168.1.100)
   - Sunucu 2 oyuncu bekleyecek şekilde hazır olur

2. **İstemci tarafı (Her iki oyuncu için):**
   ```bash
   python game_launcher.py
   ```
   - "Network Üzerinden Karşılıklı" butonuna tıklayın
   - Açılan pencerede sunucunun IP adresini girin
   - "Bağlan" butonuna tıklayın
   - İlk bağlanan oyuncu X, ikinci bağlanan oyuncu O olur
   - İki oyuncu da bağlandığında oyun otomatik başlar

## Test Case'leri

Proje 3 adet test case içerir:

1. **Test Case 1: Kazanan Tespiti**
   - X oyuncusu yatay çizgi oluşturur
   - Beklenen: 'X' kazanır

2. **Test Case 2: Beraberlik Tespiti**
   - Tüm kareler doldurulur, kimse kazanamaz
   - Beklenen: 'Berabere' sonuç

3. **Test Case 3: Çapraz Kazanma**
   - O oyuncusu çapraz çizgi oluşturur
   - Beklenen: 'O' kazanır

### Test Çalıştırma

```bash
python test_game.py
```

## Teknik Detaylar

### Socket Programlama

- **Protokol:** TCP/IP
- **Port:** 55555 (varsayılan)
- **Mesaj Formatı:** `COMMAND|param1|param2|`
- **Komutlar:**
  - `COMMAND:ASSIGN_PLAYER|X|` - Oyuncu ataması
  - `COMMAND:START_GAME|` - Oyun başlatma
  - `MOVE|row,col|char` - Hamle gönderme
  - `COMMAND:SERVER_CLOSING|` - Sunucu kapanıyor
  - `COMMAND:PLAYER_DISCONNECTED|` - Oyuncu ayrıldı

### AI Stratejisi

1. Kazanma hamlesi varsa yapar
2. Rakibin kazanmasını engeller
3. Merkezi kontrol etmeye çalışır
4. Rastgele boş kare seçer

### Zaman Modu

- Temel süre: 30 saniye
- Bonus süre: 10 saniye (her hamle sonrası)
- Süre dolduğunda otomatik sıra değişimi

## Geliştirici Notları

- Tüm GUI işlemleri tkinter ile yapılmıştır
- Thread-safe mesajlaşma için `master.after()` kullanılmıştır
- Network modunda her istemci ayrı thread'de dinler
- Oyun durumu her hamle sonrası kontrol edilir

## Sorun Giderme

### Network Modu Bağlantı Sorunları

1. **Sunucu çalışmıyor:**
   - `server_gui.py` dosyasını çalıştırdığınızdan emin olun
   - Sunucu penceresinde "Sunucu dinlemede" mesajını görüyor olmalısınız

2. **IP adresi bulunamıyor:**
   - Sunucu penceresinde IP adresi otomatik gösterilir
   - Eğer gösterilmiyorsa, sunucu bilgisayarında `ipconfig` (Windows) veya `ifconfig` (Linux/Mac) komutunu çalıştırın

3. **Bağlantı hatası:**
   - Sunucu ve istemci aynı ağda olmalı (aynı WiFi/router)
   - Firewall ayarlarını kontrol edin (Port 55555 açık olmalı)
   - IP adresinin doğru girildiğinden emin olun
   - Sunucu bilgisayarının IP adresinin değişmediğinden emin olun

4. **Port kullanımda hatası:**
   - Port 55555 başka bir program tarafından kullanılıyor olabilir
   - O programı kapatın veya `server_gui.py` ve `game_network.py` dosyalarındaki `PORT` değişkenini değiştirin

5. **Oyuncu bağlanamıyor:**
   - Maksimum 2 oyuncu bağlanabilir
   - Üçüncü bir oyuncu bağlanmaya çalışırsa reddedilir
   - Sunucuyu yeniden başlatıp tekrar deneyin

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## GitHub Kurulumu

### Projeyi GitHub'a Yükleme

1. **Yeni bir repository oluşturun:**
   - GitHub'da yeni bir repository oluşturun
   - Repository adını seçin (örnek: `xox-oyunu`)

2. **Projeyi Git ile başlatın:**
   ```bash
   git init
   git add .
   git commit -m "İlk commit: XOX Oyunu projesi"
   ```

3. **GitHub repository'sine bağlayın:**
   ```bash
   git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git
   git branch -M main
   git push -u origin main
   ```

4. **Projeyi başka bir bilgisayara indirme:**
   ```bash
   git clone https://github.com/KULLANICI_ADI/REPO_ADI.git
   cd REPO_ADI
   python game_launcher.py
   ```

### Güncellemeleri Yükleme

Değişiklik yaptıktan sonra:
```bash
git add .
git commit -m "Açıklayıcı commit mesajı"
git push
```

## İletişim

Proje hakkında sorularınız için dokümantasyonu inceleyebilirsiniz.

---

**Not:** Bu proje socket programlama dersi için geliştirilmiştir ve tüm gereksinimler karşılanmıştır:
- ✅ Aynı bilgisayardan karşılıklı oyun
- ✅ Bilgisayara karşı oyun
- ✅ Network üzerinden karşılıklı oyun (Socket programlama)
- ✅ Zaman modu (10 saniye bonus)
- ✅ 3 adet test case
- ✅ Dokümantasyon
- ✅ Otomatik IP adresi tespiti
- ✅ Kullanıcı dostu arayüz

