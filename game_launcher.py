"""
XOX Oyunu - Ana Başlatıcı
Oyun modu seçimi için menü sağlar.
"""
import tkinter as tk
from tkinter import messagebox
import game_local
import game_ai
import game_network

class GameLauncher:
    """Oyun modu seçimi için ana menü"""
    
    def __init__(self, master):
        self.master = master
        master.title("XOX Oyunu - Mod Seçimi")
        master.geometry("400x300")
        master.resizable(False, False)
        
        # Başlık
        title_label = tk.Label(master, text="XOX OYUNU", font=('Arial', 20, 'bold'))
        title_label.pack(pady=20)
        
        # Mod seçim butonları
        button_frame = tk.Frame(master)
        button_frame.pack(pady=20)
        
        # 1. Aynı Bilgisayar Modu
        btn_local = tk.Button(button_frame, text="Aynı Bilgisayardan Karşılıklı", 
                              font=('Arial', 12), width=30, height=2,
                              command=self.start_local_game)
        btn_local.pack(pady=5)
        
        # 2. Bilgisayara Karşı
        btn_ai = tk.Button(button_frame, text="Bilgisayara Karşı", 
                          font=('Arial', 12), width=30, height=2,
                          command=self.start_ai_game)
        btn_ai.pack(pady=5)
        
        # 3. Network Modu
        btn_network = tk.Button(button_frame, text="Network Üzerinden Karşılıklı", 
                                font=('Arial', 12), width=30, height=2,
                                command=self.start_network_game)
        btn_network.pack(pady=5)
        
        # Zaman Modu checkbox
        self.time_mode_var = tk.BooleanVar()
        time_check = tk.Checkbutton(master, text="Zaman Modu (10 saniye bonus)", 
                                    variable=self.time_mode_var, font=('Arial', 10))
        time_check.pack(pady=10)
        
        # Bilgi etiketi
        info_label = tk.Label(master, text="Zaman modu: Her hamle için 10 saniye ek süre verilir", 
                             font=('Arial', 8), fg='gray')
        info_label.pack(pady=5)
    
    def start_local_game(self):
        """Aynı bilgisayar modunu başlat"""
        self.master.destroy()
        root = tk.Tk()
        game_local.LocalGame(root, self.time_mode_var.get())
        root.mainloop()
    
    def start_ai_game(self):
        """AI modunu başlat"""
        self.master.destroy()
        root = tk.Tk()
        game_ai.AIGame(root, self.time_mode_var.get())
        root.mainloop()
    
    def start_network_game(self):
        """Network modunu başlat"""
        self.master.destroy()
        root = tk.Tk()
        game_network.NetworkGame(root, self.time_mode_var.get())
        root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()

