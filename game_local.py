"""
XOX Oyunu - Aynı Bilgisayar Modu
İki oyuncu aynı bilgisayarda karşılıklı oynar
"""
import tkinter as tk
from game_base import BaseGame

class LocalGame(BaseGame):
    """Aynı bilgisayar modu - iki oyuncu sırayla oynar"""
    
    def __init__(self, master, time_mode=False):
        super().__init__(master, time_mode)
        master.title("XOX Oyunu - Aynı Bilgisayar")
        self._create_widgets()
        self.update_status()
        if self.time_mode:
            self.start_timer()
    
    def on_move_made(self, r, c):
        """Hamle yapıldıktan sonra timer'ı yeniden başlat"""
        if self.time_mode and not self.game_over:
            self.start_timer()

