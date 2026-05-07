
    #import datetime ve import pytz
    #def dosyaya_yaz():
    #  with open("hesap_geçmişi.txt","a") as dosya:
    #    lokal=pytz.timezone("Europe/İstanbul")
    #    zaman=datetime.datetime.now(lokal).strftime("%Y-%m-%d %H-%M-%S")
    #    dosya.write(f"{zaman}---{x}{operator} {y}={sonuc}\n")
    #bunu da yazdıktan sonra her seçimin altına :
    #dosyaya_yaz(sayi1,sayi2,sonuc,"+")

    # def dosyadan_oku():
    #try:
    #   with open("hesap_geçmişi.txt","r") as dosya:
    #   gecmiş=dosya.read()
    #   print("----Dosya geçmişi----")
    #   print(gecmiş)
    #   print("---------------------")
    #except fileNoFoundError:
    #   print("hesap geçmişi bulunamadı.")
    #elif secim=="5":
    #dosyadan_oku()
# Görevlerin tutulduğu liste
gorevler = []

# Kullanılan dosya adı
DOSYA_ADI = "gorevler.txt"


# ------------------------------------------------
# DOSYADAN GÖREVLERİ OKUYUP LİSTEYE AKTARMA
# ------------------------------------------------
def gorevleri_yukle():
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            for satir in f:
                gorevler.append(satir.strip())   # her satırı listeye ekle
    except FileNotFoundError:
        pass  # dosya yoksa hiç hata verme, boş listeyle devam et


# ------------------------------------------------
# GÖREVLERİ DOSYAYA YAZMA
# ------------------------------------------------
def gorevleri_kaydet():
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        for g in gorevler:
            f.write(g + "\n")


# ------------------------------------------------
# GÖREVLERİ LİSTELEME (LISTE + FOR)
# ------------------------------------------------
def gorevleri_listele():
    print("\n--- GÖREVLER ---")
    if len(gorevler) == 0:
        print("Görev yok.\n")
        return

    for i, g in enumerate(gorevler, start=1):
        print(f"{i}. {g}")

    print()


# ------------------------------------------------
# YENİ GÖREV EKLEME (APPEND)
# ------------------------------------------------
def gorev_ekle():
    yeni = input("Yeni görev: ")
    gorevler.append(yeni)
    gorevleri_kaydet()
    print("Görev eklendi!\n")


# ------------------------------------------------
# GÖREV DÜZENLEME
# ------------------------------------------------
def gorev_duzenle():
    gorevleri_listele()

    try:
        sec = int(input("Düzenlemek istediğin görev numarası: "))
        if 1 <= sec <= len(gorevler):
            yeni_metin = input("Yeni görev metni: ")
            gorevler[sec - 1] = yeni_metin
            gorevleri_kaydet()
            print("Görev düzenlendi!\n")
        else:
            print("Geçersiz görev numarası!\n")
    except:
        print("Hatalı giriş!\n")


# ------------------------------------------------
# GÖREV SİLME
# ------------------------------------------------
def gorev_sil():
    gorevleri_listele()

    try:
        sec = int(input("Silmek istediğin görev numarası: "))
        if 1 <= sec <= len(gorevler):
            silinen = gorevler.pop(sec - 1)
            gorevleri_kaydet()
            print(f"'{silinen}' görevi silindi!\n")
        else:
            print("Geçersiz görev numarası!\n")
    except:
        print("Hatalı giriş!\n")


# ------------------------------------------------
# DOSYA GEÇMİŞİNİ OKUMA (SENİN İSTEDİĞİN FORMAT)
# ------------------------------------------------
def dosya_gecmisini_goster():
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            gecmis = dosya.read()
            print("---- Dosya Geçmişi ----")
            print(gecmis)
            print("-----------------------")
    except FileNotFoundError:
        print("Dosya geçmişi bulunamadı.")


def menu():
    gorevleri_yukle()
while True:
print("""*******************

To-Do List Uygulaması

İşlemler ;

1. Görevleri Listele

2. Yeni Görev Ekle

3. Görev Düzenle

4. Görev Sil

5. Çıkış

*******************""")

    işlem = input("İşlemi Seçiniz(1-5):")
    if (işlem == "5"):
        print("Programdan Çıkılıyor...")
        break
    if (işlem == "1"):
        gorevleri_listele()
    elif (işlem == "2"):
        gorev_ekle()
    elif (işlem == "3"):
        gorev_duzenle()
    elif (işlem == "4"):
        gorev_sil()
    else:
        print("Geçersiz İşlem...\n")
menu()










