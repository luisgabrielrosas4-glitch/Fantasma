"""Verifica mapas, cuadros de diálogo, título y campaña con SDL virtual."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import unittest
import tempfile
from pathlib import Path
import pygame as pg
import main
from motor_grafico import build_map, actor_sprite, Motion, Motor, light_mask, W,H
from modelo import World, MAPS
from test_demo import walk,go,accept,cinema,station,solve_extra
from main import Game,SIZE

class GraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init();pg.display.set_mode((960,540))
        cls.temp=tempfile.TemporaryDirectory()
        cls.old=main.SAVE;main.SAVE=Path(cls.temp.name)/"test.json"
    @classmethod
    def tearDownClass(cls):
        main.SAVE=cls.old;cls.temp.cleanup();pg.quit()

    def test_maps(self):
        for place in MAPS:
            self.assertEqual(build_map(place).get_size(),(W,H))
            self.assertEqual(light_mask(place).get_size(),(W,H))
        self.assertEqual(pg.image.tobytes(build_map("cine"),"RGB"),pg.image.tobytes(build_map("cine"),"RGB"))

    def test_sprites(self):
        for name,ghost in (("Tomás",False),("Brizna",True),("Mora",True),("Nico",True)):
            for direction in ("up","down","left","right"):
                for frame in range(4):
                    s=actor_sprite(name,ghost,direction,frame);self.assertEqual(s.get_size(),(24,38))

    def test_motion(self):
        m=Motion(2,2,2,2);x,y=m.advance(3,2,.03)
        self.assertTrue(2<x<3);self.assertEqual(y,2)
        for _ in range(8):m.advance(3,2,.03)
        self.assertEqual((m.x,m.y),(3,2))

    def test_new_game_ui(self):
        g=Game(pg.display.get_surface());self.assertEqual(g.modal,"title")
        self.assertEqual(g.draw().get_size(),SIZE)
        g.action("new");self.assertEqual(g.modal,"dialogue")
        while g.modal=="dialogue":g.draw();g.next_dialogue()
        self.assertEqual(g.world.place,"hospital")
        walk(g.world,5,4);g.choice="nurse";g.action("e")
        self.assertEqual(g.modal,"dialogue")
        while g.modal=="dialogue":g.draw();g.next_dialogue()
        self.assertIn("hospital:nurse",g.world.visited)
        self.assertEqual(g.world.goal()[1],"exit")
        g.draw();self.assertEqual(g.logical(g.viewport().topleft),(0.,0.))

    def test_all_scene_render(self):
        g=Game(pg.display.get_surface());g.modal=None
        w=cinema(World());g.world=w;g.draw()
        walk(w,8,3);g.open_cases();g.draw();g.close_modal()
        station(w);g.draw();g.open_cases();g.draw();g.close_modal()
        for case in ("workshop","ruiz","archive","final"):
            solve_extra(w,case);g.draw()
        g.modal="ending";g.draw();g.action(("community","archivo"));g.action(("ending","agencia"))
        g.draw();self.assertEqual(w.ending,"agencia")

if __name__=="__main__":unittest.main()
