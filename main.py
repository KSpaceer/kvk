
import pygame
from time import monotonic
from enemy import Enemy
from settings import Settings
from MC import MainCharacter
from fist import Fist
from pygame.sprite import Group
from etimer import Timer
import graphic as gr
import game_functions as gf
from stats import Stats
from Tarzan import Tarzan


def run_game():
    # Инициализация pygame, settings, статистики и дисплея
    pygame.init()
    ai_settings = Settings()
    st = Stats()
    screen = pygame.display.set_mode((ai_settings.screen_width, 
                        ai_settings.screen_height))
    gr.set_caption_and_icon()
    # Счетчик времени
    timer = Timer(monotonic())
    # Текущее время
    cur_time = Timer(monotonic())
    # Создание главного персонажа
    mc = MainCharacter(screen, ai_settings, cur_time)
    # Создание врагов
    enemies = Group()
    # Ударная поверхность главного персонажа
    mc_fist = Fist(screen)
    # Группа ударных поверхностей врагов
    en_fists = Group()
    # Объект для заставки
    tarzan = Tarzan(screen, ai_settings)
    # Кнопки
    buttons = []
    # Иконки меню выбора персонажа
    selecticons = []
    
    
    
    
    # Основной цикл игры
    while True:


        
        
        # Обработка событий
        gf.check_events(mc, st, buttons, screen, cur_time,
             timer, enemies, selecticons)
        if st.state == Stats.INTRO:
            # Заставка
            tarzan.update_intro()
        elif st.state == Stats.MAINMENU:
            # Главное меню
            gf.update_mainmenu_screen(ai_settings, screen, buttons)
        elif st.state == Stats.SELECTMODE:
            # Меню выбора персонажа
            gf.update_selectmode_screen(ai_settings, screen, selecticons)
        elif st.state == Stats.GAMEACTIVE:
            # Сама игра
            # Обновление текущего времени
            cur_time.time = monotonic()
            # Обновление главного персонажа
            mc.update(enemies, mc_fist, st)
            # Обновление врагов
            enemies.update(mc_fist, enemies, en_fists)
            # Проверка получения ударов
            gf.check_hits(mc, en_fists)
            # Обновление волн
            gf.update_waves(screen, ai_settings, mc, enemies, 
            timer, cur_time, st)
            # Обновление экрана
            gf.update_screen(ai_settings, screen, mc, enemies)
        elif st.state == Stats.SUBMENU:
            # Меню паузы
            gf.update_submenu_screen(screen, ai_settings, mc, enemies, buttons)
        elif st.state in (Stats.SAVEFILES_SAVEMODE, Stats.SAVEFILES_LOADMODE):
            # Меню файлов сохранения в режиме сохранения
            gf.update_savefiles_screen(screen, buttons)
        elif st.state == Stats.GAMEOVER:
            # Конец игры (проигрыш)
            if st.restart_flag:
                timer, mc, mc_fist = gf.restart(
                    screen, ai_settings, enemies, en_fists, st, cur_time, mc)
        elif st.state == Stats.LOADING:
            # Загрузка: это состояние нужно для перезапуска всех объектов, 
            # т.к. из модуля game_functions функции режима загрузки не 
            # позволяют это сделать (я лох).
            timer, mc, mc_fist = gf.restart(
                    screen, ai_settings, enemies, en_fists, st, cur_time, mc)
            st.state = Stats.GAMEACTIVE
        
        
        
        
run_game()