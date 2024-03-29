import pygame


class Settings():

    def __init__(self):
        '''Инициализирует настройки игры'''
        # Настройки экрана
        self.screen_width = 1300
        self.screen_height = 800
        self.bg_color = (100, 0, 0)
        # Настройки анимации
        self.animation_change = 0.25
        # Настройки аудио
        self.sound_volume = 5
        self._music_volume = 5
        # Настройки персонажа
        self.mc_speed_factor = 0.5
        self.attack_speed = 0.18
        self.mc_damage = 2
        self.mc_health = 5
        self.stun_duration = 1
        self.inv_duration = 2
        # Настройки волн и уровней
        # 0 - Bull, 1 - Sumo, 2 - Eater/Guru, 3 - Ninja, 4 - Boss
        self.waves = [ [(0, 1, 0), (1, 0, 1), (1, 0, 1, 0)],
                       [(1, 3, 1, 3), (3, 1, 3, 1), (3, 3, 3, 3)],
                       [(2, 1, 2), (2, 2, 1, 1), (2, 0, 2, 0), (2, 2, 1, 2, 2), (2, 2, 1, 1, 3)],
                       [tuple([i if i < 4 else 3 for j in range(5)]) for i in range(4)],
                       [(0, 1, 2, 3, 3, 2) for i in range(3)],
                       [(0, 1, 2, 3, 3, 2, 1, 0) for i in range(3)], 
                       [(4,)]]
        self.max_level = len(self.waves) - 1
        # Настройки врагов
        self.h_multiplier = 1
        # Бугаи:
        self.bull_speed_factor = 0.25
        self.bull_attack_speed = 0.2
        self.bull_cooldown = 2
        self.diana_appearance_chance = 50 # переменная для шанса появления Дианы
        # Сумоисты:
        self.sumo_speed_factor = 0.2
        self.sumo_attack_speed = 0.25
        self.sumo_cooldown = 3
        self.sumo_attack_range = 150
        # Пожиратели
        self.eater_speed_factor = 0.5
        self.eater_attack_speed = 0.2
        self.eater_cooldown = 1.5
        # Гуру
        self.guru_speed_factor = 0.5
        self.guru_attack_speed = 0.5
        self.guru_cooldown = 1.5
        # Ниндзя
        self.ninja_speed_factor = 0.4
        self.ninja_attack_speed = 0.2
        self.ninja_cooldown = 2
        self.ninja_launch_range = 500
        self.ninja_launch_cooldown = 5
        # Босс
        self.boss_speed_factor = 0.7
        self.boss_attack_speed = 0.5
        self.boss_cooldown = 15
        self.boss_ultimate_cooldown = 40
        self.boss_invincibility_duration = 0.5
        self.boss_health = 100 * self.h_multiplier
        # Ударные волны
        self.shockwave_speed = 0.75
        # Сюрикены
        self.shuriken_speed = 1
        # Призывающие круги (summoning circle - sc)
        self.sc_speed = 1.5
        # Шаровые молнии (ball lightning - bl)
        self.bl_speed = 2
        # Копья
        self.spear_speed = 4
        # Лезвия
        self.blade_speed = 3
        # Пилы
        self.saw_speed = 2
        self.maze_narrowing = 200 # Сужение лабиринта пил относительно экрана
        self.saw_amount = 7

    @property
    def music_volume(self):
        return self._music_volume

    @music_volume.setter
    def music_volume(self, value):
        pygame.mixer.music.set_volume(value/10)
        self._music_volume = value

    @music_volume.deleter
    def music_volume(self):
        del self._music_volume
