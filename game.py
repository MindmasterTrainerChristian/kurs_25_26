import pygame
import random

# Initialisierung
pygame.init()

# Fenster-Einstellungen
BREITE, HOEHE = 600, 400
screen = pygame.display.set_mode((BREITE, HOEHE))
pygame.display.set_caption("Fang den Ball!")

# Farben
WEISS = (255, 255, 255)
ROT = (255, 0, 0)
BLAU = (0, 102, 204)

# Spieler-Eigenschaften
spieler_groesse = 50
spieler_x = BREITE // 2
spieler_y = HOEHE - 70
spieler_speed = 7

# Ball-Eigenschaften
ball_radius = 15
ball_x = random.randint(ball_radius, BREITE - ball_radius)
ball_y = 0
ball_speed = 5

score = 0
font = pygame.font.SysFont("Arial", 30)

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WEISS) # Hintergrund leeren
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Steuerung
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and spieler_x > 0:
        spieler_x -= spieler_speed
    if keys[pygame.K_RIGHT] and spieler_x < BREITE - spieler_groesse:
        spieler_x += spieler_speed

    # Ballbewegung
    ball_y += ball_speed

    # Kollisionsprüfung (Hat der Spieler den Ball gefangen?)
    spieler_rect = pygame.Rect(spieler_x, spieler_y, spieler_groesse, spieler_groesse)
    if spieler_rect.collidepoint(ball_x, ball_y):
        score += 1
        ball_y = 0
        ball_x = random.randint(ball_radius, BREITE - ball_radius)
        ball_speed += 0.2 # Schwierigkeit steigt

    # Ball verloren?
    if ball_y > HOEHE:
        ball_y = 0
        ball_x = random.randint(ball_radius, BREITE - ball_radius)
        score = 0 # Reset Score
        ball_speed = 5

    # Zeichnen
    pygame.draw.rect(screen, BLAU, spieler_rect)
    pygame.draw.circle(screen, ROT, (ball_x, ball_y), ball_radius)
    
    score_text = font.render(f"Punkte: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip() # Bildschirm aktualisieren
    clock.tick(60) # 60 FPS

pygame.quit()
