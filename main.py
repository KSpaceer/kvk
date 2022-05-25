
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
    from background import Background
    # Задний фон
    bg = Background(mediator)
    # Звуки
    audio = Audio(mediator)
    gr.set_caption_and_icon()
    # Счетчик времени
    timer = Timer(monotonic())
    # Текущее время
    cur_time = Timer(monotonic())
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
    mediator.add(ai_settings, screen, bg, audio, timer, cur_time, 
        mc, st, enemies, mc_fist, en_fists, tarzan, buttons)
    # Отслеживание текущей вертикальной позиции заднего фона (для титров)
    cur_y = 0
    
    
    
    
    # Основной цикл игры
    while 1:


        
        
        # Обработка событий
        gf.check_events(mc, st, buttons, screen, cur_time,
             timer, enemies, selecticons, en_fists, audio, ai_settings)
        if st.state == Stats.INTRO:
            # Заставка
            tarzan.update_intro()
        elif st.state == Stats.MAINMENU:
            # Главное меню
            if enemies:
                enemies.empty()
            gf.update_mainmenu_screen(ai_settings, screen, buttons, bg)
        elif st.state == Stats.SELECTMODE:
            # Меню выбора персонажа
            gf.update_selectmode_screen(ai_settings, screen, selecticons, bg)
        elif st.state == Stats.OPTIONS:
            # Меню опций
            gf.update_options_screen(buttons, bg)
        elif st.state == Stats.GAMEACTIVE:
            # Сама игра
            # Обновление экрана
            gf.update_screen(ai_settings, screen, mc, enemies, en_fists, bg)
            # Обновление текущего времени
            cur_time.time = monotonic()
            # Обновление главного персонажа
            mc.update(enemies, mc_fist, st)
            # Обновление врагов
            enemies.update(mc_fist, enemies, en_fists)
            # Обновление ударных поверхностей врагов
            en_fists.update(en_fists, enemies)
            # Проверка получения ударов
            gf.check_hits(mc, en_fists, enemies)
            # Обновление волн
            gf.update_waves(screen, ai_settings, mc, enemies, 
            timer, cur_time, st)
            
        elif st.state == Stats.SUBMENU:
            # Меню паузы
            gf.update_submenu_screen(screen, ai_settings, mc, enemies, en_fists, buttons, bg)
        elif st.state in (Stats.SAVEFILES_SAVEMODE, Stats.SAVEFILES_LOADMODE):
            # Меню файлов сохранения в режиме сохранения
            gf.update_savefiles_screen(screen, buttons, bg)
        elif st.state == Stats.GAMEOVER:
            # Конец игры (проигрыш)
            gf.update_gameover_screen(bg, mc, ai_settings,
                enemies, en_fists, screen)
            if st.restart_flag:
                timer, mc, mc_fist = gf.restart(
                    screen, ai_settings, enemies, 
                    en_fists, st, cur_time, mc, audio)
        elif st.state == Stats.LOADING:
            # Загрузка: это состояние нужно для перезапуска всех объектов, 
            # т.к. из модуля game_functions функции режима загрузки не 
            # позволяют это сделать (я лох).
            timer, mc, mc_fist = gf.restart(
                    screen, ai_settings, enemies, en_fists, st, cur_time, mc, audio)
            st.state = Stats.GAMEACTIVE
        elif st.state == Stats.CREDITS:
            cur_y = gf.update_credits_screen(bg, cur_y, 
                st, buttons, screen)
        
        
        
run_game()