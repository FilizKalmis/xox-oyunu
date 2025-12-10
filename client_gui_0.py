import socket
import threading
import tkinter as tk
from tkinter import messagebox, Label

# Sabitler (Sunucudaki ile aynı olmalı!)
HOST = '127.0.0.1' # Deneme için yerel adresi kullanıyoruz. 
                   # Farklı bir cihazdan bağlanırken sunucunun gerçek IP'sini yazın.
PORT = 55555
PLAYER_CHAR = 'O'
OPPONENT_CHAR = 'X'

class TicTacToeClient:
    """
    XOX Oyun İstemcisi:
    - Tkinter ile oyun tahtası GUI'sini oluşturur.
    - Sunucuya bağlanır ve mesajları (hamleleri) ayrı bir thread'de dinler.
    - Hamleleri yönetir ve tahtayı günceller.
    """

    def __init__(self, master):
        self.master = master
        
        self.current_player =PLAYER_CHAR
        self.opponent_char=OPPONENT_CHAR

        master.title(f"XOX Oyuncusu-{self.current_player}")

        self.game_board = [[' ' for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        self.is_my_turn = (self.current_player=='O')    # Şu anki oyuncu X ise ve bu client da X ise true olacak
        self.game_over = False
        
        self.client_socket = None
        self.is_connected = False
        
        # GUI bileşenlerini oluştur
        self._create_widgets()
        
        # Bağlantı işlemini ayrı bir thread'de başlat
        self.connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
        self.connect_thread.start()

        # Pencere kapatma protokolünü bağla
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_widgets(self):
        """Oyun tahtası düğmelerini ve durum etiketini oluşturur."""
        self.status_label = Label(self.master, text="Sunucuya bağlanılıyor...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Tahta çerçevesi
        board_frame = tk.Frame(self.master)
        board_frame.pack(padx=10, pady=10)

        # 3x3 Düğmeleri oluştur
        for r in range(3):
            for c in range(3):
                button = tk.Button(board_frame, text='', font=('Arial', 24), width=5, height=2,
                                   command=lambda r=r, c=c: self.make_move(r, c))
                button.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = button
                
        self.set_board_enabled(False) # Bağlanana kadar tahtayı pasif yap

    def set_board_enabled(self, enabled):
        """Tüm tahta düğmelerinin durumunu ayarlar."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(state=state)
                
    def connect_to_server(self):
        """Sunucuya bağlanmayı ve dinleyici thread'i başlatmayı dener."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.is_connected = True
            
            # Sunucudan ilk mesajı (hangi oyuncu olduğumuzu) alabiliriz
            # Şimdilik varsayılan olarak X diyelim. Sunucu ataması daha sonra eklenebilir.
            
            self.master.after(0, lambda: self.status_label.config(text=f"Sunucuya Bağlandı: {HOST}:{PORT}"))
            
            # Bağlandıktan sonra dinleyici thread'i başlat
            self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
            self.listen_thread.start()
            
        except ConnectionRefusedError:
            self.master.after(0, lambda: self.status_label.config(text="Bağlantı Başarısız: Sunucu Kapalı veya Yanlış IP/Port.", fg="red"))
            self.master.after(0, lambda: messagebox.showerror("Hata", "Sunucuya bağlanılamadı. Uygulama Kapanacak."))
            self.master.after(1000, self.master.destroy) # 1 saniye sonra GUI'yi kapat
        except Exception as e:
            self.master.after(0, lambda: self.status_label.config(text=f"Beklenmedik Bağlantı Hatası: {e}", fg="red"))

    def listen_for_messages(self):
        """Sunucudan gelen mesajları sürekli dinler (Ayrı thread'de)."""
        while self.is_connected:
            try:
                # Bloklayıcı 'recv()' işlemi ayrı thread'de çalışır
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    print(f"DEBUG: Sunucudan alınan veri: {data}")
                    # Ana thread'de işlem yapmak için after kullan
                    self.master.after(0, lambda: self.process_message(data))
                else:
                    # Sunucu bağlantıyı kapattı
                    break
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"HATA: Mesaj dinleme hatası: {e}")
                break
        
        # Döngüden çıkıldıysa bağlantıyı güvenli bir şekilde kapat
        self.is_connected = False
        self.master.after(0, lambda: self.status_label.config(text="Bağlantı Kesildi.", fg="red"))
        try:
            self.client_socket.close()
        except:
            pass

    def process_message(self, message):
        """Ana thread'de gelen mesajı işler ve GUI'yi günceller."""
        parts = message.split('|')
        command = parts[0]

        if command == "COMMAND:START_GAME":
            # Sunucu oyunu başlatma komutunu gönderdi
            self.status_label.config(text="Oyun Başladı!")
            # X ilk başlar varsayımıyla (Sunucu tarafından belirlenmeli)
            
            if self.current_player=='X':
                self.is_my_turn=True
            else:
                self.is_my_turn=False

            self.set_board_enabled(self.is_my_turn)
            self.status_label.config(text=f"sıra sende({self.current_player})"if self.is_my_turn else "rakibin hamlesi bekleniyor (X)")    
               

        elif command == "MOVE":
            # Hamle mesajı: MOVE|row,col|char
            try:
                r, c = map(int, parts[1].split(','))
                char = parts[2]
                
              # Sadece rakibin yaptığı hamleyi işle
                if char != self.current_player:
                    self.update_board(r, c, char)
                    
                    # Hamle rakibimizden geldiyse, sıra bize geçer!
                    self.is_my_turn = True
                    self.set_board_enabled(True)
                    self.status_label.config(text=f"Sıra Sende ({self.current_player})")
                else:
                    # Kendi hamlemizin sunucudan geri gelmesini yoksay
                    # Bu satır, kendi hamlenizin sunucudan geri gelmesini engeller.
                    self.is_my_turn = False
                    self.set_board_enabled(False)

            except Exception as e:
                print(f"HATA: Hamle işlenemedi: {e}")
                
        elif command == "COMMAND:SERVER_CLOSING":
            messagebox.showinfo("Uyarı", "Sunucu kapatıldı. Uygulama sonlanıyor.")
            self.on_closing()

        # Buraya oyun kazanma/berabere kalma kontrolü eklenecek

    def make_move(self, r, c):
        """Kullanıcının yaptığı hamleyi işler ve sunucuya gönderir."""
        if self.game_over or not self.is_my_turn or self.game_board[r][c] != ' ':
            return # Oyun bittiyse, sıra bizde değilse veya kare doluysa işlem yapma

        # Hamleyi yerel olarak yap
        char = self.current_player
        self.update_board(r, c, char)
        
        # Sıra bitti, tahtayı kitle
        self.is_my_turn = False
        self.set_board_enabled(False)
        self.status_label.config(text="Hamle gönderildi. Rakip bekleniyor...")

        # Hamleyi sunucuya gönder: MOVE|row,col|char
        message = f"MOVE|{r},{c}|{char}"
        try:
            self.client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Hata", f"Hamle gönderilemedi: {e}")
            self.on_closing() # Hata durumunda kapat

    def update_board(self, r, c, char):
        """GUI tahtasını ve veri modelini günceller."""
        self.game_board[r][c] = char
        self.buttons[r][c].config(text=char)
        
        # !!! OYUN SONU KONTROLÜ !!!
        winner = self.check_winner()
        if winner:
            self.end_game(winner)


    def check_winner(self):
        board = self.game_board
        
        # 1. Satır ve Sütun Kontrolü
        for i in range(3):
            # Yatay kontrol
            if board[i][0] == board[i][1] == board[i][2] and board[i][0] != ' ':
                return board[i][0]
            # Dikey kontrol
            if board[0][i] == board[1][i] == board[2][i] and board[0][i] != ' ':
                return board[0][i]

        # 2. Çapraz Kontrol
        # Sol üstten sağ alta
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != ' ':
            return board[0][0]
        # Sağ üstten sol alta
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != ' ':
            return board[0][2]

        # 3. Beraberlik Kontrolü (Tahta tamamen dolu mu?)
        if all(board[r][c] != ' ' for r in range(3) for c in range(3)):
            return "Berabere"

        return None # Oyun devam ediyor

    def end_game(self, result):
        self.game_over = True
        self.set_board_enabled(False) # Tahtayı tamamen kitle
        
        if result == "Berabere":
            message = "OYUN SONU: Berabere!"
            messagebox.showinfo("Oyun Bitti", message)
        else:
            message = f"OYUN SONU: {result} Kazandı!"
            messagebox.showinfo("Oyun Bitti", message)
            
        self.status_label.config(text=message, fg="red" if result != "Berabere" else "blue")        
        
    def on_closing(self):
        """GUI penceresi kapatılırken bağlantıyı güvenli bir şekilde kapatır."""
        self.is_connected = False
        self.game_over = True # Oyun durumunu kapat
        print("İstemci kapatılıyor...")
        
        if self.client_socket:
            try:
                # Sunucuya ayrıldığımızı bildirebiliriz (isteğe bağlı)
                self.client_socket.send("COMMAND:DISCONNECT|".encode('utf-8'))
                self.client_socket.close()
            except Exception:
                pass
        
        self.master.destroy()

# Ana Kod Bloğu
if __name__ == '__main__':
    root = tk.Tk()
    app = TicTacToeClient(root)
    # Bu, GUI'yi çalıştıran ana, bloklayıcı döngüdür. 
    # Socket dinleme ayrı thread'de çalıştığı için GUI yanıt vermeye devam eder.
    root.mainloop()