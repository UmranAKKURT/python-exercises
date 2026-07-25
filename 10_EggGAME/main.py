import math
import random
import sys
import os
import json
import pygame

# --- SİSTEM & EKRAN AYARLARI ---
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Egg Catcher Pro Edition")
clock = pygame.time.Clock()

# --- RENK PALETİ ---
BG_TOP = (15, 23, 42)  # Derin Gece Mavisı
BG_BOTTOM = (30, 41, 59)  # Slate Blue
CATCHER_COLOR = (59, 130, 246)  # Neon Mavi
TEXT_COLOR = (241, 245, 249)

COLOR_NORMAL = (96, 165, 250)
COLOR_GOLD = (251, 191, 36)
COLOR_BOMB = (239, 68, 68)

# --- FONT AYARLARI ---
# Not: "Segoe UI" Windows için varsayılandır. Eğer Mac/Linux kullanıyorsanız
# pygame.font.get_default_font() veya sisteminizde bulunan bir fontu yazabilirsiniz.
font_main = pygame.font.SysFont("Segoe UI", 24, bold=True)
font_large = pygame.font.SysFont("Segoe UI", 48, bold=True)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, -1)
        self.radius = random.randint(3, 6)
        self.lifetime = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 8

    def draw(self, surface):
        if self.lifetime > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, max(0, self.lifetime)), (self.radius, self.radius), self.radius)
            surface.blit(s, (self.x - self.radius, self.y - self.radius))


class Egg:
    def __init__(self, level):
        self.width = 36
        self.height = 48
        self.x = random.randint(50, SCREEN_WIDTH - 50 - self.width)
        self.y = -self.height

        chance = random.random()
        if chance < 0.15:
            self.type = "gold"
            self.color = COLOR_GOLD
            self.score_val = 30
        elif chance < 0.35:
            self.type = "bomb"
            self.color = COLOR_BOMB
            self.score_val = 0
        else:
            self.type = "normal"
            self.color = COLOR_NORMAL
            self.score_val = 10

        base_speed = random.uniform(3.0, 5.0)
        self.speed = base_speed + (level * 0.5)

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.ellipse(surface, self.color, rect)

        highlight_rect = pygame.Rect(self.x + 8, self.y + 6, self.width // 3, self.height // 3)
        pygame.draw.ellipse(surface, (255, 255, 255, 120), highlight_rect)

        if self.type == "bomb":
            pygame.draw.circle(surface, (15, 23, 42), rect.center, self.width // 4)


class Catcher:
    def __init__(self):
        self.width = 120
        self.height = 24
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = 10
        self.target_x = self.x

    def update(self):
        self.x += (self.target_x - self.x) * 0.25
        if self.x < 10:
            self.x = 10
            self.target_x = 10
        if self.x > SCREEN_WIDTH - self.width - 10:
            self.x = SCREEN_WIDTH - self.width - 10
            self.target_x = SCREEN_WIDTH - self.width - 10

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, CATCHER_COLOR, rect, border_bottom_left_radius=15, border_bottom_right_radius=15)
        pygame.draw.line(surface, (147, 197, 253), (self.x, self.y), (self.x + self.width, self.y), 4)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        self._load_sounds()
        self.high_score = self.load_high_score()
        self.reset()

    def _load_sounds(self):
        self.sounds = {}
        sfx_files = {
            "catch": "catch.wav",
            "bomb": "bomb.wav",
            "drop": "drop.wav",
            "levelup": "levelup.wav"
        }

        for name, path in sfx_files.items():
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.6)
                self.sounds[name] = sound
            else:
                self.sounds[name] = None

        if os.path.exists("bg_music.mp3"):
            pygame.mixer.music.load("bg_music.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

    def play_sound(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()

    def load_high_score(self):
        self.score_file = "highscore.json"
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r") as file:
                    data = json.load(file)
                    return data.get("high_score", 0)
            except (json.JSONDecodeError, IOError):
                return 0
        return 0

    def save_high_score(self):
        with open(self.score_file, "w") as file:
            json.dump({"high_score": self.high_score}, file)

    def reset(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.catcher = Catcher()
        self.eggs = []
        self.particles = []
        self.spawn_timer = 0
        self.spawn_interval = 60
        self.game_over = False

        # Eğer oyun yeniden başlarsa müziği tekrar başlat
        if os.path.exists("bg_music.mp3") and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.catcher.target_x -= self.catcher.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.catcher.target_x += self.catcher.speed

    def spawn_particles(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        if self.game_over:
            return

        self.catcher.update()

        self.spawn_timer += 1
        if self.spawn_timer >= max(20, self.spawn_interval - (self.level * 4)):
            self.eggs.append(Egg(self.level))
            self.spawn_timer = 0

        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

        catcher_rect = self.catcher.get_rect()

        for egg in self.eggs[:]:
            egg.move()
            egg_rect = pygame.Rect(egg.x, egg.y, egg.width, egg.height)

            # Yakalama Kontrolü
            if catcher_rect.colliderect(egg_rect):
                if egg.y + egg.height - egg.speed <= self.catcher.y + 10:
                    self.spawn_particles(egg.x + egg.width // 2, egg.y, egg.color)

                    if egg.type == "bomb":
                        self.play_sound("bomb")
                        self.lives -= 1
                    else:
                        self.play_sound("catch")
                        self.score += egg.score_val

                        if self.score >= self.level * 100:
                            self.level += 1
                            self.play_sound("levelup")

                    self.eggs.remove(egg)
                    continue

            # Yere Düşme Kontrolü
            if egg.y > SCREEN_HEIGHT:
                if egg.type != "bomb":
                    self.play_sound("drop")
                    self.lives -= 1
                    self.spawn_particles(egg.x + egg.width // 2, SCREEN_HEIGHT - 10, (239, 68, 68), 8)

                self.eggs.remove(egg)

        # Oyun Bitiş Kontrolü ve Skor Kaydetme
        if self.lives <= 0 and not self.game_over:
            self.game_over = True

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def draw_background(self):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
            g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
            b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_ui(self):
        score_surf = font_main.render(f"SKOR: {self.score}", True, TEXT_COLOR)
        high_score_surf = font_main.render(f"REKOR: {self.high_score}", True, (16, 185, 129))
        level_surf = font_main.render(f"SEVİYE: {self.level}", True, (251, 191, 36))
        lives_surf = font_main.render(f"CAN: {'❤️' * self.lives}", True, (239, 68, 68))

        screen.blit(score_surf, (20, 20))
        screen.blit(high_score_surf, (20, 50))
        screen.blit(level_surf, (SCREEN_WIDTH // 2 - level_surf.get_width() // 2, 20))
        screen.blit(lives_surf, (SCREEN_WIDTH - 150, 20))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((15, 23, 42, 200))
            screen.blit(overlay, (0, 0))

            go_surf = font_large.render("OYUN BİTTİ", True, (239, 68, 68))
            final_score_surf = font_main.render(f"Toplam Skor: {self.score}", True, TEXT_COLOR)
            restart_surf = font_main.render("Yeniden Başlamak İçin 'SPACE' Tuşuna Basın", True, (148, 163, 184))

            screen.blit(go_surf, (SCREEN_WIDTH // 2 - go_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(final_score_surf, (SCREEN_WIDTH // 2 - final_score_surf.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.game_over and event.key == pygame.K_SPACE:
                        self.reset()

            self.handle_input()
            self.update()

            self.draw_background()

            for particle in self.particles:
                particle.draw(screen)

            for egg in self.eggs:
                egg.draw(screen)

            self.catcher.draw(screen)
            self.draw_ui()

            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()