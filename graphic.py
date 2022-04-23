
import pygame
from MC import MainCharacter
from settings import Settings
from boss import Boss

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

def draw_invincibility(mc: MainCharacter):
    '''Визуальное отображение неуязвимости'''
    if mc.invincible:
        # Рисуем прямоугольник вверху для вывода значка неуязвимости
        stripe = pygame.Surface((55,55))
        stripe.fill((49, 4, 138))
        mc.screen.blit(stripe, (mc.screen_rect.width - 105, 0))
        inv_bar = pygame.image.load(f'images/K{mc.surname}_invincibility.png')
        mc.screen.blit(inv_bar,(mc.screen_rect.width - 100, 2))

class BossHealth:
    '''Здоровье босса'''

    def __init__(self, boss: Boss) -> None:
        self.bar_image = pygame.image.load('images/boss_health.png')
        self.rect = self.bar_image.get_rect()
        self.boss = boss
        self.screen = boss.screen
        self.screen_rect = boss.screen_rect
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        self.boss_full_health = boss.ai_settings.boss_health

    def blitme(self):
        '''Отображение здоровья босса на экране'''
        health_to_draw = pygame.Surface((int(self.boss.health/self.boss_full_health * 461), 16))
        health_to_draw.fill((22, 250, 45))
        self.screen.blit(
            health_to_draw, (self.rect.left + 19, self.rect.top + 54))
        self.screen.blit(self.bar_image, self.rect)


