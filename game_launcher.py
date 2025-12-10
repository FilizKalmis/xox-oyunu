"""
XOX Oyunu - Ana Başlatıcı
Oyun modu seçimi için menü sağlar.
"""
import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
import sys
import os
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
        
        # 4. Test Modu (Aynı bilgisayarda 2 pencere ile test)
        btn_test = tk.Button(button_frame, text="🧪 Test Modu (2 Pencere - Localhost)", 
                            font=('Arial', 11), width=30, height=2,
                            command=self.start_test_mode, bg="#e8f5e9", fg="#2e7d32")
        btn_test.pack(pady=5)
        
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
    
    def start_test_mode(self):
        """Test modu: Sunucu + 2 client penceresi açar (localhost)"""
        response = messagebox.askyesno(
            "Test Modu",
            "Test modu başlatılacak:\n\n"
            "✓ Sunucu otomatik başlatılacak\n"
            "✓ 2 oyuncu penceresi açılacak (localhost)\n"
            "✓ Her iki pencere de otomatik bağlanacak\n\n"
            "Devam etmek istiyor musunuz?"
        )
        
        if not response:
            return
        
        # Ana menüyü kapat
        self.master.destroy()
        
        # Sunucuyu ayrı bir process'te başlat
        try:
            # Sunucuyu başlat (ayrı Python process)
            server_process = subprocess.Popen(
                [sys.executable, "server_gui.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            # Kısa bir gecikme (sunucunun başlaması için)
            import time
            time.sleep(2)
            
            # İki client penceresi aç
            time_mode = self.time_mode_var.get()
            
            # İlk client (X oyuncusu olacak)
            def start_client_1():
                root1 = tk.Tk()
                # IP'yi otomatik olarak 127.0.0.1 yap (auto_connect_ip parametresi ile)
                game_network.NetworkGame(root1, time_mode, auto_connect_ip='127.0.0.1')
                root1.mainloop()
            
            # İkinci client (O oyuncusu olacak)
            def start_client_2():
                # İlk client'ın bağlanması için biraz bekle
                time.sleep(1)
                root2 = tk.Tk()
                # IP'yi otomatik olarak 127.0.0.1 yap
                game_network.NetworkGame(root2, time_mode, auto_connect_ip='127.0.0.1')
                root2.mainloop()
            
            # İlk client'ı başlat (ayrı thread'de)
            thread1 = threading.Thread(target=start_client_1, daemon=True)
            thread1.start()
            
            # İkinci client'ı biraz sonra başlat (ayrı thread'de)
            thread2 = threading.Thread(target=start_client_2, daemon=True)
            thread2.start()
            
            # Ana thread'i canlı tut (GUI'ler thread'lerde çalışıyor)
            import time
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            messagebox.showerror("Hata", f"Test modu başlatılamadı:\n{e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()

