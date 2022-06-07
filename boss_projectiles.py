from math import radians, sin, cos
from random import randint, randrange
from secrets import choice
from time import monotonic
from pygame.sprite import Sprite
import pygame
from boss import Boss
from bull import Bull
from mediator import Mediator
from audiosounds import Audio
from path_handling import load_image


class SummoningCircle(Sprite):
    '''Класс призывающего круга, который босс создает во время призыва'''

    def __init__(self, boss: Boss, to_right: bool) -> None:
        '''Инициализация изображения, создателя и прямоугольника'''
        super().__init__()
        self.mediator = boss.mediator
        self.surname = boss.surname
        self.image = load_image(f'K{boss.surname}Enemies', 
            'boss', 'summoning_circle1.png')
        self.rect = self.image.get_rect()
        self.rect.center = boss.rect.center
        self.to_right = to_right
        self.ring_width = int(self.rect.width/2) 
        self.define_destination()
        # Координата в вещественном формате
        self.centerx = float(self.rect.centerx)
        self.timer = monotonic()
        self.animation_flag = False
        self.has_summoned = False
        self.mediator.call_method('audio', 'play_sound', '"summon"')
        

    def define_destination(self):
        '''Определяет точку назначения призывающего круга'''
        if self.to_right:
            # Изначально кольцо, в которое превратится круг 
            # при анимации самого призыва, является кругом.
            # Поэтому здесь используется его толщина (т.е. радиус круга)
            self.destination_point = self.mediator.get_value(
                'screen_rect', 'right') - self.ring_width
        else:
            self.destination_point = self.mediator.get_value(
                'screen_rect', 'left') + self.ring_width

    def blitme(self):
        '''Отображает призывающий круг'''
        self.mediator.blit_surface(self.image, self.rect)
    
    def update(self, *args) -> None:
        '''Обновление призывающего круга'''
        if self.rect.centerx not in range(
            self.destination_point - 3, self.destination_point + 4):
            self.movement()
            self.animation()
        else:
            if not self.has_summoned:
                self.summon_bull()
                self.circle_to_ring()
                
            if self.ring_width > 0:
                self.ring_is_narrowing()
            else:
                self.kill()

    def ring_is_narrowing(self):
        '''Сужение кольца'''
       
        self.image.fill(self.mediator.get_value('ai_settings', 'bg_color'))
        self.image.set_colorkey(
            self.mediator.get_value('ai_settings', 'bg_color'))
        pygame.draw.circle(self.image, (255, 246, 159), 
                self.ring_center, self.rect.width/2, self.ring_width)
        self.ring_width -= 2

    def circle_to_ring(self):
        '''Призывающий круг превращается в сужающееся кольцо'''
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill( self.mediator.get_value('ai_settings', 'bg_color'))
        self.image.set_colorkey(self.mediator.get_value('ai_settings', 'bg_color'))
        self.ring_center = (int(self.rect.width/2), int(self.rect.height/2))

    def summon_bull(self):
        '''Призыв бугая'''
        new_enemy = Bull(self.mediator, False)
        new_enemy.centerx, new_enemy.centery = self.centerx, \
                float(self.rect.centery)
        self.mediator.extend_collection('enemies', new_enemy)
        self.has_summoned = True

    def movement(self):
        '''Движение призывающего круга'''
        if self.to_right:
            self.centerx += self.mediator.get_value('ai_settings', 'sc_speed')
        else:
            self.centerx -= self.mediator.get_value('ai_settings', 'sc_speed')
        self.rect.centerx = int(self.centerx)
    
    def animation(self):
        '''Анимация призывающего круга'''
        if self.mediator.current_time() - self.timer >= self.mediator.get_value(
            'ai_settings', 'animation_change'):
            self.animation_flag = not self.animation_flag
            self.image = load_image(f'K{self.surname}Enemies', 
                'boss', f'summoning_circle{int(self.animation_flag) + 1}.png')
            self.timer = monotonic()


                
