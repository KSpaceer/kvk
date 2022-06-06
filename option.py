

import pygame
from mediator import Mediator
from settings import Settings




class Option:
    '''Класс опции для изменения настроек'''

    # Численные значения для опций
    MUSIC_VOLUME = 0
    SOUND_VOLUME = 1

    number_to_name = {MUSIC_VOLUME : 'music_volume',
                      SOUND_VOLUME : 'sound_volume'}
    
    def __init__(self, mediator: Mediator, 
        name_number: int) -> None:
            self.mediator = mediator
            self.name_number = name_number
            self.image = pygame.image.load('images/buttons/' +
                f'{Option.number_to_name[self.name_number]}.png').convert_alpha()
            self.rect = self.image.get_rect()
            # Опции находятся по середине экрана
            self.rect.centerx = self.mediator.get_value('screen_rect', 'centerx')
            self.__is_chosen = False

    def blitme(self):
        '''Отображение изображения опции на экране'''
        self.mediator.blit_surface(self.image, self.rect)
        ai_settings = self.mediator.get_value('ai_settings')
        current_value = eval('int(ai_settings.' +
            f'{self.number_to_name[self.name_number]})')
        # Рисуем апельсинки-указатели величины
        for i in range(10):
            orange_rect = pygame.Rect(self.rect.left + 87 + 54 * i, 
                self.rect.bottom - 50, 40, 40)
            if i <= current_value - 1:
                orange_image = pygame.image.load('images/buttons/' +
                    'active_orange.png')
            else:
                orange_image = pygame.image.load('images/buttons/' +
                    'inactive_orange.png')
            self.mediator.blit_surface(orange_image, orange_rect)

    def vary_parameter(self, is_plus: bool):
        '''Изменяет параметр текущей опции'''
        sign = '+' if is_plus else '-'
        ai_settings = self.mediator.get_value('ai_settings')
        if eval('10 > ai_settings.' +
            f'{self.number_to_name[self.name_number]} > 0'):
            exec('ai_settings.' + self.number_to_name[self.name_number] 
                + sign + '= 1')
        # Краевые события
        elif eval('ai_settings.' + 
            self.number_to_name[self.name_number] + '== 10') and not is_plus:
            exec('ai_settings.' + self.number_to_name[self.name_number] 
                + '-= 1')
        elif eval('ai_settings.' + 
            self.number_to_name[self.name_number] + '== 0') and is_plus:
            exec('ai_settings.' + self.number_to_name[self.name_number] 
                + '+= 1')
    
    @property
    def is_chosen(self):
        return self.__is_chosen

    @is_chosen.setter
    def is_chosen(self, value: bool):
        addition = '(selected)' if value else ''
        self.image = pygame.image.load('images/buttons/' 
        + f'{Option.number_to_name[self.name_number]}' + addition 
        +'.png').convert_alpha()
        self.__is_chosen = value

    @is_chosen.deleter
    def is_chosen(self):
        del self.__is_chosen

        