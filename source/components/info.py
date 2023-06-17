import pygame
from .. import constants as C
from . import coin
from .. import setup, tools
pygame.font.init()

class Info:
    def __init__(self, state, game_info):
        self.state = state  # 阶段
        self.game_info = game_info
        self.create_state_labels()  # 创造某个阶段特有的文字
        self.create_info_labels()  # 创造通用文字
        self.flash_coin = coin.FlashingCoin()  # 创建旋转金币

    def create_state_labels(self):
        self.state_labels = []
        if self.state == 'main_menu':
            self.state_labels.append((self.create_label('1  PLAYER  GAME'), (272, 360)))
            self.state_labels.append((self.create_label('2  PLAYER  GAME'), (272, 405)))
            self.state_labels.append((self.create_label('TOP - '), (305, 460)))
            self.state_labels.append((self.create_label('000000'), (415, 460)))
        elif self.state == 'load_screen':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1 - 1'), (430, 200)))
            self.state_labels.append((self.create_label('X    {}'.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 177, 80, 15, 16, (0, 0, 0), C.BG_MULTI)
        elif self.state == 'game_over':
            self.state_labels.append((self.create_label('GAME OVER'), (280, 300)))

    def create_info_labels(self):
        self.info_labels = []
        self.info_labels.append((self.create_label('MARIO'), (75, 30)))
        self.info_labels.append((self.create_label('WORLD'), (450, 30)))
        self.info_labels.append((self.create_label('TIME'), (625, 30)))
        self.info_labels.append((self.create_label('000000'), (75, 55)))
        self.info_labels.append((self.create_label('x00'), (300, 55)))
        self.info_labels.append((self.create_label('1 - 1'), (480, 55)))

    def create_label(self, label, size=40, width_scale=1.25, height_scale=1):
        font = pygame.font.SysFont(C.FONT, size)  # 可使用系统自带的字体
        label_image = font.render(label, 1, (255, 255, 255))  # 将文字转为图片，白色字体，1是产生锯齿效果
        # 产生锯齿状效果
        rect = label_image.get_rect()
        label_image = pygame.transform.scale(label_image, (int(rect.width * width_scale), int(rect.height * height_scale)))

        return label_image

    def update(self):
        self.flash_coin.update()

    def draw(self, surface):
        for label in self.state_labels:
            surface.blit(label[0], label[1])  # (图片, 位置)
        for label in self.info_labels:
            surface.blit(label[0], label[1])
        surface.blit(self.flash_coin.image, self.flash_coin.rect)

        if self.state == 'load_screen':
            surface.blit(self.player_image, (300, 270))