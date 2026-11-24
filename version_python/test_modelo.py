import unittest
from modelo import Game
class Tests(unittest.TestCase):
    def test_wall(self):
        g=Game(human=(9,4),ghost=(9,4))
        self.assertFalse(g.move(1,0))
        g.switch()
        self.assertTrue(g.move(1,0))
    def test_anchor(self):
        g=Game(ghost=(18,10),active="ghost")
        for _ in range(13): g.tick()
        self.assertEqual(g.ghost,(3,4))
        self.assertEqual(g.active,"human")
    def test_case(self):
        g=Game(human=(3,4))
        g.interact("Brizna")
        self.assertTrue(g.bond)
        g.human=(7,7); g.interact("Elena")
        g.human=(15,5); g.interact("Mateo")
        g.human=(15,3); g.interact("registro")
        g.human=(16,7); g.interact("boleto")
        g.resolve(1); self.assertFalse(g.resolved)
        g.resolve(2); self.assertTrue(g.resolved)
        g.human=(2,9); g.interact("salida")
        self.assertTrue(g.home)
    def test_no_physical_evidence(self):
        g=Game(active="ghost",ghost=(16,7))
        g.interact("boleto")
        self.assertNotIn("boleto",g.clues)
