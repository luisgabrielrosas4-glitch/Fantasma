"""Pruebas del renderizador real con el backend SDL de pantalla virtual."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import unittest
import pygame as pg
from motor_grafico import build_map, actor_sprite, Motion, Motor, light_mask, W,H
from modelo import World
from test_demo import walk, go, accept, cinema, station
from main import Game, SIZE

class GraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init();pg.display.set_mode((960,540))
    @classmethod
    def tearDownClass(cls):pg.quit()

    def test_maps_deterministic(self):
        a=build_map("cine");b=build_map("cine")
        self.assertEqual(a.get_size(),(W,H))
        self.assertEqual(pg.image.tobytes(a,"RGB"),pg.image.tobytes(b,"RGB"))
        self.assertNotEqual(pg.image.tobytes(a,"RGB"),pg.image.tobytes(build_map("office"),"RGB"))
        self.assertNotEqual(pg.image.tobytes(a,"RGB"),pg.image.tobytes(build_map("station"),"RGB"))

    def test_lighting(self):
        a=light_mask("cine");self.assertEqual(a.get_size(),(W,H))
        self.assertGreater(a.get_at((52,40)).r,a.get_at((0,0)).r)

    def test_sprites(self):
        for name,ghost in (("Tomás",False),("Rafael",False),("Brizna",True),("Mateo",True)):
            for d in ("up","down","left","right"):
                for f in range(4):
                    s=actor_sprite(name,ghost,d,f)
                    self.assertEqual(s.get_size(),(24,38));self.assertEqual(s.get_at((0,0)).a,0)
        self.assertNotEqual(pg.image.tobytes(actor_sprite("Tomás",False,"up"),"RGBA"),pg.image.tobytes(actor_sprite("Tomás",False,"down"),"RGBA"))

    def test_motion(self):
        m=Motion(2,2,2,2)
        x,y=m.advance(3,2,.03);self.assertTrue(2<x<3);self.assertEqual(y,2)
        self.assertEqual(m.direction,"right")
        for _ in range(8):m.advance(3,2,.03)
        self.assertEqual((m.x,m.y),(3,2));self.assertFalse(m.moving)
        self.assertEqual(m.advance(10,7,.03),(10,7))

    def test_cache_and_draw_no_mutation(self):
        w=World();m=Motor();before=repr(w)
        for _ in range(12):self.assertEqual(m.draw(w,.016).get_size(),(W,H))
        self.assertEqual(repr(w),before);self.assertEqual(m.background_builds,1)
        accept(w,"cine");go(w,"brizna");w.toggle()
        m.draw(w,.03,"radio")
        self.assertEqual(m.background_builds,2)
        w.recall();go(w,"exit");m.draw(w)
        self.assertEqual(m.background_builds,2)

    def test_ui_flow_and_resize(self):
        g=Game(pg.display.get_surface())
        self.assertEqual(g.draw().get_size(),SIZE)
        walk(g.world,8,3);g.choice="board";g.action("e")
        self.assertEqual(g.modal,"cases");g.draw();g.action(("accept","cine"))
        self.assertIsNone(g.modal);self.assertEqual(g.world.place,"cine")
        g.draw();g.action("tab");self.assertEqual(g.modal,"evidence");g.draw()
        before=repr(g.world);g.update(.1);self.assertEqual(repr(g.world),before)
        g.action("close");self.assertIsNone(g.modal);g.draw()
        v=g.viewport();self.assertEqual(g.logical(v.topleft),(0.,0.))
        self.assertEqual(g.screen.get_size(),(960,540))

if __name__=="__main__":unittest.main()
