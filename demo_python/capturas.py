"""Capturas de la versión real y mapas completos para revisar geometría."""
import os,tempfile
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
from pathlib import Path
import pygame as pg
import main as ui
from main import Game
from modelo import World
from niveles import LEVELS
from motor_grafico import build_map
from test_demo import near,go,prologue,practice,cinema,station,solve_extra,ally

def main():
    pg.init();out=Path("capturas");out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        ui.SAVE=Path(tmp)/"preview.json"
        g=Game(pg.display.set_mode((1280,720)))
        def cap(name):
            g.draw(0.);pg.image.save(g.frame,str(out/(name+".png")))
        cap("01_menu");g.modal=None;cap("02_hospital")
        near(g.world,"nurse");g.choice="nurse";g.action("e");cap("03_dialogo")
        g.world=World();g.close_modal();near(g.world,"rafael");g.choice="rafael";g.action("e");cap("04_rafael")
        g.world=prologue(World());g.close_modal();practice(g.world);cap("05_brinza")
        g.world=cinema(World());g.close_modal();cap("06_agencia")
        station(g.world);ally(g.world,"station",True)
        for case in ("workshop","ruiz","archive","final"):
            solve_extra(g.world,case);cap("caso_"+case)
            if case in ("workshop","ruiz"):ally(g.world,case,False)
        for name in LEVELS:pg.image.save(build_map(name),str(out/("mapa_"+name+".png")))
    pg.quit()
if __name__=="__main__":main()
