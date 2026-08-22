import pygame
import sys
import random

# Khởi tạo Pygame
pygame.init()
pygame.mixer.init() # Khởi tạo âm thanh

# Cấu hình màn hình game (phong cách retro Mario màn hình ngang)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Chibi Duy Khang Phiêu Lưu")

# Màu sắc cơ bản
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 50, 50)
BLUE = (50, 100, 230)
GREEN = (50, 200, 50)
YELLOW = (240, 200, 50)
GRAY = (200, 200, 200)

font = pygame.font.SysFont(None, 24)
font_large = pygame.font.SysFont(None, 36)

# Danh sách 7 loại vũ khí của bạn
WEAPONS = [
    {"name": "1. Kiếm", "damage": 20, "effect": "Chém cận chiến!"},
    {"name": "2. Kiếm Ánh Sáng", "damage": 35, "effect": "Tia sáng xanh chém mạnh!"},
    {"name": "3. Súng", "damage": 25, "effect": "Bắn đạn thường!"},
    {"name": "4. Súng Ánh Sáng", "damage": 45, "effect": "Luồng sáng xanh đỏ quét sạch!"},
    {"name": "5. Quả Bom Đen", "damage": 60, "effect": "Nổ tung cực lớn!"},
    {"name": "6. Thùng TNT", "damage": 80, "effect": "Siêu nổ TNT đùng đùng!"},
    {"name": "7. Tên Lửa", "damage": 100, "effect": "Phóng tên lửa đỏ trắng hủy diệt!"}
]

# Trạng thái game
# 'WALKING': Đang đi tìm quái
# 'FIGHTING': Gặp quái, mở menu chọn vũ khí
# 'EFFECT': Hiển thị hiệu ứng tấn công và âm thanh
# 'FLYING_AWAY': Quái bay lên trời khi hết máu
state = 'WALKING'

# Thông tin nhân vật và kẻ thù
player_x = 100
player_y = 330
enemy_x = 650
enemy_y = 330
enemy_hp = 100
enemy_max_hp = 100
enemy_name = "Hổ Dễ Thương"
enemy_fly_y = 330 # Dùng khi quái bay lên cao

selected_weapon_index = 0
effect_timer = 0
current_effect_text = ""

clock = pygame.time.Clock()

def reset_enemy():
    global enemy_hp, enemy_max_hp, enemy_name, enemy_y, enemy_fly_y
    enemies_list = [("Hổ Sách Bé", 100), ("Sư Tử Sách Bé", 130), ("Khủng Long Sách Bé", 160)]
    chosen = random.choice(enemies_list)
    enemy_name = chosen[0]
    enemy_max_hp = chosen[1]
    enemy_hp = chosen[1]
    enemy_y = 330
    enemy_fly_y = 330

# Vòng lặp chính của game
while True:
    screen.fill(WHITE)

    # 1. Xử lý sự kiện bàn phím
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if state == 'WALKING':
                # Nhấn SPACE để gặp quái (hoặc game tự trigger khi đi tới)
                if event.key == pygame.K_SPACE:
                    state = 'FIGHTING'
            elif state == 'FIGHTING':
                # Chọn vũ khí bằng phím số 1-7
                if pygame.K_1 <= event.key <= pygame.K_7:
                    selected_weapon_index = event.key - pygame.K_1
                    weapon = WEAPONS[selected_weapon_index]
                    
                    # Trừ máu quái
                    enemy_hp -= weapon['damage']
                    current_effect_text = weapon['effect']
                    
                    # Kích hoạt hiệu ứng và âm thanh "đùng đùng" giả lập
                    state = 'EFFECT'
                    effect_timer = 60 # Hiển thị trong 60 frames (~1 giây)

    # 2. Logic cập nhật game theo trạng thái
    if state == 'WALKING':
        # Hiển thị cảnh nền đi ngang kiểu Mario
        pygame.draw.rect(screen, (100, 200, 100), (0, 400, 800, 100)) # Mặt đất
        
        # Vẽ nhân vật Duy Khang đơn giản (hình chữ nhật hoặc ảnh nếu có)
        pygame.draw.rect(screen, BLUE, (player_x, player_y, 40, 70))
        txt_player = font.render("Duy Khang", True, BLACK)
        screen.blit(txt_player, (player_x - 10, player_y - 25))
        
        # Hướng dẫn
        txt_guide = font_large.render("Nhan SPACE de di tiep va gap quai vat!", True, BLACK)
        screen.blit(txt_guide, (200, 50))
        
        # Tự động xuất hiện quái sau một khoảng hoặc bấm Space
        # Để đơn giản, ta bấm Space để gặp quái

    elif state == 'FIGHTING':
        # Vẽ mặt đất
        pygame.draw.rect(screen, (100, 200, 100), (0, 400, 800, 100))
        
        # Vẽ Duy Khang
        pygame.draw.rect(screen, BLUE, (player_x, player_y, 40, 70))
        
        # Vẽ Quái vật
        pygame.draw.rect(screen, RED, (enemy_x, enemy_y, 60, 70))
        txt_enemy = font.render(f"{enemy_name} (HP: {enemy_hp}/{enemy_max_hp})", True, BLACK)
        screen.blit(txt_enemy, (enemy_x - 20, enemy_y - 25))
        
        # Hiển thị Menu chọn vũ khí ở góc màn hình
        pygame.draw.rect(screen, (240, 240, 240), (50, 50, 400, 220))
        pygame.draw.rect(screen, BLACK, (50, 50, 400, 220), 2)
        
        txt_menu = font_large.render("CHON VU KHI (Bam phim 1-7):", True, BLACK)
        screen.blit(txt_menu, (70, 65))
        
        for i, w in enumerate(WEAPONS):
            txt_w = font.render(f"{w['name']} (Dame: {w['damage']})", True, BLACK)
            screen.blit(txt_w, (70, 100 + i * 20))

    elif state == 'EFFECT':
        # Vẽ nền và nhân vật/quái đứng yên
        pygame.draw.rect(screen, (100, 200, 100), (0, 400, 800, 100))
        pygame.draw.rect(screen, BLUE, (player_x, player_y, 40, 70))
        pygame.draw.rect(screen, RED, (enemy_x, enemy_y, 60, 70))
        
        # Hiển thị hiệu ứng chữ đánh trúng và tiếng nổ "ĐÙNG ĐÙNG!"
        txt_eff = font_large.render(f"DUNG DUNG! {current_effect_text}", True, (255, 0, 0))
        screen.blit(txt_eff, (250, 150))
        
        effect_timer -= 1
        if effect_timer <= 0:
            if enemy_hp <= 0:
                state = 'FLYING_AWAY' # Quái hết máu sẽ bay lên trời
            else:
                state = 'FIGHTING' # Quái chưa chết, tiếp tục đánh

    elif state == 'FLYING_AWAY':
        pygame.draw.rect(screen, (100, 200, 100), (0, 400, 800, 100))
        pygame.draw.rect(screen, BLUE, (player_x, player_y, 40, 70))
        
        # Quái bay vút lên cao và mờ dần
        enemy_fly_y -= 5
        pygame.draw.rect(screen, RED, (enemy_x, enemy_fly_y, 60, 70))
        
        txt_win = font_large.render("QUAI VAT DA BAY LEN TROI! TIEP TUC DI THANG...", True, (0, 150, 0))
        screen.blit(txt_win, (150, 150))
        
        if enemy_fly_y < -50:
            reset_enemy()
            state = 'WALKING'

    pygame.display.flip()
    clock.tick(60)

