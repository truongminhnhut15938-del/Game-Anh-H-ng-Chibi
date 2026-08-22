import pygame
import sys
import random
import os

# Khởi tạo Pygame
pygame.init()
pygame.mixer.init()

# --- Cấu hình màn hình ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Chibi Duy Khang Phieu Luu")

# --- Màu sắc và Font ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 50, 50) # Màu dự phòng nếu không load được ảnh quái
font = pygame.font.SysFont(None, 24)
font_large = pygame.font.SysFont(None, 36)

# --- Hàm Load Ảnh An Toàn ---
# Hàm này giúp game không bị lỗi crash nếu bạn chưa kịp upload ảnh lên GitHub
def load_image(path, default_color, size):
    full_path = path # Ví dụ: 'assets/player_idle.png'
    try:
        # Kiểm tra xem file có tồn tại không
        if os.path.exists(full_path):
            img = pygame.image.load(full_path).convert_alpha()
            # Tự động scale (phóng to/thu nhỏ) ảnh về kích thước mong muốn
            return pygame.transform.scale(img, size)
        else:
            print(f"Warning: Image not found at {full_path}. Using default color.")
            # Tạo hình chữ nhật màu thay thế nếu không tìm thấy ảnh
            surface = pygame.Surface(size)
            surface.fill(default_color)
            return surface
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        surface = pygame.Surface(size)
        surface.fill(default_color)
        return surface

# --- Load Tài Nguyên Hình Ảnh ---
# Bạn cần đảm bảo các file ảnh đã có trong thư mục 'assets/' trên GitHub
BG_IMG = load_image('assets/background.png', (150, 200, 150), (SCREEN_WIDTH, SCREEN_HEIGHT))
PLAYER_IMG = load_image('assets/player_idle.png', (50, 100, 230), (100, 160)) # Scale nhân vật to hơn 1 chút
ENEMY_TIGER_IMG = load_image('assets/enemy_tiger.png', (200, 150, 50), (160, 160))
ENEMY_LION_IMG = load_image('assets/enemy_lion.png', (150, 150, 150), (160, 160))
ENEMY_DINO_IMG = load_image('assets/enemy_dino.png', (100, 150, 100), (160, 160))

# Gán hình ảnh cho các biến quái
enemy_images = {
    "Ho Sach Be": ENEMY_TIGER_IMG,
    "Su Tu Sach Be": ENEMY_LION_IMG,
    "Khung Long Sach Be": ENEMY_DINO_IMG
}

# --- Danh sách Vũ Khí ---
WEAPONS = [
    {"name": "1. Kiem", "damage": 20, "effect": "Chem can chien!"},
    {"name": "2. Kiem Anh Sang", "damage": 35, "effect": "Tia sang xanh chem manh!"},
    {"name": "3. Sung", "damage": 25, "effect": "Ban dan thuong!"},
    {"name": "4. Sung Anh Sang", "damage": 45, "effect": "Luong sang xanh do quet sach!"},
    {"name": "5. Qua Bom Den", "damage": 60, "effect": "No tung cuc lon!"},
    {"name": "6. Thung TNT", "damage": 80, "effect": "Sieu no TNT dung dung!"},
    {"name": "7. Ten Lua", "damage": 100, "effect": "Phong ten lua do trang huy diet!"}
]

# --- Trạng thái Game ---
state = 'WALKING'

# Thông tin vị trí nhân vật và kẻ thù (căn chỉnh lại để phù hợp ảnh to)
player_x = 150
player_y = 270 # Nhân vật đứng trên mặt đất giả định (y=~400-130)
enemy_x = 600
enemy_y = 270 # Quái đứng ngang tầm người

enemy_hp = 100
enemy_max_hp = 100
enemy_name = "Ho Sach Be"
enemy_fly_y = 270
current_enemy_img = ENEMY_TIGER_IMG

selected_weapon_index = 0
effect_timer = 0
current_effect_text = ""

clock = pygame.time.Clock()

def reset_enemy():
    global enemy_hp, enemy_max_hp, enemy_name, enemy_y, enemy_fly_y, current_enemy_img
    enemies_data = [
        ("Ho Sach Be", 100, ENEMY_TIGER_IMG), 
        ("Su Tu Sach Be", 130, ENEMY_LION_IMG), 
        ("Khung Long Sach Be", 160, ENEMY_DINO_IMG)
    ]
    chosen = random.choice(enemies_data)
    enemy_name = chosen[0]
    enemy_max_hp = chosen[1]
    enemy_hp = chosen[1]
    current_enemy_img = chosen[2]
    enemy_y = 270
    enemy_fly_y = 270

