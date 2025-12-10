"""
Test Script: Network modunu localhost üzerinden test etmek için
Sunucu + 2 client penceresi açar
"""
import subprocess
import sys
import time
import tkinter as tk
import game_network

def main():
    print("=" * 50)
    print("TEST MODU: Network Oyunu (Localhost)")
    print("=" * 50)
    
    # Sunucuyu başlat
    print("\n[1/3] Sunucu başlatılıyor...")
    server_process = subprocess.Popen(
        [sys.executable, "server_gui.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    # Sunucunun başlaması için bekle
    print("[2/3] Sunucu başlatılıyor, lütfen bekleyin...")
    time.sleep(2)
    
    # İki client penceresi aç
    print("[3/3] İki oyuncu penceresi açılıyor...")
    
    # İlk client (X oyuncusu)
    def start_client_1():
        root1 = tk.Tk()
        root1.title("Oyuncu 1 (X) - Test Modu")
        game_network.NetworkGame(root1, time_mode=False, auto_connect_ip='127.0.0.1')
        root1.mainloop()
    
    # İkinci client (O oyuncusu)
    def start_client_2():
        time.sleep(1)  # İlk client'ın bağlanması için bekle
        root2 = tk.Tk()
        root2.title("Oyuncu 2 (O) - Test Modu")
        game_network.NetworkGame(root2, time_mode=False, auto_connect_ip='127.0.0.1')
        root2.mainloop()
    
    import threading
    
    # İlk client'ı başlat
    thread1 = threading.Thread(target=start_client_1, daemon=True)
    thread1.start()
    
    # İkinci client'ı başlat
    thread2 = threading.Thread(target=start_client_2, daemon=True)
    thread2.start()
    
    print("\n✓ Test modu başlatıldı!")
    print("  - Sunucu penceresi açıldı")
    print("  - 2 oyuncu penceresi açıldı")
    print("  - Her iki oyuncu da localhost'a bağlanacak")
    print("\nİyi oyunlar! 🎮")
    
    # Ana thread'i canlı tut
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nTest modu kapatılıyor...")
        server_process.terminate()

if __name__ == '__main__':
    main()