class BallLightning(Sprite):
    '''Класс шаровых молний, испускаемых боссом'''

    def __init__(self, boss: Boss) -> None:
        super().__init__()
        self.mediator = boss.mediator
        self.image = load_image('KSEnemies', 'boss', 'ball_lightning.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = boss.rect.centerx - 9
        self.rect.centery = boss.rect.centery - 127
        self.angle = radians(randint(0, 36) * 10)
        self.speed = self.mediator.get_value('ai_settings', 'bl_speed')
        # Координаты в вещественном формате
        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)
        self.mediator.call_method('audio', 'play_sound', '"lightning"')

    def blitme(self):
        '''Отображает шаровую молнию'''
        self.mediator.blit_surface(self.image, self.rect)

    def update(self, *args) -> None:
        '''Обновление шаровой молнии'''
        if not self.rect.colliderect(self.mediator.get_value('screen_rect')):
            self.kill()
            return
        self.centerx += self.speed * cos(self.angle)
        self.centery += self.speed * sin(self.angle)
        # Из действительных в целочисленные
        self.rect.centerx = int(self.centerx)
        self.rect.centery = int(self.centery)


class SpearTip(Sprite):
    '''Класс наконечника копья, выпускаемого боссом'''

    def __init__(self, boss: Boss) -> None:
        super().__init__()
        self.boss = boss
        self.mediator = boss.mediator
        self.timer = monotonic()
        self.speed = self.mediator.get_value('ai_settings', 'spear_speed')
        self.define_cardinal_direction()
        self.spear: list[Sprite] = []
        self.spear.append(self)
        self.has_played_sound = False
        

    
    def blitme(self):
        '''Отображает наконечник копья'''
        self.mediator.blit_surface(self.image, self.rect)

    
    def define_cardinal_direction(self):
        '''Определяет то, на какую сторону света будет направлено копье'''
        # 0 - N, 1 - W, 2 - S, 3 - E
        self.cardinal_direction = randint(0, 3)
        self.image = pygame.transform.rotate(
            load_image('KZEnemies', 'boss', 'spear_tip.png').convert_alpha(), 
            90 * self.cardinal_direction)
        self.rect = self.image.get_rect()
        # Копье нацеливается на главного персонажа
        self.define_starting_position()

    def define_starting_position(self):
        '''Определяет начальное местонахождение наконечника копья'''
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        mc_rect: pygame.Rect = self.mediator.get_value('mc', 'rect')
        if self.cardinal_direction == 0:
            self.rect.bottom = screen_rect.bottom
            self.rect.centerx = mc_rect.centerx
            # Направление движения копья
            self.dir_sign = -1
        elif self.cardinal_direction == 1:
            self.rect.right = screen_rect.right
            self.rect.centery = mc_rect.centery
            self.dir_sign = -1
        elif self.cardinal_direction == 2:
            self.rect.top = screen_rect.top
            self.rect.centerx = mc_rect.centerx
            self.dir_sign = 1
        else:
            self.rect.left = screen_rect.left
            self.rect.centery = mc_rect.centery
            self.dir_sign = 1

    def update(self, *args) -> None:
        '''Обновление наконечника копья'''
        # Пока босс использует ультимативную атаку, копья вытягиваются
        # на весь экран
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        if self.boss.using_ultimate:
            if screen_rect.contains(self.rect) \
                and self.mediator.current_time() - self.timer >= 1:
                if not self.has_played_sound:
                    self.mediator.call_method('audio', 'play_sound', '"spear"')
                    self.has_played_sound = True
                if self.cardinal_direction in (0, 2):
                    self.rect.centery += self.dir_sign * self.speed
                else:
                    self.rect.centerx += self.dir_sign * self.speed
                # Если последняя часть древка полностью на экране, создает новую
                if screen_rect.contains(self.spear[-1].rect):
                    new_spear_shaft = SpearShaft(self.spear)
                    self.spear.append(new_spear_shaft)
                    self.mediator.extend_collection('en_fists', new_spear_shaft)
                
        else:
            if self.cardinal_direction in (0, 2):
                self.rect.centery -= self.dir_sign * self.speed
            else:
                self.rect.centerx -= self.dir_sign * self.speed
            # Если последняя часть древка/наконечник не пересекается с экраном, удаляет его
            if not screen_rect.colliderect(self.spear[-1].rect):
                self.spear[-1].kill()
                self.spear.pop(-1)




