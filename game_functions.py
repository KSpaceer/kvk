

from os.path import exists
from time import monotonic, time
from base64 import b64decode
import pygame
import sys
from MC import MainCharacter
from background import Background
from boss import Boss
from eater import Eater
from etimer import Timer
import graphic as gr
from guru import Guru
from mediator import Mediator
from ninja import Ninja
from path_handling import load_image, resource_path

from settings import Settings
from stats import Stats
from bull import Bull
from sumo import Sumo
from enemy import Enemy
from button import Button
from fist import Fist
from selecticon import SelectIcon
from audiosounds import Audio
from option import Option



### ОБЩИЙ БЛОК ###

def check_events(mc: MainCharacter, st: Stats, buttons: list[Button], 
    screen: pygame.Surface, cur_time: Timer, timer: Timer, 
    enemies: pygame.sprite.Group, selecticons: list[SelectIcon], 
    en_fists: pygame.sprite.Group, audio: Audio, mediator: Mediator):
    '''Обрабатывает нажатия клавиш и мыши'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Выход по нажатии крестика
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # Проверка событий нажатия
            keydown_events(event, mc, st, buttons, 
            screen, cur_time, timer, enemies, selecticons, 
            en_fists, audio, mediator)
            # Если текущее состояние - заставка или проигрыш, меняет состояние
            change_state(st, buttons, mediator, mc)
        elif event.type == pygame.KEYUP:
            # Проверка событий отпускания кнопок
            keyup_events(event, mc, st)
        elif st.state == st.CREDITS and event.type == pygame.MOUSEBUTTONDOWN\
            and event.button == 1:
            leftbutton_click_in_credits(event, screen)

def keydown_events(event, mc: MainCharacter, 
    st: Stats, buttons: list[Button], screen: pygame.Surface, 
    cur_time: Timer, timer: Timer, enemies: pygame.sprite.Group, 
    selecticons: list[SelectIcon], en_fists: pygame.sprite.Group, 
    audio: Audio, mediator: Mediator):
    '''Обрабатывает события нажатия клавиш'''
    # В зависимости от состояния игры - различная реакция на нажатия
    if st.state == st.GAMEACTIVE:
        keydown_in_game(event, mc, st, buttons, mediator, audio)
    elif st.state == st.MAINMENU:
        keydown_in_mainmenu(event, st, buttons, screen, selecticons, audio, mediator)
    elif st.state == st.SELECTMODE:
        keydown_in_selectmode(event, st, selecticons, mc, buttons, mediator, audio)
    elif st.state == st.SUBMENU:
        keydown_in_submenu(event, st, buttons, mediator, 
        cur_time, timer, mc, enemies, en_fists, audio)
    elif st.state in (st.SAVEFILES_SAVEMODE, st.SAVEFILES_LOADMODE):
        keydown_in_savefiles(event, st, buttons, mediator, mc, audio)
    elif st.state == st.OPTIONS:
        keydown_in_options(event, st, buttons, audio, mediator)
    

def keyup_events(event, mc: MainCharacter, st: Stats):
    '''Обрабатывает события отжатия клавиш'''
    if st.state == st.GAMEACTIVE:
        keyup_in_game(event, mc)


def select_button(buttons: list[Button], event: pygame.event.Event, 
    audio: Audio, do_reverse: bool = False):
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
            audio.play_sound('change_button')
            exec('buttons[i' + key_vars[event.key][0] + '1].is_chosen = True')
            break 

def change_state(st: Stats, buttons: list[Button], 
    mediator: Mediator, mc: MainCharacter):
    '''Изменяет состояние игры'''
    if st.state == st.INTRO:
        # Переход с заставки в главное меню
        buttons.clear()
        create_mainmenu_buttons(buttons, mediator)
        st.state = st.MAINMENU
    elif st.state == st.GAMEOVER and monotonic() - mc.timer > 5:
        # Рестарт после проигрыша
        st.restart_flag = True

### БЛОК ГЛАВНОГО МЕНЮ (st.state = Stats.MAINMENU) ###

def create_mainmenu_buttons(buttons: list[Button], mediator: Mediator):
    '''Создает кнопки главного меню'''
    for i in range(4):
        buttons.append(Button(mediator, i))
        if i == Button.NEWGAME:
                # Клавиша начала игры выбрана
            buttons[i].is_chosen = True
        buttons[i].rect.centery = 125 + 2 * i * 90

def update_mainmenu_screen(buttons: list[Button], bg: Background):
    '''Обновляет изображение в главном меню'''
    # Перерисовка экрана
    bg.blitme()
    # Прорисовка кнопок
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_mainmenu(event, st: Stats, buttons: list[Button], 
    screen: pygame.Surface, selecticons: list[SelectIcon], 
    audio: Audio, mediator: Mediator):
    '''Обрабатывает нажатия клавиш в главном меню'''
    if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
        select_button(buttons, event, audio)
    elif event.key == pygame.K_RETURN:
        # Активация кнопки по нажатии Enter
        audio.play_sound('click_button')
        for i in range(len(buttons)):
            if buttons[i].is_chosen:
                if buttons[i].name_number == Button.NEWGAME:
                    # Переход из главного меню в меню выбора персонажа
                    buttons.clear()
                    create_selecticons(selecticons, mediator)
                    st.state = st.SELECTMODE
                    break
                elif buttons[i].name_number == Button.LOAD:
                    # Переход из главного меню в меню файлов сохранения 
                    # в режиме загрузки
                    buttons.clear()
                    create_savefiles_buttons(buttons, mediator)
                    st.state = st.SAVEFILES_LOADMODE
                    st.pr_state = st.MAINMENU
                    break
                elif buttons[i].name_number == Button.OPTIONS:
                    # Переход в меню опций
                    buttons.clear()
                    create_option_buttons(buttons, mediator)
                    st.state = st.OPTIONS
                    break
                elif buttons[i].name_number == Button.EXIT:
                    # Выход из игры
                    sys.exit()

### БЛОК ОПЦИЙ (st.state = Stats.OPTIONS) ###

def create_option_buttons(buttons: list[Option], mediator: Mediator):
    '''Создает кнопки опций'''
    for i in range(2):
        new_option = Option(mediator, i)
        buttons.append(new_option)
        buttons[i].rect.bottom = 350 + i * 200
        if not i:
            buttons[i].is_chosen = True

def update_options_screen(buttons: list[Option], bg: Background):
    '''Обновляет изображение в меню опций'''
    # Перерисовка экрана
    bg.blitme()
    # Отображение кнопок
    for option in buttons:
        option.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_options(event, st: Stats, buttons: list[Option], 
    audio: Audio, mediator: Mediator):
    '''Обрабатывает нажатия клавиш в меню опций'''
    if event.key in (pygame.K_DOWN, pygame.K_UP):
        select_button(buttons, event, audio)
    elif event.key == pygame.K_LEFT:
        for option in buttons:
            if option.is_chosen:
                audio.play_sound('click_button')
                option.vary_parameter(False)
                break
    elif event.key == pygame.K_RIGHT:
        for option in buttons:
            if option.is_chosen:
                audio.play_sound('click_button')
                option.vary_parameter(True)
                break
    elif event.key == pygame.K_ESCAPE:
        # Выход в меню по нажатию ESC
        buttons.clear()
        audio.play_sound('back')
        create_mainmenu_buttons(buttons, mediator)
        st.state = st.MAINMENU
    


### БЛОК ВЫБОРА ПЕРСОНАЖА (st.state = Stats.SELECTMODE) ###

def create_selecticons(selecticons: list[SelectIcon], mediator: Mediator):
    '''Создает иконки выбора персонажа'''
    selecticons.extend((SelectIcon('S', mediator), SelectIcon('Z', mediator)))

def update_selectmode_screen( screen: pygame.Surface, 
    selecticons: list[SelectIcon], bg: Background):
    '''Обновляет изображение на экране во время выбора персонажа'''
    # Перерисовка экрана
    bg.blitme()
    # Вывод надписи 
    screen.blit(load_image('syf.png'), (450, 100))
    # Отображение иконок персонажей
    for selecticon in selecticons:
        selecticon.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_selectmode(event, st: Stats, selecticons: list[SelectIcon], 
    mc: MainCharacter, buttons: list[Button], mediator: Mediator, 
    audio: Audio):
    '''Обрабатывает нажатия клавиш в меню выбора персонажа'''
    if event.key == pygame.K_ESCAPE:
        # Выход в меню по нажатию ESC
        selecticons.clear()
        audio.play_sound('back')
        create_mainmenu_buttons(buttons, mediator)
        st.state = st.MAINMENU
    # Смена выбранного персонажа по нажатию стрелок
    elif event.key == pygame.K_LEFT:
        if selecticons[1].is_selected:
            audio.play_sound('сhange_character')
            selecticons[1].is_selected = False
            selecticons[0].is_selected = True
    elif event.key == pygame.K_RIGHT:
        if selecticons[0].is_selected:
            audio.play_sound('сhange_character')
            selecticons[0].is_selected = False
            selecticons[1].is_selected = True
    elif event.key == pygame.K_RETURN:
        # Выбор персонажа по нажатию ENTER и запуск игры
        audio.play_sound('select_character')
        for selecticon in selecticons:
            if selecticon.is_selected:
                mc.surname = selecticon.surname
                selecticons.clear()
                st.level = 0
                st.state = st.LOADING
                break 

### БЛОК ИГРЫ (st.state = Stats.GAMEACTIVE) ###

def update_screen(ai_settings: Settings, 
    mc: MainCharacter, enemies: pygame.sprite.Group, 
    en_fists: pygame.sprite.Group, bg: Background):
    '''Обновляет изображение на экране'''
    # Перерисовка экрана
    #screen.fill(ai_settings.bg_color)
    bg.blitme()
    # Отображение здоровья и неуязвимости
    gr.draw_health(mc, ai_settings)
    gr.draw_invincibility(mc)
    # Отображение главного персонажа и врагов
    mc.blitme()
    for enemy in enemies:
        enemy.blitme()
    for en_fist in en_fists:
        en_fist.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_game(event, mc: MainCharacter, st: Stats, 
    buttons: list[Button], mediator: Mediator, audio: Audio):
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
        audio.play_sound('pause')
        create_submenu_buttons(buttons, mediator)
        st.state = st.SUBMENU

def keyup_in_game(event, mc: MainCharacter):
    '''Обрабатывает отжатия клавиш во время самой игры'''
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

def check_hits(mc: MainCharacter, en_fists: pygame.sprite.Group):
    '''Проверка получения удара'''
    if not mc.invincible:
        # Если персонаж неуязвим, проверяет коллизии персонажа с вражескими
        # ударными поверхностями
        touching_fist = pygame.sprite.spritecollideany(mc, en_fists)
        if touching_fist:
            # В случае коллизии персонаж получает урон
            mc.get_damage(touching_fist)

def wave(mc: MainCharacter, enemies: pygame.sprite.Group, timer: Timer, 
    cur_time: Timer, mediator: Mediator, adversaries: list):
    '''Создает волну противников'''
    for i in range(len(adversaries)):
        # Враги появляются по времени. 
        if cur_time - timer >= 5 * (i + 1) and len(enemies) == i \
            and Enemy.summons < len(adversaries):
            enemy_summon(mc, enemies, mediator, adversaries, i)

def enemy_summon(mc: MainCharacter, enemies: pygame.sprite.Group, mediator: Mediator, 
    adversaries: list, i: int):
    '''Вызывает врага'''
    if adversaries[i] == 0:
        new_enemy = Bull(mediator)
        enemies.add(new_enemy)
    elif adversaries[i] == 1:
        new_enemy = Sumo(mediator)
        enemies.add(new_enemy)
    elif adversaries[i] == 2:
        if mc.surname == 'Z':
            new_enemy = Eater(mediator)
            enemies.add(new_enemy)
        else:
            new_enemy = Guru(mediator)
            enemies.add(new_enemy)
    elif adversaries[i] == 3:
        new_enemy = Ninja(mediator)
        enemies.add(new_enemy)
    elif adversaries[i] == 4:
        new_enemy = Boss(mediator)
        enemies.add(new_enemy)

def update_waves(ai_settings: Settings, 
    mc: MainCharacter, enemies: pygame.sprite.Group, 
    timer: Timer, cur_time: Timer, st: Stats, mediator: Mediator):
    '''Обновляет волны'''
    wave(mc, enemies, timer, cur_time, mediator, 
    ai_settings.waves[st.level][st.current_wave])


### БЛОК МЕНЮ ПАУЗЫ (st.state = Stats.SUBMENU) ###

def create_submenu_buttons(buttons: list[Button], 
    mediator: Mediator, selected_button: int = Button.MENU):
    '''Создает кнопки меню паузы'''
    for i in range(3, 6):
        buttons.append(Button(mediator, i))
        if i == selected_button:
            # Избранная кнопка
            buttons[i - 3].is_chosen = True
        buttons[i - 3].rect.centery = 580 - 2 * (i - 3) * 90

def update_submenu_screen(screen: pygame.Surface, ai_settings: Settings, 
    mc: MainCharacter, enemies: pygame.sprite.Group, 
    en_fists: pygame.sprite.Group, buttons: list[Button], bg: Background):
    '''Обновляет изображение в меню паузы'''
    # Аналогично функции update_screen(), чтобы во время паузы было видно игру
    bg.blitme()
    gr.draw_health(mc, ai_settings)
    gr.draw_invincibility(mc)
    mc.blitme()
    for enemy in enemies:
        enemy.blitme()
    for en_fist in en_fists:
        en_fist.blitme()
    # Затемняем экран игры
    obscure_screen(ai_settings, screen)
    # Прорисовка кнопок:
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_submenu(event, st: Stats, buttons: list[Button], 
    mediator: Mediator, cur_time: Timer, timer: Timer, 
    mc: MainCharacter, enemies: pygame.sprite.Group, 
    en_fists: pygame.sprite.Group, audio: Audio):
    '''Обрабатывает нажатия клавиш во время паузы'''
    if event.key == pygame.K_ESCAPE:
        # Возобновление игры
        buttons.clear()
        update_time(cur_time, timer, mc, enemies, en_fists)
        audio.play_sound('back')
        st.state = st.GAMEACTIVE
    elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
        select_button(buttons, event, audio, True)
    elif event.key == pygame.K_RETURN:
        audio.play_sound('click_button')
        for i in range(len(buttons)):
            if buttons[i].is_chosen:
                if buttons[i].name_number == Button.MENU:
                    # Выход в меню
                    buttons.clear()
                    create_mainmenu_buttons(buttons, mediator)
                    st.state = st.MAINMENU
                    break
                elif buttons[i].name_number == Button.SAVE:
                    # Переход в меню файлов сохранения
                    buttons.clear()
                    create_savefiles_buttons(buttons, mediator)
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
    mc: MainCharacter, enemies: pygame.sprite.Group, 
    en_fists: pygame.sprite.Group):
    '''Обновляет все атрибуты времени после возобновления игры, т.е.
    корректирует их на разницу между 
    игровым времени(cur_time) и монотонным(monotonic().'''
    delta = monotonic() - cur_time
    objects = [timer, mc] 
    objects.extend(enemies)
    objects.extend(en_fists)
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
            if object.launch_cooldown_timer:
                object.launch_cooldown_timer += delta
            if isinstance(object, Boss):
                if object.invin_timer:
                    object.invin_timer += delta
                if object.ultimate_cooldown_timer:
                    object.ultimate_cooldown_timer += delta
        elif object in en_fists and hasattr(object, 'timer'):
            object.timer += delta
            

### БЛОК МЕНЮ ФАЙЛОВ СОХРАНЕНИЯ (st.state = Stats.SAVEFILES_...) ###

def create_savefiles_buttons(buttons: list[Button], mediator: Mediator):
    '''Создает кнопки меню сохранения файлов'''
    for i in range(3):
        if exists(f'save/save{i + 1}.txt'):
            # Если файл сохранения имеется
            buttons.append(Button(mediator, Button.SAVEFILE))
            open_savefile(i, buttons)
        else:
            # Если файла сохранения нет
            buttons.append(Button(mediator, Button.EMPTY))
        if i == 0:
            # Верхняя кнопка изначально выбрана
            buttons[i].is_chosen = True
        buttons[i].rect.centery = 220 + 2 * i * 90

def update_savefiles_screen(buttons: list[Button], bg: Background):
    '''Обновляет изображение в меню файлов сохранения'''
    # Перерисовка экрана
    bg.blitme()
    # Прорисовка кнопок
    for button in buttons:
        button.blitme()
    # Обновление экрана
    pygame.display.flip()

def keydown_in_savefiles(event, st: Stats, buttons: list[Button], 
    mediator: Mediator, mc: MainCharacter, audio: Audio):
    '''Обрабатывает нажатия клавиш в меню файлов сохранения'''
    if event.key == pygame.K_ESCAPE:
        audio.play_sound('back')
        if st.pr_state == st.SUBMENU:
            # Если предыдущим состоянием игры было меню паузы, возвращает туда
            buttons.clear()
            create_submenu_buttons(buttons, mediator, Button.SAVE)
            st.state = st.SUBMENU
        elif st.pr_state == st.MAINMENU:
            # Если пред. состоянием игры было главное меню, возвращает туда
            buttons.clear()
            create_mainmenu_buttons(buttons, mediator)
            st.state = st.MAINMENU
    elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
        select_button(buttons, event, audio)
    elif event.key == pygame.K_RETURN:
        audio.play_sound('click_button')
        if st.state == st.SAVEFILES_SAVEMODE:
            # Если активен режим сохранения, сохраняет игровую информацию в выбранный слот
            for i in range(len(buttons)):
                if buttons[i].is_chosen:
                    with open(resource_path('save', f'save{i + 1}.txt'), 'w') as f:
                        f.write(str(st.level) + '\n' + mc.surname)
                    break
            # Возвращает в меню паузы
            buttons.clear()
            create_submenu_buttons(buttons, mediator, Button.SAVE)
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
    with open(resource_path('save', f'save{number + 1}.txt'), 'r') as f:
        buttons[number].saved_data = f.readlines()
        # Добавляем к изображению номер файла
        buttons[number].image.blit(load_image('Buttons', f'{number + 1}.png'), 
            (82, 13))
        # Перевернутая строка значения уровня
        reversed_level = str(int(buttons[number].saved_data[0]) + 1)[::-1]
        for i in range(len(reversed_level) + 1):
            if i == len(reversed_level):
                # Добавляем к изображению букву L (level)
                buttons[number].image.blit(
                    load_image('Buttons', 'L.png'),(179 - 20 * i, 13))
            else:
                # Добавляем к изображению одну цифру из значения уровня
                buttons[number].image.blit(
                    load_image('Buttons', f'{reversed_level[i]}.png'),
                    (179 - 20 * i, 13))
        # Добавим на кнопку иконку персонажа
        buttons[number].image.blit(load_image(
            f'K{buttons[number].saved_data[1]}_health.png'), 
            (157, 40))

### БЛОК ТИТРОВ (st.state = Stats.CREDITS) ###

def update_credits_screen(bg: Background, cur_y: int, st: Stats, 
    buttons: list[Button], mediator: Mediator) -> int:
    '''Обновление изображения во время титров'''
    # Прокрутка изображения
    if cur_y <= 4210: # 4210 - разница между высотой титров и высотой экрана
        bg.blitme()
        pygame.display.flip()
        bg.image.scroll(0, -1)
    # Находим текущую вертикальную позицию
    cur_y += 1
    if cur_y == 5210: # +1000 - выбрал интуитивно (слегка методом тыка)
        buttons.clear()
        create_mainmenu_buttons(buttons, mediator)
        mediator.call_method('audio', 'stop_all_sounds')
        st.state = st.MAINMENU
        cur_y = 0
    return cur_y

def leftbutton_click_in_credits(event, screen: pygame.Surface):
    '''Обработка нажатия левой клавиши мыши в титрах'''
    x, y = event.pos
    if pygame.PixelArray(screen)[x, y] == screen.map_rgb((255, 0, 0)): 
        if not exists('images/backgrounds/sans.png'):
            create_paster_image()
        Background.PASTER_EGG_ACTIVE = True
        Audio.PASTER_EGG_ACTIVE = True


# Старый медленный код, использовавший непосредственную работу с массивом 
# пикселей для расшифровки сохраненного в текстовом формате изображения

#def create_paster_image(screen: pygame.Surface):
#    '''Создает изображение-пасхалку из текстового файла'''
#    paster_image = pygame.Surface(
#                (screen.get_width(), screen.get_height()))
#    paster_image_pxlarr = pygame.PixelArray(paster_image)
#    with open('working_data.txt', 'r') as f:
#        file_pxlarr = f.read().splitlines()
#        for i in range(len(file_pxlarr)):
#           row = file_pxlarr[i].split('\t')
#           for j in range(len(row)):
#                paster_image_pxlarr[j, i] = tuple(map(
#                    int, row[j].split(',')))
#    paster_image = paster_image_pxlarr.make_surface()
#    pygame.image.save(paster_image, 'images/backgrounds/sans.png')

# Новый код использует кодирование Base64 для расшифровки изображения, 
# сохраненного в двоичном формате

def create_paster_image():
    '''Создает изображение-пасхалку из текстового файла'''
    with open(resource_path('some_data.bin'), 'rb') as f:
        binary_repr = f.read()
    
    with open(resource_path('images', 'backgrounds', 'sans.png'), 'wb') as img:
        img.write(b64decode(binary_repr))
                    



    

### БЛОК ПРОИГРЫША (st.state = Stats.GAMEOVER) ###

def update_gameover_screen(bg: Background, mc: MainCharacter, 
    ai_settings: Settings, enemies: pygame.sprite.Group, 
    en_fists: pygame.sprite.Group, screen: pygame.Surface):
    '''Обновление экрана при проигрыше'''
    # Аналогично функции update_screen(), чтобы во время паузы было видно игру
    bg.blitme()
    gr.draw_health(mc, ai_settings)
    gr.draw_invincibility(mc)
    mc.blitme()
    for enemy in enemies:
        enemy.blitme()
    for en_fist in en_fists:
        en_fist.blitme()
    # Затемняем экран игры
    obscure_screen(ai_settings, screen)
    # Создаем надпись
    draw_gameover_text(mc, ai_settings, screen)
    # Обновление экрана
    pygame.display.flip()

def draw_gameover_text(mc: MainCharacter, 
    ai_settings: Settings, screen: pygame.Surface):
    '''Отображает на экране текст во время проигрыша'''
    if monotonic() - mc.timer < 5:
        for i in range(5):
            if (i + 1) > monotonic() - mc.timer >= i:
                # белый текст
                text = mc.font.render(f'{5 - i}', True, (255, 255, 255))
    else:
        text = mc.font.render('PRESS ANY KEY', True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.centerx = int(ai_settings.screen_width/2)
    text_rect.centery = int(ai_settings.screen_height/2)
    screen.blit(text, text_rect)



def restart(screen: pygame.Surface, mediator: Mediator,
    enemies: pygame.sprite.Group, en_fists: pygame.sprite.Group, 
    st: Stats, mc: MainCharacter, audio: Audio) \
    -> tuple[Timer, MainCharacter, Fist]:
    '''Функция рестарта'''
    timer = Timer(monotonic())
    if mc.health < 1:
        audio.play_sound('restart')
    new_mc = MainCharacter(mediator, mc.surname)
    mc_fist = Fist(screen)
    mediator.add(mc=new_mc, mc_fist=mc_fist, timer=timer)
    enemies.empty()
    en_fists.empty()
    Enemy.deaths = 0
    Enemy.c_deaths = 0
    Enemy.summons = 0
    st.current_wave = 0
    st.state = st.GAMEACTIVE
    st.restart_flag = False
    return timer, new_mc, mc_fist 

















        



    
















    

    


    




    
