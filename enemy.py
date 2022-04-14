from sqlite3 import Time
from time import monotonic
import pygame
from pygame.sprite import Sprite
import enemy_animation as an
from fist import Fist
from settings import Settings
from MC import MainCharacter
from shockwave import Shockwave
from stats import Stats
from etimer import Timer

class Enemy(Sprite):

    '''Класс игровых врагов'''

    deaths = 0 # Кол-во смертей врагов
    c_deaths = 0 # Текущие смерти, нужны для волн и уровней
    summons = 0 # Кол-во призывов врагов

    def __init__(self, screen: pygame.Surface, ai_settings: Settings, 
        mc: MainCharacter, st: Stats, timer: Timer, cur_time: Timer):
        '''Инициализирует параметры'''
        super().__init__()
        Enemy.summons += 1
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.ai_settings = ai_settings
        self.mc = mc
        self.st = st
        self.main_timer = timer # Таймер из основного модуля
        self.image = ''
        self.define_surname()
        # Текущее время
        self.cur_time = cur_time
        # Создаем ударную поверхность
        self.fist = Fist(screen)
        # Переменные для анимаций
        self.timer = monotonic()
        self.is_right_leg = True
        self.is_dead = False
        # Флаг оглушения после получения урона
        self.is_stunned = False
        # Флаги удара
        self.is_punching = False
        self.right_punch = False
        # Таймер для перезарядки атаки
        self.cooldown_timer = 0
        # Призывает ли враг во время атаки ударную волну? (по умолчанию нет)
        self.summon_shockwave = False
        # Дальность атаки противника (по умолчанию ближний бой)
        self.attack_range = 5

    def define_surname(self):
        '''Определяет тип врагов в зависимости от главного персонажа.'''
        # Если главный персонаж - я, то враги - З.
        if self.mc.surname == 'S':
            self.surname = 'Z'
        # И наоборот
        else:
            self.surname = 'S'


    def __del__(self):
        '''Срабатывает при смерти'''
        Enemy.deaths += 1
        Enemy.c_deaths += 1
        # Если вся волна умерла:
        if Enemy.c_deaths == len(self.ai_settings.waves[self.st.level]
        [self.st.current_wave]):
            # Переход на новый уровень, если волна последняя
            if self.st.current_wave == len(
                self.ai_settings.waves[self.st.level]) - 1 and \
                    self.st.level < self.ai_settings.max_level:
                self.st.level += 1
                self.st.current_wave = 0
            # Либо вызов новой волны
            elif self.st.current_wave < len(
                self.ai_settings.waves[self.st.level]) - 1:
                self.st.current_wave += 1
            # Текущие смерти и призывы обнуляются
            Enemy.c_deaths = 0
            Enemy.summons = 0
            # Таймер тоже
            self.main_timer.time = monotonic()

        
        
        

    def blitme(self):
        '''Рисует врага в текущей позиции'''
        if not self.is_punching:
            self.screen.blit(self.image, self.rect)
        else:
            self.screen.blit(self.image, self.an_rect)

    def change_rect(self):
        '''Заменяет прямоугольник врага, центр нового находится в центре старого'''
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.centerx)
        self.rect.centery = int(self.centery)

    def spawning_point(self):
        '''Определяет начальное положение врага'''
        
        self.rect.centery = self.screen_rect.centery
        if self.mc.centerx > self.ai_settings.screen_width/2:
            self.rect.right = 0
        elif self.mc.centerx <= self.ai_settings.screen_width/2:
            self.rect.left = self.ai_settings.screen_width

    def update(self, fist: Fist, enemies: pygame.sprite.Group, 
        en_fists: pygame.sprite.Group):
        '''Обновление состояния врага(перемещение, оглушение, атака или смерть)'''
        # Если враг жив (т.е. здоровье больше нуля):
        if self.health > 0:
            # Если враг не оглушен:
            if not self.is_stunned:
                # Если враг не бьет?
                if not self.is_punching:
                    if self.rect.colliderect(fist.rect):
                        self.get_damage()
                        return
                    # Переменные для условий определения положения
                    where_am_i_y, where_am_i_x = self.check_attack_possibility()
                    # Сначала идет перемещение по вертикали
                    if not where_am_i_y:
                        self.vertical_movement()
                    # Затем по горизонтали
                    elif not where_am_i_x:
                        self.horizontal_movement()
                    # Конвертируем вещественное значение в целочисленное
                    self.rect.centerx = self.centerx
                    self.rect.centery = self.centery
                    # Если враг в зоне досягаемости, он начинает атаку
                    if where_am_i_x and where_am_i_y and \
                    self.cur_time.time - self.cooldown_timer >= \
                    self.cooldown:
                        self.initiate_punch()

                else:
                   self.attack(en_fists)
            else:
                an.stunning_animation(self)      
        else:
            if not self.is_dead:
                self.timer = monotonic()
                self.is_dead = True
            self.death_animation(enemies)

    def check_attack_possibility(self) -> tuple[bool, bool]:
        '''Возвращает флаги возможности атаки'''
        where_am_i_y = self.rect.centery in range(
                        self.mc.rect.centery - 5,self.mc.rect.centery + 6)
        where_am_i_x = self.rect.left in range(
                        self.mc.rect.right - self.attack_range, 
                        self.mc.rect.right + self.attack_range + 1)  \
                        or self.rect.right in range(
                        self.mc.rect.left - self.attack_range, 
                        self.mc.rect.left + self.attack_range + 1)
            
        return where_am_i_y,where_am_i_x

    def get_damage(self):
        '''Получение урона и оглушение'''
        if self.surname == 'D':
            # Не надо бить Диану
            self.mc.health = 0
            self.mc.tf = self
            return
        self.health -= self.ai_settings.mc_damage
        self.is_stunned = True
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/{self.name}/stunned.png')
        self.change_rect()
        self.timer = monotonic()

    def vertical_movement(self):
        '''Перемещение врага по вертикали'''
        if self.rect.centery < self.mc.rect.centery:
            an.going_vertical_animation(self)
            exec(f'self.centery += self.ai_settings.{self.name}_speed_factor')
        else:
            an.going_vertical_animation(self)
            exec(f'self.centery -= self.ai_settings.{self.name}_speed_factor')

    def horizontal_movement(self):
        '''Перемещение врага по горизонтали'''
        if self.rect.left > self.mc.rect.right:
            an.going_left_animation(self)
            exec(f'self.centerx -= self.ai_settings.{self.name}_speed_factor')
        elif self.rect.right < self.mc.rect.left:
            an.going_right_animation(self)
            exec(f'self.centerx += self.ai_settings.{self.name}_speed_factor')
        else:
            if self.rect.centerx > self.mc.rect.centerx:
                an.going_right_animation(self)
                exec(f'self.centerx += self.ai_settings.{self.name}_speed_factor')
            else:
                an.going_left_animation(self)
                exec(f'self.centerx -= self.ai_settings.{self.name}_speed_factor')

    def initiate_punch(self):
        '''Активирует флаги атаки'''
        self.is_punching = True
        if self.rect.centerx > self.mc.rect.centerx:
            self.right_punch = False
        else:
            self.right_punch = True          
        self.timer = monotonic()

    def attack(self, en_fists: pygame.sprite.Group):
        '''Обработка атаки'''
        file_end_name, sign, rect_side = self.define_attack_vars()
        
        
        # self.frames - количество кадров
        for i in range(self.frames):
            # Кадры сменяются по времени:
            if (i+1) * self.ats >= self.cur_time.time - self.timer > i * self.ats:
                # Кадров (изображений именно) всего половина от общего количества, 
                # в случае нечетного кол-ва - с округлением в большую сторону
                if i in range(round(self.frames/2) + 1):
                    if i == 0:
                        self.create_new_rect()
                        en_fists.add(self.fist)
                    self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies/{self.name}' +
                        f'/punching{i + 1}_{file_end_name}.png')                    
                    if i <= self.noload_fr - 1:
                        # Корректирует изображение на "неатакующих" кадрах, если такое предусмотрено
                        if self.pos_correction != '0':
                            self.an_rect = self.image.get_rect()
                            self.an_rect.centery = self.rect.centery
                            exec(f'self.an_rect.centerx = self.rect.{rect_side}'
                                + sign + self.pos_correction)
                        else:
                            self.correlate_rect_image(self.right_punch)
                    else:
                        self.correlate_rect_image(self.right_punch)
                        # Перемещает ударную поверхность:
                        exec('self.fist.change_position(' +
                            f'self.an_rect.{rect_side} {sign}' +
                            f'self.frl_side[i-{self.noload_fr}],' +
                            f'self.an_rect.top + self.frl_top[i-{self.noload_fr}])')
                        if self.summon_shockwave and not self.shockwave_active \
                            and i == round(self.frames/2):
                            # Вызывает ударную волну, если такое предусмотрено типом врага
                            new_shockwave = Shockwave(self.screen, self.cur_time, 
                            self.fist, self.ai_settings, self.right_punch)
                            en_fists.add(new_shockwave)
                            self.shockwave_active = True
                        
                        
                else:
                    if i == round(self.frames/2) + 1 and self.fist in en_fists:
                        # Удаляем ударную поверхность:
                        en_fists.remove(self.fist)
                        
                    # Кадры идут в обратном порядке
                    self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies/{self.name}/'+
                        f'punching{self.frames + 1 - i}_{file_end_name}.png')
                    self.correlate_rect_image(self.right_punch)
                    if i == self.frames - 1:
                        # Атака закончена, начинается перезарядка
                        self.is_punching = False
                        self.shockwave_active = False
                        self.cooldown_timer = monotonic()

    def define_attack_vars(self):
        '''Определяет значение переменных для метода атаки'''
        # Атака идет вправо или влево?
        if self.right_punch:
            file_end_name = 'right' # конец названия файлов кадров
            sign = '+'  # знак для уравнения определения положения первых кадров
            rect_side = 'left' # сторона, относительно которой располагаются
                               # первые кадры
        else:
            file_end_name = 'left'
            sign = '-'
            rect_side = 'right'
        return file_end_name, sign, rect_side

    def create_new_rect(self):
        '''Создает новый прямоугольник для удобной анимации атаки'''
        # Ширина прямоугольника - ширина самого тонкого кадра
        fake_rect = pygame.Rect((0,0), self.smallest_frame)
        fake_rect.centerx = self.rect.centerx
        fake_rect.centery = self.rect.centery
        self.rect = fake_rect

    def correlate_rect_image(self, side: bool):
        '''Соотносит изначальный прямоугольник с измененным изображением
        True - анимация вправо, т.е. у прямоугольников одинаковое расположение левой стороны.
        False - влево, соответственно одинаковое расположение правой стороны'''
        self.an_rect = self.image.get_rect()
        self.an_rect.top = self.rect.top
        if side:
            self.an_rect.left = self.rect.left
        else:
            self.an_rect.right = self.rect.right
    
    
        