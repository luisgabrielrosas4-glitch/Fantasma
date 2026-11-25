"""Pruebas de aceptación del parche 0.5.1."""
import random
import tempfile
import unittest
from pathlib import Path
from collections import deque
from modelo import World, Spirit, CASES, blocked
from campana import ORDER
from niveles import LEVELS, DIRS, occupied, distance, sight

def walk(w,x,y):
    start=w.pos;goal=(x,y);level=LEVELS[w.place];q=deque([(start,[])]);seen={start}
    taken=occupied(w.objects)
    if w.ghost_mode:taken.add((w.x,w.y))
    elif w.place=="office" and w.companion_present:taken.add((w.gx,w.gy))
    while q:
        p,path=q.popleft()
        if p==goal:
            for dx,dy in path:assert w.move(dx,dy),(w.place,w.pos,dx,dy)
            return
        for dx,dy in DIRS:
            n=(p[0]+dx,p[1]+dy)
            if n in seen or n in taken or not level.inside(n):continue
            if w.ghost_mode:
                if w.anchor is not None and distance(n,w.anchor)>w.spirit.radius+3:continue
            else:
                leaving=p in level.restricted
                if blocked(w.place,*n,w.access() or leaving,w.distracted):continue
                if n in level.restricted and not leaving and not (w.access() or (w.distracted>0 and w.place!="workshop")):continue
            seen.add(n);q.append((n,path+[(dx,dy)]))
    raise AssertionError(("Sin ruta",w.place,start,goal))

def near(w,key):
    if key in w.nearby():return
    o=w.objects[key];x,y=o[:2]
    candidates=sorted([(x+dx,y+dy) for dx,dy in DIRS]+[(x,y)],key=lambda p:distance(w.pos,p))
    for p in candidates:
        try:walk(w,*p)
        except AssertionError:continue
        if key in w.nearby():return
    raise AssertionError(("No se puede alcanzar",w.place,key,w.pos))

def go(w,key,power=False):
    near(w,key);return w.act(key,power)

def prologue(w):
    if w.place=="hospital":
        go(w,"nurse");go(w,"exit");go(w,"notebook");go(w,"photo");go(w,"exit")
    assert w.stage=="dispatch",(w.place,w.stage)
    go(w,"rafael");w.accept_rafael();go(w,"exit")
    assert w.place=="street"
    go(w,"rafael");go(w,"exit");assert w.place=="cine"
    return w

def practice(w):
    go(w,"brizna");near(w,"radio");w.toggle();go(w,"radio",True);w.recall()
    assert w.practice_done,w.log

def accept(w,case):
    if case=="cine" and w.stage=="dispatch":return prologue(w)
    go(w,"request_"+case);near(w,"board");w.accept_case(case)
    assert w.place==case,w.log
    return w

def cinema(w):
    accept(w,"cine");practice(w);go(w,"client");go(w,"poster");go(w,"guard")
    go(w,"desk");go(w,"box");go(w,"photo")
    w.resolve("cine",1,list(w.facts["cine"]));assert w.home_open,w.log
    go(w,"exit");assert w.stage=="foundation"
    go(w,"home");go(w,"board");go(w,"journal");assert w.stage=="agency"
    return w

def station(w,alternative=False):
    accept(w,"station");go(w,"client");go(w,"schedule");go(w,"guard")
    assert not w.permissions["station"]
    if alternative:
        near(w,"door");w.toggle();go(w,"desk");w.recall()
    else:
        near(w,"witness");w.toggle();go(w,"witness");w.recall()
    go(w,"guard");assert w.permissions["station"],w.log
    go(w,"desk");go(w,"box");go(w,"photo")
    w.resolve("station",2,list(w.facts["station"]));assert w.reports.get("station")=="complete",w.log
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
    near(w,"guest_"+case);w.decide_ally(case,stay)
    assert w.decisions[case]==("stayed" if stay else "departed")

def campaign(stay=False,alternative=False):
    w=station(cinema(World.new_game()),alternative)
    ally(w,"station",stay)
    solve_extra(w,"workshop");ally(w,"workshop",stay)
    solve_extra(w,"ruiz");ally(w,"ruiz",stay)
    solve_extra(w,"archive");solve_extra(w,"final")
    assert set(w.reports)==set(ORDER)
    return w

