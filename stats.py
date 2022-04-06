


class Stats():
    '''Класс статистики игры'''

    # Переменные состояния игры (чтобы в коде красиво выглядело и наглядно)
    GAMEACTIVE = 0
    GAMEOVER = 1
    INTRO = 2
    MAINMENU = 3
    SUBMENU = 4

    def __init__(self):
        '''Инициализация статистических данных'''
        self.state = Stats.INTRO # состояние игры
        self.restart_flag = False # флаг рестарта игры
        self.level = 0
        self.current_wave = 0
        