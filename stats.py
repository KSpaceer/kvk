


class Stats():
    '''Класс статистики игры'''

    # Переменные состояния игры (чтобы в коде красиво выглядело и наглядно)
    GAMEACTIVE = 0
    GAMEOVER = 1
    INTRO = 2
    MAINMENU = 3
    SUBMENU = 4
    SAVEFILES_SAVEMODE = 5
    SAVEFILES_LOADMODE = 6
    LOADING = 7
    SELECTMODE = 8

    def __init__(self):
        '''Инициализация статистических данных'''
        self.state = Stats.INTRO # состояние игры
        self.pr_state = None # предшествующее состояние игры
        self.restart_flag = False # флаг рестарта игры
        self.level = 0
        self.current_wave = 0
        