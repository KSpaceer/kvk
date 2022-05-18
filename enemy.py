
from time import monotonic
import pygame
from pygame.sprite import Sprite
from audiosounds import Audio
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
        mc: MainCharacter, st: Stats, timer: Timer, 
        cur_time: Timer, is_native: bool = True):
        '''Инициализирует параметры'''
        super().__init__()
        self.is_native = is_native
        if self.is_native:
            Enemy.summons += 1
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.ai_settings = ai_settings
        self.mc = mc
        self.st = st
        self.audio = st.audio
        # Название звука атаки (по умолчанию)
        self.audioname = 'punch'
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
        # Флаг проигрывания звука
        self.has_played_audio = False
        # Флаг оглушения после получения урона
        self.is_stunned = False
        # Флаги удара
        self.is_punching = False
        self.right_punch = False
        # Таймер для перезарядки атаки
        self.cooldown_timer = 0
        # Призывает ли враг во время атаки ударную волну? (по умолчанию нет)
        self.summon_shockwave = False
        # Выпускает ли враг сюрикены? (по умолчанию нет)
        self.launch_shuriken = False
        self.is_launching = False
        self.launch_cooldown_timer = 0
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
        if self.st.state == self.st.GAMEACTIVE and self.is_native:
            Enemy.deaths += 1
            Enemy.c_deaths += 1
            self.change_wave()

    def change_wave(self):
        '''Смена волны/уровня'''
        # Если вся волна умерла:
        if Enemy.c_deaths == len(self.ai_settings.waves[self.st.level]
        [self.st.current_wave]):
            # Переход на новый уровень, если волна последняя
            if self.st.current_wave == len(
                self.ai_settings.waves[self.st.level]) - 1 and \
                    self.st.level < self.ai_settings.max_level:
                self.st.level += 1
                # Восстановление здоровья главного персонажа
                self.mc.health = self.ai_settings.mc_health
                self.st.current_wave = 0
            # Либо вызов новой волны
            elif self.st.current_wave < len(
                self.ai_settings.waves[self.st.level]) - 1:
                self.st.current_wave += 1
            # Завершение игры
            elif self.st.level == self.ai_settings.max_level:
                self.st.state = self.st.CREDITS
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

    def change_stun_rect(self, fist: Fist):
        '''Замена прямоугольника при получении удара для анимации оглушения'''
        relative_position = fist.rect.right < self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.centery = int(self.centery)
        if relative_position:
            self.rect.left = fist.rect.right - 10
        else:
            self.rect.right = fist.rect.left + 10


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
                # Если враг не бьет и не мечет?
                if not self.is_punching and not self.is_launching:
                    if self.rect.colliderect(fist.rect):
                        self.get_damage(fist)
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
                    self.cur_time - self.cooldown_timer >= \
                    self.cooldown:
                        self.initiate_punch()
                    elif self.launch_shuriken:
                        # Если враг умеет метать сюрикены, проверяет 
                        # возможность это сделать
                        where_am_i_y, where_am_i_x = self.check_launch_possibility()
                        if where_am_i_x and where_am_i_y and \
                            self.cur_time - self.launch_cooldown_timer \
                            >= self.launch_cooldown:
                            self.initiate_launch()

                elif self.is_punching:
                   self.attack(en_fists)
                else:
                    self.launch(en_fists)
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

    def check_launch_possibility(self) -> tuple[bool, bool]:
        '''Возвращает флаги возможности запуска сюрикена'''
        where_am_i_y = self.rect.centery in range(
                        self.mc.rect.centery - 15,self.mc.rect.centery + 16)
        # Для запуска враг должен быть на расстоянии от половины дальности 
        # запуска до дальности запуска. 
        where_am_i_x = self.rect.left in range(
                        self.mc.rect.right + int(self.launch_range/2), 
                        self.mc.rect.right + self.launch_range + 1)  \
                        or self.rect.right in range(
                        self.mc.rect.left - self.launch_range - 1, 
                        self.mc.rect.left - int(self.launch_range/2))
        return where_am_i_y, where_am_i_x


    def get_damage(self, fist: Fist):
        '''Получение урона и оглушение'''
        if self.surname == 'D':
            # Не надо бить Диану
            self.mc.health = 0
            self.mc.tf = self
            return
        self.health -= self.ai_settings.mc_damage
        self.is_stunned = True
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/{self.name}' +
            '/stunned.png').convert_alpha()
        self.change_stun_rect(fist)
        self.st.audio.play_sound('punch')
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
            # Если враг внутри главного персонажа, он пытается выйти из него
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

    def initiate_launch(self):
        '''Активирует флаги запуска сюрикена'''
        self.is_launching = True
        if self.rect.centerx > self.mc.rect.centerx:
            self.right_punch = False
        else:
            self.right_punch = True
        self.timer = monotonic()

    def launch(self, en_fists: pygame.sprite.Group):
        '''Обработка запуска сюрикена'''
        if not self.shuriken_active:
            self.shuriken_active = True
            file_end_name = self.define_attack_vars()[0]
            self.image = pygame.image.load(f'images/K{self.surname}Enemies/' +
            f'{self.name}/launching_{file_end_name}.png').convert_alpha()
            self.change_rect()
            from shuriken import Shuriken
            new_shuriken = Shuriken(self.screen, self.cur_time, self, 
                self.ai_settings, self.right_punch)
            en_fists.add(new_shuriken)
            self.audio.play_sound('launch_shuriken')
        if self.cur_time - self.timer >= self.ai_settings.animation_change:
            self.is_launching = False
            self.shuriken_active = False
            self.launch_cooldown_timer = monotonic()
    
    def attack(self, en_fists: pygame.sprite.Group):
        '''Обработка атаки'''
        file_end_name, sign, rect_side = self.define_attack_vars()
        # self.frames - количество кадров
        for i in range(self.frames):
            # Кадры сменяются по времени:
            if (i+1) * self.ats >= self.cur_time - self.timer > i * self.ats:
                # Кадров (изображений именно) всего половина от общего количества, 
                # в случае нечетного кол-ва - с округлением в большую сторону
                if i in range(int(self.frames/2) + 1):
                    self.working_stroke(en_fists, file_end_name, 
                        sign, rect_side, i)
                else:
                    self.idling(en_fists, file_end_name, i)

    def idling(self, en_fists: pygame.sprite.Group , file_end_name: str, i: int):
        '''Холостой ход атаки'''
        if i == round(self.frames/2) + 1 and self.fist in en_fists:
            # Удаляем ударную поверхность:
            self.fist.change_position(-50, -50)
            en_fists.remove(self.fist)
        # Кадры идут в обратном порядке
        self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies/{self.name}/'+
                        f'punching{self.frames + 1 - i}_{file_end_name}' + 
                        '.png').convert_alpha()
        self.correlate_rect_image(self.right_punch)
        if i == self.frames - 1:
            # Атака закончена, начинается перезарядка
            self.is_punching = False
            self.shockwave_active = False
            self.has_played_audio = False
            self.cooldown_timer = monotonic()
            if hasattr(self, 'is_new_rect_created'):
                self.is_new_rect_created = False

    def working_stroke(self, en_fists: pygame.sprite.Group, 
        file_end_name: str, sign: str, rect_side: str, i: int):
        '''Рабочий ход атаки'''
        if i == 0:
            self.create_new_rect()
            en_fists.add(self.fist)
        self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies/{self.name}' +
                        f'/punching{i + 1}_{file_end_name}.png').convert_alpha()                   
        if i <= self.noload_fr - 1:
        # Корректирует изображение на "неатакующих" кадрах, если такое предусмотрено
            if self.pos_correction != '0':
                self.correct_position(sign, rect_side)
            else:
                self.correlate_rect_image(self.right_punch)
        else:
            self.correlate_rect_image(self.right_punch)
                        # Перемещает ударную поверхность:
            exec('self.fist.change_position(' +
                            f'self.an_rect.{rect_side} {sign}' +
                            f'self.frl_side[i-{self.noload_fr}],' +
                            f'self.an_rect.top + self.frl_top[i-{self.noload_fr}])')
            if not self.has_played_audio:
                self.audio.play_sound(self.audioname)
                self.has_played_audio = True
            self.shockwave_check(en_fists, i)

    def shockwave_check(self, en_fists: pygame.sprite.Group, i: int):
        '''Вызывает ударную волну, 
        если такое предусмотрено типом врага и другой волны нет'''
        if self.summon_shockwave and not self.shockwave_active \
            and i == round(self.frames/2):
            # Вызывает ударную волну, если такое предусмотрено типом врага
            self.audio.play_sound('launch_shockwave')
            new_shockwave = Shockwave(self.screen, self.cur_time, 
                self.ai_settings, self.right_punch, en_fist=self.fist)
            en_fists.add(new_shockwave)
            self.shockwave_active = True

    def correct_position(self, sign: str, rect_side: str):
        '''Корректирует положение на неатакующих кадрах'''
        self.an_rect = self.image.get_rect()
        self.an_rect.centery = self.rect.centery
        exec(f'self.an_rect.centerx = self.rect.{rect_side}'
                                + sign + self.pos_correction)

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
    
    
        