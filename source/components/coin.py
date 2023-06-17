import pygame
from .. import setup, tools
from .. import constants as C

def create_coin(centerx, centery, type):  # 根据type和Mario的状态创建道具
    return StaticCoin(centerx, centery)

class FlashingCoin(pygame.sprite.Sprite):  # 旋转金币类继承精灵类
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        frame_rects = [(1, 160, 7, 8), (9, 160, 7, 8), (17, 160, 7, 8), (9, 160, 7, 8)]  # 金币闪烁忽明忽暗
        self.load_frames(frame_rects)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = 280
        self.rect.y = 58
        self.timer = 0  # 计时器

    def load_frames(self, frame_rects):
        sheet = setup.GRAPHICS['item_objects']
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(sheet, *frame_rect, (0, 0, 0), C.BG_MULTI))

    def update(self):
        self.current_time = pygame.time.get_ticks()  # 获取当前时间
        frame_durations = [375, 125, 125, 125]

        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4  # 金币图案循环出现
            self.timer = self.current_time

        self.image = self.frames[self.frame_index]


class StaticCoin(pygame.sprite.Sprite):
    def __init__(self, centerx, centery):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        frame_rects = [(3, 98, 9, 15), (19, 98, 9, 15),
                        (35, 98, 9, 15), (51, 98, 9, 15)]
        self.load_frames(frame_rects)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.original_y = centery - self.rect.height / 2
        self.timer = 0  # 计时器

        self.state = 'grow'
        self.x_vel = 2
        self.direction = 1
        self.y_vel = -1
        self.gravity = 1
        self.max_y_vel = 8

    def load_frames(self, frame_rects):
        sheet = setup.GRAPHICS['item_objects']
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(sheet, *frame_rect, (0, 0, 0), C.BG_MULTI))

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        self.check_y_collisions(level)

        if self.rect.x < 0 or self.rect.y > C.SCREEN_H:
            self.kill()

    def check_x_collisions(self, level):
        sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if sprite:
            if self.direction:  # 向右
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1

    def check_y_collisions(self, level):
        check_group = pygame.sprite.Group(level.ground_items_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = 'walk'

        level.check_will_fall(self)

    def update(self, level):
        self.current_time = pygame.time.get_ticks()  # 获取当前时间
        frame_durations = [375, 125, 125, 125]

        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4  # 金币图案循环出现
            self.timer = self.current_time

        self.image = self.frames[self.frame_index]

        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.original_y:
                self.state = 'walk'
        elif self.state == 'walk':
            pass
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity

        if self.state != 'grow':
            self.update_position(level)

        '''if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.original_y:
                self.state = 'rest' 
                '''
