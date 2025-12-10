import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Label, messagebox
import sys

# Sabitler
HOST = '0.0.0.0'
PORT = 55555
MAX_CLIENTS = 2 # XOX oyunu için maksimum 2 istemci

def get_local_ip():
    """Bilgisayarın yerel IP adresini bulur"""
    try:
        # Dummy bir bağlantı yaparak yerel IP'yi buluyoruz
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS'ye bağlanmaya çalışıyoruz (gerçek bağlantı yapılmaz)
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            # Alternatif yöntem: hostname kullanarak
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip.startswith("127."):
                # Eğer localhost dönerse, tüm ağ arayüzlerini kontrol et
                return "Yerel IP bulunamadı"
            return ip
        except Exception:
            return "Yerel IP bulunamadı"

print("DEBUG: Uygulama başlatılıyor, kütüphaneler yüklendi.") 

class TicTacToeServer:
    """
    XOX Oyun Sunucusu:
    - Socket bağlantılarını yönetir ve thread'lerde dinler.
    - Bağlanan istemcilerin listesini tutar.
    - İstemcilerden gelen mesajları diğer istemciye yayınlar (broadcast).
    """

    def __init__(self, master):
        self.master = master
        master.title("XOX Sunucu Konsolu")
        master.geometry("500x450")
        
        # IP adresini al
        self.local_ip = get_local_ip()
        
        # 1. Temel GUI Kurulumu
        # IP adresi gösterimi (büyük ve görünür)
        ip_frame = tk.Frame(master, bg="lightblue", relief=tk.RAISED, bd=2)
        ip_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ip_title = Label(ip_frame, text="SUNUCU IP ADRESİ", font=('Arial', 10, 'bold'), bg="lightblue")
        ip_title.pack(pady=(5, 0))
        
        self.ip_label = Label(ip_frame, text=self.local_ip, font=('Arial', 16, 'bold'), 
                             bg="lightblue", fg="darkblue")
        self.ip_label.pack(pady=(0, 5))
        
        info_label = Label(ip_frame, text="Bu IP adresini istemcilere verin", 
                          font=('Arial', 8), bg="lightblue", fg="darkgray")
        info_label.pack(pady=(0, 5))
        
        # Log alanı
        self.log_area = scrolledtext.ScrolledText(master, state='disabled', width=50, height=12)
        self.log_area.pack(padx=10, pady=10)
        
        self.status_label = Label(master, text="Sunucu Başlatılıyor...", fg="blue")
        self.status_label.pack(pady=5)
        
        self.log_message("GUI arayüzü başlatıldı.")
        self.log_message(f"Yerel IP Adresi: {self.local_ip}")

        self.is_running = True
        self.server_socket = None
        self.clients = [] # Bağlı istemcilerin (socket, adres) listesi
        self._message_buffer = {}  # Her client için mesaj buffer'ı
        
        # 2. Sunucu Thread'ini Başlatma
        # Socket işlemlerini ayrı bir thread'e taşıyarak GUI'nin bloklanmasını önleriz.
        self.log_message("Sunucu dinleme thread'i başlatılıyor...")
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

        # Pencere kapatma protokolünü bağlama
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_message(self, message):
        """GUI konsoluna mesaj yazar (Thread güvenli)."""
        print(message) # Terminale de yazdır
        # Tkinter'ın ana thread'ini kullanarak GUI'yi güvenli bir şekilde güncelle
        self.master.after(0, lambda: self._update_log(message)) 
        
    def _update_log(self, message):
        """log_message'ın GUI'yi güncelleyen kısmı (Ana thread'de çalışır)."""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)

    def start_server(self):
        """Socket kurulumunu ve bağlantı dinlemeyi ayrı thread'de yapar."""
        try:
            self.log_message(f"Sunucu {HOST}:{PORT} adresinde başlatılıyor...")
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Bağlantının hızlıca yeniden kullanılmasını sağlar
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(MAX_CLIENTS)
            
            # GUI'yi thread-safe olarak güncelle
            self.master.after(0, lambda: self.status_label.config(
                text=f"Sunucu {HOST}:{PORT} adresinde dinliyor...\nİstemciler bu IP'ye bağlanabilir: {self.local_ip}", 
                fg="green"))
            self.log_message("Sunucu dinlemede, bağlantı bekleniyor...")
            self.log_message(f"İstemciler şu IP adresine bağlanmalı: {self.local_ip}")

            # Bağlantı kabul etme döngüsü (bloklayıcı 'accept()' içerir)
            while self.is_running:
                client_socket, client_address = self.server_socket.accept()
                
                if len(self.clients) < MAX_CLIENTS:
                    player_char = 'X' if len(self.clients) == 0 else 'O'
                    self.clients.append((client_socket, client_address, player_char))
                    self.log_message(f"Yeni bağlantı: {client_address} - Oyuncu: {player_char}")

                    # Oyuncu karakterini gönder
                    client_socket.send(f"COMMAND:ASSIGN_PLAYER|{player_char}|".encode('utf-8'))

                    # İstemci dinleme thread'ini başlat
                    handler_thread = threading.Thread(
                        target=self.client_handler, 
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    handler_thread.start()
                    
                    # Oyuncu sayısını güncelle
                    self.master.after(0, lambda: self.status_label.config(text=f"Bağlı istemci sayısı: {len(self.clients)}/{MAX_CLIENTS}"))
                    
                    if len(self.clients) == MAX_CLIENTS:
                        self.log_message("Maksimum oyuncu sayısına ulaşıldı. Oyun Başlıyor!")
                        # İstemcilere oyuna başlama komutu gönder
                        self.broadcast_message("COMMAND:START_GAME|") 
                        
                else:
                    # Fazla istemciyi reddet
                    self.log_message(f"Bağlantı reddedildi (Oyuncu Sınırı): {client_address}")
                    client_socket.send("COMMAND:LIMIT_REACHED|".encode('utf-8'))
                    client_socket.close()
                    
        except OSError as e:
            if self.is_running: # Sadece sunucu kendimiz kapatırken değilse hata mesajı ver
                error_msg = f"Sunucu Hatası: {e}"
                self.log_message(error_msg)
                if "Address already in use" in str(e) or "address is already in use" in str(e).lower():
                    error_msg = f"Port {PORT} zaten kullanımda!\nLütfen başka bir port kullanın veya\nkullanan programı kapatın."
                self.master.after(0, lambda msg=error_msg: messagebox.showerror("Sunucu Hatası", msg))
                self.master.after(0, lambda: self.status_label.config(text="Sunucu Hatası!", fg="red"))
        except Exception as e:
            error_msg = f"Beklenmedik Hata: {e}"
            self.log_message(error_msg)
            self.master.after(0, lambda msg=error_msg: messagebox.showerror("Hata", msg))
            self.master.after(0, lambda: self.status_label.config(text="Beklenmedik Hata!", fg="red"))

 

    def client_handler(self, client_socket, client_address):
        """Bağlı bir istemciden gelen mesajları dinler ve işler."""
        self.log_message(f"İstemci işleyici başlatıldı: {client_address}")
        
        while self.is_running:
            try:
                # Bloklayıcı 'recv()' işlemi ayrı thread'de çalışır
                data = client_socket.recv(1024).decode('utf-8')
                
                if data:
                    # Mesajları buffer'a ekle (birden fazla mesaj birleşmiş olabilir)
                    if not hasattr(self, '_message_buffer'):
                        self._message_buffer = {}
                    if client_address not in self._message_buffer:
                        self._message_buffer[client_address] = ""
                    
                    self._message_buffer[client_address] += data
                    self.log_message(f"DEBUG: Veri alındı ({client_address}): {repr(data)}, buffer: {repr(self._message_buffer[client_address])}")
                    
                    # Mesajları ayır: Her mesaj | ile bitiyor
                    # MOVE mesajları: MOVE|row,col|char| (3 | karakteri gerekli)
                    # COMMAND mesajları: COMMAND:XXX| (1 | karakteri yeterli)
                    buffer = self._message_buffer[client_address]
                    
                    while buffer:
                        # MOVE mesajları için 3 | karakteri say
                        if buffer.startswith("MOVE"):
                            pipe_count = 0
                            i = 0
                            while i < len(buffer):
                                if buffer[i] == '|':
                                    pipe_count += 1
                                    if pipe_count == 3:
                                        # Tam mesaj bulundu
                                        message = buffer[:i+1]
                                        buffer = buffer[i+1:]
                                        self.log_message(f"[{client_address}] Mesaj Alındı: {message}")
                                        self.broadcast_message(message, sender_socket=client_socket)
                                        break
                                i += 1
                            else:
                                # Tam mesaj yok, daha fazla veri bekle
                                break
                        
                        # COMMAND mesajları için ilk | karakterini bul
                        elif buffer.startswith("COMMAND:"):
                            pipe_index = buffer.find('|')
                            if pipe_index != -1:
                                message = buffer[:pipe_index + 1]
                                buffer = buffer[pipe_index + 1:]
                                self.log_message(f"[{client_address}] Mesaj Alındı: {message}")
                                
                                if message.startswith("COMMAND:DISCONNECT"):
                                    self.log_message(f"İstemci bağlantıyı kapattı: {client_address}")
                                    if client_address in self._message_buffer:
                                        del self._message_buffer[client_address]
                                    break
                                
                                self.broadcast_message(message, sender_socket=client_socket)
                            else:
                                # | karakteri yok, daha fazla veri bekle
                                break
                        else:
                            # Bilinmeyen format, ilk | karakterine kadar al
                            pipe_index = buffer.find('|')
                            if pipe_index != -1:
                                message = buffer[:pipe_index + 1]
                                buffer = buffer[pipe_index + 1:]
                                self.log_message(f"[{client_address}] Mesaj Alındı: {message}")
                                self.broadcast_message(message, sender_socket=client_socket)
                            else:
                                break
                    
                    # Kalan buffer'ı sakla
                    self._message_buffer[client_address] = buffer
                else:
                    # Bağlantı kapandı
                    break 
            except ConnectionResetError:
                # İstemci aniden bağlantıyı keserse
                self.log_message(f"İstemci bağlantıyı kesti: {client_address}")
                break
            except ConnectionAbortedError:
                # Bağlantı iptal edildi
                self.log_message(f"İstemci bağlantısı iptal edildi: {client_address}")
                break
            except Exception as e:
                self.log_message(f"İstemci İşleyici Hatası ({client_address}): {e}")
                break

        # Döngüden çıkıldı: İstemcinin bağlantısını temizle
        # Buffer'ı temizle
        if client_address in self._message_buffer:
            del self._message_buffer[client_address]
        
        self.remove_client(client_socket, client_address)
        
   
        

    def broadcast_message(self, message, sender_socket=None):
        """Gönderen dışındaki tüm bağlı istemcilere mesajı yollar."""
        if not self.clients:
            return
        
        sender_info = None
        if sender_socket:
            for sock, addr, char in self.clients:
                if sock == sender_socket:
                    sender_info = f"{addr} ({char})"
                    break
        
        self.log_message(f"Yayın yapılıyor: '{message}' (Gönderen: {sender_info})")
            
        for client_socket, client_address, player_char in self.clients[:]:  # Kopya al
            if client_socket != sender_socket:
                try:
                    self.log_message(f"  → {client_address} ({player_char})'ye gönderiliyor...")
                    client_socket.sendall(message.encode('utf-8'))
                    self.log_message(f"  ✓ {client_address} ({player_char})'ye gönderildi")
                except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                    self.log_message(f"Yayın Hatası ({client_address}): {e}")
                    # Hata varsa, o istemciyi temizle
                    self.remove_client(client_socket, client_address)
                except Exception as e:
                    self.log_message(f"Beklenmedik Yayın Hatası ({client_address}): {e}")
                    self.remove_client(client_socket, client_address)
            else:
                self.log_message(f"  ⊗ {client_address} ({player_char}) atlandı (gönderen)")


    def remove_client(self, client_socket, client_address):
        """Bağlantısı kopan istemciyi listeden çıkarır ve soketini kapatır."""
        # Buffer'ı temizle
        if hasattr(self, '_message_buffer') and client_address in self._message_buffer:
            del self._message_buffer[client_address]
        
        # Client listesini güncelle (artık tuple'da player_char var)
        for i, (sock, addr, char) in enumerate(self.clients):
            if sock == client_socket:
                self.clients.pop(i)
                self.log_message(f"Bağlantı kesildi: {client_address}")
                break
        
        # GUI'yi thread-safe olarak güncelle
        self.master.after(0, lambda: self.status_label.config(text=f"Bağlı istemci sayısı: {len(self.clients)}/{MAX_CLIENTS}"))
        
        # Bir oyuncu ayrılırsa, oyunu sıfırlama komutu gönderilebilir
        self.broadcast_message("COMMAND:PLAYER_DISCONNECTED|") 
        
        try:
            client_socket.close()
        except Exception:
            pass # Zaten kapalı olabilir

    def on_closing(self):
        """GUI penceresi kapatılırken tüm socket bağlantılarını kapatır."""
        self.is_running = False
        self.log_message("Sunucu Kapatılıyor...")
        
        # Tüm istemcilere kapanma mesajı gönder ve soketleri kapat
        for client_socket, _, _ in self.clients:
            try:
                client_socket.send("COMMAND:SERVER_CLOSING|".encode('utf-8'))
                client_socket.close()
            except Exception:
                pass
        
        # Ana sunucu soketini kapat
        if self.server_socket:
            try:
                # accept() çağrısının bloklamadan çıkmasını sağlamak için küçük bir hile (gerekmeyebilir ama güvenlidir)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', PORT)) 
                self.server_socket.close()
            except Exception:
                pass
        
        # GUI'yi tamamen kapat
        self.master.destroy()

# Ana Kod Bloğu
if __name__ == '__main__':
    root = tk.Tk()
    print("DEBUG: Tkinter root nesnesi oluşturuldu, uygulama başlatılıyor.")
    try:
        app = TicTacToeServer(root)
        root.mainloop()
    except Exception as e:
        print(f"KRİTİK HATA: Ana döngü başlamadan hata oluştu: {e}")
        sys.exit(1)
