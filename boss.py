
from random import randint
from time import monotonic
import pygame
import enemy_animation as an
from enemy import Enemy
from settings import Settings
from MC import MainCharacter
from stats import Stats
from etimer import Timer
from fist import Fist

class Boss(Enemy):
    '''Пятый тип врагов - босс'''

    def __init__(self, screen: pygame.Surface, ai_settings: Settings, 
        mc: MainCharacter, st: Stats, timer: Timer, cur_time: Timer):
        super().__init__(screen, ai_settings, mc, st, timer, cur_time)
        # Повышение скорости главного персонажа
        self.ai_settings.mc_speed_factor *= 2
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'boss'
        # Инициализация здоровья
        self.health = 100 * self.ai_settings.h_multiplier
        # Загрузка изображения
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/boss/standing.png') 
        # Руки на картинке не учитываются, поэтому основной прямоугольник
        # задаем сами 
        self.rect = pygame.Rect(-500, -500, 110, 414)
        # Враг появляется сверху
        self.spawning_point()
        # Сохранение координат центра в виде вещественных чисел
        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)
        # Сохраняем скорость атаки и время перезарядки из настроек
        self.ats = ai_settings.boss_attack_speed
        self.cooldown = ai_settings.boss_cooldown
        self.ultimate_cooldown = ai_settings.boss_ultimate_cooldown
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
        self.cooldown_timer = self.cooldown/2
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

    def __del__(self):
        self.ai_settings.mc_speed_factor /= 2
        return super().__del__()
    
    def spawning_point(self):
        '''Определяет начальное положение врага'''
        self.rect.centerx = self.screen_rect.centerx
        self.rect.centery = -int(self.rect.width/2)
        self.change_rect()

    def define_attack_frames(self):
        '''Определяет количество кадров в атаках'''
        self.ultimate_frames = 6
        if self.surname == 'S':
            self.common_attack_frames = 7
        else:
            self.common_attack_frames = 2

    def blitme(self):
        '''Рисует врага в текущей позиции'''
        self.screen.blit(self.image, self.an_rect)

    def change_rect(self):
        '''Заменяет прямоугольник анимаций.
        Низ и центр по Х совпадает с соответствующими хар-ками основного
        прямоугольника.'''
        self.an_rect = self.image.get_rect()
        self.an_rect.bottom = self.rect.bottom
        self.an_rect.centerx = self.rect.centerx

    def update(self, fist: Fist, enemies: pygame.sprite.Group, 
        en_fists: pygame.sprite.Group):
        '''Обновление состояния врага(перемещение, атаки или смерть)'''
        # Если враг жив
        if self.health > 0:
            self.damage_invin_processing(fist)
            if not self.is_punching:
                # Функция движения находится в условии, т.к. если
                # босс на нужном месте, то должна проигрываться какая-то анимация
                # в данном случае это анимация вертикального движения.
                if self.movement(self.screen_rect.centerx, 
                    self.screen_rect.centery):
                    an.going_vertical_animation(self)
                
                # Если нет перезарядки, применяет ультимативную атаку
                if self.cur_time.time - self.ultimate_cooldown_timer \
                    >= self.ultimate_cooldown:
                    self.initiate_ultimate()
                    return
                # Если нет перезарядки, применяет обычную атаку
                elif self.cur_time.time - self.cooldown_timer >= \
                    self.cooldown:
                    pass
                    #self.initiate_common_attack()
                    #return
            else:
                if self.using_ultimate:
                    self.ultimate(en_fists)
                else:
                    self.common_attack()
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

    def damage_invin_processing(self, fist: Fist):
        '''Обработка получения урона и неуязвимости'''
        # Если босс не неуязвим и в него попал кулак главного персонажа, он получает урон
        if not self.is_invincible and self.rect.colliderect(fist.rect):
            self.get_damage()
        # Если босс неуязвим и уже прошло время его неуязвимости, он ее теряет
        elif self.is_invincible and self.cur_time.time - self.invin_timer \
                >= self.ai_settings.boss_invincibility_duration:
            self.is_invincible = False
                


    def get_damage(self):
        '''Получение урона'''
        self.health -= self.ai_settings.mc_damage
        self.is_invincible = True
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
            self.centery += self.ai_settings.boss_speed_factor
        else:
            self.centery -= self.ai_settings.boss_speed_factor
        # Конвертируем вещественное значение в целочисленное
        self.rect.centery = int(self.centery)

    def horizontal_movement(self, x: int, multiplier: int = 1):
        '''Перемещение босса по горизонтали'''
        if self.rect.centerx > x:
            an.going_left_animation(self)
            self.centerx -= self.ai_settings.boss_speed_factor * multiplier
        else:
            an.going_right_animation(self)
            self.centerx += self.ai_settings.boss_speed_factor * multiplier
        # Конвертируем вещественное значение в целочисленное
        self.rect.centerx = int(self.centerx)

    def initiate_ultimate(self):
        '''Начинает применение ультимативной атаки'''
        self.using_ultimate = True
        self.is_punching = True
        self.ultimate_number = randint(2, 2)

    def initiate_common_attack(self):
        '''Начинает применение обычной атаки'''
        self.using_common_attack = True
        self.is_punching = True
        self.common_attack_number = randint(0, 1)

    def ultimate(self, en_fists):
        '''Применение ультимативной атаки'''
        if self.ultimate_number == 0:
            # Призывает врагов
            self.summon_enemies(en_fists)
        elif self.ultimate_number == 1:
            if self.surname == 'S':
                #Запуск молний
                self.launch_lightnings(en_fists)
            else:
                # Запуск копий
                self.launch_spears(en_fists)
        else:
            if self.surname == 'S':
                # Добежать от босса через лезвия
                self.blade_runner(en_fists)
            else:
                # Убежать от босса через пилы
                self.saw_runner(en_fists)

    def common_attack(self):
        '''Применение обычной атаки'''
        if self.common_attack_number:
            if self.surname == 'S':
                self.finish_common_attack()
                # Притягивающее вращение
                #self.pulling_spin()
            else:
                self.finish_common_attack()
                # Залп ударных волн
                #self.shockwave_barrage()
        else:
            if self.surname == 'S':
                self.finish_common_attack()
                # Преследующее торнадо
                #self.chasing_tornado()
            else:
                self.finish_common_attack()
                # Создание трещины
                #self.create_crack()

    def summon_enemies(self, en_fists: pygame.sprite.Group):
        '''Призывает врагов'''
        if not self.in_position:
            # Призыв может начаться в любой позиции
            self.timer = monotonic()
            self.in_position = True
        for i in range(self.ultimate_frames):
                if (i + 1) * self.ats > self.cur_time.time - self.timer\
                    >= i * self.ats:
                    if i < 3:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/ultimate{i + 1}.png')
                        self.change_rect()
                    else:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/summon{i - 2}.png')
        if self.cur_time.time - self.timer >= 6 * self.ats:
            from boss_projectiles import SummoningCircle
            summoning_circle1 = SummoningCircle(self, True)
            summoning_circle2 = SummoningCircle(self, False)
            en_fists.add(summoning_circle1, summoning_circle2)
            self.finish_ultimate()

    def launch_lightnings(self, en_fists: pygame.sprite.Group):
        '''Запуск шаровых молний'''
        if not self.position_is_chosen:
            self.define_position(self.screen_rect.centerx, 
                self.screen_rect.centery)
        if self.movement(self.positionx, self.positiony):
            if not self.in_position:
                self.timer = monotonic()
                self.in_position = True
                # Выпуск молний происходит с задержкой в 1/4 секунды
                self.delay = 0.25
                self.launch_cooldown_timer = monotonic() + 6 * self.ats
            for i in range(self.ultimate_frames):
                if (i + 1) * self.ats > self.cur_time.time - self.timer\
                    >= i * self.ats:
                    if i < 3:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/ultimate{i + 1}.png')
                        self.change_rect()
                    else:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/lightning{i - 2}.png')
            if self.cur_time.time - self.launch_cooldown_timer >= 0:
                from boss_projectiles import BallLightning
                new_ball_lightning = BallLightning(self)
                en_fists.add(new_ball_lightning)
                self.launch_cooldown_timer += self.delay
            # Выпуск молний продолжается пять секунд
            if self.cur_time.time - self.timer >= 6 * self.ats + 5:
                self.finish_ultimate()

    

    def launch_spears(self, en_fists: pygame.sprite.Group):
        '''Запуск копий'''
        if not self.position_is_chosen:
            self.define_position(self.screen_rect.centerx, 
                self.screen_rect.centery)
        if self.movement(self.positionx, self.positiony):
            if not self.in_position:
                self.timer = monotonic()
                self.in_position = True
                # Запуск копий происходит с задержкой в 1/3 секунды
                self.delay = 0.33
                self.launch_cooldown_timer = monotonic() + 6 * self.ats
            for i in range(self.ultimate_frames):
                if (i + 1) * self.ats > self.cur_time.time - self.timer\
                    >= i * self.ats:
                    if i < 3:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/ultimate{i + 1}.png')
                        self.change_rect()
                    else:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/spears{i - 2}.png')
            if self.cur_time.time - self.launch_cooldown_timer >= 0:
                from boss_projectiles import SpearTip
                new_spear_tip = SpearTip(self)
                en_fists.add(new_spear_tip)
                self.launch_cooldown_timer += self.delay
            # Запуск копьев продолжается пять секунд
            if self.cur_time.time - self.timer >= 6 * self.ats + 5:
                self.finish_ultimate()

    def blade_runner(self, en_fists: pygame.sprite.Group):
        '''Забег с лезвиями'''
        if not self.position_is_chosen:
            x = self.define_direction()
            self.define_position(x, self.screen_rect.centery)
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
            for i in range(self.ultimate_frames):
                if (i + 1)/2 * self.ats > self.cur_time.time - self.timer\
                    >= i/2 * self.ats:
                    if i < 3:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/ultimate{i + 1}.png')
                        self.change_rect()
                    else:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/' +
                            f'blades{i - 2}_{int(not self.side)}.png')
            # Условие построено так, что персонажа переносит только после того,
            # как анимация босса проигралась
            if self.cur_time.time - self.launch_cooldown_timer >= 0 \
                and self.moving_mc():
                from boss_projectiles import Blade
                for n in range(3):
                    new_blade = Blade(self)
                    en_fists.add(new_blade)
                self.launch_cooldown_timer += self.delay
            if self.health != self.ultimate_starting_health:
                self.finish_ultimate()

    def saw_runner(self, en_fists: pygame.sprite.Group):
        '''Забег с пилами'''
        if not self.position_is_chosen:
            x = self.define_direction(-1)
            self.define_position(x, self.screen_rect.centery)
        if self.movement(self.positionx, self.positiony, 2):
            if not self.in_position:
                self.timer = monotonic()
                self.in_position = True
                self.is_invincible = True
            for i in range(self.ultimate_frames):
                if (i + 1) * self.ats > self.cur_time.time - self.timer\
                    >= i/2 * self.ats:
                    if i < 3:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/ultimate{i + 1}.png')
                        self.change_rect()
                    else:
                        self.image = pygame.image.load(
                            f'images/K{self.surname}Enemies/boss/maze{i - 2}.png')
            # ДОДЕЛАТЬ

    def moving_mc(self) -> bool:
        '''Отталкивание главного персонажа'''
        if self.mc_achieved_position:
            # Для подстановки в условие
            return True
        self.mc.centerx += 2 * self.ai_settings.mc_speed_factor \
            * self.mc_dir_sign
        if not self.screen_rect.contains(self.mc.rect):
            self.mc_achieved_position = True
        return False

    def define_direction(self, kind_of_action: int = 1):
        '''Определяет то, в какую сторону полетит босс
        и отлетит главный персонаж'''
        # Сторона, в которую полетит босс
        self.side = randint(0, 1)
        if self.side:
            x = self.screen_rect.right - int(self.rect.width/2)
                # В какую сторону отбросит главного персонажа
                # kind_of_action определяет, что происходит с персонажем:
                # его притягивает или отталкивает от босса
            self.mc_dir_sign = -1 * kind_of_action
        else:
            x = self.screen_rect.left + int(self.rect.width/2)
            self.mc_dir_sign = 1 * kind_of_action
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
        self.is_punching = False
        self.using_common_attack = False
        self.cooldown_timer = False
        
            


    

        