import pygame
import json
import os
from .. import constants as C
from .. import tools, setup


class Player(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.load_data()
        self.setup_states()
        self.setup_velocities()
        self.setup_timers()
        self.load_images()

    def load_data(self):
        file_name = self.name + '.json'
        file_path = os.path.join('source/data/player', file_name)
        with open(file_path) as f:
            self.player_data = json.load(f)

    def setup_states(self):  # 主角状态
        self.state = 'stand'
        self.face_right = True
        self.dead = False
        self.big = False
        self.fire = False
        self.can_jump = True
        self.hurt_immune = False

    def setup_velocities(self):  # 设置速度
        speed = self.player_data['speed']
        self.x_vel = 0
        self.y_vel = 0

        self.max_walk_vel = speed['max_walk_speed']
        self.max_run_vel = speed['max_run_speed']
        self.max_y_vel = speed['max_y_velocity']
        self.jump_vel = speed['jump_velocity']
        self.walk_accel = speed['walk_accel']
        self.run_accel = speed['run_accel']
        self.turn_accel = speed['turn_accel']  # 急刹车转身时的加速度
        self.gravity = C.GRAVITY  # 全局重力加速度
        self.anti_gravity =C.ANTI_GRAVITY

        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

    def setup_timers(self):  # 创建计时器
        self.walking_timer = 0
        self.transition_timer = 0
        self.death_timer = 0
        self.hurt_immune_timer = 0

    def load_images(self):  # 载入主角各种帧造型
        sheet = setup.GRAPHICS['mario_bros']
        frame_rects = self.player_data['image_frames']

        self.right_small_normal_frames = []
        self.right_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []

        self.small_normal_frames = [self.right_small_normal_frames, self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames, self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames, self.left_big_fire_frames]

        self.all_frames = [
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames,
        ]

        # 设置默认左右帧库
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames

        # 遍历键值对
        for group, group_frame_rects in frame_rects.items():
            for frame_rect in group_frame_rects:
                right_image = tools.get_image(sheet, frame_rect['x'], frame_rect['y'],
                                              frame_rect['width'], frame_rect['height'], (0, 0, 0), C.PLAYER_MULTI)
                left_image = pygame.transform.flip(right_image, True, False)  # 翻转
                if group == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                elif group == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                elif group == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)

        self.frame_index = 0
        self.frames = self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

    def update(self, keys):
        # 设置角色速度并更新角色帧
        self.current_time = pygame.time.get_ticks()
        self.handle_states(keys)
        self.is_hurt_immune()

    # 根据角色所处的不同状态调用不同的方法
    def handle_states(self, keys):

        self.can_jump_or_not(keys)

        if self.state == 'stand':
            self.stand(keys)
        elif self.state == 'walk':
            self.walk(keys)
        elif self.state == 'jump':
            self.jump(keys)
        elif self.state == 'fall':
            self.fall(keys)
        elif self.state == 'die':
            self.die(keys)
        elif self.state == 'smalltobig':
            self.smalltobig(keys)
        elif self.state == 'bigtosmall':
            self.bigtosmall(keys)
        elif self.state == 'bigtofire':
            self.bigtofire(keys)

        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def can_jump_or_not(self, keys):
        if not keys[pygame.K_UP]:
            self.can_jump = True

    def stand(self, keys):
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            self.state = 'walk'
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            self.state = 'walk'
        elif keys[pygame.K_UP] and self.can_jump:
            self.state = 'jump'
            self.y_vel = self.jump_vel

    def walk(self, keys):

        if keys[pygame.K_LSHIFT]:
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel

        if keys[pygame.K_UP] and self.can_jump:
            self.state = 'jump'
            self.y_vel =self.jump_vel

        if self.current_time - self.walking_timer > self.calc_frame_duration():
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            if self.x_vel < 0:
                self.frame_index = 5  #刹车帧
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel =self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        else:  # 什么键都不按时让角色停止运动
            if self.face_right:
                self.x_vel -= self.x_accel
                if self.x_vel < 0:
                    self.x_vel = 0
                    self.state = 'stand'
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.state = 'stand'


    def jump(self, keys):
        self.frame_index = 4
        self.y_vel += self.anti_gravity
        self.can_jump = False

        if self.y_vel >= 0:
            self.state = 'fall'

        # 起跳时也可以左右移动
        if keys[pygame.K_RIGHT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        if keys[pygame.K_LEFT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)

        if not keys[pygame.K_UP]:  # 小跳
            self.state = 'fall'

    def fall(self, keys):
        self.y_vel = self.calc_vel(self.y_vel, self.gravity, self.max_y_vel)

        # 下落时也可以左右移动
        if keys[pygame.K_RIGHT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        if keys[pygame.K_LEFT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)

    def die(self, keys):
        # 避免死亡状态下会触发碰撞检测
        self.rect.y += self.y_vel
        self.y_vel += self.anti_gravity

    def go_die(self):
        self.dead = True
        self.y_vel = self.jump_vel
        self.frame_index = 6
        self.state = 'die'
        self.death_timer = self.current_time

    def smalltobig(self, keys):
        frame_dur = 65
        sizes = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]
        frames_and_dix = [(self.small_normal_frames, 0), (self.small_normal_frames, 7), (self.big_normal_frames, 0)]
        if self.transition_timer == 0:
            self.big = True
            self.transition_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time -self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, idx = frames_and_dix[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):  # 如果为变身最后一帧
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def bigtosmall(self, keys):
        frame_dur = 65
        sizes = [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_dix = [(self.small_normal_frames, 8), (self.small_normal_frames, 8), (self.big_normal_frames, 4)]
        if self.transition_timer == 0:
            self.big = False
            self.transition_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time -self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, idx = frames_and_dix[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):  # 如果为变身最后一帧
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def bigtofire(self, keys):
        frame_dur = 65
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_dix = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]
        if self.transition_timer == 0:
            self.fire = False
            self.transition_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time -self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, idx = frames_and_dix[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):  # 如果为变身最后一帧
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_big_fire_frames

    def change_player_image(self, frames, idx):
        self.frame_index = idx
        if self.face_right:
            self.right_frames = frames[0]
            self.image = self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[self.frame_index]
        # 变化时下一帧位置与上一帧统一
        last_frame_bottom = self.rect.bottom
        last_frame_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = last_frame_bottom
        self.rect.centerx = last_frame_centerx


    # 设置速度
    def calc_vel(self, vel, accel, max_vel, is_positive=True):
        if is_positive:
            return min(vel + accel, max_vel)
        else:
            return max(vel - accel, -max_vel)

    def calc_frame_duration(self):  # 函数计算不同速度帧的持续时间
        duration = -60 / self.max_run_vel * abs(self.x_vel) + 80
        return duration

    def is_hurt_immune(self):
        if self.hurt_immune:
            if self.hurt_immune_timer == 0:
                self.hurt_immune_timer = self.current_time
                self.blank_image =pygame.Surface((1, 1))
            elif self.current_time - self.hurt_immune_timer < 2000:
                # Mario由大变小后无敌的一段时间全身会一闪一闪的
                # 前50ms显示空白帧，后50ms显示实体
                if (self.current_time -self.hurt_immune_timer) % 100 < 50:
                    self.image = self.blank_image
            else:
                self.hurt_immune = False
                self.hurt_immune_timer = 0
