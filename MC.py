from math import floor
from time import monotonic
import mc_animation as an
import mc_movement as mv
import pygame
from pygame.sprite import Sprite
from mediator import Mediator
from settings import Settings
from etimer import Timer
from fist import Fist
from stats import Stats
from audiosounds import Audio

class MainCharacter(Sprite):
    '''Класс главного персонажа'''
    def __init__(self, mediator: Mediator, surname: str = None):
        '''Инициализация главного персонажа и задание его начальной позиции'''
        super().__init__()
        self.mediator = mediator
        self.speed = mediator.get_value('ai_settings', 'mc_speed_factor')
        # Первая буква фамилии персонажа
        self.__surname = surname
        # Загрузка изображения
        self.image = pygame.image.load('images/KSMain/standing.png').convert_alpha()
        self.rect = self.image.get_rect()
        # Прямоугольник для анимаций
        self.an_rect = self.rect
        # Персонаж появляется ближе к левому экрану
        self.rect.centery = mediator.get_value('screen_rect','centery')
        self.rect.left = mediator.get_value('screen_rect','left') + 200
        # Сохранение вещественной координаты центра персонажа
        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)
        # Здоровье
        self.health = mediator.get_value('ai_settings', 'mc_health')
        # Флаги перемещения и переключатели анимации:
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.is_right_leg = True
        self.timer = 0
        self.attack_timer = 0
        self.space_active = False
        # Таймер неуязвимости
        self.invin_timer = 0
        # Флаги удара
        self.is_punching = False
        self.right_punch = False
        # Флаги оглушения и неуязвимости
        self.is_stunned = False
        self.invincible = False
        # Скорость атаки (для удобства зададим новую переменную)
        self.ats = mediator.get_value('ai_settings', 'attack_speed')
        # Количество кадров атаки:
        self.frames = 5
        # frl - fist relative location
        self.frl = [-57, 26, 35, -57, -57]
        
        
    @property
    def surname(self):
        return self.__surname

    @surname.setter
    def surname(self, surname):
        Stats.mc_surname = surname
        Stats.update_state_to_bg_dict()
        Stats.update_state_to_audio_dict()
        self.__surname = surname

    @surname.deleter
    def surname(self):
        del self.__surname

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
    
    def blitme(self):
        '''Рисует персонажа в текущей позиции'''
        if not self.is_punching and self.health > 0:
            self.mediator.blit_surface(self.image, self.rect)
        else:
            self.mediator.blit_surface(self.image, self.an_rect)
    
    def update(self):
        '''Обновляет позицию главного персонажа'''
        # Если персонаж жив
        if self.health > 0:
            # Если персонаж неуязвим:
            if self.invincible:
                if self.mediator.current_time() - self.invin_timer >=\
                    self.mediator.get_value('ai_settings', 'inv_duration'):
                    # По истечении времени он теряет неуязвимость
                    self.invincible = False

            # Когда персонаж не оглушен
            if not self.is_stunned:
                # Когда персонаж не атакует:
                if not self.is_punching:
                    if not (self.moving_right or self.moving_left or 
                    self.moving_down or self.moving_up):
                        # если персонаж не двигается. то он будет анимация стояния
                        an.standing_animation(self)
                    else:
                        self.movement()
                        
                else:
                    self.attack()
            else:
                # Удар был справа
                if self.damaged_from_right:
                    an.stunning_animation(self, 'right', '-')
                # Удар был слева
                else:
                    an.stunning_animation(self, 'left', '+')
            
        else:
            self.death()
        
        self.rect.centerx = self.centerx
        self.rect.centery = self.centery

    def movement(self):
        if self.moving_right and self.rect.right <\
            self.mediator.get_value('screen_rect', 'right'):
            mv.going_right(self)
                            # Если активен пробел, то начинает атаку:
            self.initiate_punch(True, True)
        if self.moving_left and self.rect.left > 0:
            mv.going_left(self)
            self.initiate_punch(True, False)
        if self.moving_down and self.rect.bottom <\
            self.mediator.get_value('screen_rect', 'bottom'):
            mv.going_down(self)
        if self.moving_up and self.rect.top > 0:
            mv.going_up(self)
            

    def attack(self):
        '''Обработка атаки'''
        side = 'right' if self.right_punch else 'left'
        for i in range(self.frames):
            if (i + 1) * self.ats >= self.mediator.current_time() \
                - self.attack_timer > i * self.ats:
                self.image = pygame.image.load(f'images/K{self.surname}Main/' + 
                    f'punching_{side}' +
                    f'{i + 1 if i < floor(self.frames/2) else self.frames - i}' +
                    '.png').convert_alpha()
                self.correlate_rect_image(self.right_punch)
                mc_fist: Fist = self.mediator.get_value('mc_fist')
                mc_fist.change_position(
                    eval(f'self.an_rect.{side}'), 
                    self.rect.top + self.frl[i] if self.frl[i] > 0 else self.frl[i]) 
        if self.mediator.current_time() - self.attack_timer\
            >= self.frames * self.ats:
            self.is_punching = False
                    

    def initiate_punch(self, is_punching: bool, right_punch: bool):
        '''Активирует флаги атаки'''
        if self.space_active:
            self.is_punching = is_punching
            self.right_punch = right_punch
            self.attack_timer = monotonic()

    def get_damage(self, touching_fist: Fist):
        '''Активирует флаги получения урона'''
        tf = touching_fist
        self.damaged_from_right = tf.rect.centerx >= self.rect.centerx
        # Если ударивший противник - Диана, то она не выносит греха 
        # нанесенного ущерба и покидает поле боя.
        for enemy in self.mediator.get_collection('enemies'):
            if enemy.surname == 'D' and enemy.fist is tf:
                enemy.health = 0
                enemy.is_punching = False
                tf.kill()
                if self.rect.centerx > enemy.rect.centerx:
                    enemy.leaving_left = True
        self.health -= 1
        self.invincible = True
        self.is_stunned = True
        self.attack_timer = 0
        self.invin_timer = monotonic()
        

    def death(self):
        ''' "Анимация" смерти, смена состояния игры'''
        if hasattr(self, 'damaged_from_right'):
            if self.damaged_from_right:
                self.death_side = 'right'
            else:
                self.death_side = 'left'
            self.image = pygame.image.load(
                f'images/K{self.surname}Main/death_{self.death_side}.png').convert_alpha()
        else:
            self.image = pygame.image.load(f'images/K{self.surname}Main' +
            '/death_right.png').convert_alpha()
        self.an_rect = self.image.get_rect()
        self.an_rect.bottom = self.rect.bottom
        self.an_rect.centerx = self.rect.centerx
        self.blitme()
        pygame.display.flip()
        self.timer = monotonic()
        # Остановка всех звуков
        for name in self.mediator.get_value('audio', 'sounds').keys():
            self.mediator.get_value('audio', 'sounds')[name].stop()
        self.font = pygame.font.SysFont('tahoma', 48)
        self.mediator.set_value('st', 'state', 'Stats.GAMEOVER') 

    
    
        

    