class SpearShaft(Sprite):
    '''Класс древка копья, выпускаемого боссом'''

    def __init__(self, spear: pygame.sprite.Group) -> None:
        super().__init__()
        # Передний перед данным элемент копья
        self.the_next_in_spear: Sprite = spear[-1]
        self.spear_tip: SpearTip = spear[0]
        self.mediator = self.spear_tip.mediator
        self.cardinal_direction = self.spear_tip.cardinal_direction
        self.speed = self.spear_tip.speed
        self.image = pygame.transform.rotate(
            load_image('KZEnemies', 'boss', 'spear_shaft.png').convert_alpha(), 
            90 * self.cardinal_direction)
        self.rect = self.image.get_rect()
        self.define_starting_position()
        
    def blitme(self):
        '''Отображает древко копья'''
        self.mediator.blit_surface(self.image, self.rect)

    def define_starting_position(self):
        '''Определяет начальное положение древка'''
        if self.cardinal_direction == 0:
            self.dir_sign = -1
            self.rect.centerx = self.spear_tip.rect.centerx
            # Поскольку после появления новой части копья произойдет обновление старых,
            # необходимо скорректировать позицию новой части копья на скорость копья
            self.rect.top = self.the_next_in_spear.rect.bottom\
                 + self.speed * self.dir_sign
        elif self.cardinal_direction == 1:
            self.dir_sign = -1
            self.rect.centery = self.spear_tip.rect.centery
            self.rect.left = self.the_next_in_spear.rect.right\
                 + self.speed * self.dir_sign
        elif self.cardinal_direction == 2:
            self.dir_sign = 1
            self.rect.centerx = self.spear_tip.rect.centerx
            self.rect.bottom = self.the_next_in_spear.rect.top\
                 + self.speed * self.dir_sign
        else:
            self.dir_sign = 1
            self.rect.centery = self.spear_tip.rect.centery
            self.rect.right = self.the_next_in_spear.rect.left\
                 + self.speed * self.dir_sign
            

    def update(self, *args) -> None:
        '''Обновление древка копья'''
        if self.spear_tip.boss.using_ultimate:
            screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
            if screen_rect.contains(self.spear_tip.rect):
                if self.cardinal_direction in (0, 2):
                    self.rect.centery += self.dir_sign * self.speed
                else:
                    self.rect.centerx += self.dir_sign * self.speed
        else:
            if self.cardinal_direction in (0, 2):
                self.rect.centery -= self.dir_sign * self.speed
            else:
                self.rect.centerx -= self.dir_sign * self.speed


class Blade(Sprite):
    '''Класс лезвий, выпускаемых боссом'''

    def __init__(self, boss: Boss) -> None:
        super().__init__()
        self.mediator = boss.mediator
        self.speed = self.mediator.get_value('ai_settings', 'blade_speed')
        self.image = load_image('KSEnemies', 'boss', 'blade.png')
        self.rect = self.image.get_rect()
        self.define_starting_position(boss)
        self.timer = monotonic()
        self.has_played_sound = False
        
        

    def define_starting_position(self, boss: Boss):
        '''Определяет начальную позицию лезвия'''
        # В зависимости от выбранной боссом стороны,
        # пределы местонахождения кинжала по Х меняются
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        mc_rect: pygame.Rect = self.mediator.get_value('mc', 'rect')
        if boss.side:
            allowed_x = (screen_rect.left + mc_rect.width * 2, 
                screen_rect.right - boss.rect.width)
        else:
            allowed_x = (screen_rect.left + boss.rect.width, 
                screen_rect.right - mc_rect.width * 2)
        self.rect.centerx = randrange(allowed_x[0], allowed_x[1], 10)
        # Положение по Y (сверху или снизу) выбирается случайно
        self.rect.bottom, self.direction = choice(
            [(screen_rect.top + self.rect.height, 1), 
            (screen_rect.bottom, -1)])

    def blitme(self):
        '''Отображает лезвие'''
        self.mediator.blit_surface(self.image, self.rect)

    def update(self, *args) -> None:
        '''Обновление лезвия'''
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        if screen_rect.colliderect(self.rect):
            if self.mediator.current_time() - self.timer >= 1:
                if not self.has_played_sound:
                    self.mediator.call_method('audio', 'play_sound', '"blade"')
                    self.has_played_sound = True
                self.rect.centery += self.direction * self.speed
        else:
            self.kill()

    
            
        
