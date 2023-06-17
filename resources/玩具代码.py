import pygame
pygame.init()
w, h = 500, 500
pygame.display.set_mode((w, h))
screen = pygame.display.get_surface()

# 载入图片背景并缩放到宽高
bgpic = pygame.image.load("bgpic.png")
bgpic = pygame.transform.scale(bgpic, (w, h))
# 载入人物图
mario_image = pygame.image.load("mario_bros(1).png")
# 创建精灵
mario = pygame.sprite.Sprite()
mario.image = mario_image
mario.rect = mario.image.get_rect()
mario.rect.x, mario.rect.y = w/2, h/2
# 玩家组
player_group = pygame.sprite.Group()
player_group.add(mario)

# 开始游戏
while True:
    # 更新部分
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                mario.rect.y += 10
            if keys[pygame.K_UP]:
                mario.rect.y -= 10
    # 画图部分
    screen.blit(bgpic, (0, 0))  # 左上角起
    player_group.draw(screen)  # 在画布上放精灵
    pygame.display.update()



