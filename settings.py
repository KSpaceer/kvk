


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
        self.waves = [ [ (4,), (2, 2, 1), (1, 0, 1) ],
                        ]
        self.max_level = 0
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