class Saw(Sprite):
    '''Класс пил, вызываемых боссом'''

    vertical_positions = [0,]
    horizontal_positions = [0,]
    
    def __init__(self, boss: Boss) -> None:
        super().__init__()
        self.boss = boss
        self.mediator = boss.mediator
        self.speed = self.mediator.get_value('ai_settings', 'saw_speed')
        self.image = load_image('KZEnemies', 'boss', 'saw1.png')
        self.rect = self.image.get_rect()
        self.is_vertical = randint(0, 1) # пила двигается вертикально или горизонтально
        self.define_starting_position()
        # Атрибуты для анимации
        self.timer = monotonic()
        self.animation_change = self.mediator.get_value(
            'ai_settings', 'animation_change')/2
        self.animation_number = True # bool -> int
        audio: Audio = self.mediator.get_value('audio')
        if 'saw' not in audio.sounds.keys():
            audio.play_sound('saw', -1)

    def define_starting_position(self):
        '''Определяет начальное положение пилы'''
        self.rect.center = 0, 0
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        maze_narrowing = self.mediator.get_value('ai_settings', 'maze_narrowing')
        left_border = screen_rect.left + maze_narrowing
        right_border = screen_rect.right - maze_narrowing
        if self.is_vertical:
            self.vertical_starting_position(
                left_border, right_border, screen_rect)
        else:
            self.horisontal_starting_position(
                left_border, right_border, screen_rect)

    def horisontal_starting_position(self, left_border, right_border, 
        screen_rect: pygame.Rect):
        '''Начальная позиция для горизонтально движущейся пилы'''
        # Пилы не могут быть на одной высоте
        while self.rect.centery in Saw.horizontal_positions:
            self.rect.centery = randrange(25, screen_rect.height - 25, 25)
        Saw.horizontal_positions.append(self.rect.centery)
        self.border1 = self.border2 = 0
        while abs(self.border1 - self.border2) < 100:
            self.border1 = randrange(left_border, right_border, 25)
            self.border2 = randrange(left_border, right_border, 25)
        # Изначально пила идет влево или вправо
        if self.border1 > self.border2:
            # Влево
            self.dir_sign = -1
            self.rect.right = self.border1
        else:
            # Вправо
            self.dir_sign = 1
            self.rect.left = self.border1

    def vertical_starting_position(self, left_border, right_border, 
        screen_rect: pygame.Rect):
        '''Начальная позиция для вертикально движущейся пилы'''
        # Пилы не могут быть на одной ширине
        while self.rect.centerx in Saw.vertical_positions:
            self.rect.centerx = randrange(left_border, right_border, 25)
        Saw.vertical_positions.append(self.rect.centerx)
        self.border1 = self.border2 = 0
            # Случайный выбор границ (должны различаться как минимум на 100 пикселей)
        while abs(self.border1 - self.border2) < 100:
            self.border1 = randrange(0, screen_rect.height, 25)
            self.border2 = randrange(0, screen_rect.height, 25)
            # Изначально пила идет вверх или вниз
        if self.border1 > self.border2:
                # Вверх
            self.dir_sign = -1
            self.rect.bottom = self.border1
        else:
                # Вниз
            self.dir_sign = 1
            self.rect.top = self.border1
    
    

    def blitme(self):
        '''Отображение пилы'''
        self.mediator.blit_surface(self.image, self.rect)

    def update(self, *args) -> None:
        '''Обновление пилы'''
        self.movement()
        self.animation()
        if not self.boss.using_ultimate:
            self.kill()
            del self.boss

    def animation(self):
        '''Анимация пилы'''
        if self.mediator.current_time() - self.timer >= self.animation_change:
            self.image = load_image('KZEnemies', 'boss', 
                f'saw{int(self.animation_number) + 1}.png')
            self.timer = monotonic()
            self.animation_number = not self.animation_number

    def movement(self):
        '''Движение пилы'''
        if self.is_vertical:
            # Если пила вышла за пределы границ
            if all((self.rect.top < self.border1, 
                self.rect.top < self.border2)) or all(
                (self.rect.bottom > self.border1, 
                self.rect.bottom > self.border2)):
                self.dir_sign *= -1
            self.rect.centery += self.dir_sign * self.speed
        else:
            # Если пила вышла за пределы границ
            if all((self.rect.right > self.border1, 
                self.rect.right > self.border2)) or all(
                (self.rect.left < self.border1, 
                self.rect.left < self.border2)):
                self.dir_sign *= -1
            self.rect.centerx += self.dir_sign * self.speed

    

class Crack(Sprite):
    '''Класс разлома, создаваемого боссом'''

    def __init__(self, centerx: int, centery: int, mediator: Mediator) -> None:
        super().__init__()
        self.image = load_image('KZEnemies', 'boss', 'crack.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.mediator = mediator
        self.timer = monotonic()

    def blitme(self):
        '''Отображение разлома'''
        self.mediator.blit_surface(self.image, self.rect)

    def update(self, *args) -> None:
        '''Обновление разлома'''
        if self.mediator.current_time() - self.timer >= 25:
            self.kill()

    






        