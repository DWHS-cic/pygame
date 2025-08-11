import pygame
import random
import sys

# ---------- 設定 ----------
pygame.init()
WIDTH, HEIGHT = 600, 480
CELL_SIZE = 20
FPS = 10

# 顏色
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (240, 220, 80)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("貪吃蛇 Snake Game")
clock = pygame.time.Clock()

# 字體
font_small = pygame.font.SysFont("mingliu", 18)
font_med = pygame.font.SysFont("mingliu", 26)
font_big = pygame.font.SysFont("mingliu", 46)

# ---------- 幫助函式 ----------
def draw_snake(snake):
    for seg in snake:
        pygame.draw.rect(screen, GREEN, (seg[0], seg[1], CELL_SIZE, CELL_SIZE))

def draw_food(pos):
    pygame.draw.rect(screen, RED, (pos[0], pos[1], CELL_SIZE, CELL_SIZE))

def random_food_position(snake):
    # 產生不與蛇身重疊的食物位置
    while True:
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        if (x, y) not in snake:
            return (x, y)

def draw_text_center(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)

# ---------- 初始遊戲狀態與函式 ----------
def new_game():
    snake = [(100, 100), (80, 100), (60, 100)]
    direction = "RIGHT"
    next_direction = direction
    food = random_food_position(snake)
    score = 0
    return snake, direction, next_direction, food, score

snake, direction, next_direction, food, score = new_game()
state = "START"  # START / PLAYING / GAME_OVER

def handle_input(event, state, direction, next_direction):
    # 回傳更新後的 (state, next_direction)（不直接改全域）
    if event.type == pygame.KEYDOWN:
        if state == "START":
            if event.key == pygame.K_SPACE:
                return "PLAYING", next_direction
            elif event.key == pygame.K_q:
                pygame.quit(); sys.exit()
        elif state == "PLAYING":
            # 支援方向鍵與 WASD
            if event.key in (pygame.K_UP, pygame.K_w) and direction != "DOWN":
                next_direction = "UP"
            elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != "UP":
                next_direction = "DOWN"
            elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != "RIGHT":
                next_direction = "LEFT"
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != "LEFT":
                next_direction = "RIGHT"
            elif event.key == pygame.K_p:
                return "START", next_direction  # 暫停回 START 當示範（可改）
        elif state == "GAME_OVER":
            if event.key == pygame.K_r:
                return "PLAYING", next_direction  # 由外層 new_game() 處理重置
            #elif event.key == pygame.K_q:
            #    pygame.quit(); sys.exit()
    return state, next_direction

# ---------- 主迴圈 ----------
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            new_state, new_next_dir = handle_input(event, state, direction, next_direction)
            # 如果從 START 進入 PLAYING，或從 GAME_OVER 按 R，要重置遊戲
            if state != new_state and new_state == "PLAYING":
                snake, direction, next_direction, food, score = new_game()
                state = "PLAYING"
                # 如果從 GAME_OVER 按 R，new_game 已經重置
                # 如果從 START 按 SPACE，也已重置
            else:
                state = new_state
                next_direction = new_next_dir

    if state == "START":
        draw_text_center("貪吃蛇 Snake Game", font_big, YELLOW, HEIGHT//3)
        draw_text_center("按 SPACE 開始遊戲", font_med, WHITE, HEIGHT//3 + 80)
        draw_text_center("方向鍵 / WASD 操作", font_small, WHITE, HEIGHT//3 + 120)
        draw_text_center("若方向沒有反應，請先用滑鼠點一下遊戲視窗使其取得焦點。", font_small, WHITE, HEIGHT - 40)
        pygame.display.flip()
        clock.tick(15)
        continue

    if state == "PLAYING":
        # 更新方向：在每個幀開始採用 next_direction（防止同幀內反向）
        direction = next_direction

        head_x, head_y = snake[0]
        if direction == "UP":
            head_y -= CELL_SIZE
        elif direction == "DOWN":
            head_y += CELL_SIZE
        elif direction == "LEFT":
            head_x -= CELL_SIZE
        elif direction == "RIGHT":
            head_x += CELL_SIZE
        new_head = (head_x, head_y)

        # 碰撞偵測：牆壁或撞到自己
        if (head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT) or (new_head in snake):
            state = "GAME_OVER"
        else:
            # 吃到食物
            if new_head == food:
                snake.insert(0, new_head)
                score += 1
                food = random_food_position(snake)
            else:
                snake.insert(0, new_head)
                snake.pop()

        # 繪圖
        draw_snake(snake)
        draw_food(food)
        score_surf = font_small.render(f"分數: {score}", True, WHITE)
        screen.blit(score_surf, (10, 10))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    if state == "GAME_OVER":
        # 顯示遊戲結束畫面，並提供重玩與退出提示（置中、較大字）
        draw_text_center("遊戲結束！", font_big, RED, HEIGHT//3 - 20)
        draw_text_center("阿你都玩了 還不要加入資訊社嗎 : )", font_med, GREEN, HEIGHT//3 - 80)
        draw_text_center(f"最終分數: {score}", font_med, WHITE, HEIGHT//3 + 40)
        draw_text_center("按 R 重玩", font_med, YELLOW, HEIGHT//3 + 110)
        pygame.display.flip()

        # 在 GAME_OVER 狀態不要急著用忙碌的 while，讓主迴圈繼續處理事件（避免卡死）
        clock.tick(15)
        continue

pygame.quit()