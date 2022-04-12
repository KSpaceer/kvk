
import pygame
from MC import MainCharacter
from settings import Settings

def set_caption_and_icon():
    '''Устанавливает иконку и название игры'''
    icon = pygame.image.load('images/icon.png')
    pygame.display.set_caption('KvK')
    pygame.display.set_icon(icon)

def draw_health(mc: MainCharacter, ai_settings: Settings):
    '''Визуальное отображение здоровья главного персонажа'''
    # Рисуем полосу вверху для вывода здоровья
    stripe_width = 35 * (1 + 2 * ai_settings.mc_health)
    stripe = pygame.Surface((stripe_width, 55))
    stripe.fill((49, 4, 138))
    mc.screen.blit(stripe, (0,0))
    for i in range(mc.health):
        new_healthbar = pygame.image.load(f'images/K{mc.surname}_health.png')
        rect = new_healthbar.get_rect()
        rect.top = mc.screen_rect.top
        rect.left = rect.width + i * 2 * rect.width
        mc.screen.blit(new_healthbar, rect)

def draw_invincibility(mc):
    '''Визуальное отображение неуязвимости'''
    if mc.invincible:
        # Рисуем прямоугольник вверху для вывода значка неуязвимости
        stripe = pygame.Surface((55,55))
        stripe.fill((49, 4, 138))
        mc.screen.blit(stripe, (mc.screen_rect.width - 105, 0))
        inv_bar = pygame.image.load(f'images/K{mc.surname}_invincibility.png')
        mc.screen.blit(inv_bar,(mc.screen_rect.width - 100, 2))