"""Capturas reales del prototipo completo; no usa el guardado del jugador."""
import os,tempfile
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
from pathlib import Path
import pygame as pg
import main as ui
from main import Game
from modelo import World
from test_demo import prologue,practice,cinema,station,solve_extra,walk,go,accept

def main():
    pg.init();out=Path("capturas");out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        ui.SAVE=Path(tmp)/"preview.json"
        g=Game(pg.display.set_mode((1280,720)))
        def cap(name):
            g.draw(.05);pg.image.save(g.frame,str(out/(name+".png")))
        cap("01_menu");g.action("new");cap("02_accidente")
        while g.modal=="dialogue":g.next_dialogue()
        cap("03_hospital")
        prologue(g.world);walk(g.world,5,4);g.choice="brizna";g.action("e");cap("04_encuentro")
        g.close_modal();g.world=cinema(World());cap("05_agencia")
        walk(g.world,8,3);g.open_cases();cap("06_tablon");g.close_modal()
        station(g.world)
        for i,case in enumerate(("workshop","ruiz","archive","final"),7):
            solve_extra(g.world,case);cap(f"{i:02}_{case}")
        g.modal="ending";cap("11_final")
    pg.quit()
if __name__=="__main__":main()
