from pygame import *
import socket
import json
from threading import Thread
import math

# --- PYGAME ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Neon Ping Pong")

# --- COLORS ---
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 50, 200)
WHITE = (255, 255, 255)
BG = (10, 10, 25)

# --- SERVER ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass

def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            break

# --- FONTS ---
font_big = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- HELPERS ---
def glow_rect(x, y, w, h, color):
    for i in range(6, 0, -1):
        s = Surface((w + i*4, h + i*4), SRCALPHA)
        draw.rect(s, (*color, 30), s.get_rect(), border_radius=8)
        screen.blit(s, (x - i*2, y - i*2))
    draw.rect(screen, color, (x, y, w, h), border_radius=8)

def glow_circle(x, y, r, color):
    for i in range(8, 0, -1):
        s = Surface((r*2+i*4, r*2+i*4), SRCALPHA)
        draw.circle(s, (*color, 25), s.get_rect().center, r+i*2)
        screen.blit(s, (x-r-i*2, y-r-i*2))
    draw.circle(screen, color, (x, y), r)

# --- GAME ---
game_over = False
winner = None
you_winner = None

my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()

# --- LOOP ---
while True:
    for e in event.get():
        if e.type == QUIT:
            quit()
            exit()

    screen.fill(BG)

    # --- GRID ---
    for x in range(0, WIDTH, 40):
        draw.line(screen, (20, 20, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        draw.line(screen, (20, 20, 40), (0, y), (WIDTH, y))

    # --- COUNTDOWN ---
    if "countdown" in game_state and game_state["countdown"] > 0:
        text = font_big.render(str(game_state["countdown"]), True, NEON_PINK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        display.update()
        continue

    # --- WIN ---
    if "winner" in game_state and game_state["winner"] is not None:
        msg = "ТИ ПЕРЕМІГ!" if game_state["winner"] == my_id else "ПОРАЗКА"
        text = font_big.render(msg, True, NEON_PINK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        display.update()
        continue

    # --- GAME DRAW ---
    if game_state:
        back = image.load("diddy.jpg")
        back = transform.scale(back, (800, 600))
        screen.blit(back, (0, 0))

        # Center circle
        draw.circle(screen, NEON_PINK, (WIDTH//2, HEIGHT//2), 80, 2)

        # Paddles
        glow_rect(30, game_state['paddles']['0'], 20, 100, NEON_BLUE)
        glow_rect(WIDTH-50, game_state['paddles']['1'], 20, 100, NEON_BLUE)

        # Ball
        glow_circle(game_state['ball']['x'], game_state['ball']['y'], 10, NEON_PINK)

        # Score
        score = font_main.render(
            f"{game_state['scores'][0]}   :   {game_state['scores'][1]}",
            True, WHITE
        )
        screen.blit(score, score.get_rect(center=(WIDTH//2, 40)))

    else:
        wait = font_main.render("Очікування гравців...", True, WHITE)
        screen.blit(wait, wait.get_rect(center=(WIDTH//2, HEIGHT//2)))

    display.update()
    clock.tick(60)

    # --- INPUT ---
    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")