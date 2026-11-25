"""Regresión de campaña, reglas de anclaje y persistencia."""
import unittest
import tempfile
import random
from pathlib import Path
from collections import deque
from modelo import World, Spirit, CASES, blocked, WIDTH, HEIGHT

def walk(w,x,y):
    start=w.pos;goal=(x,y);queue=deque([(start,[])]);seen={start}
    while queue:
        pos,path=queue.popleft()
        if pos==goal:
            for dx,dy in path:assert w.move(dx,dy),(w.place,w.pos,dx,dy)
            return
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            p=pos[0]+dx,pos[1]+dy
            if p in seen or not (1<=p[0]<WIDTH-1 and 1<=p[1]<HEIGHT-1):continue
            if not w.ghost_mode and blocked(w.place,*p,w.permissions.get(w.place,False),w.distracted):continue
            if w.ghost_mode and w.anchor is not None:
                a,b=w.anchor
                if abs(p[0]-a)+abs(p[1]-b)>w.spirit.radius+3:continue
            seen.add(p);queue.append((p,path+[(dx,dy)]))
    raise AssertionError(("Sin ruta",w.place,start,goal))

def go(w,key,power=False):
    x,y,*_=w.objects[key];walk(w,x,y);return w.act(key,power)

def accept(w,case):
    go(w,"board");w.accept_case(case);assert w.place==case

def cinema(w):
    accept(w,"cine")
    go(w,"brizna");go(w,"client");go(w,"guard");go(w,"desk");go(w,"box");go(w,"photo")
    w.resolve("cine",1,list(w.facts["cine"]))
    assert w.home_open
    go(w,"exit");assert w.place=="office";go(w,"home")
    return w

def station(w):
    accept(w,"station");go(w,"client");go(w,"schedule");go(w,"guard")
    assert not w.permissions["station"]
    walk(w,8,7);w.toggle();go(w,"witness");w.recall()
    go(w,"guard");go(w,"desk");go(w,"box");go(w,"photo")
    w.resolve("station",2,list(w.facts["station"]))
    assert w.reports.get("station")=="complete"
    go(w,"exit");go(w,"guest")
    return w

class Tests(unittest.TestCase):
    def test_office_hub_and_gating(self):
        w=World()
        self.assertEqual(w.place,"office")
        self.assertIsNone(w.anchor)
        self.assertFalse(w.companion_present)
        w.accept_case("cine");self.assertEqual(w.place,"office")
        go(w,"board");w.accept_case("station");self.assertEqual(w.place,"office")
        w.accept_case("cine");self.assertEqual(w.place,"cine")
        self.assertEqual(w.accepted,["cine"])
        w.travel("office");self.assertEqual(w.place,"cine")

    def test_return_and_resume(self):
        w=World();accept(w,"cine");go(w,"brizna");go(w,"client");go(w,"exit")
        self.assertEqual(w.place,"office")
        self.assertFalse(w.companion_present)
        accept(w,"cine");self.assertTrue(w.companion_present)
        self.assertIn("request",w.facts["cine"])
        self.assertEqual(w.accepted,["cine"])
        self.assertEqual(w.anchor,(w.x,w.y))

    def test_full_campaign_recruitment(self):
        w=station(cinema(World()))
        w.recruit()
        self.assertIn("Mateo",w.spirits)
        self.assertTrue(w.spirits["Mateo"].home)
        self.assertEqual(w.guest_decision,"stayed")
        w.choose_spirit("Mateo")
        self.assertEqual(w.active,"Mateo")
        self.assertEqual(w.spirit.power,"sound")

    def test_optional_departure(self):
        w=station(cinema(World()));w.release_guest()
        self.assertEqual(w.guest_decision,"departed");self.assertNotIn("guest",w.objects)
        w.recruit();self.assertNotIn("Mateo",w.spirits)

    def test_no_fake_evidence(self):
        w=World();accept(w,"cine")
        w.resolve("cine",1,["request","desk","item"])
        self.assertFalse(w.home_open)
        go(w,"brizna");go(w,"client")
        w.resolve("cine",0,["request"])
        self.assertEqual(w.reports["cine"],"provisional")
        self.assertFalse(w.home_open)

    def test_read_hear_but_not_collect(self):
        w=cinema(World());accept(w,"station");go(w,"client")
        walk(w,9,3);w.toggle();go(w,"desk")
        self.assertIn("desk",w.facts["station"])
        self.assertNotIn("desk",w.physical["station"])
        w.recall();go(w,"guard")
        self.assertTrue(w.permissions["station"])
        go(w,"desk");self.assertIn("desk",w.physical["station"])
        walk(w,16,7);w.toggle();go(w,"box")
        self.assertNotIn("item",w.facts["station"])
        w.recall();go(w,"box");self.assertIn("item",w.physical["station"])

    def test_anchor_and_recovery(self):
        w=World();accept(w,"cine");go(w,"brizna");w.toggle()
        a,b=w.anchor;walk(w,a+5,b);before=w.spirit.stability;w.tick(1)
        self.assertLess(w.spirit.stability,before)
        self.assertTrue(w.move(1,0));self.assertFalse(w.move(1,0))
        w.spirit.stability=1;w.tick(1)
        self.assertFalse(w.ghost_mode);self.assertEqual((w.gx,w.gy),w.anchor)
        w.tick(1);self.assertGreater(w.spirit.stability,20)

    def test_office_free_movement_and_recovery(self):
        w=cinema(World());self.assertTrue(w.spirit.home);self.assertIsNone(w.anchor)
        w.toggle();walk(w,18,9);w.spirit.energy=20;w.spirit.stability=20;w.tick(1)
        self.assertGreater(w.spirit.energy,20);self.assertGreater(w.spirit.stability,20)
        self.assertEqual(w.pos,(18,9));w.recall()
        accept(w,"station");self.assertEqual(w.anchor,(w.x,w.y))

    def test_errant_weakness(self):
        s=Spirit("Errante","",energy=30,stability=45,errant=True);s.update(0,10)
        self.assertLess(s.stability,45);self.assertLess(s.energy,30);self.assertEqual(s.bond,0)

    def test_movement_and_power(self):
        w=World();accept(w,"cine");go(w,"brizna");walk(w,9,5)
        self.assertFalse(w.move(1,0))
        w.toggle();go(w,"radio",True);self.assertEqual(w.distracted,10);self.assertEqual(w.spirit.energy,80)
        w.recall();self.assertTrue(w.move(1,0))

    def test_furniture_blocks_humans_not_ghosts(self):
        w=World();accept(w,"cine");go(w,"brizna");walk(w,4,5)
        self.assertFalse(w.move(0,1))
        w.toggle();self.assertTrue(w.move(0,1))

    def test_save(self):
        w=station(cinema(World()));w.recruit()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"save.json";w.save(p);self.assertEqual(w,World.load(p))

    def test_simulation(self):
        w=cinema(World());accept(w,"station");r=random.Random(121)
        for _ in range(10000):
            w.move(*r.choice([(1,0),(-1,0),(0,1),(0,-1)]))
            if r.randrange(10)==0:w.toggle()
            if r.randrange(20)==0:w.recall()
            w.tick(.125)
            if w.nearby() and r.randrange(5)==0:w.act(w.nearby()[0],r.randrange(2)==0)
            self.assertTrue(0<=w.spirit.energy<=100 and 0<=w.spirit.stability<=100)
            self.assertTrue(1<=w.x<WIDTH-1 and 1<=w.y<HEIGHT-1)

if __name__=="__main__":unittest.main()
