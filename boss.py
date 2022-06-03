
import gc
from itertools import cycle
from random import randint
from time import monotonic

import pygame

import enemy_animation as an
from enemy import Enemy
from etimer import Timer
from fist import Fist
from MC import MainCharacter
from mediator import Mediator
from settings import Settings
from stats import Stats
from audiosounds import Audio



class Boss(Enemy):
    '''Пятый тип врагов - босс'''

    def __init__(self, mediator: Mediator):
        super().__init__(mediator)
        self.mediator = mediator
        # Повышение скорости главного персонажа
        new_mc_speed = self.mediator.get_value('mc', 'speed') * 2
        self.mediator.set_value('mc', 'speed', f'{new_mc_speed}')
        # Скорость босса
        self.speed = self.mediator.get_value('ai_settings', 'boss_speed_factor')
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'boss'
        # Инициализация здоровья и панели здоровья
        self.health = self.mediator.get_value('ai_settings', 'boss_health')
        from graphic import BossHealth
        self.healthbar = BossHealth(self)
        # Загрузка изображения
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/boss/standing.png').convert_alpha() 
        # Руки на картинке не учитываются, поэтому основной прямоугольник
        # задаем сами 
        self.rect = pygame.Rect(-500, -500, 110, 414)
        # Враг появляется сверху
        self.spawning_point()
        # Сохранение координат центра в виде вещественных чисел
        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)
        # Сохраняем скорость атаки и время перезарядки из настроек
        self.ats = self.mediator.get_value('ai_settings', 'boss_attack_speed')
        self.cooldown = self.mediator.get_value('ai_settings', 'boss_cooldown')
        self.ultimate_cooldown = self.mediator.get_value(
            'ai_settings', 'boss_ultimate_cooldown')
        # Флаг неуязвимости (босса нельзя оглушить, поэтому он получает неуязвимость на время)
        # Т.к. он может делать другие действия во время неуязвимости, 
        # использовать обычный таймер (Enemy.timer) нельзя - он используется
        # для этих действий. Для отслеживания неуязвимости добавим новый таймер
        self.is_invincible = False
        self.invin_timer = 0
        # Таймер перезарядки для ультимативной атаки
        # (изначально на середине перезарядки)
        self.ultimate_cooldown_timer = monotonic() - self.ultimate_cooldown/2
        # Таймер перезарядки обычной атаки изначально на середине перезарядки
        self.cooldown_timer = monotonic() - self.cooldown/2
        # Номер ультимативной и обычной способности
        self.ultimate_number = None
        self.common_attack_number = None
        # Флаги применения обычной и ультимативной атак
        self.using_common_attack = False
        self.using_ultimate = False
        # Иногда врагу нужно переместиться на позицию, чтобы
        # начать применение способности. Следующий флаг
        # отслеживает то, выбрана ли нужная позиция
        self.position_is_chosen = False
        # Флаг отслеживания того, что враг на позиции
        self.in_position = False
        # Координаты позиции
        self.positionx = None
        self.positiony = None
        # Определяем количество кадров для различных атак
        self.define_attack_frames()
        # Запуск музыки
        self.mediator.set_value('audio', 'current_music', f'boss{self.surname}')
        Stats.state_to_audio[Stats.GAMEACTIVE] = f'boss{self.surname}'

    def __del__(self):
        audio: Audio = self.mediator.get_value('audio')
        if 'spinning' in audio.sounds.keys():
            audio.sounds.pop('spinning')
        new_mc_speed = self.mediator.get_value('mc', 'speed')
        self.mediator.set_value('mc', 'speed', f'{new_mc_speed}')
        return super().__del__()
    
    def spawning_point(self):
        '''Определяет начальное положение врага'''
        self.rect.centerx = self.mediator.get_value('screen_rect', 'centerx')
        self.rect.centery = -int(self.rect.width/2)
        self.change_rect()

    def define_attack_frames(self):
        '''Определяет количество кадров в атаках'''
        self.ultimate_frames = 6
        if self.surname == 'S':
            self.common_attack_frames = 7
        else:
            self.common_attack_frames = 2

    @staticmethod
    def lava_blit_decorator(method):
        '''Декоратор для прорисовки лавы во время смерти'''
        def wrapper(self, *args, **kwargs):
            if self.is_dead:
                self.mediator.blit_surface(self.backlava, self.bl_rect)
            method(self, *args, **kwargs)
            if self.is_dead:
                self.mediator.blit_surface(self.frontlava, self.fl_rect)
        return wrapper
    
    @lava_blit_decorator.__func__
    def blitme(self):
        '''Рисует врага в текущей позиции'''
        self.mediator.blit_surface(self.image, self.an_rect)
        self.additional_draw()

    def change_rect(self):
        '''Заменяет прямоугольник анимаций.
        Низ и центр по Х совпадает с соответствующими хар-ками основного
        прямоугольника.'''
        self.an_rect = self.image.get_rect()
        self.an_rect.bottom = self.rect.bottom
        self.an_rect.centerx = self.rect.centerx

    def update(self):
        '''Обновление состояния врага(перемещение, атаки или смерть)'''
        # Если враг жив
        if self.health > 0:
            self.damage_invin_processing()
            if not self.is_punching:
                screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
                # Функция движения находится в условии, т.к. если
                # босс на нужном месте, то должна проигрываться какая-то анимация;
                # в данном случае это анимация вертикального движения.
                if self.movement(screen_rect.centerx, 
                    screen_rect.centery):
                    an.going_vertical_animation(self)
                
                # Если нет перезарядки, применяет ультимативную атаку
                if self.mediator.current_time() - self.ultimate_cooldown_timer \
                    >= self.ultimate_cooldown:
                    self.initiate_ultimate()
                    return
                # Если нет перезарядки, применяет обычную атаку
                elif self.mediator.current_time() - self.cooldown_timer >= \
                    self.cooldown:
                    self.initiate_common_attack()
                    return
            else:
                if self.using_ultimate:
                    self.ultimate()
                else:
                    self.common_attack()
        else:    
            self.death_animation()
        self.blitme()

        
    def movement(self, x, y, multiplier: int = 1) -> bool:
        '''Перемещение босса. 
        Возвращает bool, соответствующий нахождению босса в нужном месте'''
        where_am_i_x, where_am_i_y = self.check_position(x, y) 
            # Сначала идет перемещение по вертикали
        if not where_am_i_y:
            self.vertical_movement(y)
                # Затем по горизонтали
        elif not where_am_i_x:
            self.horizontal_movement(x, multiplier)
        # Для использования в условии
        return where_am_i_x and where_am_i_y

    @staticmethod
    def zubkov_third_ultimate_decorator(method):
        '''
        Декоратор для функции обработки неуязвимости,
        поскольку во время третьей ультимативной атаки 
        Зубкова неуязвимость не должна
        спадать.
        '''
        def wrapper(self, *args, **kwargs):
            a = bool(self.using_ultimate)
            b = bool(self.ultimate_number == 2)
            c = bool(self.surname == 'Z')
            if not (a and b and c):
                method(self, *args, **kwargs)
            else:
                
                return None
        return wrapper

    
    
    @zubkov_third_ultimate_decorator.__func__
    def damage_invin_processing(self):
        '''Обработка получения урона и неуязвимости'''
        # Если босс не неуязвим и в него попал кулак главного персонажа, он получает урон
        mc_fist: Fist = self.mediator.get_value('mc_fist')
        if not self.is_invincible and self.rect.colliderect(mc_fist.rect):
            self.get_damage()
        # Если босс неуязвим и уже прошло время его неуязвимости, он ее теряет
        elif self.is_invincible and self.mediator.current_time() - self.invin_timer \
                >= self.mediator.get_value(
                'ai_settings', 'boss_invincibility_duration'):
                    self.is_invincible = False
                


    def get_damage(self):
        '''Получение урона'''
        self.health -= self.mediator.get_value('ai_settings', 'mc_damage')
        self.is_invincible = True
        self.mediator.call_method('audio', 'play_sound', '"punch"')
        self.invin_timer = monotonic()

    def check_position(self, x: int, y: int) -> tuple[bool, bool]:
        '''Определяет то, находится ли босс в нужном положении. 
        Возвращает два флага для координат.'''
        where_am_i_x = self.rect.centerx in range(x - 10, x + 10)
        where_am_i_y = self.rect.centery in range(y - 10, y + 10)
        return where_am_i_x, where_am_i_y

    def vertical_movement(self, y: int):
        '''Перемещение босса по вертикали'''
        an.going_vertical_animation(self)
        if self.rect.centery < y:
            self.centery += self.speed
        else:
            self.centery -= self.speed
        # Конвертируем вещественное значение в целочисленное
        self.rect.centery = int(self.centery)

    def horizontal_movement(self, x: int, multiplier: int = 1):
        '''Перемещение босса по горизонтали'''
        if self.rect.centerx > x:
            an.going_left_animation(self)
            self.centerx -= self.speed * multiplier
        else:
            an.going_right_animation(self)
            self.centerx += self.speed * multiplier
        # Конвертируем вещественное значение в целочисленное
        self.rect.centerx = int(self.centerx)

    def initiate_ultimate(self):
        '''Начинает применение ультимативной атаки'''
        self.using_ultimate = True
        self.is_punching = True
        self.ultimate_number = randint(0, 2)

    def initiate_common_attack(self):
        '''Начинает применение обычной атаки'''
        self.using_common_attack = True
        self.is_punching = True
        self.common_attack_number = randint(0, 1)

    def ultimate(self):
        '''Применение ультимативной атаки'''
        if self.ultimate_number == 0:
            # Призывает врагов
            self.summon_enemies()
        elif self.ultimate_number == 1:
            if self.surname == 'S':
                #Запуск молний
                self.launch_lightnings()
            else:
                # Запуск копий
                self.launch_spears()
        else:
            if self.surname == 'S':
                # Добежать от босса через лезвия
                self.blade_runner()
            else:
                # Убежать от босса через пилы
                self.saw_runner()

    def common_attack(self):
        '''Применение обычной атаки'''
        # Не перепутать: тут сначала идет номер 1, потом номер 0
        if self.common_attack_number:
            if self.surname == 'S':
                # Притягивающее вращение
                self.pulling_spin()
            else:
                # Залп ударных волн
                self.shockwave_barrage()
        else:
            if self.surname == 'S':
                # Преследующее торнадо
                self.chasing_tornado()
            else:
                # Создание трещины
                self.create_crack()

    def pulling_spin(self):
        '''Атака, при которой босс вращается и притягивает главного персонажа'''
        if not self.in_position:
            self.in_position = True
            self.timer = monotonic()
            self.mediator.call_method('audio', 'play_method', '"spinning"', '-1')
            # Во время атаки таймер перезарядки используется
            # как таймер для отсчета начала нанесения урона и притяжения,
            # а также конца применения атаки
            self.cooldown_timer = monotonic()
            self.frame_cycler = cycle(
                [i for i in range(self.common_attack_frames)])
        self.spinning_animation()
        if self.mediator.current_time() - self.cooldown_timer >= 1.5:
            mc: MainCharacter = self.mediator.get_value('mc')
            # Притяжение персонажа
            if not mc.rect.colliderect(self.an_rect):
                self.pulling_mc(mc)
            elif not mc.invincible:
                self.deal_nonstunning_damage(mc)
        if self.mediator.current_time() - self.cooldown_timer >= 4.5:
            self.finish_common_attack()

    def pulling_mc(self, mc: MainCharacter):
        '''Притяжение главного персонажа'''
        pulling_speed = self.mediator.get_value(
            'ai_settings', 'mc_speed_factor')/2
        if mc.centerx < self.rect.centerx:
            mc.centerx += pulling_speed
        else:
            mc.centerx -= pulling_speed
        if mc.centery < self.rect.centery:
            mc.centery += pulling_speed
        else:
            mc.centery -= pulling_speed

    def chasing_tornado(self):
        '''Атака, при которой босс вращается и идет за главным персонажем'''
        if not self.in_position:
            self.in_position = True
            self.timer = monotonic()
            self.mediator.call_method('audio', 'play_sound', '"spinning"', '-1')
            # Таймер перезарядки используется как таймер начала
            # преследования и нанесения урона
            self.cooldown_timer = monotonic()
            self.frame_cycler = cycle(
                [i for i in range(self.common_attack_frames)])
            self.speed /= 1.5
        self.spinning_animation()
        if self.mediator.current_time() - self.cooldown_timer >= 1.5:
            mc: MainCharacter = self.mediator.get_value('mc')
            if not mc.rect.colliderect(self.an_rect):
                self.chasing_mc(mc)
            elif not mc.invincible:
                self.deal_nonstunning_damage(mc)
        if self.mediator.current_time() - self.cooldown_timer >= 5:
            self.speed *= 1.5
            self.finish_common_attack()

    def chasing_mc(self, mc: MainCharacter):
        '''Преследование главного персонажа'''
        if self.rect.centerx < mc.rect.centerx:
            self.centerx += self.speed
        else:
            self.centerx -= self.speed
        if self.rect.centery < mc.rect.centery:
            self.centery += self.speed
        else:
            self.centery -= self.speed
        self.rect.centerx = int(self.centerx)
        self.rect.centery = int(self.centery)
        self.change_rect()

    def deal_nonstunning_damage(self, mc: MainCharacter):
        '''Наносит главному персонажу урон, не оглушая его'''
        mc.health -= 1
        mc.invincible = True
        mc.invin_timer = monotonic()
        mc.attack_timer = 0
    
    
    def shockwave_barrage(self):
        '''Атака с вращением и вызовом ударных волн'''
        if not self.in_position:
            self.in_position = True
            self.timer = monotonic()
            self.mediator.call_method('audio', 'play_sound', '"spinning"', '-1')
            # Во время атаки таймер перезарядки используется
            # как таймер прекращения атаки
            self.cooldown_timer = monotonic()
            # Таймер запуска (ВНЕЗАПНО) используется для запуска ударных волн
            self.launch_cooldown_timer = monotonic()
            self.frame_cycler = cycle(
                [i for i in range(self.common_attack_frames)])
        self.spinning_animation()
        if self.mediator.current_time() - self.launch_cooldown_timer >= 1:
            self.launch_shockwaves()
        if self.mediator.current_time() - self.cooldown_timer >= 5.5:
            self.finish_common_attack()

    def launch_shockwaves(self):
        '''Запуск ударных волн во время вращения'''
        from shockwave import Shockwave
        for i in range(2):
            for j in range(3):
                self.mediator.call_method(
                    'audio', 'play_sound', '"launch_shockwave"')
                new_shockwave = Shockwave(
                    self.mediator, True if i else False, boss=self)
                self.mediator.extend_collection('en_fists', new_shockwave)
        self.launch_cooldown_timer = monotonic()

    def create_crack(self):
        '''Атака, создающая разлом'''
        if not self.position_is_chosen:
            self.choose_cracking_point()
        if self.movement(self.positionx, self.positiony, 2):
            if not self.in_position:
                self.in_position = True
                self.timer = monotonic()
            self.cracking_animation()
            # Поскольку босса нельзя оглушить, флаг оглушения здесь используется
                # как флаг создания разлома
            if not self.is_stunned and (self.mediator.current_time() - self.timer 
                >= 5/2 * self.ats):
                self.new_crack_creation()
            if self.mediator.current_time() - self.timer >= 4 * self.ats:
                self.is_stunned = False
                self.finish_common_attack()

    def new_crack_creation(self):
        '''Создание нового разлома'''
        from boss_projectiles import Crack

        self.mediator.call_method('audio', 'play_sound', '"launch_shockwave"')
        crack_y = self.an_rect.top + 89
        x_addition = 257 if self.right_punch else 13
        crack_x = self.an_rect.left + x_addition
        new_crack = Crack(crack_x, crack_y, self.mediator)
        self.mediator.extend_collection('en_fists', new_crack)
        self.is_stunned = True

    def cracking_animation(self):
        '''Анимация вызова разлома'''
        for i in range(6):
            if (i + 1)/2 * self.ats > self.mediator.current_time()\
                - self.timer >= i/2 * self.ats:
                if i != 5:
                    self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/' +
                            f'boss/cracking{i + 1}.png').convert_alpha()
                else:
                    self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/' +
                            f'boss/spinning{int(self.right_punch) + 1}' + 
                            '.png').convert_alpha()
                self.change_rect()

    def choose_cracking_point(self):
        '''Выбирает точку для вызова разлома'''
        mc_rect: pygame.Rect = self.mediator.get_value('mc', 'rect')
        if self.rect.centerx < mc_rect.centerx:
            self.right_punch = True
            self.define_position(mc_rect.centerx - 135, 
                    mc_rect.centery - 37)
        else:
            self.right_punch = False
            self.define_position(mc_rect.centerx + 135, 
                    mc_rect.centery - 37)
                        
    def spinning_animation(self):
        '''Анимация вращения босса во время обычной атаки'''
        if self.ats/2 >= self.mediator.current_time() - self.timer:
            self.image = pygame.image.load(f'images/K{self.surname}Enemies/' +
                f'boss/spinning{self.frame_cycler.__next__() + 1}.png').convert_alpha()
            self.change_rect()
            self.timer = monotonic()
        
    def summon_enemies(self):
        '''Призывает врагов'''
        if not self.in_position:
            # Призыв может начаться в любой позиции
            self.timer = monotonic()
            self.in_position = True
        self.ultimate_animation('summon')
        if self.mediator.current_time() - self.timer >= 6 * self.ats:
            from boss_projectiles import SummoningCircle
            summoning_circle1 = SummoningCircle(self, True)
            summoning_circle2 = SummoningCircle(self, False)
            self.mediator.extend_collection(
                'en_fists', summoning_circle1, summoning_circle2)
            self.finish_ultimate()

    def launch_lightnings(self):
        '''Запуск шаровых молний'''
        if not self.position_is_chosen:
            screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
            self.define_position(screen_rect.centerx, screen_rect.centery)
        if self.movement(self.positionx, self.positiony):
            if not self.in_position:
                self.timer = monotonic()
                self.in_position = True
                # Выпуск молний происходит с задержкой в 1/4 секунды
                self.delay = 0.25
                self.launch_cooldown_timer = monotonic() + 6 * self.ats
            self.ultimate_animation('lightning')
            if self.mediator.current_time() - self.launch_cooldown_timer >= 0:
                from boss_projectiles import BallLightning
                new_ball_lightning = BallLightning(self)
                self.mediator.extend_collection('en_fists', new_ball_lightning)
                self.launch_cooldown_timer += self.delay
            # Выпуск молний продолжается пять секунд
            if self.mediator.current_time() - self.timer >= 6 * self.ats + 5:
                self.finish_ultimate()

    

    def launch_spears(self):
        '''Запуск копий'''
        if not self.position_is_chosen:
            screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
            self.define_position(screen_rect.centerx, 
                screen_rect.centery)
        if self.movement(self.positionx, self.positiony):
            if not self.in_position:
                self.timer = monotonic()
                self.in_position = True
                # Запуск копий происходит с задержкой в 1/3 секунды
                self.delay = 0.33
                self.launch_cooldown_timer = monotonic() + 6 * self.ats
            self.ultimate_animation('spears')
            if self.mediator.current_time() - self.launch_cooldown_timer >= 0:
                from boss_projectiles import SpearTip
                new_spear_tip = SpearTip(self)
                self.mediator.extend_collection('en_fists', new_spear_tip)
                self.launch_cooldown_timer += self.delay
            # Запуск копьев продолжается пять секунд
            if self.mediator.current_time() - self.timer >= 6 * self.ats + 5:
                self.finish_ultimate()

    def blade_runner(self):
        '''Забег с лезвиями'''
        if not self.position_is_chosen:
            x = self.define_direction()
            self.define_position(x, self.mediator.get_value(
                'screen_rect', 'centery'))
        if self.movement(self.positionx, self.positiony, 2):
            if not self.in_position:
                self.timer = monotonic()
                self.in_position = True
                # Запуск лезвий происходит с задержкой в секунду
                self.delay = 1
                self.launch_cooldown_timer = monotonic() + 3 * self.ats
                # Данная ультимативная способность прерывается при нанесении боссу урона
                # поэтому нужно запомнить здоровье на время начала применения
                self.ultimate_starting_health = self.health
            self.ultimate_animation('blades', 2, True)
            # Условие построено так, что персонажа переносит только после того,
            # как анимация босса проигралась
            if self.mediator.current_time() - self.launch_cooldown_timer >= 0 \
                and self.moving_mc():
                from boss_projectiles import Blade
                for n in range(3):
                    new_blade = Blade(self)
                    self.mediator.extend_collection('en_fists', new_blade)
                self.launch_cooldown_timer += self.delay
            if self.health != self.ultimate_starting_health:
                self.finish_ultimate()

    def saw_runner(self):
        '''Забег с пилами'''
        if not self.position_is_chosen:
            x = self.define_direction(-1)
            self.define_position(x, self.mediator.get_value(
                'screen_rect', 'centery'))
        if self.movement(self.positionx, self.positiony, 2):
            if not self.in_position:
                self.timer = monotonic()
                self.in_position = True
                self.is_invincible = True
                self.summoned_saws = False
            self.ultimate_animation('maze', 2)
            # После конца времени персонаж перемещается. Когда персонаж
            # переместился, призываются пилы и цель, которую нужно достичь
            mc_rect: pygame.Rect = self.mediator.get_value('mc', 'rect')
            if self.mediator.current_time() - self.timer\
                >= 3 * self.ats and self.moving_mc():
                # Призыв пил происходит единожды, также инициализируется цель
                if not self.summoned_saws:
                    from boss_projectiles import Saw
                    self.summoned_saws = True
                    self.create_target_surface(mc_rect)
                    saw_amount = self.mediator.get_value('ai_settings')
                    saw_amount = randint(saw_amount - 2, saw_amount + 2) + 1
                    for saw in range(saw_amount):
                        new_saw = Saw(self)
                        self.mediator.extend_collection('en_fists', new_saw)
                
                elif mc_rect.colliderect(self.target_rect):
                    from boss_projectiles import Saw
                    self.mediator.call_method('audio', 'stop_audio', '"saw"')
                    self.mediator.call_method('audio', 'play_sound', '"target_achieved"')
                    Saw.vertical_positions = [0,]
                    Saw.horizontal_positions = [0,]
                    del self.target_surface
                    del self.target_rect
                    self.is_invincible = False
                    self.finish_ultimate()
                
        
    def ultimate_animation(self, ultimate_name: str, 
        animation_speed_factor: int = 1, side_does_matter: bool = False):
        '''Анимация применения ультимативной способности'''  
        if side_does_matter:
            side_factor = '_' + str(int(not self.side))
        else:
            side_factor = ''            
        for number in range(self.ultimate_frames):
            if (number + 1)/animation_speed_factor * self.ats >\
                self.mediator.current_time() - self.timer >=\
                number/animation_speed_factor * self.ats:
                if number < 3:
                    self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies' +
                        f'/boss/ultimate{number + 1}.png').convert_alpha()
                    self.change_rect()
                else:
                    self.image = pygame.image.load(f'images/K{self.surname}' +
                        f'Enemies/boss/{ultimate_name}{number - 2}' 
                        + side_factor + '.png').convert_alpha()

   
    def create_target_surface(self, mc_rect : pygame.Rect):
        '''Создает поверхность цели, которую главному персонажу
        нужно достичь.'''
        self.target_surface = pygame.Surface((mc_rect.width, mc_rect.height))
        self.target_surface.fill((8, 255, 251)) # голубой цвет
        self.target_surface.set_alpha(127) # полупрозрачный
        self.target_rect = self.target_surface.get_rect()
        # Цель в противоположной стороне от босса
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        if self.positionx > screen_rect.centerx:
            self.target_rect.left = screen_rect.left
        else:
            self.target_rect.right = screen_rect.right
        self.target_rect.centery = screen_rect.centery

    def additional_draw(self):
        '''Отображение дополнительных элементов на экране'''
        if hasattr(self, 'target_surface'):
            self.mediator.blit_surface(self.target_surface, self.target_rect)
        if hasattr(self, 'healthbar'):
            self.healthbar.blitme()

    
    def moving_mc(self) -> bool:
        '''Отталкивание/притягивание главного персонажа'''
        mc: MainCharacter = self.mediator.get_value('mc')
        if self.mc_achieved_position:
            # Для подстановки в условие
            return True
        mc.centerx += 2 * mc.speed \
            * self.mc_dir_sign
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        if not screen_rect.contains(mc.rect):
            self.mc_achieved_position = True
        return False

    def define_direction(self, kind_of_action: int = 1):
        '''Определяет то, в какую сторону полетит босс
        и отлетит главный персонаж'''
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        # Сторона, в которую полетит босс
        self.side = randint(0, 1)
        if self.side:
            x = screen_rect.right - int(self.rect.width/2)
                # В какую сторону отбросит главного персонажа
                # kind_of_action определяет, что происходит с персонажем:
                # его притягивает или отталкивает от босса
            self.mc_dir_sign = -kind_of_action
        else:
            x = screen_rect.left + int(self.rect.width/2)
            self.mc_dir_sign = kind_of_action
            # Флаг достижения главным персонажем 
        self.mc_achieved_position = False
        return x


    def define_position(self, x, y):
        '''Определяет позицию, выбранную для проведения атаки'''
        self.positionx = x
        self.positiony = y
        self.position_is_chosen = True 
            
    def finish_ultimate(self):
        '''Заканчивает применение ультимативной атаки'''
        self.is_punching = False
        self.using_ultimate = False
        self.position_is_chosen = False
        self.in_position = False
        self.ultimate_cooldown_timer = monotonic()

    def finish_common_attack(self):
        '''Заканчивает применение обычной атаки'''
        audio: Audio = self.mediator.get_value('audio')
        if 'spinning' in audio.sounds.keys():
            audio.stop_sound('spinning')
        self.is_punching = False
        self.using_common_attack = False
        self.position_is_chosen = False
        self.in_position = False
        self.cooldown_timer = monotonic()

    def death_animation(self):
        '''Анимация смерти босса'''
        if not self.is_dead:
            self.mediator.call_method('audio', 'stop_music')
            self.mediator.call_method('audio', 'play_sound', '"boss_death"')
            self.is_dead = True
            self.timer = monotonic()
            self.image = pygame.image.load(
                f'images/K{self.surname}Enemies/boss/death.png').convert_alpha()
            self.change_rect()
            self.frontlava = pygame.image.load(f'images/' + 
                'front_lava.png').convert_alpha()
            self.backlava = pygame.image.load(f'images/' + 
            'back_lava.png').convert_alpha()
            # fl - frontlava, bl - backlava
            self.fl_rect = self.frontlava.get_rect()
            self.bl_rect = self.backlava.get_rect()
            self.fl_rect.centerx = self.bl_rect.centerx = self.an_rect.centerx
            self.bl_rect.centery = self.an_rect.bottom
            self.fl_rect.bottom = self.bl_rect.bottom
        self.image = self.image.subsurface(
            pygame.Rect(0, 0, self.an_rect.width, self.an_rect.height - 1))
        self.an_rect = self.image.get_rect()
        if not self.an_rect.height:
            self.kill()
            # Необходимо удалить ссылку на панель здоровья, чтобы она и босс не ссылались друг на друга
            # и не было никаких ссылок на босса
            del self.healthbar
            return
        self.an_rect.centerx = self.bl_rect.centerx
        self.an_rect.bottom = self.bl_rect.centery


        
        
            


    

        