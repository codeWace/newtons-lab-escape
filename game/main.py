import pygame
import random
import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# --- Initialize Pygame ---
pygame.init()

# --- Window settings ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1024, 576  # landscape size
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Newtons Lab Escape")

# --- Assets path ---
ASSETS_PATH = os.path.join(os.getcwd(), "..", "assets")  # ../assets relative to game/

# --- Clock ---
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# --- Load Minecraft font ---
font_path = os.path.join(ASSETS_PATH, "Minecraft.ttf")
if os.path.exists(font_path):
    title_font = pygame.font.Font(font_path, 48)
    score_font = pygame.font.Font(font_path, 32)
else:
    title_font = pygame.font.SysFont("Arial", 48)
    score_font = pygame.font.SysFont("Arial", 32)

# --- Load sprites ---
def load_sprite(name, size):
    img = pygame.image.load(os.path.join(ASSETS_PATH, name)).convert_alpha()
    return pygame.transform.scale(img, size)

mouse_img = load_sprite("mouse.png", (70, 70))
heart_img = load_sprite("heart.png", (30, 30))

# Collectibles per level
collectibles_imgs = {
    1: load_sprite("cheese.png", (60, 60)),
    2: load_sprite("newspaper.png", (60, 60)),
    3: load_sprite("bag.png", (80, 80))
}

# Hazards per level
hazards_imgs = {
    1: load_sprite("bulb.png", (60, 60)),
    2: load_sprite("beaker.png", (60, 60)),
    3: load_sprite("deathbeaker.png", (60, 60))
}

# Backgrounds per level
bg_files = {
    1: "lab_bg.png",
    2: "lab2_bg.png",
    3: "lab3_bg.png"
}

# --- Player setup ---
player_rect = mouse_img.get_rect(midbottom=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
player_vel_y = 0
player_speed = 7
gravity = 0.6
jump_strength = -12

# --- Game variables ---
score = 0
lives = 3
level = 1
cheeses_to_collect = 5  # collectibles per level
collected_items = 0
hazard_speed_increase = 0.5
collectible_list = []
hazard_list = []

# --- Load initial background ---
def load_bg(level):
    file = bg_files.get(level, "lab_bg.jpg")
    path = os.path.join(ASSETS_PATH, file)
    bg = pygame.image.load(path).convert()
    return pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))

bg = load_bg(level)

# --- Functions ---
def draw_text_center(text, y, font_obj, color=BLACK):
    text_surf = font_obj.render(text, True, color)
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, y))
    screen.blit(text_surf, text_rect)

def spawn_collectible(level):
    x = random.randint(50, WINDOW_WIDTH - 50)
    y = WINDOW_HEIGHT - 60  # floor level
    img = collectibles_imgs[level]
    rect = img.get_rect(midbottom=(x, y))
    collectible_list.append({"rect": rect, "img": img})

def spawn_hazard(level):
    x = random.randint(50, WINDOW_WIDTH - 50)
    img = hazards_imgs[level]
    rect = img.get_rect(topleft=(x, -50))
    speed = random.uniform(3 + level * hazard_speed_increase, 7 + level * hazard_speed_increase)
    hazard_list.append({"rect": rect, "img": img, "speed": speed})

def reset_level():
    global collectible_list, hazard_list, collected_items, bg
    collected_items = 0
    collectible_list.clear()
    hazard_list.clear()
    for _ in range(cheeses_to_collect):
        spawn_collectible(level)
    for _ in range(5 + level):
        spawn_hazard(level)
    bg = load_bg(level)

# --- Initial spawn ---
reset_level()

# --- Game states ---
START, PLAYING, GAME_OVER = 0, 1, 2
game_state = START

# --- Main loop ---
running = True
while running:
    clock.tick(FPS)
    screen.blit(bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if game_state == START:
        draw_text_center("PRESS SPACE TO START", WINDOW_HEIGHT // 2, title_font)
        if keys[pygame.K_SPACE]:
            game_state = PLAYING

    elif game_state == PLAYING:
        # Player movement
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed
        if keys[pygame.K_SPACE] and player_rect.bottom >= WINDOW_HEIGHT:
            player_vel_y = jump_strength

        # Gravity
        player_vel_y += gravity
        player_rect.y += player_vel_y

        # Keep player inside screen
        if player_rect.bottom >= WINDOW_HEIGHT:
            player_rect.bottom = WINDOW_HEIGHT
            player_vel_y = 0
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > WINDOW_WIDTH:
            player_rect.right = WINDOW_WIDTH

        # Draw player
        screen.blit(mouse_img, player_rect)

        # Collectibles
        for item in collectible_list[:]:
            screen.blit(item["img"], item["rect"])
            if player_rect.colliderect(item["rect"]):
                collectible_list.remove(item)
                collected_items += 1
                score += 1
                if collected_items < cheeses_to_collect:
                    spawn_collectible(level)

        # Hazards
        for hazard in hazard_list[:]:
            hazard["rect"].y += hazard["speed"]
            screen.blit(hazard["img"], hazard["rect"])
            if hazard["rect"].top > WINDOW_HEIGHT:
                hazard_list.remove(hazard)
                spawn_hazard(level)
            if player_rect.colliderect(hazard["rect"]):
                hazard_list.remove(hazard)
                lives -= 1
                spawn_hazard(level)
                if lives <= 0:
                    game_state = GAME_OVER

        # Hearts
        for i in range(lives):
            screen.blit(heart_img, (10 + i * 40, 10))

        # Score and level
        score_surf = score_font.render(f"SCORE: {score}", True, BLACK)
        screen.blit(score_surf, (WINDOW_WIDTH - 180, 10))
        level_surf = score_font.render(f"LEVEL: {level}", True, BLACK)
        screen.blit(level_surf, (WINDOW_WIDTH - 180, 50))

        # Level completion
        if collected_items >= cheeses_to_collect:
            if level < 3:
                level += 1
                reset_level()
            else:
                draw_text_center("YOU ESCAPED!", WINDOW_HEIGHT // 2, title_font, RED)
                draw_text_center(f"FINAL SCORE: {score}", WINDOW_HEIGHT // 2 + 60, score_font)
                pygame.display.flip()
                pygame.time.wait(3000)
                game_state = GAME_OVER

    elif game_state == GAME_OVER:
        draw_text_center("GAME OVER", WINDOW_HEIGHT // 2 - 50, title_font, RED)
        draw_text_center(f"SCORE: {score}", WINDOW_HEIGHT // 2 + 20, score_font)
        draw_text_center("PRESS SPACE TO RESTART", WINDOW_HEIGHT // 2 + 80, score_font)
        if keys[pygame.K_SPACE]:
            # Reset everything
            score = 0
            lives = 3
            level = 1
            player_rect.midbottom = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
            player_vel_y = 0
            reset_level()
            game_state = PLAYING

    pygame.display.flip()

pygame.quit()
sys.exit()
