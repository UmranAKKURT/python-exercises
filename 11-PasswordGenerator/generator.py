import math
import secrets
import string
import tkinter as tk
from tkinter import messagebox, ttk


class SifreOlusturucuUygulamasi:
    def __init__(self, pencere):
        self.pencere = pencere

        self.pencere.title("Güçlü Şifre Oluşturucu")
        self.pencere.geometry("480x610")
        self.pencere.resizable(False, False)

        # Uygulama değişkenleri
        self.uzunluk = tk.IntVar(value=16)

        self.kucuk_harf = tk.BooleanVar(value=True)
        self.buyuk_harf = tk.BooleanVar(value=True)
        self.rakam = tk.BooleanVar(value=True)
        self.ozel_karakter = tk.BooleanVar(value=True)

        self.benzer_karakterleri_cikar = tk.BooleanVar(value=False)
        self.sifreyi_goster = tk.BooleanVar(value=False)

        self.sifre = tk.StringVar()
        self.guc_metni = tk.StringVar(value="Henüz şifre oluşturulmadı")
        self.durum_metni = tk.StringVar(value="Hazır")

        self.stil_ayarla()
        self.arayuzu_olustur()

        # Enter tuşuna basıldığında şifre oluşturur.
        self.pencere.bind("<Return>", lambda event: self.sifre_olustur())

    def stil_ayarla(self):
        """Uygulamanın görsel stillerini ayarlar."""

        self.stil = ttk.Style()

        try:
            self.stil.theme_use("clam")
        except tk.TclError:
            pass

        self.stil.configure(
            "Baslik.TLabel",
            font=("Segoe UI", 20, "bold")
        )

        self.stil.configure(
            "AltBaslik.TLabel",
            font=("Segoe UI", 10)
        )

        self.stil.configure(
            "Bolum.TLabel",
            font=("Segoe UI", 11, "bold")
        )

        self.stil.configure(
            "Normal.TLabel",
            font=("Segoe UI", 10)
        )

        self.stil.configure(
            "Secenek.TCheckbutton",
            font=("Segoe UI", 10)
        )

        self.stil.configure(
            "Olustur.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=10
        )

        self.stil.configure(
            "Islem.TButton",
            font=("Segoe UI", 10),
            padding=7
        )

        self.stil.configure(
            "Weak.Horizontal.TProgressbar",
            background="#e74c3c"
        )

        self.stil.configure(
            "Medium.Horizontal.TProgressbar",
            background="#f39c12"
        )

        self.stil.configure(
            "Strong.Horizontal.TProgressbar",
            background="#2ecc71"
        )

        self.stil.configure(
            "VeryStrong.Horizontal.TProgressbar",
            background="#1abc9c"
        )

    def arayuzu_olustur(self):
        """Uygulama arayüzünü oluşturur."""

        ana_cerceve = ttk.Frame(self.pencere, padding=25)
        ana_cerceve.pack(fill="both", expand=True)

        # Başlık
        ttk.Label(
            ana_cerceve,
            text="Güçlü Şifre Oluşturucu",
            style="Baslik.TLabel"
        ).pack()

        ttk.Label(
            ana_cerceve,
            text="Güvenli ve özelleştirilebilir şifreler oluşturun.",
            style="AltBaslik.TLabel"
        ).pack(pady=(3, 20))

        # Şifre uzunluğu alanı
        uzunluk_cercevesi = ttk.LabelFrame(
            ana_cerceve,
            text="Şifre uzunluğu",
            padding=12
        )
        uzunluk_cercevesi.pack(fill="x", pady=(0, 12))

        ttk.Label(
            uzunluk_cercevesi,
            text="Karakter sayısı:",
            style="Normal.TLabel"
        ).pack(side="left")

        self.uzunluk_spinbox = ttk.Spinbox(
            uzunluk_cercevesi,
            from_=4,
            to=128,
            textvariable=self.uzunluk,
            width=8,
            justify="center"
        )
        self.uzunluk_spinbox.pack(side="right")

        # Karakter seçenekleri
        secenekler_cercevesi = ttk.LabelFrame(
            ana_cerceve,
            text="Karakter seçenekleri",
            padding=12
        )
        secenekler_cercevesi.pack(fill="x", pady=(0, 12))

        ttk.Checkbutton(
            secenekler_cercevesi,
            text="Küçük harfler (a-z)",
            variable=self.kucuk_harf,
            style="Secenek.TCheckbutton"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=4)

        ttk.Checkbutton(
            secenekler_cercevesi,
            text="Büyük harfler (A-Z)",
            variable=self.buyuk_harf,
            style="Secenek.TCheckbutton"
        ).grid(row=0, column=1, sticky="w", padx=15, pady=4)

        ttk.Checkbutton(
            secenekler_cercevesi,
            text="Rakamlar (0-9)",
            variable=self.rakam,
            style="Secenek.TCheckbutton"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=4)

        ttk.Checkbutton(
            secenekler_cercevesi,
            text="Özel karakterler (!@#)",
            variable=self.ozel_karakter,
            style="Secenek.TCheckbutton"
        ).grid(row=1, column=1, sticky="w", padx=15, pady=4)

        ttk.Separator(
            secenekler_cercevesi,
            orient="horizontal"
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=8
        )

        ttk.Checkbutton(
            secenekler_cercevesi,
            text="Benzer karakterleri çıkar: 0, O, 1, I, l",
            variable=self.benzer_karakterleri_cikar,
            style="Secenek.TCheckbutton"
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            padx=5,
            pady=4
        )

        # Şifre oluştur butonu
        ttk.Button(
            ana_cerceve,
            text="🔐 Şifre Oluştur",
            command=self.sifre_olustur,
            style="Olustur.TButton"
        ).pack(fill="x", pady=(3, 15))

        # Sonuç bölümü
        sonuc_cercevesi = ttk.LabelFrame(
            ana_cerceve,
            text="Oluşturulan şifre",
            padding=12
        )
        sonuc_cercevesi.pack(fill="x")

        self.sifre_girdisi = ttk.Entry(
            sonuc_cercevesi,
            textvariable=self.sifre,
            font=("Consolas", 14),
            justify="center",
            show="●"
        )
        self.sifre_girdisi.pack(fill="x", pady=(0, 10), ipady=6)

        ttk.Checkbutton(
            sonuc_cercevesi,
            text="Şifreyi göster",
            variable=self.sifreyi_goster,
            command=self.sifre_gorunurlugunu_degistir,
            style="Secenek.TCheckbutton"
        ).pack(anchor="w")

        # Şifre gücü
        guc_cercevesi = ttk.Frame(sonuc_cercevesi)
        guc_cercevesi.pack(fill="x", pady=(12, 5))

        ttk.Label(
            guc_cercevesi,
            text="Şifre gücü:",
            style="Normal.TLabel"
        ).pack(side="left")

        self.guc_etiketi = ttk.Label(
            guc_cercevesi,
            textvariable=self.guc_metni,
            style="Normal.TLabel"
        )
        self.guc_etiketi.pack(side="right")

        self.guc_cubugu = ttk.Progressbar(
            sonuc_cercevesi,
            maximum=100,
            value=0,
            style="Weak.Horizontal.TProgressbar"
        )
        self.guc_cubugu.pack(fill="x", pady=(2, 12))

        # Kopyalama ve temizleme butonları
        buton_cercevesi = ttk.Frame(sonuc_cercevesi)
        buton_cercevesi.pack(fill="x")

        ttk.Button(
            buton_cercevesi,
            text="📋 Panoya Kopyala",
            command=self.panoya_kopyala,
            style="Islem.TButton"
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button(
            buton_cercevesi,
            text="🗑 Temizle",
            command=self.temizle,
            style="Islem.TButton"
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Durum çubuğu
        ttk.Separator(
            ana_cerceve,
            orient="horizontal"
        ).pack(fill="x", pady=(18, 8))

        self.durum_etiketi = ttk.Label(
            ana_cerceve,
            textvariable=self.durum_metni,
            anchor="center",
            style="AltBaslik.TLabel"
        )
        self.durum_etiketi.pack(fill="x")

    def karakter_gruplarini_al(self):
        """Kullanıcının seçtiği karakter gruplarını döndürür."""

        karakter_gruplari = []

        if self.kucuk_harf.get():
            karakter_gruplari.append(string.ascii_lowercase)

        if self.buyuk_harf.get():
            karakter_gruplari.append(string.ascii_uppercase)

        if self.rakam.get():
            karakter_gruplari.append(string.digits)

        if self.ozel_karakter.get():
            karakter_gruplari.append(string.punctuation)

        if self.benzer_karakterleri_cikar.get():
            benzer_karakterler = "0O1Il"

            karakter_gruplari = [
                "".join(
                    karakter
                    for karakter in grup
                    if karakter not in benzer_karakterler
                )
                for grup in karakter_gruplari
            ]

        # Boş kalan grupları kaldırır.
        return [grup for grup in karakter_gruplari if grup]

    def sifre_olustur(self):
        """Seçeneklere göre güvenli bir şifre oluşturur."""

        try:
            uzunluk = int(self.uzunluk.get())
        except (ValueError, tk.TclError):
            messagebox.showerror(
                "Geçersiz değer",
                "Şifre uzunluğu için geçerli bir sayı girin."
            )
            return

        if uzunluk < 4:
            messagebox.showwarning(
                "Geçersiz uzunluk",
                "Şifre uzunluğu en az 4 karakter olmalıdır."
            )
            return

        if uzunluk > 128:
            messagebox.showwarning(
                "Geçersiz uzunluk",
                "Şifre uzunluğu en fazla 128 karakter olabilir."
            )
            return

        karakter_gruplari = self.karakter_gruplarini_al()

        if not karakter_gruplari:
            messagebox.showwarning(
                "Karakter seçilmedi",
                "En az bir karakter türü seçmelisiniz."
            )
            return

        if uzunluk < len(karakter_gruplari):
            messagebox.showwarning(
                "Şifre çok kısa",
                "Seçilen tüm karakter türlerinin kullanılabilmesi için "
                f"şifre uzunluğu en az {len(karakter_gruplari)} olmalıdır."
            )
            return

        # Her seçili karakter grubundan en az bir karakter eklenir.
        sifre_karakterleri = [
            secrets.choice(grup)
            for grup in karakter_gruplari
        ]

        tum_karakterler = "".join(karakter_gruplari)

        # Geri kalan karakterler tüm havuzdan rastgele seçilir.
        kalan_karakter_sayisi = uzunluk - len(sifre_karakterleri)

        sifre_karakterleri.extend(
            secrets.choice(tum_karakterler)
            for _ in range(kalan_karakter_sayisi)
        )

        # Karakterlerin konumlarını güvenli biçimde karıştırır.
        secrets.SystemRandom().shuffle(sifre_karakterleri)

        yeni_sifre = "".join(sifre_karakterleri)

        self.sifre.set(yeni_sifre)
        self.sifre_gucunu_hesapla(yeni_sifre, len(tum_karakterler))
        self.durum_goster("Yeni şifre başarıyla oluşturuldu.")

        self.sifre_girdisi.focus_set()
        self.sifre_girdisi.selection_range(0, tk.END)

    def sifre_gucunu_hesapla(self, sifre, karakter_havuzu_boyutu):
        """Tahmini entropiye göre şifre gücünü gösterir."""

        if not sifre or karakter_havuzu_boyutu == 0:
            self.guc_cubugu["value"] = 0
            self.guc_metni.set("Henüz şifre oluşturulmadı")
            return

        entropi = len(sifre) * math.log2(karakter_havuzu_boyutu)

        if entropi < 35:
            puan = 25
            guc = "Zayıf"
            stil = "Weak.Horizontal.TProgressbar"

        elif entropi < 60:
            puan = 50
            guc = "Orta"
            stil = "Medium.Horizontal.TProgressbar"

        elif entropi < 90:
            puan = 75
            guc = "Güçlü"
            stil = "Strong.Horizontal.TProgressbar"

        else:
            puan = 100
            guc = "Çok güçlü"
            stil = "VeryStrong.Horizontal.TProgressbar"

        self.guc_cubugu.configure(
            value=puan,
            style=stil
        )

        self.guc_metni.set(
            f"{guc} — yaklaşık {entropi:.0f} bit"
        )

    def sifre_gorunurlugunu_degistir(self):
        """Şifrenin görünür veya gizli olmasını değiştirir."""

        if self.sifreyi_goster.get():
            self.sifre_girdisi.configure(show="")
        else:
            self.sifre_girdisi.configure(show="●")

    def panoya_kopyala(self):
        """Oluşturulan şifreyi panoya kopyalar."""

        uretilen_sifre = self.sifre.get()

        if not uretilen_sifre:
            messagebox.showwarning(
                "Şifre bulunamadı",
                "Önce bir şifre oluşturmalısınız."
            )
            return

        self.pencere.clipboard_clear()
        self.pencere.clipboard_append(uretilen_sifre)
        self.pencere.update_idletasks()

        self.durum_goster("Şifre panoya kopyalandı.")

    def temizle(self):
        """Şifre alanını ve güç göstergesini temizler."""

        self.sifre.set("")
        self.sifreyi_goster.set(False)
        self.sifre_girdisi.configure(show="●")

        self.guc_cubugu.configure(
            value=0,
            style="Weak.Horizontal.TProgressbar"
        )

        self.guc_metni.set("Henüz şifre oluşturulmadı")
        self.durum_goster("Şifre alanı temizlendi.")

    def durum_goster(self, mesaj):
        """Alt bölümde geçici durum mesajı gösterir."""

        self.durum_metni.set(mesaj)

        # Önceki zamanlayıcı varsa iptal edilir.
        if hasattr(self, "durum_zamanlayicisi"):
            self.pencere.after_cancel(self.durum_zamanlayicisi)

        self.durum_zamanlayicisi = self.pencere.after(
            3000,
            lambda: self.durum_metni.set("Hazır")
        )


if __name__ == "__main__":
    pencere = tk.Tk()
    uygulama = SifreOlusturucuUygulamasi(pencere)
    pencere.mainloop()