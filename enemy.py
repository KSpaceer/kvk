

from time import monotonic
import pygame
from pygame.sprite import Sprite, Group
from audiosounds import Audio
import enemy_animation as an
from fist import Fist
from mediator import Mediator
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

    def __init__(self, mediator: Mediator, is_native: bool = True):
        '''Инициализирует параметры'''
        super().__init__()
        self.is_native = is_native
        if self.is_native:
            Enemy.summons += 1
        self.mediator = mediator
        # Название звука атаки (по умолчанию)
        self.audioname = 'punch'
        self.image = ''
        self.define_surname()
        # Создаем ударную поверхность
        self.fist = Fist(mediator)
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
        if self.mediator.get_value('mc', 'surname') == 'S':
            self.surname = 'Z'
        # И наоборот
        else:
            self.surname = 'S'


    def __del__(self):
        '''Срабатывает при смерти'''
        if self.mediator.get_value('st', 'state') == Stats.GAMEACTIVE\
            and self.is_native:
            Enemy.deaths += 1
            Enemy.c_deaths += 1
            self.change_wave()

    def change_wave(self):
        '''Смена волны/уровня'''
        # Если вся волна умерла:
        current_level = self.mediator.get_value('st', 'level')
        current_wave_number = self.mediator.get_value('st', 'current_wave')
        wave_size = len(self.mediator.get_value('ai_settings',
            f'waves[{current_level}]' +
            f'[{self.mediator.get_value("st", "current_wave")}]'))
        last_wave_number = len(self.mediator.get_value('ai_settings',
            f'waves[{current_level}]')) - 1
        max_level = self.mediator.get_value('ai_settings', 'max_level')
        
        if Enemy.c_deaths == wave_size:
            
            # Переход на новый уровень, если волна последняя
            if current_wave_number == last_wave_number and \
                    current_level < max_level:
                # Инкремент уровня
                self.mediator.set_value('st', 'level', f'{current_level} + 1')
                # Восстановление здоровья главного персонажа
                self.mediator.set_value('mc', 'health', 
                f'{self.mediator.get_value("ai_settings", "mc_health")}')
                self.mediator.set_value('st', 'current_wave', '0')
            # Либо вызов новой волны
            elif current_wave_number < last_wave_number:
                # Инкремент номера волны
                self.mediator.set_value(
                    'st', 'current_wave', f'{current_wave_number} + 1')
            # Завершение игры
            elif current_level == max_level:
                self.mediator.set_value('st', 'state', f'{Stats.CREDITS}')
            # Текущие смерти и призывы обнуляются
            Enemy.c_deaths = 0
            Enemy.summons = 0
            # Таймер тоже
            self.mediator.set_value('timer', 'time', f'{monotonic()}')
            

        
        
        

    def blitme(self):
        '''Рисует врага в текущей позиции'''
        if not self.is_punching:
            self.mediator.blit_surface(self.image, self.rect)
        else:
            self.mediator.blit_surface(self.image, self.rect)

    def change_rect(self):
        '''Заменяет прямоугольник врага, центр нового находится в центре старого'''
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.centerx)
        self.rect.centery = int(self.centery)

    def change_stun_rect(self):
        '''Замена прямоугольника при получении удара для анимации оглушения'''
        mc_fist_rect = self.mediator.get_value('mc_fist', 'rect')
        relative_position = mc_fist_rect.right < self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.centery = int(self.centery)
        if relative_position:
            self.rect.left = mc_fist_rect.right - 10
        else:
            self.rect.right = mc_fist_rect.left + 10


    def spawning_point(self):
        '''Определяет начальное положение врага'''
        mc_centerx = self.mediator.get_value('mc', 'centerx')
        screen_width = self.mediator.get_value('ai_settings','screen_width')
        self.rect.centery = self.mediator.get_value('screen_rect', 'centery')
        if mc_centerx > screen_width/2:
            self.rect.right = 0
        elif mc_centerx <= screen_width/2:
            self.rect.left = screen_width

    def update(self):
        '''Обновление состояния врага(перемещение, оглушение, атака или смерть)'''
        # Если враг жив (т.е. здоровье больше нуля):
        mc_fist: Fist = self.mediator.get_value('mc_fist')
        
        if self.health > 0:
            # Если враг не оглушен:
            if not self.is_stunned:
                # Если враг не бьет и не мечет?
                if not self.is_punching and not self.is_launching:
                    if self.rect.colliderect(mc_fist.rect):
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
                    self.mediator.get_value('cur_time', 'time') - self.cooldown_timer >= \
                    self.cooldown:
                        self.initiate_punch()
                    elif self.launch_shuriken:
                        # Если враг умеет метать сюрикены, проверяет 
                        # возможность это сделать
                        where_am_i_y, where_am_i_x = self.check_launch_possibility()
                        if where_am_i_x and where_am_i_y and \
                            self.mediator.get_value('cur_time', 'time') - self.launch_cooldown_timer \
                            >= self.launch_cooldown:
                            self.initiate_launch()

                elif self.is_punching:
                   self.attack()
                else:
                    self.launch()
            else:
                an.stunning_animation(self)      
        else:
            if not self.is_dead:
                self.timer = monotonic()
                self.is_dead = True
            self.death_animation()

    def check_attack_possibility(self) -> tuple[bool, bool]:
        '''Возвращает флаги возможности атаки'''
        mc_rect: pygame.Rect = self.mediator.get_value('mc', 'rect')
        where_am_i_y = self.rect.centery in range(
                        mc_rect.centery - 5, mc_rect.centery + 6)
        where_am_i_x = self.rect.left in range(
                        mc_rect.right - self.attack_range, 
                        mc_rect.right + self.attack_range + 1)  \
                        or self.rect.right in range(
                        mc_rect.left - self.attack_range, 
                        mc_rect.left + self.attack_range + 1)
            
        return where_am_i_y,where_am_i_x

    def check_launch_possibility(self) -> tuple[bool, bool]:
        '''Возвращает флаги возможности запуска сюрикена'''
        mc_rect: pygame.Rect = self.mediator.get_value('mc', 'rect')
        where_am_i_y = self.rect.centery in range(
                        mc_rect.centery - 15, mc_rect.centery + 16)
        # Для запуска враг должен быть на расстоянии от половины дальности 
        # запуска до дальности запуска. 
        where_am_i_x = self.rect.left in range(
                        mc_rect.right + int(self.launch_range/2), 
                        mc_rect.right + self.launch_range + 1)  \
                        or self.rect.right in range(
                        mc_rect.left - self.launch_range - 1, 
                        mc_rect.left - int(self.launch_range/2))
        return where_am_i_y, where_am_i_x


    def get_damage(self, fist: Fist):
        '''Получение урона и оглушение'''
        if self.surname == 'D':
            # Не надо бить Диану
            self.mediator.set_value('mc', 'health', '0')
            is_diana_standing_to_the_right = self.rect.centerx >=\
                self.mediator.get_value('mc', 'rect.centerx')
            self.mediator.set_value(
                'mc', 'damaged_from_right', f'{is_diana_standing_to_the_right}')
            return
        self.health -= self.mediator.get_value('ai_settings', 'mc_damage')
        self.is_stunned = True
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/{self.name}' +
            '/stunned.png').convert_alpha()
        self.change_stun_rect(fist)
        self.mediator.call_method('audio', 'play_sound', '"punch"')
        self.timer = monotonic()

    def vertical_movement(self):
        '''Перемещение врага по вертикали'''
        if self.rect.centery < self.mediator.get_value('mc', 'rect.centery'):
            an.going_vertical_animation(self)
            exec(f'self.centery += self.ai_settings.{self.name}_speed_factor')
        else:
            an.going_vertical_animation(self)
            exec(f'self.centery -= self.ai_settings.{self.name}_speed_factor')

    def horizontal_movement(self):
        '''Перемещение врага по горизонтали'''
        if self.rect.left > self.mediator.get_value('mc', 'rect.right'):
            an.going_left_animation(self)
            exec(f'self.centerx -= self.ai_settings.{self.name}_speed_factor')
        elif self.rect.right < self.mediator.get_value('mc', 'rect.left'):
            an.going_right_animation(self)
            exec(f'self.centerx += self.ai_settings.{self.name}_speed_factor')
        else:
            # Если враг внутри главного персонажа, он пытается выйти из него
            if self.rect.centerx > self.mediator.get_value('mc','rect.centerx'):
                an.going_right_animation(self)
                exec(f'self.centerx += self.ai_settings.{self.name}_speed_factor')
            else:
                an.going_left_animation(self)
                exec(f'self.centerx -= self.ai_settings.{self.name}_speed_factor')

    def initiate_punch(self):
        '''Активирует флаги атаки'''
        self.is_punching = True
        if self.rect.centerx > self.mediator.get_value('mc', 'rect.centerx'):
            self.right_punch = False
        else:
            self.right_punch = True          
        self.timer = monotonic()

    def initiate_launch(self):
        '''Активирует флаги запуска сюрикена'''
        self.is_launching = True
        if self.rect.centerx > self.mediator.get_value('mc', 'rect.centerx'):
            self.right_punch = False
        else:
            self.right_punch = True
        self.timer = monotonic()

    def launch(self):
        '''Обработка запуска сюрикена'''
        if not self.shuriken_active:
            self.shuriken_active = True
            file_end_name = self.define_attack_vars()[0]
            self.image = pygame.image.load(f'images/K{self.surname}Enemies/' +
            f'{self.name}/launching_{file_end_name}.png').convert_alpha()
            self.change_rect()
            from shuriken import Shuriken
            new_shuriken = Shuriken(self.mediator)
            self.mediator.extend_collection(new_shuriken)
            self.mediator.call_method(
                'audio', 'play_sound', '"launch_shuriken"')
        if self.mediator.current_time() - self.timer >=\
            self.mediator.get_value('ai_settings', 'animation_change'):
            self.is_launching = False
            self.shuriken_active = False
            self.launch_cooldown_timer = monotonic()
    
    def attack(self):
        '''Обработка атаки'''
        file_end_name, sign, rect_side = self.define_attack_vars()
        # self.frames - количество кадров
        for i in range(self.frames):
            # Кадры сменяются по времени:
            if (i+1) * self.ats >= self.mediator.current_time() - self.timer >\
                i * self.ats:
                # Кадров (изображений именно) всего половина от общего количества, 
                # в случае нечетного кол-ва - с округлением в большую сторону
                if i in range(int(self.frames/2) + 1):
                    self.working_stroke(file_end_name, sign, rect_side, i)
                else:
                    self.idling(file_end_name, i)

    def idling(self, file_end_name: str, i: int):
        '''Холостой ход атаки'''
        en_fists: Group = self.mediator.get_collection('en_fists')
        if i == round(self.frames/2) + 1 and\
            self.fist in en_fists:
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

    def working_stroke(self, file_end_name: str, sign: str, rect_side: str, i: int):
        '''Рабочий ход атаки'''
        if i == 0:
            self.create_new_rect()
            self.mediator.extend_collection('en_fists', self.fist)
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
                self.mediator.call_method(
                    'audio', 'play_sound', f'"{self.audioname}"')
                self.has_played_audio = True
            self.shockwave_check(i)

    def shockwave_check(self, i: int):
        '''Вызывает ударную волну, 
        если такое предусмотрено типом врага и другой волны нет'''
        if self.summon_shockwave and not self.shockwave_active \
            and i == round(self.frames/2):
            # Вызывает ударную волну, если такое предусмотрено типом врага
            self.mediator.call_method('audio', 'play_sound', '"launch_shockwave"')
            new_shockwave = Shockwave(self.mediator, self.right_punch)
            self.mediator.extend_collection('en_fists', new_shockwave)
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
    
    
        