import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import tempfile
import unittest
from pathlib import Path
import pygame as pg
import main
from main import Game,SIZE
from modelo import World
from niveles import LEVELS
from motor_grafico import build_map,light_mask,Motor,TILE,W,H
from test_demo import near,go,cinema,prologue,practice,station,solve_extra,ally

class GraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init();pg.display.set_mode((960,540))
        cls.temp=tempfile.TemporaryDirectory();cls.old=main.SAVE;main.SAVE=Path(cls.temp.name)/"save.json"
    @classmethod
    def tearDownClass(cls):
        main.SAVE=cls.old;cls.temp.cleanup();pg.quit()

    def test_distinct_maps_and_camera(self):
        for name,level in LEVELS.items():
            size=tuple(v*TILE for v in level.size)
            self.assertEqual(build_map(name).get_size(),size)
            self.assertEqual(light_mask(name).get_size(),size)
        w=World.new_game();m=Motor();w.x,w.y=25,15
        self.assertEqual(m.draw(w,0.,goal="exit").get_size(),(W,H))
        self.assertGreater(m.camera[0],0)

    def test_rafael_ui_and_dialogue(self):
        g=Game(pg.display.get_surface());g.world=World();g.modal=None
        near(g.world,"rafael");g.choice="rafael";g.action("e")
        self.assertEqual(g.modal,"dialogue");self.assertGreaterEqual(len(g.dialogue),9)
        self.assertEqual(g.world.place,"office")
        for _ in range(len(g.dialogue)):g.draw();g.next_dialogue()
        self.assertEqual(g.modal,"rafael_choice")
        g.draw();g.action(("rafael","later"));self.assertEqual(g.world.place,"office")
        self.assertNotIn("office:rafael",g.world.visited)
        g.action("e");g.action(("rafael","accept"))
        self.assertEqual(g.world.place,"office");self.assertIn("office:rafael",g.world.visited)
        near(g.world,"exit");g.choice="exit";g.action("e");self.assertEqual(g.world.place,"street")
        near(g.world,"rafael");g.choice="rafael";g.action("e")
        self.assertEqual(g.modal,"dialogue");self.assertNotIn("street:rafael",g.world.visited)
        while g.modal=="dialogue":g.next_dialogue()
        self.assertIn("street:rafael",g.world.visited);self.assertEqual(g.world.place,"street")

    def test_ui_window_sizes(self):
        for size in ((1366,768),(1280,720),(960,540)):
            g=Game(pg.display.set_mode(size));g.modal=None
            self.assertEqual(g.draw().get_size(),SIZE)
            v=g.viewport()
            self.assertEqual(g.logical(v.topleft),(0.,0.))
            self.assertTrue(all(pg.Rect((0,0),SIZE).contains(box) for box,_ in g.buttons))
            g.present()
            near(g.world,"nurse");g.choice="nurse";g.draw()
            self.assertTrue(any(a=="e" for _,a in g.buttons))

    def test_modal_pauses(self):
        g=Game(pg.display.get_surface());g.start_game()
        before=repr(g.world);g.update(.15)
        self.assertEqual(repr(g.world),before)
        while g.modal=="dialogue":g.next_dialogue()
        self.assertEqual(g.world.place,"hospital")

if __name__=="__main__":unittest.main()
