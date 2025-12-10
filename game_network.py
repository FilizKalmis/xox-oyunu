"""
XOX Oyunu - Network Modu
İki oyuncu network üzerinden karşılıklı oynar
"""
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from game_base import BaseGame

# Sabitler
PORT = 55555

class NetworkGame(BaseGame):
    """Network modu - socket üzerinden oyun"""
    
    def __init__(self, master, time_mode=False):
        super().__init__(master, time_mode)
        master.title("XOX Oyunu - Network Modu")
        
        self.client_socket = None
        self.is_connected = False
        self.current_player = None  # Sunucu atayacak
        self.opponent_char = None
        self.host = None
        
        # IP adresi sor
        self.ask_server_ip()
        
        if self.host:  # Eğer IP girildiyse devam et
            self._create_widgets()
            self.set_board_enabled(False)
            self.status_label.config(text="Sunucuya bağlanılıyor...")
            
            # Bağlantı işlemini ayrı bir thread'de başlat
            self.connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
            self.connect_thread.start()
        else:
            # IP girilmediyse pencereyi kapat
            self.master.destroy()
            return
        
        # Pencere kapatma protokolünü bağla
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def ask_server_ip(self):
        """Sunucu IP adresini kullanıcıdan sorar"""
        # Daha kullanıcı dostu bir dialog oluştur
        dialog = tk.Toplevel(self.master)
        dialog.title("Sunucu IP Adresi")
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()  # Modal dialog
        
        # Başlık
        title_label = tk.Label(dialog, text="Sunucu IP Adresini Girin", 
                              font=('Arial', 12, 'bold'))
        title_label.pack(pady=10)
        
        # Açıklama
        info_text = ("Sunucu bilgisayarının IP adresini girin:\n\n"
                    "• Aynı bilgisayarda test için: 127.0.0.1\n"
                    "• Farklı bilgisayar için: Sunucunun IP adresi\n"
                    "  (Örnek: 192.168.1.100)")
        info_label = tk.Label(dialog, text=info_text, justify=tk.LEFT, 
                             font=('Arial', 9))
        info_label.pack(pady=10)
        
        # IP giriş alanı
        ip_frame = tk.Frame(dialog)
        ip_frame.pack(pady=10)
        
        tk.Label(ip_frame, text="IP Adresi:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        ip_entry = tk.Entry(ip_frame, font=('Arial', 11), width=20)
        ip_entry.pack(side=tk.LEFT, padx=5)
        ip_entry.insert(0, "127.0.0.1")
        ip_entry.focus()
        ip_entry.select_range(0, tk.END)
        
        # Sonuç değişkeni
        result = {'ip': None}
        
        def on_ok():
            ip = ip_entry.get().strip()
            if ip:
                result['ip'] = ip
                dialog.destroy()
            else:
                messagebox.showwarning("Uyarı", "Lütfen bir IP adresi girin!")
        
        def on_cancel():
            dialog.destroy()
        
        # Butonlar
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ok_button = tk.Button(button_frame, text="Bağlan", command=on_ok, 
                             font=('Arial', 10), width=10)
        ok_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="İptal", command=on_cancel, 
                                 font=('Arial', 10), width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Enter tuşu ile bağlan
        ip_entry.bind('<Return>', lambda e: on_ok())
        
        # Dialog'u göster ve sonucu bekle
        dialog.wait_window()
        
        self.host = result['ip']
        
        if not self.host:
            messagebox.showwarning("Uyarı", "IP adresi girilmedi. Uygulama kapatılıyor.")
            return
    
    def connect_to_server(self):
        """Sunucuya bağlanmayı dener"""
        if not self.host:
            return
            
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)  # 5 saniye timeout
            self.client_socket.connect((self.host, PORT))
            self.client_socket.settimeout(None)  # Timeout'u kaldır
            self.is_connected = True
            
            self.master.after(0, lambda: self.status_label.config(
                text=f"Sunucuya Bağlandı: {self.host}:{PORT}", fg="green"))
            
            # Dinleyici thread'i başlat
            self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
            self.listen_thread.start()
            
        except socket.timeout:
            self.master.after(0, lambda: self.status_label.config(
                text="Bağlantı Zaman Aşımı: Sunucu yanıt vermiyor.", fg="red"))
            self.master.after(0, lambda: messagebox.showerror(
                "Bağlantı Hatası", 
                f"Sunucuya bağlanılamadı.\n\n"
                f"Kontrol edin:\n"
                f"- Sunucu çalışıyor mu? (python server_gui.py)\n"
                f"- IP adresi doğru mu? ({self.host})\n"
                f"- Firewall ayarları\n"
                f"- Aynı ağda mısınız?"))
        except ConnectionRefusedError:
            self.master.after(0, lambda: self.status_label.config(
                text="Bağlantı Reddedildi: Sunucu kapalı veya erişilemiyor.", fg="red"))
            self.master.after(0, lambda: messagebox.showerror(
                "Bağlantı Hatası", 
                f"Sunucuya bağlanılamadı.\n\n"
                f"Lütfen sunucunun çalıştığından emin olun:\n"
                f"python server_gui.py"))
        except Exception as e:
            self.master.after(0, lambda: self.status_label.config(
                text=f"Bağlantı Hatası: {e}", fg="red"))
            self.master.after(0, lambda: messagebox.showerror(
                "Hata", f"Beklenmedik bağlantı hatası:\n{e}"))
    
    def listen_for_messages(self):
        """Sunucudan gelen mesajları dinler"""
        while self.is_connected:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    self.master.after(0, lambda d=data: self.process_message(d))
                else:
                    break
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"HATA: Mesaj dinleme hatası: {e}")
                break
        
        self.is_connected = False
        self.master.after(0, lambda: self.status_label.config(text="Bağlantı Kesildi.", fg="red"))
        try:
            self.client_socket.close()
        except:
            pass
    
    def process_message(self, message):
        """Sunucudan gelen mesajı işler"""
        parts = message.split('|')
        command = parts[0]
        
        if command == "COMMAND:ASSIGN_PLAYER":
            # Sunucu oyuncu karakterini atadı
            if len(parts) > 1:
                self.current_player = parts[1]
                self.opponent_char = 'O' if self.current_player == 'X' else 'X'
                self.master.title(f"XOX Oyunu - Network Modu ({self.current_player})")
        
        elif command == "COMMAND:START_GAME":
            self.status_label.config(text="Oyun Başladı!")
            if self.current_player is None:
                self.current_player = 'X'
                self.opponent_char = 'O'
            self.is_my_turn = (self.current_player == 'X')
            self.set_board_enabled(self.is_my_turn)
            self.update_status()
            if self.time_mode:
                self.start_timer()
        
        elif command == "MOVE":
            # Hamle mesajı: MOVE|row,col|char
            try:
                r, c = map(int, parts[1].split(','))
                char = parts[2]
                
                if char != self.current_player:
                    self.update_board(r, c, char)
                    self.current_player = 'X' if self.current_player == 'O' else 'O'
                    self.is_my_turn = True
                    self.set_board_enabled(True)
                    self.update_status()
                    if self.time_mode:
                        self.start_timer()
            except Exception as e:
                print(f"HATA: Hamle işlenemedi: {e}")
        
        elif command == "GAME_OVER":
            # Oyun sonu mesajı: GAME_OVER|winner|player_char|
            # Bu mesaj rakibin gönderdiği oyun sonu bildirimi
            try:
                winner = parts[1]
                sender_char = parts[2] if len(parts) > 2 else None
                
                # Eğer bu rakibin gönderdiği mesajsa ve oyun henüz bitmediyse
                if sender_char and sender_char != self.current_player and not self.game_over:
                    # Rakip oyun sonu durumunu bildirdi, bizim de kontrol edelim
                    # Ama önce kendi tahtamızda kontrol edelim
                    local_winner = self.check_winner()
                    if local_winner:
                        # Kendi tahtamızda da oyun bitti, end_game'i çağır
                        self.end_game(local_winner)
                    else:
                        # Sadece rakibin bildirdiği durumu göster
                        # (Bu durumda rakibin kazandığını bildiriyor)
                        self.end_game(winner)
            except Exception as e:
                print(f"HATA: Oyun sonu mesajı işlenemedi: {e}")
        
        elif command == "COMMAND:REMATCH_ACCEPTED":
            # Rakip tekrar oynamayı kabul etti
            messagebox.showinfo("Tekrar Oyna", "Rakip oyuncu tekrar oynamayı kabul etti!")
            self.restart_game()
        
        elif command == "COMMAND:REMATCH_REJECTED":
            # Rakip tekrar oynamayı reddetti
            messagebox.showinfo("Tekrar Oyna", "Rakip oyuncu tekrar oynamayı reddetti.")
            self.status_label.config(text="Rakip oyuncu ayrıldı.", fg="red")
            self.master.after(2000, self.return_to_menu)
        
        elif command == "COMMAND:REMATCH_REQUEST":
            # Rakip tekrar oynamak istiyor
            choice = messagebox.askyesno(
                "Tekrar Oyna",
                "Rakip oyuncu tekrar oynamak istiyor. Kabul ediyor musunuz?"
            )
            if choice:
                if self.is_connected:
                    try:
                        self.client_socket.sendall("COMMAND:REMATCH_ACCEPTED|".encode('utf-8'))
                        self.restart_game()
                    except Exception as e:
                        messagebox.showerror("Hata", f"Yanıt gönderilemedi: {e}")
            else:
                if self.is_connected:
                    try:
                        self.client_socket.sendall("COMMAND:REMATCH_REJECTED|".encode('utf-8'))
                    except:
                        pass
                self.return_to_menu()
        
        elif command == "COMMAND:SERVER_CLOSING":
            messagebox.showinfo("Uyarı", "Sunucu kapatıldı.")
            self.on_closing()
    
    def on_move_made(self, r, c):
        """Hamleyi sunucuya gönder"""
        if not self.is_connected:
            return
        
        message = f"MOVE|{r},{c}|{self.current_player}"
        try:
            self.client_socket.sendall(message.encode('utf-8'))
            self.is_my_turn = False
            self.set_board_enabled(False)
            self.status_label.config(text="Hamle gönderildi. Rakip bekleniyor...")
            if self.time_mode:
                self.timer_running = False
        except Exception as e:
            messagebox.showerror("Hata", f"Hamle gönderilemedi: {e}")
    
    def end_game(self, result):
        """Oyunu sonlandırır ve sunucuya bildirir"""
        self.game_over = True
        self.timer_running = False
        self.set_board_enabled(False)
        
        # Kazanan/kaybeden mesajını belirle
        if result == "Berabere":
            message = "OYUN SONU: Berabere!"
            result_message = "Berabere"
        else:
            if result == self.current_player:
                message = "🎉 TEBRİKLER! KAZANDINIZ! 🎉"
                result_message = "Kazandınız"
            else:
                message = "😔 KAYBETTİNİZ 😔"
                result_message = "Kaybettiniz"
        
        # Mesajı göster
        messagebox.showinfo("Oyun Bitti", message)
        self.status_label.config(text=result_message, fg="green" if result == self.current_player else "red")
        
        # Sunucuya oyun sonu durumunu bildir
        if self.is_connected:
            try:
                game_over_msg = f"GAME_OVER|{result}|{self.current_player}|"
                self.client_socket.sendall(game_over_msg.encode('utf-8'))
            except Exception as e:
                print(f"HATA: Oyun sonu mesajı gönderilemedi: {e}")
        
        # Oyun bittikten sonra seçenekler sun
        self.master.after(500, self.show_network_game_over_options)
    
    def show_network_game_over_options(self):
        """Network modunda oyun bittikten sonra seçenekler sunar"""
        from tkinter import messagebox
        
        # Seçenekler penceresi
        choice = messagebox.askyesnocancel(
            "Oyun Bitti",
            "Ne yapmak istersiniz?\n\n"
            "Evet: Tekrar Aynı Kişiyle Oyna\n"
            "Hayır: Ana Menüye Dön\n"
            "İptal: Pencereyi Kapat"
        )
        
        if choice is True:  # Tekrar oyna
            self.send_rematch_request()
        elif choice is False:  # Ana menüye dön
            self.send_menu_request()
        else:  # İptal - pencereyi kapat
            self.send_quit_request()
    
    def send_rematch_request(self):
        """Tekrar oynama isteğini sunucuya gönderir"""
        if self.is_connected:
            try:
                self.client_socket.sendall("COMMAND:REMATCH_REQUEST|".encode('utf-8'))
                self.status_label.config(text="Rakip oyuncunun cevabı bekleniyor...", fg="blue")
            except Exception as e:
                messagebox.showerror("Hata", f"İstek gönderilemedi: {e}")
    
    def send_menu_request(self):
        """Menüye dönme isteğini sunucuya gönderir ve menüye döner"""
        if self.is_connected:
            try:
                self.client_socket.sendall("COMMAND:MENU_REQUEST|".encode('utf-8'))
            except:
                pass
        self.return_to_menu()
    
    def send_quit_request(self):
        """Çıkış isteğini sunucuya gönderir ve pencereyi kapatır"""
        if self.is_connected:
            try:
                self.client_socket.sendall("COMMAND:QUIT_REQUEST|".encode('utf-8'))
            except:
                pass
        self.master.destroy()
    
    def restart_game(self):
        """Oyunu sıfırlar ve yeniden başlatır (Network modu için)"""
        # Oyun tahtasını sıfırla
        self.game_board = [[' ' for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.timer_running = False
        
        # Butonları sıfırla
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text='', state=tk.NORMAL, fg='black')
        
        # Yeni oyunda X oyuncusu başlar
        # Eğer biz X oyuncusuysak, biz başlarız
        # Eğer biz O oyuncusuysak, rakibimiz başlar
        starting_player = 'X'
        self.is_my_turn = (self.current_player == starting_player)
        
        # Tahtayı aktif/pasif yap
        if self.is_my_turn:
            self.set_board_enabled(True)
            self.status_label.config(text=f"Yeni Oyun Başladı! Sıra Sende ({self.current_player})", fg='black')
        else:
            self.set_board_enabled(False)
            self.status_label.config(text="Yeni Oyun Başladı! Rakibin hamlesi bekleniyor...", fg='black')
        
        if self.time_mode:
            self.timer_running = False
            if self.timer_label:
                self.timer_label.config(text="Süre: 30 saniye", fg='red')
            if self.is_my_turn:
                self.start_timer()
    
    def update_status(self):
        """Durum etiketini günceller"""
        if not self.game_over:
            if hasattr(self, 'is_my_turn') and self.is_my_turn:
                self.status_label.config(text=f"Sıra Sende ({self.current_player})")
            else:
                self.status_label.config(text=f"Rakibin Hamlesi Bekleniyor...")
    
    def on_closing(self):
        """Pencere kapatılırken bağlantıyı kapat"""
        self.is_connected = False
        self.game_over = True
        if self.time_mode:
            self.timer_running = False
        
        if self.client_socket:
            try:
                self.client_socket.send("COMMAND:DISCONNECT|".encode('utf-8'))
                self.client_socket.close()
            except:
                pass
        
        self.master.destroy()

