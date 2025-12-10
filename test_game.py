"""
XOX Oyunu - Test Case'leri
3 adet test case içerir
"""
import unittest
from game_base import BaseGame
import tkinter as tk

class TestTicTacToe(unittest.TestCase):
    """XOX Oyunu için test case'leri"""
    
    def setUp(self):
        """Her test öncesi çalışır"""
        self.root = tk.Tk()
        self.root.withdraw()  # GUI'yi gizle
    
    def tearDown(self):
        """Her test sonrası çalışır"""
        self.root.destroy()
    
    def test_case_1_winner_detection(self):
        """
        Test Case 1: Kazanan Tespiti
        Amaç: Oyunun kazananı doğru şekilde tespit edip edemediğini kontrol eder.
        Senaryo: X oyuncusu yatay bir çizgi oluşturur.
        Beklenen: check_winner() metodu 'X' döndürmelidir.
        """
        game = BaseGame(self.root, time_mode=False)
        game._create_widgets()  # GUI bileşenlerini oluştur
        
        # X oyuncusu yatay çizgi oluşturur (ilk satır)
        game.game_board[0][0] = 'X'
        game.game_board[0][1] = 'X'
        game.game_board[0][2] = 'X'
        
        winner = game.check_winner()
        self.assertEqual(winner, 'X', "Test Case 1 Başarısız: X kazanmalıydı")
        print("✓ Test Case 1: Kazanan Tespiti - BAŞARILI")
    
    def test_case_2_draw_detection(self):
        """
        Test Case 2: Beraberlik Tespiti
        Amaç: Oyunun berabere bitip bitmediğini kontrol eder.
        Senaryo: Tüm kareler doldurulur ancak kimse kazanamaz.
        Beklenen: check_winner() metodu 'Berabere' döndürmelidir.
        """
        game = BaseGame(self.root, time_mode=False)
        game._create_widgets()  # GUI bileşenlerini oluştur
        
        # Beraberlik senaryosu
        # X O X
        # O O X
        # O X O
        game.game_board[0][0] = 'X'
        game.game_board[0][1] = 'O'
        game.game_board[0][2] = 'X'
        game.game_board[1][0] = 'O'
        game.game_board[1][1] = 'O'
        game.game_board[1][2] = 'X'
        game.game_board[2][0] = 'O'
        game.game_board[2][1] = 'X'
        game.game_board[2][2] = 'O'
        
        winner = game.check_winner()
        self.assertEqual(winner, 'Berabere', "Test Case 2 Başarısız: Berabere olmalıydı")
        print("✓ Test Case 2: Beraberlik Tespiti - BAŞARILI")
    
    def test_case_3_diagonal_win(self):
        """
        Test Case 3: Çapraz Kazanma
        Amaç: Çapraz kazanma durumunu kontrol eder.
        Senaryo: O oyuncusu sol üstten sağ alta çapraz çizgi oluşturur.
        Beklenen: check_winner() metodu 'O' döndürmelidir.
        """
        game = BaseGame(self.root, time_mode=False)
        game._create_widgets()  # GUI bileşenlerini oluştur
        
        # O oyuncusu çapraz çizgi oluşturur (sol üstten sağ alta)
        game.game_board[0][0] = 'O'
        game.game_board[1][1] = 'O'
        game.game_board[2][2] = 'O'
        
        winner = game.check_winner()
        self.assertEqual(winner, 'O', "Test Case 3 Başarısız: O kazanmalıydı")
        print("✓ Test Case 3: Çapraz Kazanma - BAŞARILI")

if __name__ == '__main__':
    print("=" * 50)
    print("XOX OYUNU TEST CASE'LERİ")
    print("=" * 50)
    unittest.main(verbosity=2)

