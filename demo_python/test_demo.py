"""Pruebas de recorrido y contratos del GDD."""
import unittest
import tempfile
from collections import deque
from pathlib import Path
import random
from modelo import World, Spirit, CASES, blocked, WIDTH, HEIGHT
from campana import ORDER

def walk(w,x,y):
    start=w.pos;goal=(x,y);q=deque([(start,[])]);seen={start}
    while q:
        pos,path=q.popleft()
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
            seen.add(p);q.append((p,path+[(dx,dy)]))
    raise AssertionError(("Sin ruta",w.place,start,goal))

def go(w,key,power=False):
    x,y,*_=w.objects[key];walk(w,x,y);return w.act(key,power)

def prologue(w):
    if w.place=="hospital":
        go(w,"nurse");go(w,"exit")
        go(w,"notebook");go(w,"photo");go(w,"exit")
    go(w,"rafael");assert w.place=="street"
    go(w,"rafael");go(w,"exit");assert w.place=="cine"
    return w

def practice(w):
    go(w,"brizna");w.toggle();go(w,"radio",True);w.recall()
    assert w.practice_done

def accept(w,case):
    if case=="cine" and w.stage=="dispatch":return prologue(w)
    go(w,"request_"+case);go(w,"board");w.accept_case(case);assert w.place==case
    return w

def cinema(w):
    accept(w,"cine");practice(w);go(w,"client");go(w,"poster")
    go(w,"guard");go(w,"desk");go(w,"box");go(w,"photo")
    w.resolve("cine",1,list(w.facts["cine"]))
    assert w.home_open
    go(w,"exit");assert w.stage=="foundation"
    go(w,"home");go(w,"board");go(w,"journal");assert w.stage=="agency"
    return w

def station(w):
    accept(w,"station");go(w,"client");go(w,"schedule");go(w,"guard")
    assert not w.permissions["station"]
    walk(w,8,7);w.toggle();go(w,"witness");w.recall()
    go(w,"guard");go(w,"desk");go(w,"box");go(w,"photo")
    w.resolve("station",2,list(w.facts["station"]))
    assert w.reports.get("station")=="complete"
    go(w,"exit");return w

def solve_extra(w,case):
    accept(w,case);go(w,"client");go(w,"schedule");go(w,"guard")
    if case in ("workshop","ruiz"):go(w,"witness")
    if case=="ruiz":go(w,"mora")
    if case=="final":go(w,"wish")
    go(w,"desk");go(w,"box");go(w,"photo")
    cfg=CASES[case];w.resolve(case,cfg["correct"],list(w.facts[case]))
    assert w.reports.get(case)=="complete",(case,w.log[-1])
    if case!="final":go(w,"exit")
    return w

def ally(w,case,stay):
    go(w,"guest_"+case);w.decide_ally(case,stay)
    assert w.decisions[case]==("stayed" if stay else "departed")

class Tests(unittest.TestCase):
    def test_prologue_gates(self):
        w=World.new_game();go(w,"exit")
        self.assertEqual(w.place,"hospital")
        go(w,"nurse");go(w,"exit");go(w,"exit");self.assertEqual(w.place,"house")
        go(w,"notebook");go(w,"photo");go(w,"exit")
        self.assertEqual(w.stage,"dispatch")
        self.assertNotIn("board",w.objects)
        prologue(w);self.assertIn("cine",w.accepted)
        go(w,"client");self.assertNotIn("request",w.facts["cine"])
        practice(w);go(w,"client");self.assertIn("request",w.facts["cine"])

    def test_complete_campaign_and_endings(self):
        w=station(cinema(World.new_game()));ally(w,"station",True)
        solve_extra(w,"workshop");ally(w,"workshop",True)
        solve_extra(w,"ruiz");ally(w,"ruiz",True)
        solve_extra(w,"archive");solve_extra(w,"final")
        self.assertEqual(set(w.reports),set(ORDER))
        self.assertEqual(set(w.spirits),{"Brizna","Mateo","Nico","Mora"})
        for community in ("centro cultural","archivo","traslado"):
            for ending in ("agencia","explorar","colaborar"):
                w.choose_ending(community,ending)
                self.assertEqual(w.ending,ending);self.assertEqual(w.community_choice,community)

    def test_all_optional_allies_leave(self):
        w=station(cinema(World()));ally(w,"station",False)
        solve_extra(w,"workshop");ally(w,"workshop",False)
        solve_extra(w,"ruiz");ally(w,"ruiz",False)
        solve_extra(w,"archive");solve_extra(w,"final")
        self.assertEqual(list(w.spirits),["Brizna"])

    def test_return_resume(self):
        w=cinema(World());accept(w,"station");go(w,"client");go(w,"exit")
        self.assertEqual(w.place,"office");self.assertIn("request",w.facts["station"])
        accept(w,"station");self.assertIn("request",w.facts["station"])

    def test_no_fake_evidence(self):
        w=World();accept(w,"cine");w.resolve("cine",1,["request","desk","item"])
        self.assertFalse(w.home_open)
        practice(w);go(w,"client");w.resolve("cine",0,["request"])
        self.assertEqual(w.reports["cine"],"provisional")

    def test_read_not_collect(self):
        w=cinema(World());accept(w,"station");go(w,"client")
        walk(w,9,3);w.toggle();go(w,"desk")
        self.assertIn("desk",w.facts["station"]);self.assertNotIn("desk",w.physical["station"])
        w.recall();go(w,"guard");go(w,"desk");self.assertIn("desk",w.physical["station"])
        walk(w,16,7);w.toggle();go(w,"box")
        self.assertNotIn("item",w.facts["station"]);w.recall();go(w,"box")
        self.assertIn("item",w.physical["station"])

    def test_anchor_limits_and_recovery(self):
        w=World();accept(w,"cine");go(w,"brizna");w.toggle()
        a,b=w.anchor;walk(w,a+5,b);before=w.spirit.stability;w.tick(1)
        self.assertLess(w.spirit.stability,before)
        self.assertTrue(w.move(1,0));self.assertFalse(w.move(1,0))
        w.spirit.stability=1;w.tick(1);self.assertFalse(w.ghost_mode)
        self.assertEqual((w.gx,w.gy),w.anchor)

    def test_office_safe(self):
        w=cinema(World());self.assertIsNone(w.anchor);w.toggle();walk(w,18,9)
        w.spirit.energy=20;w.spirit.stability=20;w.tick(1)
        self.assertGreater(w.spirit.energy,20);self.assertGreater(w.spirit.stability,20)
        self.assertEqual(w.pos,(18,9))

    def test_errant_weakness(self):
        s=Spirit("Errante","",energy=30,stability=45,errant=True);s.update(0,10)
        self.assertLess(s.stability,45);self.assertLess(s.energy,30)

    def test_save_progress(self):
        w=World.new_game()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"save.json"
            for world in (w,cinema(World()),station(cinema(World()))):
                world.save(p);self.assertEqual(world,World.load(p))

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
            if w.place=="office":break

if __name__=="__main__":unittest.main()
