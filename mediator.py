
from pygame import Surface, Rect
from pygame.sprite import Group




class Mediator():
    '''Класс-посредник для объектов игры'''

    def add(self, ai_settings, screen: Surface, bg, audio, timer, cur_time, 
        mc, st, enemies, mc_fist, en_fists, 
        tarzan, buttons):
        '''Добавление в тело посредника ссылок на все объекты'''
        
        self._ai_settings = ai_settings
        self._screen = screen
        self._screen_rect = screen.get_rect()
        self._bg = bg
        self._audio = audio
        self._timer = timer
        self._cur_time = cur_time
        self._mc = mc
        self._st = st
        self._enemies = enemies
        self._mc_fist = mc_fist
        self._en_fists = en_fists
        self._tarzan = tarzan
        self._buttons = buttons
        

    def get_value(self, obj_name: str, value_name: str = None):
        '''Позволяет получить значение объекта или сам объект из посредника'''
        value_to_return = eval('self._' + obj_name + '.' + value_name) if value_name\
            is not None else eval('self._' + obj_name)
        return value_to_return

    def set_value(self, obj_name: str, value_name: str, new_value_name: str):
        '''Позволяет изменить некоторое значение в объекте из посредника'''
        exec(f'self._{obj_name}.{value_name} = {new_value_name}')
        

    def extend_collection(self, collection_name: str, *new_elements):
        '''Позволяет добавить новые элементы в коллекцию'''
        collection = eval('self._' + collection_name)
        if isinstance(collection, Group):
            collection.add(new_elements)
        elif isinstance(collection, list):
            collection.extend(new_elements)

    def get_collection(self, collection_name: str):
        '''Позволяет получить коллекцию из посредника'''
        collection_to_return = eval('self._' + collection_name)
        return collection_to_return

    def blit_surface(self, surface: Surface, dest: tuple[int, int] | Rect):
        '''Отображение поверхности на экране'''
        self._screen.blit(surface, dest)
        
    def current_time(self):
        '''Возвращает текущее время игры'''
        return self._cur_time.time

    def call_method(self, obj_name: str, method_name: str, *args_names: str):
        '''Вызывает метод объекта с заданными аргументами'''
        args = ','.join(args_names)
        exec(f'self._{obj_name}.{method_name}({args})')