
import pygame
from time import monotonic

from settings import Settings
from MC import MainCharacter
from fist import Fist
from pygame.sprite import Group
from etimer import Timer
import graphic as gr
import game_functions as gf
from stats import Stats
from Tarzan import Tarzan
from audiosounds import Audio
from mediator import Mediator


def run_game():
    # Инициализация pygame, settings, статистики и дисплея
    pygame.init()
    mediator = Mediator()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, 
                        ai_settings.screen_height))
    mediator.add(ai_settings=ai_settings, 
        screen=screen, screen_rect = screen.get_rect())
    from background import Background
    # Задний фон
    bg = Background(mediator)
    mediator.add(bg=bg)
    # Звуки
    audio = Audio(mediator)
    mediator.add(audio=audio)
    gr.set_caption_and_icon()
    # Счетчик времени
    timer = Timer(monotonic())
    # Текущее время
    cur_time = Timer(monotonic())
    mediator.add(timer=timer, cur_time=cur_time)
    # Создание главного персонажа
    mc = MainCharacter(mediator)
    st = Stats(mediator)
    # Создание врагов
    enemies = Group()
    # Ударная поверхность главного персонажа
    mc_fist = Fist(mediator)
    # Группа ударных поверхностей врагов
    en_fists = Group()
    # Объект для заставки
    tarzan = Tarzan(mediator)
    # Кнопки
    buttons = []
    # Иконки меню выбора персонажа
    selecticons = []
    # Добавляем ссылки на все объекты в посредника
    mediator.add(mc=mc, st=st, enemies=enemies, mc_fist=mc_fist, 
    en_fists=en_fists, tarzan=tarzan, buttons=buttons, selecticons=selecticons)
    # Отслеживание текущей вертикальной позиции заднего фона (для титров)
    cur_y = 0
    
    
    
    
    # Основной цикл игры
    while 1:


        
        
        # Обработка событий
        gf.check_events(mc, st, buttons, screen, cur_time,
             timer, enemies, selecticons, en_fists, audio, mediator)
        if st.state == Stats.INTRO:
            # Заставка
            tarzan.update_intro()
        elif st.state == Stats.MAINMENU:
            # Главное меню
            if enemies:
                enemies.empty()
            gf.update_mainmenu_screen(buttons, bg)
        elif st.state == Stats.SELECTMODE:
            # Меню выбора персонажа
            gf.update_selectmode_screen(screen, selecticons, bg)
        elif st.state == Stats.OPTIONS:
            # Меню опций
            gf.update_options_screen(buttons, bg)
        elif st.state == Stats.GAMEACTIVE:
            # Сама игра
            # Обновление экрана
            gf.update_screen(ai_settings, mc, enemies, en_fists, bg)
            # Обновление текущего времени
            cur_time.time = monotonic()
            # Обновление главного персонажа
            mc.update()
            # Обновление врагов
            enemies.update()
            # Обновление ударных поверхностей врагов
            en_fists.update()
            # Проверка получения ударов
            gf.check_hits(mc, en_fists)
            # Обновление волн
            gf.update_waves(ai_settings, mc, enemies, 
            timer, cur_time, st, mediator)
            
        elif st.state == Stats.SUBMENU:
            # Меню паузы
            gf.update_submenu_screen(screen, ai_settings, mc, enemies, en_fists, buttons, bg)
        elif st.state in (Stats.SAVEFILES_SAVEMODE, Stats.SAVEFILES_LOADMODE):
            # Меню файлов сохранения в режиме сохранения
            gf.update_savefiles_screen(buttons, bg)
        elif st.state == Stats.GAMEOVER:
            # Конец игры (проигрыш)
            gf.update_gameover_screen(bg, mc, ai_settings,
                enemies, en_fists, screen)
            if st.restart_flag:
                timer, mc, mc_fist = gf.restart(
                    screen, mediator, enemies, 
                    en_fists, st, mc, audio)
        elif st.state == Stats.LOADING:
            # Загрузка: это состояние нужно для перезапуска всех объектов, 
            # т.к. из модуля game_functions функции режима загрузки не 
            # позволяют это сделать (я лох).
            timer, mc, mc_fist = gf.restart(
                    screen, mediator, enemies, en_fists, st, mc, audio)
            st.state = Stats.GAMEACTIVE
        elif st.state == Stats.CREDITS:
            cur_y = gf.update_credits_screen(bg, cur_y, 
                st, buttons, mediator)
           
        
run_game()
