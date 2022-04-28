import pygame



class SelectIcon():
    '''Класс для иконок выбора персонажа'''

    def __init__(self, surname: str, screen: pygame.Surface) -> None:
        '''Инициализация параметров по первой букве фамилии персонажа'''
        # Добавление изображение, прямоугольника, первой буквы фамилии
        self.image = pygame.image.load(f'images/K{surname}Main/' + 
        'selection.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.surname = surname
        self.screen = screen
        self.screen_rect = screen.get_rect()
        # Вертикально изображения находятся на середине экрана
        self.rect.centery = self.screen_rect.centery
        # Изображение активного выбора (ярко-желтый силуэт):
        self.a_image = pygame.image.load(
            f'images/K{surname}Main/selection(active).png').convert_alpha()
        # Соотв. прямоугольник, тоже вертикально по центру
        self.a_rect = self.a_image.get_rect()
        self.a_rect.centery = self.screen_rect.centery

        if surname == 'S':
            # Если фамилия моя, то изображение будет чуть левее центра
            # Изначально выбран я
            self.rect.centerx = self.screen_rect.centerx - 180
            self.a_rect.centerx = self.screen_rect.centerx - 180
            self.is_selected = True
        else:
            # Если З., то чуть правее
            self.rect.centerx = self.screen_rect.centerx + 180
            self.a_rect.centerx = self.screen_rect.centerx + 180
            self.is_selected = False
        
    def blitme(self):
        '''Отображение изображения на экране'''
        if self.is_selected:
            # Если выбран данный персонаж, подсвечивает его
            self.screen.blit(self.a_image, self.a_rect)
        self.screen.blit(self.image, self.rect)