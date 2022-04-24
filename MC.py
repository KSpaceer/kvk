from time import monotonic
import mc_animation as an
import pygame
from pygame.sprite import Sprite
from settings import Settings
from etimer import Timer
from fist import Fist
from stats import Stats

class MainCharacter(Sprite):
    '''Класс главного персонажа'''
    def __init__(self, screen: pygame.Surface, ai_settings: Settings, 
        cur_time: Timer, surname: str = None):
        '''Инициализация главного персонажа и задание его начальной позиции'''
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        self.speed = self.ai_settings.mc_speed_factor
        # Первая буква фамилии персонажа
        self.surname = surname
        # Загрузка изображения
        self.image = pygame.image.load('images/KSMain/standing.png')
        self.rect = self.image.get_rect()
        # Прямоугольник для анимаций
        self.an_rect = self.rect
        # Персонаж появляется ближе к левому экрану
        self.screen_rect = screen.get_rect()
        self.rect.centery = self.screen_rect.centery
        self.rect.left = self.screen_rect.left + 200
        # Сохранение вещественной координаты центра персонажа
        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)
        # Здоровье
        self.health = ai_settings.mc_health
        # Флаги перемещения и переключатели анимации:
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.is_right_leg = True
        self.timer = 0
        self.attack_timer = 0
        self.space_active = False
        # Текущее время
        self.cur_time = cur_time
        # Таймер неуязвимости
        self.invin_timer = 0
        # Флаги удара
        self.is_punching = False
        self.right_punch = False
        # Флаги оглушения и неуязвимости
        self.is_stunned = False
        self.invincible = False
        # Скорость атаки (для удобства зададим новую переменную)
        self.ats = self.ai_settings.attack_speed
        

    def blitme(self):
        '''Рисует персонажа в текущей позиции'''
        if not self.is_punching and self.health > 0:
            self.screen.blit(self.image, self.rect)
        else:
            self.screen.blit(self.image, self.an_rect)
    
    def update(self, enemies: pygame.sprite.Group, fist: Fist, st: Stats):
        '''Обновляет позицию главного персонажа'''
        # Если персонаж жив
        if self.health > 0:
            # Если персонаж неуязвим:
            if self.invincible:
                if self.cur_time - self.invin_timer >= self.ai_settings.inv_duration:
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
                        if self.moving_right and self.rect.right < self.screen_rect.right:
                            self.going_right(enemies)
                            # Если активен пробел, то начинает атаку:
                            self.initiate_punch(True, True)
                        if self.moving_left and self.rect.left > 0:
                            self.going_left(enemies)
                            self.initiate_punch(True, False)
                        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
                            self.going_down(enemies)
                        if self.moving_up and self.rect.top > 0:
                            self.going_up(enemies)
                        
                else:
                    if self.right_punch:
                        self.right_attack(fist)
                    else:
                        self.left_attack(fist)
            else:
                # Удар был справа
                if self.tf.rect.centerx >= self.rect.centerx:
                    an.stunning_animation(self, 'right', '-')
                # Удар был слева
                else:
                    an.stunning_animation(self, 'left', '+')
            
        else:
            self.death(st)
        
        self.rect.centerx = self.centerx
        self.rect.centery = self.centery
            

    


    def right_attack(self, fist: Fist):
        '''Процесс атаки на правую сторону'''
        if self.attack_timer == 0:
            # Загружаем изображение
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right1.png')
            self.correlate_rect_image(True)
            self.attack_timer = monotonic() # Обновление таймера
        elif 2 * self.ats >= self.cur_time - self.attack_timer \
                    > self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right2.png')
            self.correlate_rect_image(True)
            # Изменение позиции кулака
            fist.change_position(self.an_rect.right, self.rect.top + 26) 
        elif 3 * self.ats >= self.cur_time - self.attack_timer > \
                    2 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right3.png')
            self.correlate_rect_image(True)
            fist.change_position(self.an_rect.right, self.rect.top + 35)
            
        elif 4 * self.ats >= self.cur_time - self.attack_timer > \
                    3 * self.ats:
            fist.change_position(-50, -50)
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right2.png')
            self.correlate_rect_image(True)
        elif 5 * self.ats >= self.cur_time - self.attack_timer > \
                     4 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_right1.png')
            self.correlate_rect_image(True)
        elif self.cur_time - self.attack_timer > 5 * self.ats:
            self.is_punching = False # Атака закончена

    def left_attack(self, fist: Fist):                   
        '''Процесс атаки на левую сторону'''
        if self.attack_timer == 0:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left1.png')
            self.correlate_rect_image(False)
            self.attack_timer = monotonic()
            
        elif 2 * self.ats >= self.cur_time - self.attack_timer \
                    > self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left2.png')
            self.correlate_rect_image(False)
            fist.change_position(self.an_rect.left, self.rect.top + 25) 
            
        elif 3 * self.ats >= self.cur_time - self.attack_timer > \
                    2 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left3.png')
            self.correlate_rect_image(False)
            fist.change_position(self.an_rect.left, self.rect.top + 34)
           
            
        elif 4 * self.ats >= self.cur_time - self.attack_timer > \
                    3 * self.ats:
            fist.change_position(-50, -50)
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left2.png')
            self.correlate_rect_image(False)

        elif 5 * self.ats >= self.cur_time - self.attack_timer > \
                     4 * self.ats:
            self.image = pygame.image.load(
                        f'images/K{self.surname}Main/punching_left1.png')
            self.correlate_rect_image(False)

        elif self.cur_time - self.attack_timer > 5 * self.ats:
            self.is_punching = False
                    
    
    def going_right(self, enemies: pygame.sprite.Group):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение 
        вправо'''
        for enemy in enemies:
            if self.rect.right in range(enemy.rect.left - 10, enemy.rect.left + 10):
                # Если персонаж расположен намного ниже врага, то он может пройти
                if self.rect.centery in range(
                enemy.rect.bottom - enemy.rect.height, 
                enemy.rect.bottom - int(enemy.rect.height/3)):
                    return
        
        self.centerx += self.speed
        an.going_right_animation(self)

    def going_left(self, enemies: pygame.sprite.Group):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение 
        влево'''
        for enemy in enemies:
            if self.rect.left in range(enemy.rect.right - 10, enemy.rect.right + 10):
                # Если персонаж расположен намного ниже врага, то он может пройти
                if self.rect.centery in range(
                enemy.rect.bottom - enemy.rect.height, 
                enemy.rect.bottom - int(enemy.rect.height/3)):
                    return
        self.centerx -= self.speed
        an.going_left_animation(self)

    def going_down(self, enemies: pygame.sprite.Group):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение
        вниз'''
        for enemy in enemies:
            if self.rect.bottom in range(enemy.rect.top - 10, enemy.rect.top + 10):
                if self.rect.centerx in range(
                enemy.rect.left, enemy.rect.left + enemy.rect.width):               
                    return
        self.centery += self.speed
        an.going_down_animation(self)

    def going_up(self, enemies: pygame.sprite.Group):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение
        вверх'''
        for enemy in enemies:
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

    def get_damage(self, touching_fist, en_fists, enemies):
        '''Активирует флаги получения урона'''
        self.tf = touching_fist
        # Если ударивший противник - Диана, то она не выносит греха 
        # нанесенного ущерба и покидает поле боя.
        for enemy in enemies:
            if enemy.surname == 'D' and enemy.fist is self.tf:
                enemy.health = 0
                enemy.is_punching = False
                en_fists.remove(self.tf)
                if self.rect.centerx > enemy.rect.centerx:
                    enemy.leaving_left = True
        self.health -= 1
        self.invincible = True
        self.is_stunned = True
        self.attack_timer = 0
        self.invin_timer = monotonic()
        

    def death(self, st: Stats):
        ''' "Анимация" смерти, смена состояния игры'''
        if hasattr(self, 'tf'):
            if self.tf.rect.centerx >= self.rect.centerx:
                self.death_side = 'right'
            else:
                self.death_side = 'left'
            self.image = pygame.image.load(
                f'images/K{self.surname}Main/death_{self.death_side}.png')
        else:
            self.image = pygame.image.load(f'images/K{self.surname}Main/death_right.png')
        self.an_rect = self.image.get_rect()
        self.an_rect.bottom = self.rect.bottom
        self.an_rect.centerx = self.rect.centerx
        self.blitme()
        st.state = st.GAMEOVER 

    
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
        

    