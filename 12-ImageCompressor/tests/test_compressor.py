import os
import sys
import unittest
from PIL import Image

# src klasöründeki modülleri import edebilmek için ana dizini yola ekliyoruz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.compressor import ImageCompressor


class TestImageCompressor(unittest.TestCase):

    def setUp(self):
        """Her testten önce çalışıp hazırlık yapar."""
        self.compressor = ImageCompressor()
        self.test_input_img = "test_input.jpg"
        self.test_output_img = "test_output.jpg"

        # Testler için bellekte basit bir kırmızı kare çizip test görseli olarak kaydediyoruz
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_input_img)

    def tearDown(self):
        """Her testten sonra çalışıp oluşturulan çöp (dummy) dosyaları siler."""
        if os.path.exists(self.test_input_img):
            os.remove(self.test_input_img)
        if os.path.exists(self.test_output_img):
            os.remove(self.test_output_img)

    def test_format_size(self):
        """Boyut formatlama fonksiyonunun doğruluğunu test eder."""
        # 512 Byte -> KB kontrolü
        self.assertEqual(ImageCompressor.format_size(512), "0.50 KB")
        # 1.5 MB -> MB kontrolü (1.5 * 1024 * 1024)
        self.assertEqual(ImageCompressor.format_size(1572864), "1.50 MB")

    def test_compression_ratio(self):
        """Sıkıştırma oranı (yüzde) matematiğini test eder."""
        # %50 sıkıştırma testi
        self.assertEqual(ImageCompressor.compression_ratio(100, 50), 50.0)
        # Orijinal boyut 0 gelirse 0 dönmeli (Sıfıra bölünme hatasını engelleme)
        self.assertEqual(ImageCompressor.compression_ratio(0, 50), 0)

    def test_compress_function(self):
        """Gerçek bir dosyanın sıkıştırılıp kaydedildiğini test eder."""
        result = self.compressor.compress(self.test_input_img, self.test_output_img, quality=50)

        # Çıktı dosyası başarıyla oluşturulmuş mu?
        self.assertTrue(os.path.exists(self.test_output_img))

        # Result sözlüğünde orijinal ve yeni boyut bilgileri var mı?
        self.assertIn("original_size", result)
        self.assertIn("compressed_size", result)

        # Yeni dosya orijinalden daha küçük veya eşit mi?
        self.assertLessEqual(result["compressed_size"], result["original_size"])


if __name__ == "__main__":
    unittest.main()