class Tests(unittest.TestCase):
    def test_maps(self):
        self.assertEqual(len(LEVELS),10)
        self.assertEqual(LEVELS["hospital"].size,(28,18))
        self.assertEqual(LEVELS["station"].size,(42,22))
        for name,l in LEVELS.items():
            self.assertTrue(l.inside(l.spawn),name)
            self.assertFalse(blocked(name,*l.spawn,True),name)
            for k,p in l.points.items():self.assertTrue(l.inside(p),(name,k,p))
        self.assertNotEqual(LEVELS["hospital"].walls,LEVELS["house"].walls)
        self.assertTrue(LEVELS["cine"].walls<=LEVELS["final"].walls)

    def test_no_character_overlap(self):
        w=World.new_game();x,y=w.objects["nurse"][:2]
        for dx,dy in DIRS:
            walk(w,x-dx,y-dy);self.assertFalse(w.move(dx,dy))
            self.assertNotEqual(w.pos,(x,y))

    def test_rafael_explicit_transition(self):
        w=World();go(w,"rafael")
        self.assertEqual(w.place,"office");go(w,"exit");self.assertEqual(w.place,"office")
        w.accept_rafael();go(w,"exit");self.assertEqual(w.place,"street")
        go(w,"rafael");self.assertEqual(w.place,"street")
        go(w,"exit");self.assertEqual(w.place,"cine")

    def test_follow(self):
        w=prologue(World());go(w,"brizna")
        rng=random.Random(42);steps=0
        for _ in range(150):
            dx,dy=rng.choice(DIRS)
            if w.move(dx,dy):steps+=1
            self.assertNotEqual((w.x,w.y),(w.gx,w.gy))
            self.assertNotIn((w.gx,w.gy),occupied(w.objects))
            self.assertLessEqual(w.distance,2)
        self.assertGreaterEqual(steps,30)
        w.toggle();w.recall();self.assertEqual(w.distance,1)

    def test_spirit_range(self):
        w=prologue(World());go(w,"brizna");near(w,"radio");w.toggle()
        a,b=w.anchor
        points=[(x,y) for x in range(1,37) for y in range(1,25) if distance((x,y),(a,b))==5]
        for x,y in points:
            try:walk(w,x,y);break
            except AssertionError:continue
        self.assertEqual(w.distance,5)
        w.spirit.stability=1;w.tick(1)
        self.assertFalse(w.ghost_mode);self.assertEqual(w.distance,1)
        self.assertEqual(w.spirit.stability,20)

    def test_context(self):
        w=World.new_game();near(w,"nurse")
        self.assertEqual(w.interaction("nurse"),("Hablar",True))
        self.assertFalse(w.interaction(None)[1])
        w=prologue(World());go(w,"brizna");near(w,"radio")
        self.assertFalse(w.power_action("radio")[1]);w.toggle();near(w,"radio")
        self.assertEqual(w.power_action("radio"),("Vibrar",True))

    def test_alert_and_recovery(self):
        w=prologue(World());practice(w)
        guard=w.objects["guard"][:2]
        w.stimulus((1,1),"noise")
        self.assertLessEqual(w.alert_value("guard"),10)
        w.alert_state("guard")["facing"]=[-1,0]
        w.stimulus((guard[0]-1,guard[1]),"noise")
        self.assertEqual(w.alert_value("guard"),28)
        for _ in range(3):w.stimulus((guard[0]-1,guard[1]),"noise")
        self.assertGreaterEqual(w.alert_value("guard"),75)
        self.assertFalse(w.access())
        w.permissions["cine"]=True
        for _ in range(25):w.tick(1)
        self.assertLess(w.alert_value("guard"),50);self.assertTrue(w.access())

    def test_los_and_ghost_walk(self):
        l=LEVELS["cine"];self.assertFalse(sight(l,(24,10),(26,10)))
        w=prologue(World());practice(w);w.toggle()
        v=w.alert_value("guard")
        for dx,dy in DIRS:w.move(dx,dy)
        self.assertEqual(w.alert_value("guard"),v)

    def test_office_safe(self):
        w=cinema(World());self.assertIsNone(w.anchor);w.toggle()
        walk(w,28,20);w.spirit.energy=20;w.spirit.stability=20;w.tick(1)
        self.assertGreater(w.spirit.energy,20);self.assertGreater(w.spirit.stability,20)
        self.assertFalse(w.alert_enabled())

    def test_complete_with_allies(self):
        w=campaign(True)
        self.assertEqual(set(w.spirits),{"Brizna","Mateo","Nico","Mora"})
        w.choose_ending("archivo","agencia");self.assertEqual(w.ending,"agencia")

    def test_complete_without_allies_alternate_route(self):
        w=campaign(False,True)
        self.assertEqual(list(w.spirits),["Brizna"])
        w.choose_ending("traslado","explorar");self.assertEqual(w.ending,"explorar")

    def test_save(self):
        w=prologue(World());practice(w);w.alert_state("guard")["value"]=43
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"save.json";w.save(p);loaded=World.load(p)
            self.assertEqual(w,loaded)

    def test_wrong_hypothesis(self):
        w=prologue(World());practice(w);go(w,"client")
        w.resolve("cine",0,["request"]);self.assertEqual(w.reports["cine"],"provisional")
        self.assertFalse(w.home_open)

if __name__=="__main__":unittest.main()
