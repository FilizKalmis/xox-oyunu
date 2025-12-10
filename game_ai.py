"""
XOX Oyunu - Bilgisayara Karşı Modu
Kullanıcı bilgisayara karşı oynar
"""
import tkinter as tk
import random
from game_base import BaseGame

class AIGame(BaseGame):
    """AI modu - kullanıcı bilgisayara karşı oynar"""
    
    def __init__(self, master, time_mode=False):
        super().__init__(master, time_mode)
        master.title("XOX Oyunu - Bilgisayara Karşı")
        self.player_char = 'X'
        self.ai_char = 'O'
        self._create_widgets()
        self.update_status()
        if self.time_mode:
            self.start_timer()
    
    def on_move_made(self, r, c, player_char=None):
        """Kullanıcı hamle yaptıktan sonra AI hamle yapar"""
        if self.time_mode and not self.game_over:
            self.start_timer()
        
        # Eğer oyun bitmediyse ve sıra AI'da ise
        if not self.game_over and self.current_player == self.ai_char:
            self.master.after(500, self.ai_move)  # 0.5 saniye bekle
    
    def ai_move(self):
        """AI hamle yapar"""
        if self.game_over:
            return
        
        # Önce kazanma hamlesi var mı kontrol et
        move = self.find_winning_move(self.ai_char)
        if move is None:
            # Sonra rakibin kazanmasını engelle
            move = self.find_winning_move(self.player_char)
        if move is None:
            # Merkezi al
            if self.game_board[1][1] == ' ':
                move = (1, 1)
            else:
                # Rastgele boş kare seç
                move = self.find_random_move()
        
        if move:
            r, c = move
            self.update_board(r, c, self.ai_char)
            
            # Zaman modunda bonus süre ekle
            if self.time_mode and self.timer_running:
                self.time_remaining += self.bonus_time
                if self.timer_label:
                    self.timer_label.config(text=f"Süre: {self.time_remaining} saniye (+{self.bonus_time} bonus)")
            
            self.current_player = self.player_char
            self.update_status()
            if self.time_mode:
                self.start_timer()
    
    def find_winning_move(self, char):
        """Belirli bir karakter için kazanma hamlesi bulur"""
        board = self.game_board
        
        # Tüm boş kareleri kontrol et
        for r in range(3):
            for c in range(3):
                if board[r][c] == ' ':
                    # Bu hamleyi yap ve kazanma kontrolü yap
                    board[r][c] = char
                    winner = self.check_winner()
                    board[r][c] = ' '  # Geri al
                    if winner == char:
                        return (r, c)
        return None
    
    def find_random_move(self):
        """Rastgele boş kare bulur"""
        empty_cells = [(r, c) for r in range(3) for c in range(3) 
                      if self.game_board[r][c] == ' ']
        if empty_cells:
            return random.choice(empty_cells)
        return None