def draw_game_elements():
    # Vẽ Nền (Background)
    screen.blit(BG_IMG, (0, 0))
    
    # Vẽ Nhân vật Duy Khang (Dùng hàm blit thay vì draw.rect)
    screen.blit(PLAYER_IMG, (player_x, player_y))
    
    # Vẽ Tên và HP của người chơi
    txt_player = font.render("Duy Khang", True, BLACK)
    screen.blit(txt_player, (player_x + 10, player_y - 25))

    # Vẽ Kẻ thù
    # Chỉ vẽ kẻ thù khi chưa bay đi mất
    if state != 'FLYING_AWAY':
        screen.blit(current_enemy_img, (enemy_x, enemy_y))
        
        # Vẽ Tên và HP của kẻ thù
        hp_color = GREEN if enemy_hp > enemy_max_hp * 0.5 else RED
        txt_enemy = font.render(f"{enemy_name} (HP: {enemy_hp}/{enemy_max_hp})", True, hp_color)
        screen.blit(txt_enemy, (enemy_x - 30, enemy_y - 25))
        
        # Vẽ Thanh máu phụ cho dễ nhìn
        pygame.draw.rect(screen, GRAY, (enemy_x, enemy_y - 5, 160, 10))
        health_width = int((enemy_hp / enemy_max_hp) * 160)
        pygame.draw.rect(screen, RED, (enemy_x, enemy_y - 5, health_width, 10))


# --- Vòng lặp chính của game ---
while True:
    # 1. Xử lý sự kiện bàn phím
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if state == 'WALKING':
                if event.key == pygame.K_SPACE:
                    state = 'FIGHTING'
            elif state == 'FIGHTING':
                if pygame.K_1 <= event.key <= pygame.K_7:
                    selected_weapon_index = event.key - pygame.K_1
                    weapon = WEAPONS[selected_weapon_index]
                    enemy_hp -= weapon['damage']
                    current_effect_text = weapon['effect']
                    state = 'EFFECT'
                    effect_timer = 60 # Hiển thị hiệu ứng trong 1 giây

    # 2. Logic cập nhật game theo trạng thái
    if state == 'WALKING':
        draw_game_elements()
        # Hiển thị hướng dẫn trên nền
        txt_guide = font_large.render("Nhan SPACE de di tiep va gap quai vat!", True, BLACK)
        screen.blit(txt_guide, (210, 50))

    elif state == 'FIGHTING':
        draw_game_elements()
        
        # Vẽ Menu chọn vũ khí (Màu xám nhạt)
        menu_rect = pygame.Rect(50, 50, 450, 250)
        pygame.draw.rect(screen, (240, 240, 240), menu_rect)
        pygame.draw.rect(screen, BLACK, menu_rect, 3)
        
        txt_menu = font_large.render("CHON VU KHI (Bam phim 1-7 tren ban phim):", True, BLACK)
        screen.blit(txt_menu, (70, 70))
        
        for i, w in enumerate(WEAPONS):
            txt_w = font.render(f"{w['name']} (Dame: {w['damage']})", True, BLACK)
            screen.blit(txt_w, (70, 105 + i * 25))

    elif state == 'EFFECT':
        draw_game_elements()
        # Hiển thị chữ hiệu ứng tấn công
        txt_eff = font_large.render(f"DUNG DUNG! {current_effect_text}", True, (255, 0, 0))
        screen.blit(txt_eff, (280, 150))
        effect_timer -= 1
        if effect_timer <= 0:
            if enemy_hp <= 0:
                state = 'FLYING_AWAY'
            else:
                state = 'FIGHTING'

    elif state == 'FLYING_AWAY':
        # Vẽ Nền
        screen.blit(BG_IMG, (0, 0))
        screen.blit(PLAYER_IMG, (player_x, player_y))
        
        # Quái bay vút lên cao và mờ dần (alpha)
        enemy_fly_y -= 6
        # Để tạo hiệu ứng mờ, ta phải tạo surface mới (nâng cao)
        # Tạm thời chỉ vẽ quái bay lên
        screen.blit(current_enemy_img, (enemy_x, enemy_fly_y))
        
        txt_win = font_large.render("QUAI VAT DA BAY LEN TROI! TIEP TUC DI THANG...", True, (0, 150, 0))
        screen.blit(txt_win, (130, 150))
        
        if enemy_fly_y < -200: # Bay cao hẳn ra khỏi màn hình
            reset_enemy()
            state = 'WALKING'

    pygame.display.flip()
    clock.tick(60)
