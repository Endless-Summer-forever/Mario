# 主菜单
import pygame
import random
from .. import setup
from .. import tools
from .. import constants as C
from .. components import info

class MainMenu:
    def __init__(self):
        game_info = {
            'score': 0,
            'coin': 0,
            'lives': 3,
            'player_state': 'small'
        }
        self.start(game_info)

    def start(self, game_info):
        self.game_info = game_info
        self.setup_background()
        self.setup_player()
        self.setup_cursor()
        self.info = info.Info('main_menu', self.game_info)
        self.finished = False
        self.next = 'load_screen'  # 下一个状态

    def setup_background(self):
        # 背景图
        self.background = setup.GRAPHICS['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (int(self.background_rect.width * C.BG_MULTI),
                                                 int(self.background_rect.height * C.BG_MULTI)))
        # 滑动窗口
        self.viewport = setup.SCREEN.get_rect()
        self.caption = tools.get_image(setup.GRAPHICS['title_screen'], 1, 60, 176, 88, (255, 0, 220), C.BG_MULTI)

    def setup_player(self):
        self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 112, 48, 16, 33, (0, 0, 0), C.PLAYER_MULTI)

    def setup_cursor(self):
        self.cursor = pygame.sprite.Sprite()
        self.cursor.image = tools.get_image(setup.GRAPHICS['item_objects'], 0, 16, 16, 16, (0, 0, 0), C.PLAYER_MULTI)
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = (220, 355)
        self.cursor.rect = rect
        self.cursor.state = '1P'  # 初始化光标状态

    def update_cursor(self, keys):  # 更新光标位置
        if keys[pygame.K_UP]:
            self.cursor.state = '1P'
            self.cursor.rect.y = 355
        elif keys[pygame.K_DOWN]:
            self.cursor.state = '2P'
            self.cursor.rect.y = 400
        elif keys[pygame.K_RETURN]:
            self.reset_game_info()
            if self.cursor.state == '1P':
                self.finished = True
            elif self.cursor.state == '2P':
                self.finished = True

    def update(self, surface, keys):

        self.update_cursor(keys)

        surface.blit(self.background, self.viewport)
        surface.blit(self.caption, (170, 100))
        surface.blit(self.player_image, (90, 470))
        surface.blit(self.cursor.image, self.cursor.rect)

        self.info.update()
        self.info.draw(surface)

    def reset_game_info(self):
        self.game_info.update({
            'score': 0,
            'coin': 0,
            'lives': 3,
            'player_state': 'small'
        })