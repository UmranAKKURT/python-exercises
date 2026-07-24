import tkinter as tk
from tkinter import messagebox, font
from itertools import cycle
from random import randrange, random
import os

try:
    import pygame

    pygame.mixer.init()
    AUDIO_ENABLED = True
except ImportError:
    AUDIO_ENABLED = False

# --- OYUN AYARLARI ---
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 400
EGG_WIDTH = 45
EGG_HEIGHT = 55
INITIAL_EGG_SPEED = 500
INITIAL_EGG_INTERVAL = 4000
DIFFICULTY_MULTIPLIER = 0.95
LEVEL_UP_THRESHOLD = 50
CATCHER_COLOR = "blue"
CATCHER_WIDTH = 100
CATCHER_HEIGHT = 100
CATCHER_SPEED = 20


class EggCatcherGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Yumurta Yakalama Oyunu - Özel Nesneler")
        self.root.resizable(False, False)

        self.score = 0
        self.level = 1
        self.lives_remaining = 3
        self.egg_speed = INITIAL_EGG_SPEED
        self.egg_interval = INITIAL_EGG_INTERVAL
        self.eggs = {}  # Sözlük yapısı: {egg_id: egg_type}
        self.is_game_over = False
        self.color_cycle = cycle(["light blue", "light green", "light pink", "light yellow", "light cyan"])

        self._load_sounds()
        self._setup_ui()

        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.canvas.focus_set()

        self._start_game_loops()

    def _load_sounds(self):
        self.sounds = {}
        if not AUDIO_ENABLED: return

        sound_files = {
            "catch": "catch.wav",
            "drop": "drop.wav",
            "gold": "gold.wav",  # Altın yumurta sesi
            "bomb": "bomb.wav",  # Bomba patlama sesi
            "levelup": "levelup.wav",
            "gameover": "gameover.wav"
        }

        for name, filename in sound_files.items():
            if os.path.exists(filename):
                self.sounds[name] = pygame.mixer.Sound(filename)
            else:
                self.sounds[name] = None

    def play_sound(self, sound_name):
        if AUDIO_ENABLED and self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def _setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background="deep sky blue")
        self.canvas.pack()

        self.canvas.create_rectangle(-5, CANVAS_HEIGHT - 100, CANVAS_WIDTH + 5, CANVAS_HEIGHT + 5, fill="sea green",
                                     width=0)
        self.canvas.create_oval(-80, -80, 120, 120, fill='orange', width=0)

        catcher_start_x = (CANVAS_WIDTH - CATCHER_WIDTH) / 2
        catcher_start_y = CANVAS_HEIGHT - CATCHER_HEIGHT - 20
        self.catcher = self.canvas.create_arc(
            catcher_start_x, catcher_start_y,
            catcher_start_x + CATCHER_WIDTH, catcher_start_y + CATCHER_HEIGHT,
            start=200, extent=140, style="arc", outline=CATCHER_COLOR, width=3
        )

        game_font = font.nametofont("TkFixedFont")
        game_font.config(size=18)

        self.score_text = self.canvas.create_text(10, 10, anchor="nw", font=game_font, fill="darkblue",
                                                  text=f"Skor: {self.score}")
        self.lives_text = self.canvas.create_text(CANVAS_WIDTH - 10, 10, anchor="ne", font=game_font, fill="darkblue",
                                                  text=f"Can: {self.lives_remaining}")
        self.level_text = self.canvas.create_text(CANVAS_WIDTH / 2, 10, anchor="n", font=game_font, fill="darkred",
                                                  text=f"Seviye: {self.level}")

    def _start_game_loops(self):
        self.root.after(1000, self.create_egg)
        self.root.after(1000, self.move_eggs)
        self.root.after(1000, self.check_catch)

    def create_egg(self):
        if self.is_game_over: return

        x = randrange(10, CANVAS_WIDTH - EGG_WIDTH - 10)
        y = 40

        # Yumurta türünü şansa bağlı belirleyelim:
        # %15 İhtimalle Altın Yumurta, %15 İhtimalle Bomba, %70 Normal Yumurta
        chance = random()
        if chance < 0.15:
            egg_type = "gold"
            color = "gold"
        elif chance < 0.30:
            egg_type = "bomb"
            color = "dimgrey"
        else:
            egg_type = "normal"
            color = next(self.color_cycle)

        new_egg = self.canvas.create_oval(x, y, x + EGG_WIDTH, y + EGG_HEIGHT, fill=color, width=1,
                                          outline="black" if egg_type == "bomb" else "")

        # Yumurtayı ve türünü sözlüğe kaydediyoruz
        self.eggs[new_egg] = egg_type

        self.root.after(self.egg_interval, self.create_egg)

    def move_eggs(self):
        if self.is_game_over: return

        for egg in list(self.eggs.keys()):
            self.canvas.move(egg, 0, 10)
            _, _, _, egg_y2 = self.canvas.coords(egg)

            if egg_y2 > CANVAS_HEIGHT:
                self.egg_dropped(egg)

        self.root.after(self.egg_speed, self.move_eggs)

    def check_catch(self):
        if self.is_game_over: return

        catcher_x1, _, catcher_x2, catcher_y2 = self.canvas.coords(self.catcher)

        for egg in list(self.eggs.keys()):
            egg_x1, _, egg_x2, egg_y2 = self.canvas.coords(egg)

            if (catcher_x1 < egg_x1) and (egg_x2 < catcher_x2) and (catcher_y2 - egg_y2 < 40):
                egg_type = self.eggs[egg]
                self.eggs.pop(egg)
                self.canvas.delete(egg)

                # Türüne göre işlem yap
                self.handle_catch(egg_type)

        self.root.after(100, self.check_catch)

    def handle_catch(self, egg_type):
        """Yakalanan nesnenin türüne göre puan ve can işlemlerini yönetir."""
        if egg_type == "normal":
            self.play_sound("catch")
            self.increase_score(10)
        elif egg_type == "gold":
            self.play_sound("gold")
            self.increase_score(30)  # Altın yumurta ekstra çok puan verir
        elif egg_type == "bomb":
            self.play_sound("bomb")
            self.lose_a_life()  # Bomba yakalanırsa can gider!
            # Görsel efekt (Ekranı kırmızı yap)
            self.canvas.configure(background="tomato")
            self.root.after(200, lambda: self.canvas.configure(background="deep sky blue"))

    def egg_dropped(self, egg):
        egg_type = self.eggs.pop(egg)
        self.canvas.delete(egg)

        # Normal veya altın yumurta yere düşerse can gider. Bomba düşerse ceza yok (kurtulduk).
        if egg_type != "bomb":
            self.play_sound("drop")
            self.lose_a_life()

    def lose_a_life(self):
        self.lives_remaining -= 1
        self.canvas.itemconfigure(self.lives_text, text=f"Can: {self.lives_remaining}")
        if self.lives_remaining <= 0:
            self.game_over()

    def increase_score(self, points):
        self.score += points
        self.canvas.itemconfigure(self.score_text, text=f"Skor: {self.score}")

        if self.score > 0 and self.score >= self.level * LEVEL_UP_THRESHOLD:
            self.level_up()
        else:
            self.egg_speed = int(self.egg_speed * DIFFICULTY_MULTIPLIER)
            self.egg_interval = int(self.egg_interval * DIFFICULTY_MULTIPLIER)

    def level_up(self):
        self.level += 1
        self.play_sound("levelup")
        self.canvas.itemconfigure(self.level_text, text=f"Seviye: {self.level}")

        self.egg_speed = int(self.egg_speed * 0.8)
        self.egg_interval = int(self.egg_interval * 0.8)

        self.canvas.configure(background="gold")
        self.root.after(300, lambda: self.canvas.configure(background="deep sky blue"))

    def move_left(self, event):
        if self.is_game_over: return
        x1, _, _, _ = self.canvas.coords(self.catcher)
        if x1 > 0:
            self.canvas.move(self.catcher, -CATCHER_SPEED, 0)

    def move_right(self, event):
        if self.is_game_over: return
        _, _, x2, _ = self.canvas.coords(self.catcher)
        if x2 < CANVAS_WIDTH:
            self.canvas.move(self.catcher, CATCHER_SPEED, 0)

    def game_over(self):
        self.is_game_over = True
        self.play_sound("gameover")
        messagebox.showinfo("Oyun Bitti!", f"Ulaştığın Seviye: {self.level}\nFinal Skorunuz: {self.score}")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = EggCatcherGame(root)
    root.mainloop()