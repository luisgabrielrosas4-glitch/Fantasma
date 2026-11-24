import tempfile
import unittest
from pathlib import Path
from modelo import World

class PilotTests(unittest.TestCase):
    def at(self,w,x,y):
        w.x,w.y=x,y

    def test_patient_route(self):
        w=World()
        self.at(w,3,10);w.interact("archivo")
        for _ in range(15):w.tick()
        self.at(w,18,3);w.interact("registro")
        self.at(w,18,8);w.interact("armario")
        for _ in range(12):w.tick()
        self.at(w,5,7);w.interact("sofa")
        w.resolve("clara",w.clues)
        self.assertEqual(w.report,"confirmado")
        self.assertEqual(w.energy,100)
        self.assertEqual(w.trust,2)

    def test_intervention_route(self):
        w=World(t=3)
        self.at(w,18,3);w.interact("registro")
        self.assertNotIn("E02",w.clues)
        self.at(w,13,5);w.interact("radio",True)
        self.assertEqual(w.energy,91)
        self.assertEqual(w.distraction,10)
        self.at(w,18,3);w.interact("registro")
        self.assertIn("E02",w.clues)
        w.t=16
        self.at(w,15,8);w.interact("cuadro",True)
        self.assertIn("E03",w.clues)
        w.resolve("clara",w.clues)
        self.assertEqual(w.report,"confirmado_parcial")

    def test_block_and_recovery(self):
        w=World()
        self.at(w,13,5)
        for _ in range(5):w.interact("radio",True)
        self.assertTrue(w.blocked)
        self.at(w,18,3);w.interact("registro")
        self.assertNotIn("E02",w.clues)
        w.return_office()
        self.assertFalse(w.blocked)
        self.assertEqual(w.energy,100)
        w.t=15
        self.at(w,18,3);w.interact("registro")
        self.assertIn("E02",w.clues)

    def test_wrong_report_and_rectification(self):
        w=World()
        w.resolve("hermano",["T01"])
        self.assertEqual(w.trust,-1)
        w.resolve("clara",["E02","E03"])
        self.assertEqual(w.report,"provisional")
        w.t=18
        self.at(w,18,3);w.interact("registro")
        self.at(w,18,8);w.interact("armario")
        w.resolve("clara",w.clues)
        self.assertEqual(w.report,"confirmado_parcial")

    def test_energy_and_anchors(self):
        w=World(energy=7)
        self.at(w,3,10);w.interact("archivo")
        self.at(w,5,3);w.interact("lampara",True)
        self.assertEqual(w.energy,100)
        self.assertEqual(w.visits,2)
        self.assertIn("E01",w.clues)
        w.energy=50
        self.at(w,9,9);w.interact("ancla1");w.interact("ancla1")
        self.assertEqual(w.energy,75)

    def test_save_load(self):
        w=World()
        self.at(w,3,10);w.interact("archivo")
        w.resolve("hermano",["T01"])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"save.json"
            w.save(path)
            self.assertEqual(World.load(path),w)

    def test_movement_and_range(self):
        w=World(x=1,y=2)
        self.assertFalse(w.move(-1,0))
        self.assertFalse(w.move(1,1))
        self.assertTrue(w.move(1,0))
        w.interact("radio",True)
        self.assertEqual(w.energy,100)
        w.x,w.y=10,5;w.blocked=True
        self.assertFalse(w.move(1,0))

    def test_long_simulation(self):
        import random
        rng=random.Random(1234)
        w=World()
        for _ in range(10000):
            if rng.randrange(5)==0:
                w.return_office()
            else:
                w.move(*rng.choice([(0,1),(0,-1),(1,0),(-1,0)]))
                w.tick()
                w.interact(rng.choice(["archivo","radio","lampara","ancla1","cuadro","reloj"]),True)
            self.assertTrue(0<=w.energy<=100 and 0<=w.suspicion<=100)
            self.assertTrue(1<=w.x<=20 and 2<=w.y<=11)

class GuiTests(unittest.TestCase):
    def test_graphical_smoke(self):
        import os
        if os.name != "nt" and not os.getenv("DISPLAY"):
            self.skipTest("Requiere pantalla o Xvfb.")
        import tkinter as tk
        from main import Game
        root=tk.Tk()
        try:
            game=Game(root)
            root.update()
            self.assertGreater(len(game.cv.find_all()),100)
            game.open_board()
            root.update()
            self.assertTrue(game.paused)
            t=game.world.t
            game.tick()
            self.assertEqual(game.world.t,t)
        finally:
            root.destroy()

if __name__=="__main__":
    unittest.main()
