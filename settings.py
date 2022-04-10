


class Settings():

    def __init__(self):
        '''Инициализирует настройки игры'''
        # Настройки экрана
        self.screen_width = 1300
        self.screen_height = 800
        self.bg_color = (100, 0, 0)
        # Настройки анимации
        self.animation_change = 0.25
        # Настройки персонажа
        self.mc_speed_factor = 0.5
        self.attack_speed = 0.18
        self.mc_damage = 2
        self.mc_health = 5
        self.stun_duration = 1
        self.inv_duration = 2
        # Настройки волн и уровней
        self.waves = [ [[0, 0], [0, 0, 0]],
                        ]
        self.max_level = 0
        # Настройки врагов
        self.h_multiplier = 1
        # Бугаи:
        self.bull_speed_factor = 0.25
        self.bull_attack_speed = 0.2
        self.bull_cooldown = 2
        self.diana_appearance_chance = 50 # переменная для шанса появления Дианы