
import pygame
import random
import time
from dataclasses import dataclass

WIDTH, HEIGHT = 900, 600
FPS = 60

SANTA_SPEED = 420.0
FALL_SPEED_BASE = 170.0
SPAWN_GIFT_BASE = 0.55   # Sekunden
SPAWN_COAL_BASE = 0.75
SPAWN_COCOA_BASE = 6.0

SHIELD_DURATION = 5.0

pygame.init()
pygame.display.set_caption("Santa Dash — Gifts vs Coal")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)
bigfont = pygame.font.SysFont("consolas", 54)

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

@dataclass
class Santa:
    x: float = WIDTH / 2
    y: float = HEIGHT - 70
    r: int = 24
    shield_until: float = 0.0

    def has_shield(self):
        return time.time() < self.shield_until

    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r * 2, self.r * 2)

@dataclass
class FallingThing:
    kind: str  # "gift" | "coal" | "cocoa"
    x: float
    y: float
    vy: float
    size: int

    def rect(self):
        return pygame.Rect(int(self.x - self.size), int(self.y - self.size), self.size * 2, self.size * 2)

def spawn(kind, difficulty):
    x = random.uniform(40, WIDTH - 40)
    y = -30
    speed = FALL_SPEED_BASE * (1.0 + 0.18 * difficulty) * random.uniform(0.9, 1.2)
    size = 16 if kind != "cocoa" else 14
    return FallingThing(kind, x, y, speed, size)

def draw_santa(s: Santa):
    # Santa Körper
    pygame.draw.circle(screen, (220, 40, 40), (int(s.x), int(s.y)), s.r)
    # Mütze
    pygame.draw.polygon(screen, (180, 20, 20), [
        (int(s.x - 12), int(s.y - 18)),
        (int(s.x + 18), int(s.y - 22)),
        (int(s.x + 6),  int(s.y - 42))
    ])
    pygame.draw.circle(screen, (245, 245, 245), (int(s.x + 7), int(s.y - 42)), 6)
    # Bart
    pygame.draw.circle(screen, (245, 245, 245), (int(s.x), int(s.y + 10)), 13)

    # Shield
    if s.has_shield():
        pygame.draw.circle(screen, (120, 200, 255), (int(s.x), int(s.y)), s.r + 10, 3)

def draw_thing(t: FallingThing):
    if t.kind == "gift":
        pygame.draw.rect(screen, (40, 190, 80), t.rect(), border_radius=6)
        pygame.draw.line(screen, (255, 220, 70),
                         (t.rect().centerx, t.rect().top),
                         (t.rect().centerx, t.rect().bottom), 3)
        pygame.draw.line(screen, (255, 220, 70),
                         (t.rect().left, t.rect().centery),
                         (t.rect().right, t.rect().centery), 3)
    elif t.kind == "coal":
        pygame.draw.circle(screen, (40, 40, 40), (int(t.x), int(t.y)), t.size)
        pygame.draw.circle(screen, (80, 80, 80), (int(t.x - 4), int(t.y - 4)), max(2, t.size // 4))
    else:  # cocoa
        pygame.draw.rect(screen, (140, 90, 50), t.rect(), border_radius=6)
        pygame.draw.circle(screen, (240, 240, 240), (t.rect().centerx, t.rect().top + 6), 6)

def snow_background(frame):
    # sehr leichte “Snow”-Dots
    random.seed(frame // 2)
    for _ in range(120):
        x = random.randrange(0, WIDTH)
        y = random.randrange(0, HEIGHT)
        r = random.randrange(1, 3)
        #TODO
def run():
    santa = Santa()
    things = []
    score = 0
    lives = 3
    game_over = False
    frame = 0

    last_gift = time.time()
    last_coal = time.time()
    last_cocoa = time.time()

    while True:
        dt = clock.tick(FPS) / 1000.0
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if game_over and event.key == pygame.K_r:
                    santa = Santa()
                    things = []
                    score = 0
                    lives = 3
                    game_over = False
                    last_gift = last_coal = last_cocoa = time.time()

        keys = pygame.key.get_pressed()

        if not game_over:
            # Bewegung
            #TODO
            # Difficulty steigt über Score
            difficulty = min(12.0, score / 15.0)

            now = time.time()
            # Spawns: mit Difficulty etwas schneller
            gift_cd = max(0.18, SPAWN_GIFT_BASE - 0.03 * difficulty)
            coal_cd = max(0.22, SPAWN_COAL_BASE - 0.02 * difficulty)

            if now - last_gift > gift_cd:
                things.append(spawn("gift", difficulty))
                last_gift = now

            if now - last_coal > coal_cd:
                things.append(spawn("coal", difficulty))
                last_coal = now

            if now - last_cocoa > SPAWN_COCOA_BASE:
                things.append(spawn("cocoa", difficulty))
                last_cocoa = now

            # Update fallende Dinge
            for t in things:
                t.y += t.vy * dt

            # Kollisionen + Cleanup
            santa_r = santa.rect()
            new_things = []
            for t in things:
                if t.y > HEIGHT + 40:
                    continue

                if santa_r.colliderect(t.rect()):
                    if t.kind == "gift":
                        score += 1
                    elif t.kind == "coal":
                        if santa.has_shield():
                            score += 1  # Shield “konvertiert” Kohle zu Punkt
                        else:
                            lives -= 1
                            if lives <= 0:
                                game_over = True
                    else:  # cocoa
                        santa.shield_until = time.time() + SHIELD_DURATION
                    continue

                new_things.append(t)
            things = new_things

        # Render
        screen.fill((15, 18, 28))
        snow_background(frame)

        # Boden
        pygame.draw.rect(screen, (25, 90, 55), pygame.Rect(0, HEIGHT - 40, WIDTH, 40))

        # Dinge + Santa
        for t in things:
            draw_thing(t)
        draw_santa(santa)

        # HUD
        shield_left = max(0.0, santa.shield_until - time.time())
        hud = f"Score: {score}   Lives: {lives}   Shield: {shield_left:0.1f}s"
        screen.blit(font.render(hud, True, (235, 235, 235)), (16, 14))

        if game_over:
            #TODO

        pygame.display.flip()

if __name__ == "__main__":
    run()
    pygame.quit()

