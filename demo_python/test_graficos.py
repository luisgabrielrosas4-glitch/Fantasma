"""Pruebas independientes de la ventana para raster, sprites y animación."""
import unittest
from motor_grafico import Raster, build_map, sprite_pixels, Motion, W, H

class GraphicsTests(unittest.TestCase):
    def test_raster_clipping(self):
        r=Raster(4,4,"#000000")
        r.rect(-2,-2,4,4,"#ff0000")
        self.assertEqual(len(r.data),48)
        self.assertEqual(r.data[:6],bytes([255,0,0,255,0,0]))
        self.assertEqual(r.data[6:12],bytes(6))
        self.assertEqual(r.data[24:],bytes(24))

    def test_map_dimensions_and_determinism(self):
        a=build_map("cine")
        b=build_map("cine")
        self.assertEqual((a.w,a.h),(W,H))
        self.assertEqual(a.ppm(),b.ppm())
        self.assertEqual(len(a.data),W*H*3)
        self.assertTrue(a.ppm().startswith(f"P6\n{W} {H}\n255\n".encode()))
        self.assertNotEqual(a.ppm(),build_map("office").ppm())
        self.assertNotEqual(a.ppm(),build_map("station").ppm())

    def test_sprite_frames(self):
        for name,ghost in (("Tomás",False),("Rafael",False),("Brizna",True),("Mateo",True)):
            for direction in ("up","down","left","right"):
                for frame in (0,1,2):
                    rows,palette=sprite_pixels(name,ghost,direction,frame,False)
                    self.assertEqual(len(rows),24)
                    self.assertTrue(all(len(row)==16 for row in rows))
                    self.assertTrue(set("".join("".join(row) for row in rows))<=set(palette)|{"."})
        self.assertNotEqual(sprite_pixels("Tomás",False,"down",0),sprite_pixels("Tomás",False,"down",1))
        self.assertNotEqual(sprite_pixels("Brizna",True,"down",0,False),sprite_pixels("Brizna",True,"down",0,True))

    def test_motion_interpolation(self):
        m=Motion(2,2,2,2)
        x,y=m.advance(3,2,.03)
        self.assertTrue(2<x<3)
        self.assertEqual(y,2)
        self.assertEqual(m.direction,"right")
        for _ in range(8):m.advance(3,2,.03)
        self.assertEqual((m.x,m.y),(3,2))
        self.assertFalse(m.moving)
        self.assertEqual(m.advance(10,7,.03),(10,7))

if __name__=="__main__":unittest.main()
