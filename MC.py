from time import monotonic
import mc_animation as an
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


    
    def blitme(self):
        '''Рисует персонажа в текущей позиции'''
        if not self.is_punching and self.health > 0:
            self.mediator.blit_surface(self.image, self.rect)
        else:
            self.mediator.blit_surface(self.image, self.rect)
    
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
                    if self.right_punch:
                        self.right_attack()
                    else:
                        self.left_attack()
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
            self.going_right()
                            # Если активен пробел, то начинает атаку:
            self.initiate_punch(True, True)
        if self.moving_left and self.rect.left > 0:
            self.going_left()
            self.initiate_punch(True, False)
        if self.moving_down and self.rect.bottom <\
            self.mediator.get_value('screen_rect', 'right'):
            self.going_down()
        if self.moving_up and self.rect.top > 0:
            self.going_up()
            

    


    def right_attack(self):
        '''Процесс атаки на правую сторону'''
        if self.attack_timer == 0:
            # Загружаем изображение
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right1.png').convert_alpha()
            self.correlate_rect_image(True)
            self.attack_timer = monotonic() # Обновление таймера
        elif 2 * self.ats >= self.mediator.current_time() - self.attack_timer \
                    > self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right2.png').convert_alpha()
            self.correlate_rect_image(True)
            # Изменение позиции кулака
            self.mediator.get_value('mc_fist').change_position(
                self.an_rect.right, self.rect.top + 26) 
        elif 3 * self.ats >= self.mediator.current_time() - self.attack_timer > \
                    2 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right3.png').convert_alpha()
            self.correlate_rect_image(True)
            self.mediator.get_value('mc_fist').change_position(
                self.an_rect.right, self.rect.top + 35)
            
        elif 4 * self.ats >= self.mediator.current_time() - self.attack_timer > \
                    3 * self.ats:
            self.mediator.get_value('mc_fist').change_position(-50, -50)
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right2.png').convert_alpha()
            self.correlate_rect_image(True)
        elif 5 * self.ats >= self.mediator.current_time() - self.attack_timer > \
                     4 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right1.png').convert_alpha()
            self.correlate_rect_image(True)
        elif self.mediator.current_time() - self.attack_timer > 5 * self.ats:
            self.is_punching = False # Атака закончена

    def left_attack(self):                   
        '''Процесс атаки на левую сторону'''
        if self.attack_timer == 0:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left1.png').convert_alpha()
            self.correlate_rect_image(False)
            self.attack_timer = monotonic()
            
        elif 2 * self.ats >= self.mediator.current_time() - self.attack_timer \
                    > self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left2.png').convert_alpha()
            self.correlate_rect_image(False)
            self.mediator.get_value('mc_fist').change_position(
                self.an_rect.left, self.rect.top + 25) 
            
        elif 3 * self.ats >= self.mediator.current_time() - self.attack_timer > \
                    2 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left3.png').convert_alpha()
            self.correlate_rect_image(False)
            self.mediator.get_value('mc_fist').change_position(
                self.an_rect.left, self.rect.top + 34)
           
            
        elif 4 * self.ats >= self.mediator.current_time() - self.attack_timer > \
                    3 * self.ats:
            self.mediator.get_value('mc_fist').change_position(-50, -50)
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left2.png').convert_alpha()
            self.correlate_rect_image(False)

        elif 5 * self.ats >= self.mediator.current_time() - self.attack_timer > \
                     4 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left1.png').convert_alpha()
            self.correlate_rect_image(False)

        elif self.mediator.current_time() - self.attack_timer > 5 * self.ats:
            self.is_punching = False
                    
    
    def going_right(self):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение 
        вправо'''
        for enemy in self.mediator.get_collection('enemies'):
            if self.rect.right in range(enemy.rect.left - 10, enemy.rect.left + 10):
                # Если персонаж расположен намного ниже врага, то он может пройти
                if self.rect.centery in range(
                enemy.rect.bottom - enemy.rect.height, 
                enemy.rect.bottom - int(enemy.rect.height/3)):
                    return
        
        self.centerx += self.speed
        an.going_right_animation(self)

    def going_left(self):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение 
        влево'''
        for enemy in self.mediator.get_collection('enemies'):
            if self.rect.left in range(enemy.rect.right - 10, enemy.rect.right + 10):
                # Если персонаж расположен намного ниже врага, то он может пройти
                if self.rect.centery in range(
                enemy.rect.bottom - enemy.rect.height, 
                enemy.rect.bottom - int(enemy.rect.height/3)):
                    return
        self.centerx -= self.speed
        an.going_left_animation(self)

    def going_down(self):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение
        вниз'''
        for enemy in self.mediator.get_collection('enemies'):
            if self.rect.bottom in range(enemy.rect.top - 10, enemy.rect.top + 10):
                if self.rect.centerx in range(
                enemy.rect.left, enemy.rect.left + enemy.rect.width):               
                    return
        self.centery += self.speed
        an.going_down_animation(self)

    def going_up(self):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение
        вверх'''
        for enemy in self.mediator.get_collection('enemies'):
            if self.rect.top in range(enemy.rect.bottom - 10, enemy.rect.bottom + 10):
                if self.rect.centerx in range(
                enemy.rect.left, enemy.rect.left + enemy.rect.width):                
                    return
        self.centery -= self.speed
        an.going_up_animation(self)

    def initiate_punch(self, is_punching: bool, right_punch: bool):
        '''Активирует флаги атаки'''
        if self.space_active:
            self.is_punching = is_punching
            self.right_punch = right_punch
            self.attack_timer = 0

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
        self.mediator.set_value('st', 'state', 'st.GAMEOVER') 

    
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
        

    