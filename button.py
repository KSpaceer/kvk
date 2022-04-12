import pygame


class Button():
    '''Класс для кнопок'''
    
    # Численные значения для кнопок, чтобы в коде вызов выглядел наглядно
    NEWGAME = 0
    LOAD = 1
    OPTIONS = 2
    EXIT = 3
    SAVE = 4
    MENU = 5
    SAVEFILE = 6
    EMPTY = 7
    # Словарь для того, чтобы соотнести численные значения с именами файлов
    image_names_dict = {NEWGAME : 'new_game',
                        LOAD : 'load',
                        OPTIONS : 'options',
                        EXIT : 'exit',
                        MENU : 'menu',
                        SAVE : 'save',
                        SAVEFILE : 'savefile',
                        EMPTY : 'empty'}

    def __init__(self, screen: pygame.Surface, name_number: int) -> None:
        '''Инициализация параметров'''
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.name_number = name_number
        self.image = pygame.image.load(
            f'images/Buttons/{Button.image_names_dict[name_number]}.png')
        self.rect = self.image.get_rect()
        # Кнопки находятся по середине экрана (по ширине)
        self.rect.centerx = self.screen_rect.centerx
        # Выбрана ли кнопка
        self.is_chosen = False
        # Данные из файлов сохранения для кнопок выбора файла
        self.saved_data = None

    def blitme(self):
        '''Отображение изображения кнопки на экране'''
        self.screen.blit(self.image, self.rect)
        if self.is_chosen:
            # Рисуем то, что кнопка выбрана 
            # surfaces -  светлые уголки
            surfaces = [pygame.Surface((10,30)),
            pygame.Surface((30,10))]
            for surface in surfaces:
                surface.fill((255, 246, 117))
                # Расставляем их по углам:
                self.screen.blit(surface, (
                    self.rect.left + 2, 
                    self.rect.bottom - 2 - surface.get_height()))
                self.screen.blit(surface, (
                    self.rect.right - 2 - surface.get_width(), 
                    self.rect.top + 2))
