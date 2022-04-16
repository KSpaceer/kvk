
from os.path import exists
from time import monotonic
import pygame
import sys
from MC import MainCharacter
from eater import Eater
from etimer import Timer
import graphic as gr
from guru import Guru
from ninja import Ninja

from settings import Settings
from stats import Stats
from bull import Bull
from sumo import Sumo
from enemy import Enemy
from button import Button
from fist import Fist
from selecticon import SelectIcon


### ОБЩИЙ БЛОК ###

def check_events(mc: MainCharacter, st: Stats, buttons: list[Button], 
    screen: pygame.Surface, cur_time: Timer, timer: Timer, 
    enemies: pygame.sprite.Group, selecticons: list[SelectIcon]):
    '''Обрабатывает нажатия клавиш и мыши'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Выход по нажатии крестика
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # Проверка событий нажатия
            keydown_events(event, mc, st, buttons, 
            screen, cur_time, timer, enemies, selecticons)
            # Если текущее состояние - заставка или проигрыш, меняет состояние
            change_state(st, buttons, screen)
        elif event.type == pygame.KEYUP:
            # Проверка событий отпускания кнопок
            keyup_events(event, mc)

def keydown_events(event, mc: MainCharacter, 
    st: Stats, buttons: list[Button], screen: pygame.Surface, 
    cur_time: Timer, timer: Timer, enemies: pygame.sprite.Group, 
    selecticons: list[SelectIcon]):
    '''Обрабатывает события нажатия клавиш'''
    # В зависимости от состояния игры - различная реакция на нажатия
    if st.state == st.GAMEACTIVE:
        keydown_in_game(event, mc, st, buttons, screen)
    elif st.state == st.MAINMENU:
        keydown_in_mainmenu(event, st, buttons, screen, selecticons)
    elif st.state == st.SELECTMODE:
        keydown_in_selectmode(event, st, selecticons, mc, buttons, screen)
    elif st.state == st.SUBMENU:
        keydown_in_submenu(event, st, buttons, screen, 
        cur_time, timer, mc, enemies)
    elif st.state in (st.SAVEFILES_SAVEMODE, st.SAVEFILES_LOADMODE):
        keydown_in_savefiles(event, st, buttons, screen, mc)
    

def keyup_events(event, mc: MainCharacter):
    '''Обрабатывает события отжатия клавиш'''
    # Т.к. отпускание важно только во время состояния активной игры,
    # можно не создавать отдельные функции, как для нажатия
    if event.key == pygame.K_RIGHT:
        # Обнуление таймера анимации и отмена флага ходьбы
        mc.timer = 0
        mc.moving_right = False
    elif event.key == pygame.K_LEFT:
        mc.timer = 0
        mc.moving_left = False
    elif event.key == pygame.K_UP:
        mc.timer = 0
        mc.moving_up = False
    elif event.key == pygame.K_DOWN:
        mc.timer = 0
        mc.moving_down = False
    elif event.key == pygame.K_SPACE:
        # Выключение флага зажатого пробела
        mc.space_active = False

def select_button(buttons: list[Button], event: pygame.event.Event, 
    do_reverse: bool = False):
    '''Смена выбранной кнопки по нажатию кнопок вверх или вниз'''
    upper = 0
    lower = len(buttons) - 1
    key_vars = {pygame.K_DOWN : ('+', lower),
            pygame.K_UP : ('-', upper)} 
    if do_reverse:
        # Если при создании набора кнопок они создавались снизу вверх,
        # то меняет местами реакцию на нажатие стрелки вниз или вверх
        key_vars[pygame.K_DOWN], key_vars[pygame.K_UP] = \
            key_vars[pygame.K_UP], key_vars[pygame.K_DOWN]
    for i in range(len(buttons)):
        # Если кнопка выбрана и это не граничная кнопка (т.е. например,
        # не верхняя кнопка при нажатии клавиши вверх)
        if buttons[i].is_chosen and i != key_vars[event.key][1]:
            # Меняет выбранную кнопку на другую (выше или ниже)
            buttons[i].is_chosen = False
            exec('buttons[i' + key_vars[event.key][0] + '1].is_chosen = True')
            break 

def change_state(st: Stats, buttons: list[Button], screen: pygame.Surface):
    '''Изменяет состояние игры'''
    if st.state == st.INTRO:
        # Переход с заставки в главное меню
        buttons.clear()
        create_mainmenu_buttons(buttons, screen)
        st.state = st.MAINMENU
    elif st.state == st.GAMEOVER:
        # Рестарт после проигрыша
        st.restart_flag = True

### БЛОК ГЛАВНОГО МЕНЮ (st.state = Stats.MAINMENU) ###

def create_mainmenu_buttons(buttons: list[Button], screen: pygame.Surface):
    '''Создает кнопки главного меню'''
    for i in range(4):
        buttons.append(Button(screen, i))
        if i == Button.NEWGAME:
                # Клавиша начала игры выбрана
            buttons[i].is_chosen = True
        buttons[i].rect.centery = 125 + 2 * i * 90

def update_mainmenu_screen(ai_settings: Settings, screen: pygame.Surface, 
    buttons: list[Button]):
    '''Обновляет изображение в главном меню'''
    # Перерисовка экрана
    screen.fill(ai_settings.bg_color)
    # Прорисовка кнопок
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_mainmenu(event, st: Stats, buttons: list[Button], 
    screen: pygame.Surface, selecticons: list[SelectIcon]):
    '''Обрабатывает нажатия клавиш в главном меню'''
    if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
        select_button(buttons, event)
    elif event.key == pygame.K_RETURN:
        # Активация кнопки по нажатии Enter
        for i in range(len(buttons)):
            if buttons[i].is_chosen:
                if buttons[i].name_number == Button.NEWGAME:
                    # Переход из главного меню в меню выбора персонажа
                    buttons.clear()
                    create_selecticons(selecticons, screen)
                    st.state = st.SELECTMODE
                    break
                elif buttons[i].name_number == Button.LOAD:
                    # Переход из главного меню в меню файлов сохранения 
                    # в режиме загрузки
                    buttons.clear()
                    create_savefiles_buttons(buttons, screen)
                    st.state = st.SAVEFILES_LOADMODE
                    st.pr_state = st.MAINMENU
                    break
                elif buttons[i].name_number == Button.EXIT:
                    # Выход из игры
                    sys.exit()

### БЛОК ВЫБОРА ПЕРСОНАЖА (st.state = Stats.SELECTMODE) ###

def create_selecticons(selecticons: list[SelectIcon], screen: pygame.Surface):
    '''Создает иконки выбора персонажа'''
    selecticons.extend((SelectIcon('S', screen), SelectIcon('Z', screen)))

def update_selectmode_screen(ai_settings: Settings, 
    screen: pygame.Surface, selecticons: list[SelectIcon]):
    '''Обновляет изображение на экране во время выбора персонажа'''
    # Перерисовка экрана
    screen.fill(ai_settings.bg_color)
    # Вывод надписи 
    screen.blit(pygame.image.load('images/syf.png'), (450, 100))
    # Отображение иконок персонажей
    for selecticon in selecticons:
        selecticon.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_selectmode(event, st: Stats, selecticons: list[SelectIcon], 
    mc: MainCharacter, buttons: list[Button], screen: pygame.Surface):
    '''Обрабатывает нажатия клавиш в меню выбора персонажа'''
    if event.key == pygame.K_ESCAPE:
        # Выход в меню по нажатию ESC
        selecticons.clear()
        create_mainmenu_buttons(buttons, screen)
        st.state = st.MAINMENU
    # Смена выбранного персонажа по нажатию стрелок
    elif event.key == pygame.K_LEFT:
        if selecticons[1].is_selected:
            selecticons[1].is_selected = False
            selecticons[0].is_selected = True
    elif event.key == pygame.K_RIGHT:
        if selecticons[0].is_selected:
            selecticons[0].is_selected = False
            selecticons[1].is_selected = True
    elif event.key == pygame.K_RETURN:
        # Выбор персонажа по нажатию ENTER и запуск игры
        for selecticon in selecticons:
            if selecticon.is_selected:
                mc.surname = selecticon.surname
                selecticons.clear()
                st.state = st.LOADING
                break 

### БЛОК ИГРЫ (st.state = Stats.GAMEACTIVE) ###

def update_screen(ai_settings: Settings, screen: pygame.Surface, 
    mc: MainCharacter, enemies: pygame.sprite.Group, 
    en_fists: pygame.sprite.Group):
    '''Обновляет изображение на экране'''
    # Перерисовка экрана
    screen.fill(ai_settings.bg_color)
    # Отображение здоровья и неуязвимости
    gr.draw_health(mc, ai_settings)
    gr.draw_invincibility(mc)
    # Отображение главного персонажа и врагов
    mc.blitme()
    for enemy in enemies:
        enemy.blitme()
    for en_fist in en_fists:
        en_fist.update(en_fists)
    # Обновление экрана
    pygame.display.flip()

def keydown_in_game(event, mc: MainCharacter, st: Stats, 
    buttons: list[Button], screen: pygame.Surface):
    '''Обрабатывает нажатия клавиш во время самой игры'''
    if event.key == pygame.K_RIGHT:
        # Обнуление таймера анимации и включение флага ходьбы
        mc.timer = 0
        mc.moving_right = True
    elif event.key == pygame.K_LEFT:
        mc.timer = 0
        mc.moving_left = True
    elif event.key == pygame.K_UP:
        mc.timer = 0
        mc.moving_up = True
    elif event.key == pygame.K_DOWN:
        mc.timer = 0
        mc.moving_down = True
    elif event.key == pygame.K_SPACE:
        # Включение флага зажатого пробела
        mc.space_active = True
    elif event.key == pygame.K_ESCAPE:
        # Переход в меню паузы
        create_submenu_buttons(buttons, screen)
        st.state = st.SUBMENU

def check_hits(mc: MainCharacter, en_fists: pygame.sprite.Group, 
    enemies: pygame.sprite.Group):
    '''Проверка получения удара'''
    if not mc.invincible:
        # Если персонаж неуязвим, проверяет коллизии персонажа с вражескими
        # ударными поверхностями
        touching_fist = pygame.sprite.spritecollideany(mc, en_fists)
        if touching_fist:
            # В случае коллизии персонаж получает урон
            mc.get_damage(touching_fist, en_fists, enemies)

def wave(screen: pygame.Surface, ai_settings: Settings, mc: MainCharacter, 
    enemies: pygame.sprite.Group, timer: Timer, 
    cur_time: Timer, st: Stats, adversaries: list):
    '''Создает волну противников'''
    for i in range(len(adversaries)):
        # Враги появляются по времени. 
        if cur_time.time - timer.time >= 5 * (i + 1) and len(enemies) == i \
            and Enemy.summons < len(adversaries):
            enemy_summon(screen, ai_settings, mc, enemies, timer, 
                cur_time, st, adversaries, i)

def enemy_summon(screen, ai_settings, mc, enemies, timer, cur_time, st, adversaries, i):
    '''Вызывает врага'''
    if adversaries[i] == 0:
        new_enemy = Bull(screen, ai_settings, mc, st, timer, cur_time)
        enemies.add(new_enemy)
    elif adversaries[i] == 1:
        new_enemy = Sumo(screen, ai_settings, mc, st, timer, cur_time)
        enemies.add(new_enemy)
    elif adversaries[i] == 2:
        if mc.surname == 'Z':
            new_enemy = Eater(screen, ai_settings, mc, st, timer, cur_time)
            enemies.add(new_enemy)
        else:
            new_enemy = Guru(screen, ai_settings, mc, st, timer, cur_time)
            enemies.add(new_enemy)
    elif adversaries[i] == 3:
        new_enemy = Ninja(screen, ai_settings, mc, st, timer, cur_time)
        enemies.add(new_enemy)

def update_waves(screen: pygame.Surface, ai_settings: Settings, 
    mc: MainCharacter, enemies: pygame.sprite.Group, 
        timer: Timer, cur_time: Timer, st: Stats):
    '''Обновляет волны'''
    wave(screen, ai_settings, mc, enemies, timer, cur_time, st, 
    ai_settings.waves[st.level][st.current_wave])


### БЛОК МЕНЮ ПАУЗЫ (st.state = Stats.SUBMENU) ###

def create_submenu_buttons(buttons: list[Button], 
    screen: pygame.Surface, selected_button: int = Button.MENU):
    '''Создает кнопки меню паузы'''
    for i in range(3, 6):
        buttons.append(Button(screen, i))
        if i == selected_button:
            # Избранная кнопка
            buttons[i - 3].is_chosen = True
        buttons[i - 3].rect.centery = 580 - 2 * (i - 3) * 90

def update_submenu_screen(screen: pygame.Surface, ai_settings: Settings, 
    mc: MainCharacter, enemies: pygame.sprite.Group, 
    en_fists: pygame.sprite.Group, buttons: list[Button]):
    '''Обновляет изображение в меню паузы'''
    # Аналогично функции update_screen(), чтобы во время паузы было видно игру
    screen.fill(ai_settings.bg_color)
    gr.draw_health(mc, ai_settings)
    gr.draw_invincibility(mc)
    mc.blitme()
    for enemy in enemies:
        enemy.blitme()
    for en_fist in en_fists:
        en_fist.update(en_fists)
    # Затемняем экран игры
    obscure_screen(ai_settings, screen)
    # Прорисовка кнопок:
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_submenu(event, st: Stats, buttons: list[Button], 
    screen: pygame.Surface, cur_time: Timer, timer: Timer, 
    mc: MainCharacter, enemies: pygame.sprite.Group):
    '''Обрабатывает нажатия клавиш во время паузы'''
    if event.key == pygame.K_ESCAPE:
        # Возобновление игры
        buttons.clear()
        update_time(cur_time, timer, mc, enemies)
        st.state = st.GAMEACTIVE
    elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
        select_button(buttons, event, True)
    elif event.key == pygame.K_RETURN:
        for i in range(len(buttons)):
            if buttons[i].is_chosen:
                if buttons[i].name_number == Button.MENU:
                    # Выход в меню
                    buttons.clear()
                    create_mainmenu_buttons(buttons, screen)
                    st.state = st.MAINMENU
                    break
                elif buttons[i].name_number == Button.SAVE:
                    # Переход в меню файлов сохранения
                    buttons.clear()
                    create_savefiles_buttons(buttons, screen)
                    st.state = st.SAVEFILES_SAVEMODE
                    st.pr_state = st.SUBMENU
                    break
                elif buttons[i].name_number == Button.EXIT:
                    sys.exit()

def obscure_screen(ai_settings: Settings, screen: pygame.Surface):
    '''Затемняет экран'''
    # Добавляет частично прозрачную черную заслонку на экран
    damper = pygame.Surface((ai_settings.screen_width, 
    ai_settings.screen_height))
    damper.set_alpha(100)
    screen.blit(damper, (0,0))

def update_time(cur_time: Timer, timer: Timer, 
    mc: MainCharacter, enemies: pygame.sprite.Group):
    '''Обновляет все атрибуты времени после возобновления игры, т.е.
    корректирует их на разницу между 
    игровым времени(cur_time) и монотонным(monotonic().'''
    delta = monotonic() - cur_time.time
    objects = [timer, mc] 
    objects.extend(enemies)
    for object in objects:
        if isinstance(object, Timer):
            if object.time:
                object.time += delta
        elif isinstance(object, MainCharacter):
            if object.timer:
                object.timer += delta
            if object.attack_timer:
                object.attack_timer += delta
            if object.invin_timer:
                object.invin_timer += delta
        elif isinstance(object, Enemy):
            if object.timer:
                object.timer += delta
            if object.cooldown_timer:
                object.cooldown_timer += delta

### БЛОК МЕНЮ ФАЙЛОВ СОХРАНЕНИЯ (st.state = Stats.SAVEFILES_...) ###

def create_savefiles_buttons(buttons: list[Button], screen: pygame.Surface):
    '''Создает кнопки меню сохранения файлов'''
    for i in range(3):
        if exists(f'save/save{i + 1}.txt'):
            # Если файл сохранения имеется
            buttons.append(Button(screen, Button.SAVEFILE))
            open_savefile(i, buttons)
        else:
            # Если файла сохранения нет
            buttons.append(Button(screen, Button.EMPTY))
        if i == 0:
            # Верхняя кнопка изначально выбрана
            buttons[i].is_chosen = True
        buttons[i].rect.centery = 220 + 2 * i * 90

def update_savefiles_screen(screen: pygame.Surface, buttons: list[Button]):
    '''Обновляет изображение в меню файлов сохранения'''
    # Перерисовка экрана
    screen.fill((0, 0, 0))
    # Прорисовка кнопок
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_savefiles(event, st: Stats, buttons: list[Button], 
    screen: pygame.Surface, mc: MainCharacter):
    '''Обрабатывает нажатия клавиш в меню файлов сохранения'''
    if event.key == pygame.K_ESCAPE:
        if st.pr_state == st.SUBMENU:
            # Если предыдущим состоянием игры было меню паузы, возвращает туда
            buttons.clear()
            create_submenu_buttons(buttons, screen, Button.SAVE)
            st.state = st.SUBMENU
        elif st.pr_state == st.MAINMENU:
            # Если пред. состоянием игры было главное меню, возвращает туда
            buttons.clear()
            create_mainmenu_buttons(buttons, screen)
            st.state = st.MAINMENU
    elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
        select_button(buttons, event)
    elif event.key == pygame.K_RETURN:
        if st.state == st.SAVEFILES_SAVEMODE:
            # Если активен режим сохранения, сохраняет игровую информацию в выбранный слот
            for i in range(len(buttons)):
                if buttons[i].is_chosen:
                    with open(f'save/save{i + 1}.txt', 'w') as f:
                        f.write(str(st.level) + '\n' + mc.surname)
                    break
            # Возвращает в меню паузы
            buttons.clear()
            create_submenu_buttons(buttons, screen, Button.SAVE)
            st.state = st.SUBMENU
        elif st.state == st.SAVEFILES_LOADMODE:
            # Если активен режим загрузки, передает данные файла, сохраненные
            # в объекте кнопки, объекту игровой статистики и персонажу
            for i in range(len(buttons)):
                if buttons[i].is_chosen and \
                buttons[i].name_number == Button.SAVEFILE:
                    st.level = int(buttons[i].saved_data[0])
                    mc.surname = buttons[i].saved_data[1]
                    # Запуск игры
                    buttons.clear()
                    st.state = st.LOADING
                    break
            



def open_savefile(number: int, buttons: list[Button]):
    '''Открывает файл, передает данные из него кнопке'''
    with open(f'save/save{number + 1}.txt', 'r') as f:
        buttons[number].saved_data = f.readlines()
        # Добавляем к изображению номер файла
        buttons[number].image.blit(
            pygame.image.load(f'images/Buttons/{number + 1}.png'), (82, 13))
        # Перевернутая строка значения уровня
        reversed_level = str(int(buttons[number].saved_data[0]) + 1)[::-1]
        for i in range(len(reversed_level) + 1):
            if i == len(reversed_level):
                # Добавляем к изображению букву L (level)
                buttons[number].image.blit(
                    pygame.image.load('images/Buttons/L.png'),
                (179 - 20 * i, 13))
            else:
                # Добавляем к изображению одну цифру из значения уровня
                buttons[number].image.blit(
                    pygame.image.load(
                        f'images/Buttons/{reversed_level[i]}.png'),
                    (179 - 20 * i, 13))
        # Добавим на кнопку иконку персонажа
        buttons[number].image.blit(pygame.image.load(
            f'images/K{buttons[number].saved_data[1]}_health.png'), (157, 40))

### БЛОК ПРОИГРЫША (st.state = Stats.GAMEOVER) ###

def restart(screen: pygame.Surface, ai_settings: Settings, 
    enemies: pygame.sprite.Group, en_fists: pygame.sprite.Group, 
    st: Stats, cur_time: Timer, mc: MainCharacter) \
    -> tuple[Timer, MainCharacter, Fist]:
    '''Функция рестарта'''
    timer = Timer(monotonic())
    new_mc = MainCharacter(screen, ai_settings, cur_time, mc.surname)
    mc_fist = Fist(screen)
    enemies.empty()
    en_fists.empty()
    Enemy.deaths = 0
    Enemy.c_deaths = 0
    Enemy.summons = 0
    st.current_wave = 0
    st.state = st.GAMEACTIVE
    return timer, new_mc, mc_fist 

















        



    
















    

    


    




    
