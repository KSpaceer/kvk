from time import monotonic
import pygame
from enemy import Enemy
from fist import Fist
import bull_animation as an



class Bull(Enemy):
    '''Класс первого типа врагов - бугаев'''

    def __init__(self, screen, ai_settings, mc, st, timer, cur_time):
        '''Инициализация параметров, начального положения и изображения'''
        super().__init__(screen, ai_settings, mc, st, timer, cur_time)
        # Инициализация здоровья
        self.health = 10 * self.ai_settings.h_multiplier
        
        # Загрузка изображения
        self.image = pygame.image.load('images/KSEnemies/Bull/standing.png')
        self.rect = self.image.get_rect()
        # Враг появляется с отдаленной от главного персонажа стороны экрана
        self.spawning_point()
        # Прямоугольник для анимаций
        self.an_rect = self.rect
        # Сохранение координат центра в виде вещественных чисел
        self.centerx = self.rect.centerx
        self.centery = self.rect.centery
        # Сохраняем скорость атаки в более удобном виде
        self.ats = ai_settings.bull_attack_speed
        # Создаем ударную поверхность
        self.fist = Fist(screen)
        # Список координат верха прямоугольника ударной поверхности
        # относительно верха прямоугольника анимаций для 4 последних кадров
        self.frl_top = [16, 15, 12, 15] # frl - fist relative location
        self.frl_side = [63, 87, 104, 114]
        
    
    def update(self, fist, enemies, en_fists):
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
                    where_am_i_y = self.rect.centery in range(
                        self.mc.rect.centery - 5,self.mc.rect.centery + 6)
                    where_am_i_x = self.rect.left in range(
                        self.mc.rect.right - 5, self.mc.rect.right + 6)  \
                        or self.rect.right in range(
                        self.mc.rect.left - 5, self.mc.rect.left + 6)
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
                    self.ai_settings.bull_cooldown:
                        self.initiate_punch()

                else:
                   self.attack(en_fists)
            else:
                an.stunning_animation(self, self.ai_settings)      
        else:
            if not self.is_dead:
                self.timer = monotonic()
                self.is_dead = True
            an.death_animation(self, self.ai_settings, enemies)
        

    def get_damage(self):
        '''Получение урона и оглушение'''
        self.health -= self.ai_settings.mc_damage
        self.is_stunned = True
        self.image = pygame.image.load(
                        'images/KSEnemies/Bull/stunned.png')
        self.change_rect()
        self.timer = monotonic()
            
    def vertical_movement(self):
        '''Перемещение врага по вертикали'''
        if self.rect.centery < self.mc.rect.centery:
            an.going_vertical_animation(self, self.ai_settings)
            self.centery += self.ai_settings.bull_speed_factor
        else:
            an.going_vertical_animation(self, self.ai_settings)
            self.centery -= self.ai_settings.bull_speed_factor

    def horizontal_movement(self):
        '''Перемещение врага по горизонтали'''
        if self.rect.left > self.mc.rect.right:
            an.going_left_animation(self, self.ai_settings)
            self.centerx -= self.ai_settings.bull_speed_factor
        elif self.rect.right < self.mc.rect.left:
            an.going_right_animation(self, self.ai_settings)
            self.centerx += self.ai_settings.bull_speed_factor
        else:
            if self.rect.centerx > self.mc.rect.centerx:
                an.going_right_animation(self, self.ai_settings)
                self.centerx += self.ai_settings.bull_speed_factor
            else:
                an.going_left_animation(self, self.ai_settings)
                self.centerx -= self.ai_settings.bull_speed_factor

    def initiate_punch(self):
        '''Активирует флаги атаки'''
        self.is_punching = True
        if self.rect.centerx > self.mc.rect.centerx:
            self.right_punch = False
        else:
            self.right_punch = True          
        self.timer = monotonic()

    def attack(self, en_fists):
        '''Обработка атаки'''
        file_end_name, sign, rect_side = self.define_attack_vars()
        

        # 10 - количество кадров
        for i in range(10):
            # Кадры сменяются по времени:
            if (i+1) * self.ats >= self.cur_time.time - self.timer > i * self.ats:
                # Кадров (изображений именно) всего 5
                if i in range(6):
                    if i == 0:
                        self.create_new_rect()
                        en_fists.add(self.fist)
                        
                    self.image = pygame.image.load(
                        'images/KSEnemies/Bull/punching{0}_{1}.png'.format(
                            i + 1, file_end_name))                    
                    if i <= 1:
                        # Т.к. в первом и втором кадрах рука расположена
                        # за телом, то центр этих кадров размещаются
                        # чуть дальше боковой стороны прямоугольника
                        self.an_rect = self.image.get_rect()
                        self.an_rect.centery = self.rect.centery
                        exec('self.an_rect.centerx = self.rect.{}'.format(
                            rect_side) + sign + '20')
                    else:
                        self.correlate_rect_image(self.right_punch)
                        # Перемещает ударную поверхность:
                        exec('self.fist.change_position( \
                        self.an_rect.{0} {1} self.frl_side[i-2], \
                        self.an_rect.top + self.frl_top[i-2])'.format(
                            rect_side, sign))
                        
                        
                else:
                    if i == 6 and self.fist in en_fists:
                        # Удаляем ударную поверхность:
                        en_fists.remove(self.fist)
                        
                    # Кадры идут в обратном порядке
                    self.image = pygame.image.load(
                        'images/KSEnemies/Bull/punching{0}_{1}.png'.format(
                            11 - i, file_end_name))
                    self.correlate_rect_image(self.right_punch)
                    if i == 9:
                        # Атака закончена, начинается перезарядка
                        self.is_punching = False
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
        fake_rect = pygame.Rect(0, 0, 77, 238)
        fake_rect.centerx = self.rect.centerx
        fake_rect.centery = self.rect.centery
        self.rect = fake_rect

    def correlate_rect_image(self, side):
        '''Соотносит изначальный прямоугольник с измененным изображением
        True - анимация вправо, т.е. у прямоугольников одинаковое расположение левой стороны.
        False - влево, соответственно одинаковое расположение правой стороны'''
        self.an_rect = self.image.get_rect()
        self.an_rect.top = self.rect.top
        if side:
            self.an_rect.left = self.rect.left
        else:
            self.an_rect.right = self.rect.right


    