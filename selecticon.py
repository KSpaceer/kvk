import pygame



class SelectIcon():
    '''Класс для иконок выбора персонажа'''

    def __init__(self, surname, screen) -> None:
        '''Инициализация параметров по первой букве фамилии персонажа'''
        self.image = pygame.image.load(f'images/K{surname}Main/selection.png')
        self.rect = self.image.get_rect()
        self.surname = surname
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.rect.centery = self.screen_rect.centery
        self.a_image = pygame.image.load(
            f'images/K{surname}Main/selection(active).png')
        self.a_rect = self.a_image.get_rect()
        self.a_rect.centery = self.screen_rect.centery

        if surname == 'S':
            self.rect.centerx = self.screen_rect.centerx - 180
            self.a_rect.centerx = self.screen_rect.centerx - 180
            self.is_selected = True
        else:
            self.rect.centerx = self.screen_rect.centerx + 180
            self.a_rect.centerx = self.screen_rect.centerx + 180
            self.is_selected = False
        
    def blitme(self):
        '''Отображение изображения на экране'''
        if self.is_selected:
            self.screen.blit(self.a_image, self.a_rect)
        self.screen.blit(self.image, self.rect)