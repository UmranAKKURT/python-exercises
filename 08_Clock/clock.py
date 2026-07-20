import customtkinter as ctk
from tkinter import filedialog
import datetime
import time
import winsound
import threading

# Tema ve Görünüm Ayarları
ctk.set_appearance_mode("dark")  # Karanlık mod
ctk.set_default_color_theme("blue")  # Varsayılan vurgu rengi

# Arka plan işlemlerini ve alarmı kontrol etmek için bayrak
stop_alarm_event = threading.Event()
selected_sound_path = None


# --- Canlı Dijital Saat Fonksiyonu ---
def update_live_clock():
    # Anlık saati al
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    live_clock_label.configure(text=now_str)
    # Arayüzü dondurmadan 200 ms'de bir kendini tekrar çalıştır
    root.after(200, update_live_clock)


# --- Müzik Seçme Fonksiyonu ---
def choose_sound_file():
    global selected_sound_path
    filepath = filedialog.askopenfilename(
        title="Alarm Sesi Seçin",
        filetypes=[("WAV Dosyaları", "*.wav"), ("Tüm Dosyalar", "*.*")]
    )
    if filepath:
        selected_sound_path = filepath
        # Dosya adını kesip ekranda göster
        file_name = filepath.split("/")[-1]
        sound_label.configure(text=f"Seçilen Ses: {file_name[:20]}...", text_color="#2FA572")


# --- Alarm İşlemleri ---
def start_alarm_thread():
    if hasattr(root, 'alarm_thread') and root.alarm_thread.is_alive():
        status_label.configure(text="Alarm zaten kurulu!", text_color="#F39C12")
        return

    stop_alarm_event.clear()
    btn_cancel.configure(state="normal")
    btn_snooze.configure(state="disabled")

    target_time = f"{hour_var.get()}:{minute_var.get()}:{second_var.get()}"
    root.alarm_thread = threading.Thread(target=check_alarm, args=(target_time,), daemon=True)
    root.alarm_thread.start()


def check_alarm(target_time):
    status_label.configure(text=f"Alarm kuruldu: {target_time}", text_color="#2FA572")

    while not stop_alarm_event.is_set():
        time.sleep(0.5)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        if current_time == target_time:
            if stop_alarm_event.is_set():
                break

            status_label.configure(text="⏰ Uyanma Vakti! ⏰", text_color="#E74C3C")
            btn_snooze.configure(state="normal")

            try:
                # Özel ses seçilmişse onu, yoksa default çalar
                sound_to_play = selected_sound_path if selected_sound_path else "sound.wav"
                winsound.PlaySound(sound_to_play, winsound.SND_ASYNC | winsound.SND_LOOP)
            except Exception:
                # Ses bulunamazsa bip sesi
                for _ in range(10):
                    if stop_alarm_event.is_set(): break
                    winsound.Beep(1000, 800)
                    time.sleep(0.3)
            break


def cancel_alarm():
    stop_alarm_event.set()
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)  # Çalan sesi sustur
    except:
        pass
    status_label.configure(text="Alarm İptal Edildi.", text_color="gray")
    btn_cancel.configure(state="disabled")
    btn_snooze.configure(state="disabled")


def snooze_alarm():
    cancel_alarm()
    now = datetime.datetime.now()
    snooze_time = now + datetime.timedelta(minutes=5)  # Saate 5 dk ekle

    # Menüleri yeni saate göre ayarla
    hour_var.set(snooze_time.strftime("%H"))
    minute_var.set(snooze_time.strftime("%M"))
    second_var.set(snooze_time.strftime("%S"))

    start_alarm_thread()


# ==========================================
# --- ARAYÜZ (GUI) KURULUMU (CustomTkinter) ---
# ==========================================
root = ctk.CTk()
root.title("Modern Çalar Saat")
root.geometry("450x460")
root.resizable(False, False)

# 1. CANLI DİJİTAL SAAT PANELİ
live_clock_frame = ctk.CTkFrame(root, corner_radius=15, fg_color="#1E1E1E")
live_clock_frame.pack(fill="x", padx=30, pady=25)

live_clock_label = ctk.CTkLabel(
    live_clock_frame,
    text="00:00:00",
    font=("Consolas", 46, "bold"),
    text_color="#00FFCC"
)
live_clock_label.pack(pady=15)

# 2. ALARM KURMA MENÜLERİ (Saat : Dakika : Saniye)
time_frame = ctk.CTkFrame(root, fg_color="transparent")
time_frame.pack(pady=10)

hours_list = [f"{i:02d}" for i in range(24)]
mins_secs_list = [f"{i:02d}" for i in range(60)]

hour_var = ctk.StringVar(value=hours_list[0])
minute_var = ctk.StringVar(value=mins_secs_list[0])
second_var = ctk.StringVar(value=mins_secs_list[0])

ctk.CTkComboBox(time_frame, values=hours_list, variable=hour_var, width=80, font=("Helvetica", 14)).pack(side="left",
                                                                                                         padx=10)
ctk.CTkLabel(time_frame, text=":", font=("Helvetica", 18, "bold")).pack(side="left")
ctk.CTkComboBox(time_frame, values=mins_secs_list, variable=minute_var, width=80, font=("Helvetica", 14)).pack(
    side="left", padx=10)
ctk.CTkLabel(time_frame, text=":", font=("Helvetica", 18, "bold")).pack(side="left")
ctk.CTkComboBox(time_frame, values=mins_secs_list, variable=second_var, width=80, font=("Helvetica", 14)).pack(
    side="left", padx=10)

# 3. MÜZİK SEÇME ALANI
sound_frame = ctk.CTkFrame(root, fg_color="transparent")
sound_frame.pack(pady=15)

ctk.CTkButton(sound_frame, text="🎵 Ses Dosyası Seç (.wav)", command=choose_sound_file, width=200, fg_color="#4B4B4B",
              hover_color="#333333").pack()
sound_label = ctk.CTkLabel(sound_frame, text="Varsayılan ses ayarlı", text_color="gray", font=("Helvetica", 12))
sound_label.pack(pady=5)

# 4. KONTROL BUTONLARI (Kur, İptal, Ertele)
btn_frame = ctk.CTkFrame(root, fg_color="transparent")
btn_frame.pack(pady=15)

ctk.CTkButton(btn_frame, text="Alarmı Kur", font=("Helvetica", 13, "bold"), command=start_alarm_thread, width=100,
              fg_color="#27AE60", hover_color="#1E8449").grid(row=0, column=0, padx=8)
btn_cancel = ctk.CTkButton(btn_frame, text="İptal Et", font=("Helvetica", 13, "bold"), command=cancel_alarm, width=100,
                           fg_color="#E74C3C", hover_color="#C0392B", state="disabled")
btn_cancel.grid(row=0, column=1, padx=8)
btn_snooze = ctk.CTkButton(btn_frame, text="Ertele (+5)", font=("Helvetica", 13, "bold"), command=snooze_alarm,
                           width=100, fg_color="#2980B9", hover_color="#1A5276", state="disabled")
btn_snooze.grid(row=0, column=2, padx=8)

# 5. DURUM BİLGİSİ ETİKETİ
status_label = ctk.CTkLabel(root, text="Lütfen bir saat seçin", font=("Helvetica", 13))
status_label.pack(pady=10)

# Uygulama başlarken canlı saati tetikle
update_live_clock()

# Döngüyü başlat
root.mainloop()