
from os import listdir
import pygame.mixer as mix
from mediator import Mediator
from path_handling import load_sound, resource_path


class Audio:
    '''Класс проигрывания звуков и музыки'''

    list_of_soundfiles = listdir('audio/sounds')
    
    PASTER_EGG_ACTIVE = False
    
    def __init__(self, mediator: Mediator) -> None:
        self.__current_music: str = ''
        self.mediator = mediator
        self.current_music = 'mainmenu'
        self.sounds: dict[str, mix.Sound] = {}

    @property
    def current_music(self) -> str:
        return self.__current_music

    @current_music.setter
    def current_music(self, value: str):
        '''Запускает проигрывание другой музыки'''
        if not Audio.PASTER_EGG_ACTIVE:
            if self.__current_music != value:
                value = value + '.mp3'
                mix.music.load(resource_path('audio', value))
                self.__current_music = value
        else:
            mix.music.load(resource_path('audio', 'savemode.mp3'))
        mix.music.set_volume(self.mediator.get_value(
            'ai_settings', 'music_volume')/10)
        mix.music.play(-1)

    @current_music.deleter
    def current_music(self):
        del self.__current_music

    def stop_music(self):
        '''Останавливает проигрывание музыки'''
        mix.music.stop()

    def play_sound(self, name: str, loops: int = 0):
        '''Проигрывание звука'''
        filename = ''.join(list
            (filter(lambda x : str(x).startswith(name), 
            self.list_of_soundfiles)))
        self.sounds[name] = load_sound('sounds', filename)
        self.sounds[name].set_volume(self.mediator.get_value(
            'ai_settings', 'music_volume')/10)
        self.sounds[name].play(loops)


    def stop_sound(self, name: str):
        '''Остановка звука'''
        self.sounds[name].stop()
        self.sounds.pop(name)
        
    def stop_all_sounds(self):
        '''Остановка всех звуков'''
        mix.stop()
        