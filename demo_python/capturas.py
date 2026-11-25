"""Renderiza capturas reales desde el mismo código del juego, sin edición."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
from pathlib import Path
import pygame as pg
from main import Game
from modelo import World
from test_demo import accept, go, walk, cinema

def main():
    pg.init()
    out=Path("capturas");out.mkdir(exist_ok=True)
    game=Game(pg.display.set_mode((1280,720)))
    def capture(name):
        for _ in range(8):game.draw(.05)
        pg.image.save(game.frame,str(out/(name+".png")))
    capture("01_agencia_inicio")
    walk(game.world,8,3);game.open_cases();capture("02_tablon");game.close_modal()
    accept(game.world,"cine");go(game.world,"brizna");go(game.world,"client");capture("03_cine")
    game.world.toggle();go(game.world,"radio");capture("04_vinculo")
    game.world=cinema(World());game.motor.reset_motion();capture("05_agencia_con_brizna")
    accept(game.world,"station");go(game.world,"client");capture("06_estacion")
    game.open_evidence();capture("07_expediente")
    pg.quit()

if __name__=="__main__":main()
