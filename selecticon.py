import pygame
from mediator import Mediator
from path_handling import load_image



class SelectIcon():
    '''Класс для иконок выбора персонажа'''

    def __init__(self, surname: str, mediator: Mediator) -> None:
        '''Инициализация параметров по первой букве фамилии персонажа'''
        # Добавление изображение, прямоугольника, первой буквы фамилии
        self.image = load_image(f'K{surname}Main', 'selection.png')
        self.rect = self.image.get_rect()
        self.surname = surname
        self.mediator = mediator
        # Вертикально изображения находятся на середине экрана
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        self.rect.centery = screen_rect.centery
        # Изображение активного выбора (ярко-желтый силуэт):
        self.a_image = load_image(f'K{surname}Main', 'selection(active).png')
        # Соотв. прямоугольник, тоже вертикально по центру
        self.a_rect = self.a_image.get_rect()
        self.a_rect.centery = screen_rect.centery

        if surname == 'S':
            # Если фамилия моя, то изображение будет чуть левее центра
            # Изначально выбран я
            self.rect.centerx = screen_rect.centerx - 180
            self.a_rect.centerx = screen_rect.centerx - 180
            self.is_selected = True
        else:
            # Если З., то чуть правее
            self.rect.centerx = screen_rect.centerx + 180
            self.a_rect.centerx = screen_rect.centerx + 180
            self.is_selected = False
        
    def blitme(self):
        '''Отображение изображения на экране'''
        if self.is_selected:
            # Если выбран данный персонаж, подсвечивает его
            self.mediator.blit_surface(self.a_image, self.a_rect)
        self.mediator.blit_surface(self.image, self.rect)