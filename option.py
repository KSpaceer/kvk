

import pygame
from settings import Settings




class Option:
    '''Класс опции для изменения настроек'''

    # Численные значения для опций
    MUSIC_VOLUME = 0
    SOUND_VOLUME = 1

    number_to_name = {MUSIC_VOLUME : 'music_volume',
                      SOUND_VOLUME : 'sound_volume'}
    
    def __init__(self, screen: pygame.Surface, ai_settings: Settings, 
        name_number: int) -> None:
            self.screen = screen
            self.screen_rect = screen.get_rect()
            self.ai_settings = ai_settings
            self.name_number = name_number
            self.image = pygame.image.load('images/buttons/' +
                f'{Option.number_to_name[self.name_number]}.png').convert_alpha()
            self.rect = self.image.get_rect()
            # Опции находятся по середине экрана
            self.rect.centerx = self.screen_rect.centerx
            self.__is_chosen = False

    def blitme(self):
        '''Отображение изображения опции на экране'''
        self.screen.blit(self.image, self.rect)
        current_value = eval('int(self.ai_settings.' +
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
            self.screen.blit(orange_image, orange_rect)

    def vary_parameter(self, is_plus: bool):
        '''Изменяет параметр текущей опции'''
        sign = '+' if is_plus else '-'
        if eval('10 > self.ai_settings.' +
            f'{self.number_to_name[self.name_number]} > 0'):
            exec('self.ai_settings.' + self.number_to_name[self.name_number] 
                + sign + '= 1')
        # Краевые события
        elif eval('self.ai_settings.' + 
            self.number_to_name[self.name_number] + '== 10') and not is_plus:
            exec('self.ai_settings.' + self.number_to_name[self.name_number] 
                + '-= 1')
        elif eval('self.ai_settings.' + 
            self.number_to_name[self.name_number] + '== 0') and is_plus:
            exec('self.ai_settings.' + self.number_to_name[self.name_number] 
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

        