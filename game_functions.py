
from os.path import exists
from time import monotonic
import pygame
import sys
from MC import MainCharacter
from etimer import Timer
import graphic as gr

from bull import Bull
from enemy import Enemy
from button import Button
from fist import Fist
from selecticon import SelectIcon


### ОБЩИЙ БЛОК ###

def check_events(mc, st, buttons, screen, 
    cur_time, timer, enemies, selecticons):
    '''Обрабатывает нажатия клавиш и мыши'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            keydown_events(event, mc, st, buttons, 
            screen, cur_time, timer, enemies, selecticons)
            change_state(st, buttons, screen)
        elif event.type == pygame.KEYUP:
            keyup_events(event, mc)

def keydown_events(event, mc, st, buttons, screen, 
    cur_time, timer, enemies, selecticons):
    '''Обрабатывает события нажатия клавиш'''
    if event.key == pygame.K_q:
        sys.exit()
    elif st.state == st.GAMEACTIVE:
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
    

def keyup_events(event, mc):
    '''Обрабатывает события отжатия клавиш'''
    if event.key == pygame.K_RIGHT:
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
        mc.space_active = False

def select_button(buttons, event, do_reverse = False):
    '''Смена выбранной кнопки по нажатию кнопок вверх или вниз'''
    upper = 0
    lower = len(buttons) - 1
    key_vars = {pygame.K_DOWN : ('+', lower),
            pygame.K_UP : ('-', upper)} 
    if do_reverse:
        key_vars[pygame.K_DOWN], key_vars[pygame.K_UP] = \
            key_vars[pygame.K_UP], key_vars[pygame.K_DOWN]
    for i in range(len(buttons)):
        if buttons[i].is_chosen and i != key_vars[event.key][1]:
            buttons[i].is_chosen = False
            exec('buttons[i' + key_vars[event.key][0] + '1].is_chosen = True')
            break 

def change_state(st, buttons, screen):
    '''Изменяет состояние игры'''
    if st.state == st.INTRO:
        buttons.clear()
        create_mainmenu_buttons(buttons, screen)
        st.state = st.MAINMENU
    elif st.state == st.GAMEOVER:
        st.restart_flag = True

### БЛОК ГЛАВНОГО МЕНЮ (st.state = Stats.MAINMENU) ###

def create_mainmenu_buttons(buttons, screen):
    '''Создает кнопки главного меню'''
    for i in range(4):
        buttons.append(Button(screen, i))
        if i == Button.NEWGAME:
                # Клавиша начала игры выбрана
            buttons[i].is_chosen = True
        buttons[i].rect.centery = 125 + 2 * i * 90

def update_mainmenu_screen(ai_settings, screen, buttons):
    '''Обновляет изображение в главном меню'''
    # Перерисовка экрана
    screen.fill(ai_settings.bg_color)
    # Прорисовка кнопок
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_mainmenu(event, st, buttons, screen, selecticons):
    '''Обрабатывает нажатия клавиш в главном меню'''
    if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
        select_button(buttons, event)
    elif event.key == pygame.K_RETURN:
        for i in range(len(buttons)):
            if buttons[i].is_chosen:
                if buttons[i].name_number == Button.NEWGAME:
                    buttons.clear()
                    create_selecticons(selecticons, screen)
                    st.state = st.SELECTMODE
                    break
                elif buttons[i].name_number == Button.LOAD:
                    buttons.clear()
                    create_savefiles_buttons(buttons, screen)
                    st.state = st.SAVEFILES_LOADMODE
                    st.pr_state = st.MAINMENU
                    break
                elif buttons[i].name_number == Button.EXIT:
                    sys.exit()

### БЛОК ВЫБОРА ПЕРСОНАЖА (st.state = Stats.SELECTMODE) ###

def create_selecticons(selecticons, screen):
    '''Создает иконки выбора персонажа'''
    selecticons.extend((SelectIcon('S', screen), SelectIcon('Z', screen)))

def update_selectmode_screen(ai_settings, screen, selecticons):
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

def keydown_in_selectmode(event, st, selecticons, mc, buttons, screen):
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

def update_screen(ai_settings, screen, mc, enemies, timer):
    '''Обновляет изображение на экране'''
    # Перерисовка экрана
    screen.fill(ai_settings.bg_color)
    # Отображение здоровья и неуязвимости
    gr.draw_health(mc, ai_settings)
    gr.draw_invincibility(mc)
    mc.blitme()
    for enemy in enemies:
        enemy.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_game(event, mc, st, buttons, screen):
    '''Обрабатывает нажатия клавиш во время самой игры'''
    if event.key == pygame.K_RIGHT:
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
        mc.space_active = True
    elif event.key == pygame.K_ESCAPE:
        create_submenu_buttons(buttons, screen)
        st.state = st.SUBMENU

def check_hits(mc, en_fists):
    '''Проверка получения удара'''
    if not mc.invincible:
        touching_fist = pygame.sprite.spritecollideany(mc, en_fists)
        if touching_fist:
            mc.get_damage(touching_fist)

def wave(screen, ai_settings, mc, enemies, timer, cur_time, st, adversaries):
    '''Создает волну противников'''
    for i in range(len(adversaries)):
        # Враги появляются по времени. Если кто-то умер, новые появляться не будут
        if cur_time.time - timer.time >= 5 * (i + 1) and len(enemies) == i \
            and Enemy.summons < len(adversaries):
            if adversaries[i] == 0:
                new_enemy = Bull(screen, ai_settings, mc, st, timer, cur_time)
                enemies.add(new_enemy)

def update_waves(screen, ai_settings, mc, enemies, timer, cur_time, st):
    '''Обновляет волны'''
    wave(screen, ai_settings, mc, enemies, timer, cur_time, st, 
    ai_settings.waves[st.level][st.current_wave])


### БЛОК МЕНЮ ПАУЗЫ (st.state = Stats.SUBMENU) ###

def create_submenu_buttons(buttons, screen, selected_button = Button.MENU):
    '''Создает кнопки меню паузы'''
    for i in range(3, 6):
        buttons.append(Button(screen, i))
        if i == selected_button:
            buttons[i - 3].is_chosen = True
        buttons[i - 3].rect.centery = 580 - 2 * (i - 3) * 90

def update_submenu_screen(screen, ai_settings, mc, enemies, buttons):
    '''Обновляет изображение в меню паузы'''
    # Аналогично функции update_screen(), чтобы во время паузы было видно игру
    screen.fill(ai_settings.bg_color)
    gr.draw_health(mc, ai_settings)
    gr.draw_invincibility(mc)
    mc.blitme()
    for enemy in enemies:
        enemy.blitme()
    # Затемняем экран игры
    obscure_screen(ai_settings, screen)
    # Прорисовка кнопок:
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_submenu(event, st, buttons, screen, 
                cur_time, timer, mc, enemies):
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

def obscure_screen(ai_settings, screen):
    '''Затемняет экран'''
    damper = pygame.Surface((ai_settings.screen_width, 
    ai_settings.screen_height))
    damper.set_alpha(100)
    screen.blit(damper, (0,0))

def update_time(cur_time, timer, mc, enemies):
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

def create_savefiles_buttons(buttons, screen):
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
            buttons[i].is_chosen = True
        buttons[i].rect.centery = 220 + 2 * i * 90

def update_savefiles_screen(screen, buttons):
    '''Обновляет изображение в меню файлов сохранения'''
    # Перерисовка экрана
    screen.fill((0, 0, 0))
    # Прорисовка кнопок
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_savefiles(event, st, buttons, screen, mc):
    '''Обрабатывает нажатия клавиш в меню файлов сохранения'''
    if event.key == pygame.K_ESCAPE:
        if st.pr_state == st.SUBMENU:
            # Если предыдущим состоянием игры было меню паузы, возвращает туда
            buttons.clear()
            create_submenu_buttons(buttons, screen)
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
            create_submenu_buttons(buttons, screen)
            st.state = st.SUBMENU
        elif st.state == st.SAVEFILES_LOADMODE:
            # Если активен режим загрузки, передает данные файла, сохраненные
            # в объекте кнопки, объекту игровой статистики
            for i in range(len(buttons)):
                if buttons[i].is_chosen and \
                buttons[i].name_number == Button.SAVEFILE:
                    st.level = int(buttons[i].saved_data[0])
                    mc.surname = buttons[i].saved_data[1]
                    buttons.clear()
                    st.state = st.LOADING
                    break
            



def open_savefile(number, buttons):
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

def restart(screen, ai_settings, enemies, en_fists, st, cur_time, mc):
    '''Функция рестарта'''
    timer = Timer(monotonic())
    m_c = MainCharacter(screen, ai_settings, cur_time, mc.surname)
    mc_fist = Fist(screen)
    enemies.empty()
    en_fists.empty()
    Enemy.deaths = 0
    Enemy.c_deaths = 0
    Enemy.summons = 0
    st.current_wave = 0
    st.state = st.GAMEACTIVE
    return timer, m_c, mc_fist 

















        



    
















    

    


    




    
