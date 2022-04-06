from time import monotonic
import pygame
from MC import MainCharacter
from enemy import Enemy
from stats import Stats
from etimer import Timer
from fist import Fist


def restart(screen, ai_settings, enemies, en_fists, st, cur_time):
    '''Функция рестарта'''
    timer = Timer(monotonic())
    mc = MainCharacter(screen, ai_settings, cur_time)
    mc_fist = Fist(screen)
    enemies.empty()
    en_fists.empty()
    Enemy.deaths = 0
    Enemy.c_deaths = 0
    Enemy.summons = 0
    st.state = Stats.GAMEACTIVE
    return timer, mc, mc_fist