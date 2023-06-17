# 工具和游戏主控
import pygame
import random
import os

class Game:
    def __init__(self, state_dict, start_state):  # 实例刚产生时要做的事
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()  # 跟踪游戏运行的时间+控制帧速率
        self.keys = pygame.key.get_pressed()
        self.state_dict = state_dict
        self.state = self.state_dict[start_state]  # 初始化状态

    def update(self):  # 更新状态
        if self.state.finished:
            game_info = self.state.game_info
            next_state = self.state.next
            self.state.finished = False
            self.state = self.state_dict[next_state]
            self.state.start(game_info)  # 传给下一阶段的start
        self.state.update(self.screen, self.keys)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()

            self.update()

            pygame.display.update()
            self.clock.tick(60)

def load_graphics(path, accept=('.jpg', '.png', '.bmp', '.gif')):  # 一次性加载素材文件夹里的所有文件到字典里
    graphics = {}
    for pic in os.listdir(path):  # 遍历路径所指向的文件夹
        name, ext = os.path.splitext(pic)  # 拆分文件名(名+后缀)
        if ext.lower() in accept:  # 格式正确则载入图片
            img = pygame.image.load(os.path.join(path, pic))
            # 加快游戏画面渲染的操作
            if img.get_alpha():  # 如果图片有透明层
                img = img.convert_alpha()
            else:
                img = img.convert()
            graphics[name] = img
    return graphics

def get_image(sheet, x, y, width, height, colorkey, scale):  # 从已加载好的图片里获取部分图片的方法
    # sheet传入图片，(x,y)为所需部分图片左上角坐标，colorkey为快速抠图的底色，scale为放大/缩小倍数
    image = pygame.Surface((width, height)) #创建和方框一样大的空图层
    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
    return image

def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', 'jpg', 'bmp')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics