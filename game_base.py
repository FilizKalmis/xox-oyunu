"""
XOX Oyunu - Temel Oyun Sınıfı
Tüm oyun modları için ortak fonksiyonlar
"""
import tkinter as tk
from tkinter import messagebox, Label

class BaseGame:
    """Tüm oyun modları için temel sınıf"""
    
    def __init__(self, master, time_mode=False):
        self.master = master
        self.time_mode = time_mode
        self.game_board = [[' ' for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.time_remaining = 0
        self.bonus_time = 10 if time_mode else 0
        
        # Zaman modu için timer
        self.timer_label = None
        self.timer_running = False
        self.base_time_per_turn = 30  # Her hamle için 30 saniye
        
    def _create_widgets(self):
        """Oyun tahtası ve GUI bileşenlerini oluşturur"""
        # Durum etiketi
        self.status_label = Label(self.master, text="Oyun Başlıyor...", 
                                 bd=1, relief=tk.SUNKEN, anchor=tk.W, font=('Arial', 10))
        self.status_label.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Zaman modu için timer etiketi
        if self.time_mode:
            self.timer_label = Label(self.master, text="Süre: 30 saniye", 
                                    font=('Arial', 12, 'bold'), fg='red')
            self.timer_label.pack(pady=5)
        
        # Tahta çerçevesi
        board_frame = tk.Frame(self.master)
        board_frame.pack(padx=10, pady=10)
        
        # 3x3 Düğmeleri oluştur
        for r in range(3):
            for c in range(3):
                button = tk.Button(board_frame, text='', font=('Arial', 24), 
                                   width=5, height=2,
                                   command=lambda r=r, c=c: self.make_move(r, c))
                button.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = button
        
        # Oyun sonu butonları çerçevesi (başlangıçta gizli)
        self.end_game_frame = tk.Frame(self.master)
        # Başlangıçta pack edilmez, oyun bittiğinde gösterilir
    
    def set_board_enabled(self, enabled):
        """Tüm tahta düğmelerinin durumunu ayarlar"""
        state = tk.NORMAL if enabled else tk.DISABLED
        for r in range(3):
            for c in range(3):
                if self.game_board[r][c] == ' ':  # Sadece boş kareleri aktif et
                    self.buttons[r][c].config(state=state)
                else:
                    self.buttons[r][c].config(state=tk.DISABLED)
    
    def make_move(self, r, c):
        """Kullanıcının yaptığı hamleyi işler"""
        if self.game_over or self.game_board[r][c] != ' ':
            return
        
        # Hamle yapılmadan önceki oyuncuyu sakla (network modu için)
        move_player = self.current_player
        
        # Hamleyi yerel olarak yap
        self.update_board(r, c, self.current_player)
        
        # Zaman modunda bonus süre ekle
        if self.time_mode and self.timer_running:
            self.time_remaining += self.bonus_time
            if self.timer_label:
                self.timer_label.config(text=f"Süre: {self.time_remaining} saniye (+{self.bonus_time} bonus)")
        
        # Sıra değiş
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.update_status()
        
        # Alt sınıfların hamle işleme metodunu çağır (hamle yapan oyuncuyu parametre olarak geç)
        self.on_move_made(r, c, move_player)
    
    def update_board(self, r, c, char):
        """GUI tahtasını ve veri modelini günceller"""
        self.game_board[r][c] = char
        color = 'blue' if char == 'X' else 'red'
        self.buttons[r][c].config(text=char, fg=color, state=tk.DISABLED)
        
        # Oyun sonu kontrolü
        winner = self.check_winner()
        if winner:
            self.end_game(winner)
    
    def check_winner(self):
        """Kazananı kontrol eder"""
        board = self.game_board
        
        # Satır ve sütun kontrolü
        for i in range(3):
            # Yatay kontrol
            if board[i][0] == board[i][1] == board[i][2] and board[i][0] != ' ':
                return board[i][0]
            # Dikey kontrol
            if board[0][i] == board[1][i] == board[2][i] and board[0][i] != ' ':
                return board[0][i]
        
        # Çapraz kontrol
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != ' ':
            return board[0][2]
        
        # Beraberlik kontrolü
        if all(board[r][c] != ' ' for r in range(3) for c in range(3)):
            return "Berabere"
        
        return None
    
    def end_game(self, result):
        """Oyunu sonlandırır"""
        self.game_over = True
        self.timer_running = False
        self.set_board_enabled(False)
        
        if result == "Berabere":
            message = "OYUN SONU: Berabere!"
            messagebox.showinfo("Oyun Bitti", message)
        else:
            message = f"OYUN SONU: {result} Kazandı!"
            messagebox.showinfo("Oyun Bitti", message)
        
        self.status_label.config(text=message, fg="red" if result != "Berabere" else "blue")
        
        # Oyun bittikten sonra seçenekler sun
        self.master.after(500, self.show_game_over_options)
    
    def show_game_over_options(self):
        """Oyun bittikten sonra kullanıcıya seçenekler sunar"""
        from tkinter import messagebox
        
        # Seçenekler penceresi - daha anlaşılır mesaj
        choice = messagebox.askyesnocancel(
            "Oyun Bitti",
            "Ne yapmak istersiniz?\n\n"
            "Evet: Yeni Oyun Başlat\n"
            "Hayır: Ana Menüye Dön\n"
            "İptal: Pencereyi Kapat"
        )
        
        if choice is True:  # Yeni oyun
            self.restart_game()
        elif choice is False:  # Ana menüye dön
            self.return_to_menu()
        else:  # İptal - pencereyi kapat
            self.master.destroy()
    
    def restart_game(self):
        """Oyunu sıfırlar ve yeniden başlatır"""
        # Oyun tahtasını sıfırla
        self.game_board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.timer_running = False
        
        # Butonları sıfırla
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text='', state=tk.NORMAL, fg='black')
        
        # Oyun sonu butonlarını gizle
        self.end_game_frame.pack_forget()
        
        # Durumu güncelle
        self.status_label.config(text="Oyun Başladı! Sıra: X", fg='black')
        self.update_status()
        
        if self.time_mode:
            self.timer_running = False
            if self.timer_label:
                self.timer_label.config(text="Süre: 30 saniye", fg='red')
            self.start_timer()
        
        # AI modundaysa ve AI ilk başlıyorsa
        if hasattr(self, 'ai_char') and self.current_player == self.ai_char:
            self.master.after(500, self.ai_move)
    
    def return_to_menu(self):
        """Ana menüye döner"""
        self.master.destroy()
        # Ana menüyü başlat
        import game_launcher
        root = tk.Tk()
        game_launcher.GameLauncher(root)
        root.mainloop()
    
    def update_status(self):
        """Durum etiketini günceller"""
        if not self.game_over:
            self.status_label.config(text=f"Sıra: {self.current_player}")
            self.set_board_enabled(True)
    
    def start_timer(self):
        """Zaman modunda timer'ı başlatır"""
        if not self.time_mode:
            return
        
        self.time_remaining = self.base_time_per_turn + self.bonus_time
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Timer'ı günceller"""
        if not self.timer_running or not self.time_mode:
            return
        
        if self.time_remaining > 0:
            if self.timer_label:
                self.timer_label.config(text=f"Süre: {self.time_remaining} saniye")
            self.time_remaining -= 1
            self.master.after(1000, self.update_timer)
        else:
            # Süre doldu
            self.timer_running = False
            if self.timer_label:
                self.timer_label.config(text="Süre Doldu!", fg='red')
            messagebox.showwarning("Süre Doldu", f"{self.current_player} oyuncusunun süresi doldu!")
            # Sıra değiş
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            self.update_status()
            if self.timer_running:
                self.start_timer()
    
    def on_move_made(self, r, c, player_char=None):
        """Alt sınıflar tarafından override edilecek hamle işleme metodu
        player_char: Hamleyi yapan oyuncunun karakteri (X veya O)
        """
        pass

