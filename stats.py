
from audiosounds import Audio
from background import Background


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
    OPTIONS = 9
    CREDITS = 10
    

    
    mc_surname = 'S'
    
    # Словарь, соотносящий состояния с изображениями заднего плана
    state_to_bg: dict[int, str] = {GAMEACTIVE : 'SLevel1',
                                   INTRO : 'intro',
                                   MAINMENU : 'mainmenu',
                                   SAVEFILES_SAVEMODE : 'saving_files',
                                   SAVEFILES_LOADMODE : 'loading_files',
                                   SELECTMODE : 'selection',
                                   OPTIONS : 'options',
                                   CREDITS : 'theend'}

    # Словарь, соотносящий состояния с аудиодорожками
    state_to_audio: dict[int, str] = {GAMEACTIVE : 'level1S',
                                      GAMEOVER : 'gameover',
                                      INTRO : 'mainmenu',
                                      MAINMENU : 'mainmenu',
                                      SUBMENU : 'submenu',
                                      SAVEFILES_LOADMODE : 'load',
                                      OPTIONS : 'options'}

    @classmethod
    def update_state_to_bg_dict(cls):
        '''Обновление значения в словаре для заднего фона'''
        cls.state_to_bg[cls.GAMEACTIVE] = (cls.mc_surname + 
            cls.state_to_bg[cls.GAMEACTIVE][1:])

    @classmethod
    def update_state_to_audio_dict(cls):
        '''Обновление значения в словаре для аудио'''
        cls.state_to_audio[cls.GAMEACTIVE] = (cls.state_to_audio[cls.GAMEACTIVE][:-1] 
            + cls.mc_surname)
    
    def __init__(self, bg: Background, audio: Audio, max_level: int):
        '''Инициализация статистических данных'''
        self.__state = Stats.INTRO # состояние игры
        self.pr_state = None # предшествующее состояние игры
        self.restart_flag = False # флаг рестарта игры
        self.__level = 0
        self.current_wave = 0
        self.bg = bg
        self.audio = audio
        self.max_level = max_level
        
    @property
    def level(self):
        return self.__level

    # При смене уровня происходит смена фона
    @level.setter
    def level(self, value):
        Stats.state_to_bg[Stats.GAMEACTIVE] = (
            Stats.state_to_bg[Stats.GAMEACTIVE][:-1] + f'{value + 1}')
        Stats.state_to_audio[Stats.GAMEACTIVE] = (
            Stats.state_to_audio[Stats.GAMEACTIVE][:-2] + f'{value + 1}' 
            + Stats.state_to_audio[Stats.GAMEACTIVE][-1])
        self.audio.current_music = Stats.state_to_audio[Stats.GAMEACTIVE]
        self.state = Stats.LOADING
        self.__level = value

    @level.deleter
    def level(self):
        del self.__level


    @property
    def state(self):
        '''Состояние игры объекта статистики игры'''
        return self.__state
    
    # При смене состояния происходит смена фона
    @state.setter
    def state(self, value):
        if value in Stats.state_to_bg.keys():
            self.bg.change(Stats.state_to_bg[value])
        elif value == Stats.SUBMENU:
            self.bg.change(Stats.state_to_bg[Stats.GAMEACTIVE])
        if value in Stats.state_to_audio.keys():
            self.audio.current_music = Stats.state_to_audio[value]
        if value == Stats.MAINMENU:
            self.state_to_audio[Stats.GAMEACTIVE] = f'level{self.level + 1}S'
        self.__state = value
    
    @state.deleter
    def state(self):
        del self.__state