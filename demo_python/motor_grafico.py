"""Motor de prototipado 2D en Python/Pygame-ce.

Arte procedural original a resolución nativa de píxel. No contiene reglas de
investigación. Los mapas, sprites y máscaras de luz pueden exportarse a PNG.
"""
import math
import random
from dataclasses import dataclass
import pygame as pg
from modelo import WIDTH, HEIGHT, WALLS, FURNITURE, CASES
from campana import THEMES

TILE=24
W,H=WIDTH*TILE,HEIGHT*TILE
MINT="#a7e9d3"
PALETTES={
 "cine":("#51404a","#634852","#312837","#9c7770","#b88876"),
 "office":("#6b5143","#80644c","#382d36","#b08a68","#c6a57f"),
 "station":("#485762","#596973","#263641","#86938e","#b8a88a"),
}
LIGHTS={
 "cine":[(52,40,90,(255,183,117)),(190,86,100,(231,170,126)),(390,62,95,(233,180,120))],
 "office":[(105,62,115,(255,211,143)),(290,108,135,(246,190,130)),(420,66,98,(184,216,180))],
 "station":[(70,60,100,(203,221,216)),(244,114,95,(251,195,129)),(404,70,105,(193,220,218))],
}

def rgb(c):return pg.Color(c)
def blend(a,b,t):
    a,b=rgb(a),rgb(b)
    return tuple(round(x+(y-x)*t) for x,y in zip(a[:3],b[:3]))

def rect(s,c,x,y,w,h):
    if w>0 and h>0:pg.draw.rect(s,c,(int(x),int(y),int(w),int(h)))
def line(s,c,a,b,width=1):pg.draw.line(s,c,a,b,width)
def poly(s,c,pts):pg.draw.polygon(s,c,pts)
def ellipse(s,c,x,y,w,h):pg.draw.ellipse(s,c,(int(x),int(y),int(w),int(h)))

def wood(s,x,y,w,h,color="#997457"):
    rect(s,"#312733",x+2,y+3,w,h)
    rect(s,"#4e3940",x,y,w,h)
    rect(s,color,x+1,y+1,w-2,h-4)
    rect(s,"#c5a07a",x+2,y+1,w-4,1)
    rect(s,"#755144",x+2,y+h-4,w-4,2)
    for i in range(3,w-3,7):line(s,"#82604e",(x+i,y+3),(x+i+2,y+h-5))

def rug(s,x,y,w,h,base,edge):
    rect(s,"#372c39",x+2,y+3,w,h)
    rect(s,edge,x,y,w,h);rect(s,base,x+2,y+2,w-4,h-4)
    pg.draw.rect(s,edge,(x+4,y+4,w-8,h-8),1)
    for i in range(x+8,x+w-7,8):
        poly(s,edge,[(i,y+5),(i+2,y+7),(i,y+9),(i-2,y+7)])
        poly(s,edge,[(i,y+h-10),(i+2,y+h-8),(i,y+h-6),(i-2,y+h-8)])
    for j in range(y+12,y+h-10,12):
        for i in range(x+12,x+w-10,15):rect(s,blend(base,edge,.30),i,j,2,2)

def shelf(s,x,y,w,seed=1):
    rng=random.Random(seed)
    wood(s,x,y,w,20,"#89634e")
    rect(s,"#392f3b",x+3,y+3,w-6,12)
    for i in range(x+4,x+w-5,5):
        h=rng.randrange(6,12)
        c=rng.choice(["#b87b71","#829b8d","#b7a56e","#897b9d","#cead8d"])
        rect(s,c,i,y+15-h,4,h);rect(s,"#d1b68c",i,y+15-h+2,4,1)
    rect(s,"#ba9270",x+1,y+15,w-2,2)

def seat(s,x,y,station=False):
    c="#64848a" if station else "#995764"
    hi="#9eb0a5" if station else "#ce8390"
    ellipse(s,"#302b36",x+1,y+13,22,8)
    rect(s,"#40313b",x+1,y+3,22,16)
    rect(s,c,x+3,y+2,18,11)
    rect(s,hi,x+3,y+2,18,2)
    rect(s,blend(c,"#2d2936",.28),x+4,y+10,16,7)
    rect(s,"#ac927c",x+1,y+7,3,10);rect(s,"#ac927c",x+20,y+7,3,10)

def build_map(place):
    s=pg.Surface((W,H))
    actual=place
    place=THEMES.get(place,place)
    floor,alternate,wall,trim,highlight=PALETTES[place]
    s.fill(wall)
    rng=random.Random({"cine":13,"office":43,"station":71}[place])
    for y in range(1,HEIGHT-1):
        for x in range(1,WIDTH-1):
            px,py=x*TILE,y*TILE
            rect(s,blend(floor,alternate,rng.random()*.55),px,py,TILE,TILE)
            if place=="office":
                for j in (0,8,16):
                    line(s,floor,(px,py+j),(px+23,py+j))
                    joint=(x*7+y*5+j)%21
                    line(s,floor,(px+joint,py+j),(px+joint,py+j+7))
                    rect(s,blend(floor,highlight,.21),px+2,py+j+2,12,1)
            else:
                line(s,wall,(px,py),(px+23,py))
                line(s,wall,(px,py),(px,py+23))
                line(s,blend(floor,highlight,.35),(px+1,py+1),(px+22,py+1))
                for _ in range(3):rect(s,alternate,px+rng.randrange(2,20),py+rng.randrange(3,21),2,1)
    # Perimeter moulding and windows with mullions, exterior rain streaks.
    rect(s,wall,0,0,W,24)
    rect(s,trim,0,17,W,4);rect(s,highlight,0,17,W,1)
    for x in (26,126,273,396):
        rect(s,"#211f2d",x,1,42,17)
        rect(s,"#686f83" if place!="office" else "#80777c",x+3,3,36,12)
        for j in (8,20,32):rect(s,"#a1a5af",x+j,4,1,8)
        rect(s,wall,x+20,2,2,14);rect(s,wall,x+2,8,38,2)
        rect(s,trim,x-2,15,46,3)
    if place=="cine":
        rug(s,74,132,99,89,"#714653","#b07980")
        # Projection screen, velvet curtains and seats.
        rect(s,"#2e2735",44,26,139,23)
        rect(s,"#c5bbad",50,28,126,15)
        rect(s,"#83726e",50,42,126,2)
        for x in (34,178):
            rect(s,"#673747",x,25,16,31)
            for j in (1,5,9,13):rect(s,"#9b5968",x+j,25,2,26)
        shelf(s,272,26,58,11);shelf(s,397,26,54,12)
        shelf(s,420,206,34,14)
    elif place=="office":
        rug(s,114,128,115,75,"#765768","#c4a07a")
        shelf(s,25,26,56,15);shelf(s,257,26,74,16);shelf(s,383,26,62,17)
        # Meeting table on its exact physical footprint.
        wood(s,6*TILE+2,6*TILE+3,3*TILE-4,2*TILE-6,"#a48261")
        rect(s,"#e4d1ae",159,154,12,9);rect(s,"#6e877c",187,155,9,7)
        rect(s,"#c6b6a1",167,169,8,8);rect(s,"#55434a",180,178,20,4)
        for x,y in ((27,49),(449,53),(437,212)):
            rect(s,"#ad7656",x,y+15,12,8)
            poly(s,"#6c9473",[(x+6,y+17),(x,y+5),(x+5,y+9),(x+7,y),(x+10,y+11),(x+15,y+4),(x+12,y+17)])
            rect(s,"#9ab68a",x+5,y+4,2,11)
    else:
        rug(s,28,111,112,70,"#4c626a","#879b91")
        shelf(s,271,26,64,18);shelf(s,395,26,55,19)
        rect(s,"#28363e",24,HEIGHT*TILE-24,W-48,9)
        rect(s,"#c4ac70",24,HEIGHT*TILE-24,W-48,2)
        for x in range(26,W-28,12):rect(s,"#7b7364",x,HEIGHT*TILE-16,6,1)
        # Clock in the non-walkable wall strip.
        ellipse(s,"#bfaa83",230,2,17,17);ellipse(s,"#dad1b7",232,4,13,13)
        line(s,"#5e5254",(238,10),(238,5));line(s,"#5e5254",(238,10),(242,12))
    for x,y in sorted(FURNITURE[actual]):
        if place!="office":seat(s,x*TILE,y*TILE,place=="station")
    if actual in CASES:
        for x,y in sorted(WALLS):
            px,py=x*TILE,y*TILE
            rect(s,"#211f2b",px+4,py+2,20,24)
            rect(s,wall,px,py,18,24)
            rect(s,alternate,px+2,py+2,14,8)
            rect(s,floor,px+2,py+13,14,9)
            rect(s,trim,px,py,2,24);rect(s,"#272331",px+17,py,3,24)
            rect(s,highlight,px+2,py+2,12,1)
    return s

def light_mask(place):
    # Cached low-resolution radial illumination; multiply after drawing actors.
    small=pg.Surface((W//4,H//4))
    for y in range(small.get_height()):
        for x in range(small.get_width()):
            px,py=x*4,y*4
            values=[118.,119.,140.]
            for lx,ly,radius,color in LIGHTS[THEMES.get(place,place)]:
                d=math.hypot(px-lx,py-ly)
                if d<radius:
                    f=(1-d/radius)**1.45
                    for i in range(3):values[i]+=color[i]*.68*f
            edge=min(1.,min(px,py,W-1-px,H-1-py)/28)
            small.set_at((x,y),tuple(max(0,min(255,int(v*(.78+.22*edge)))) for v in values))
    return pg.transform.smoothscale(small,(W,H))

def glow(radius,color):
    s=pg.Surface((radius*2+1,radius*2+1))
    for y in range(s.get_height()):
        for x in range(s.get_width()):
            d=math.hypot(x-radius,y-radius)/radius
            if d<1:
                f=(1-d)**2
                s.set_at((x,y),tuple(int(c*f) for c in color))
    return s

def actor_sprite(name,ghost,direction="down",frame=0,weak=False):
    """24x38 pixel sprite: silhouette, shaded clothing, directional walk."""
    s=pg.Surface((24,38),pg.SRCALPHA)
    if ghost:
        brizna=name=="Brizna"
        dark="#44766f" if brizna else "#5f7297"
        mid="#82c9b7" if brizna else ("#92aed8" if name=="Mateo" else "#b4a0cf")
        light="#d0f9df" if brizna else "#dbe2f8"
        if weak:mid=blend(mid,"#555e69",.45);light=blend(light,"#68717a",.45)
        tail=frame%2
        poly(s,dark,[(4,27),(3,16),(6,9),(10,6),(14,6),(19,10),(21,17),(20,27),(17,30),(13,27+tail),(8,31-tail)])
        poly(s,mid,[(5,25),(5,15),(8,9),(13,8),(18,12),(20,17),(18,26),(15,28),(12,25+tail),(8,29-tail)])
        poly(s,light,[(6,15),(8,10),(12,9),(15,10),(10,11),(8,16),(8,22),(6,23)])
        if brizna:
            poly(s,dark,[(7,9),(6,4),(11,7),(14,1),(17,9)])
            poly(s,mid,[(9,8),(8,5),(12,8),(14,3),(16,8)])
            rect(s,light,14,4,1,3)
        else:
            rect(s,mid,8,24,8,5);rect(s,dark,9,25,6,1)
            if name=="Elena":rect(s,"#c6add7",5,10,3,12)
        if direction!="up":
            eyes= (7,13) if direction=="left" else ((10,16) if direction=="right" else (8,15))
            for ex in eyes:rect(s,"#304651",ex,16,2,4);rect(s,light,ex,16,1,1)
            rect(s,"#537c7b",11,23,3,1)
        rect(s,light,5,21,1,3)
        return s
    # Detective and townspeople. Four directions, asymmetric highlights.
    coat="#b38b65" if name=="Tomás" else ("#829e9b" if name=="Inés" else "#7a8b9d")
    shade=blend(coat,"#3b3443",.45)
    hi=blend(coat,"#eed7b4",.35)
    skin="#d9ae90";shadow="#a87869";hair="#4b3840";ink="#302b39"
    step=(0,-2,0,2)[frame%4]
    rect(s,ink,7,28+max(0,step),5,7- max(0,step));rect(s,ink,13,28+max(0,-step),5,7-max(0,-step))
    rect(s,"#56606c",8,28+max(0,step),3,5-max(0,step));rect(s,"#56606c",14,28+max(0,-step),3,5-max(0,-step))
    rect(s,"#201e29",6,34,6,3);rect(s,"#201e29",13,34,6,3)
    poly(s,ink,[(5,17),(9,14),(16,14),(20,17),(22,27),(18,29),(19,31),(5,31),(6,27),(2,27)])
    poly(s,coat,[(6,18),(10,16),(15,16),(19,18),(20,26),(17,26),(18,30),(6,30),(7,26),(4,26)])
    rect(s,shade,6,23,2,6);rect(s,shade,16,22,2,8)
    rect(s,hi,7,18,2,4);rect(s,hi,17,18,1,4)
    if direction!="up":
        poly(s,"#e4d4b9",[(10,16),(15,16),(12,23)])
        poly(s,shade,[(9,17),(12,23),(9,25),(10,20)])
        poly(s,shade,[(16,17),(13,23),(16,25),(15,20)])
        rect(s,"#5e4d49",12,24,1,6)
        for yy in (25,28):rect(s,"#dfc09b",13,yy,1,1)
    else:line(s,shade,(12,18),(12,29))
    rect(s,shadow,3,25,3,3);rect(s,skin,19,25,2,3)
    poly(s,ink,[(6,4),(9,1),(16,1),(19,5),(19,12),(16,16),(8,16),(5,12)])
    poly(s,skin,[(7,5),(17,5),(18,9),(17,13),(15,15),(9,15),(7,12)])
    rect(s,shadow,8,13,8,2)
    rect(s,hair,6,3,12,4)
    rect(s,"#76554e",8,2,7,2)
    if name=="Tomás":
        # Greying temples and long coat make the retired detective recognizable.
        rect(s,"#a0998d",6,7,2,4);rect(s,"#a0998d",16,7,2,4)
    if direction=="up":rect(s,hair,7,5,11,9);rect(s,"#76554e",8,5,9,2)
    else:
        eyes=(8,13) if direction=="left" else ((10,15) if direction=="right" else (9,15))
        for ex in eyes:rect(s,ink,ex,9,2,2)
        rect(s,shadow,11,11,2,2)
        rect(s,"#815f5d",10,13,4,1)
    return s

def prop_sprite(kind,key,opened=False):
    s=pg.Surface((32,32),pg.SRCALPHA)
    if kind=="paper":
        wood(s,3,12,26,17)
        rect(s,"#d9c7a3",10,8,13,14)
        rect(s,"#f1e1bd",10,8,12,2)
        for y in (12,15,18):rect(s,"#8f7767",12,y,8,1)
        if key=="photo":rect(s,"#7e8d91",12,11,8,7);rect(s,"#c5a493",15,13,3,4)
        if key=="poster":rect(s,"#a25e6d",11,9,11,4)
    elif kind=="box":
        wood(s,3,6,26,23,"#98765d")
        rect(s,"#624b43",6,14,20,2);rect(s,"#c9ae7b",13,15,6,6)
        rect(s,"#58483d",15,16,2,3);rect(s,"#735247",5,22,22,2)
        rect(s,"#c5a17a",6,9,1,13);rect(s,"#c5a17a",25,9,1,13)
    elif kind=="device":
        wood(s,3,12,26,16,"#997658")
        rect(s,"#3c3442",7,15,14,10)
        for y in (17,20,23):rect(s,"#bca996",8,y,12,1)
        ellipse(s,"#e3c394",23,16,4,4);line(s,"#c4b5ac",(24,11),(28,4))
    elif kind=="door":
        rect(s,"#3a2936",4,2,24,29)
        rect(s,"#6c9580" if opened else "#956a56",7,4,18,25)
        rect(s,"#af9277",9,6,13,1);rect(s,"#5d4844",9,7,1,20)
        rect(s,"#594639",12,10,8,9);rect(s,"#b18d68",13,11,6,7)
        rect(s,"#e5bf79",21,19,3,3)
    elif kind=="home":
        wood(s,3,15,26,14)
        ellipse(s,"#477d75",9,5,14,15);ellipse(s,"#b4ecd7",11,5,10,11)
        rect(s,"#e0ffec",13,7,2,3);rect(s,"#d4a675",10,20,12,2)
    elif kind=="board":
        wood(s,1,3,30,25,"#937657")
        rect(s,"#594352",4,6,24,17)
        for x,y in ((6,8),(18,8),(12,16)):
            rect(s,"#e7d7b6",x,y,7,6);rect(s,"#a78070",x+1,y+2,5,1)
        line(s,"#d58385",(9,9),(21,10));line(s,"#d58385",(21,10),(15,18))
    else:
        rect(s,"#314b47",3,6,26,24);pg.draw.rect(s,"#a5c5a5",(3,6,26,24),1)
        poly(s,"#bce5ca",[(9,18),(19,8),(19,13),(24,13),(24,16),(19,16),(19,22),(15,18),(11,22)])
    return s

@dataclass
class Motion:
    x:float
    y:float
    tx:int
    ty:int
    direction:str="down"
    phase:float=0.
    moving:bool=False
    def advance(self,x,y,dt):
        dx,dy=x-self.tx,y-self.ty
        if abs(dx)+abs(dy)>1:self.x,self.y=float(x),float(y)
        elif dx or dy:self.direction=("right" if dx>0 else "left") if dx else ("down" if dy>0 else "up")
        self.tx,self.ty=x,y
        d=math.hypot(x-self.x,y-self.y)
        self.moving=d>.005
        if self.moving:
            amount=min(1.,dt*10/max(d,.001))
            self.x+=(x-self.x)*amount;self.y+=(y-self.y)*amount
            self.phase+=dt*12
        else:self.x,self.y=float(x),float(y);self.phase=0.
        return self.x,self.y

class Motor:
    def __init__(self):
        self.maps={};self.lights={};self.sprites={};self.props={};self.motions={}
        self.place=None;self.time=0.;self.background_builds=0
        self.scene=pg.Surface((W,H))
        self.aura=glow(24,(20,61,48))
        self.lamp=glow(38,(55,36,12))
        self.font=pg.font.Font(None,14)
    def reset_motion(self):self.motions.clear()
    def load_map(self,place):
        if place not in self.maps:
            self.maps[place]=build_map(place);self.lights[place]=light_mask(place)
            self.background_builds+=1
    def get_sprite(self,name,ghost,direction,frame,weak):
        k=(name,ghost,direction,frame,weak)
        if k not in self.sprites:self.sprites[k]=actor_sprite(*k)
        return self.sprites[k]
    def get_prop(self,kind,key,opened):
        k=(kind,key,opened)
        if k not in self.props:self.props[k]=prop_sprite(*k)
        return self.props[k]
    def position(self,key,x,y,dt):
        if key not in self.motions:self.motions[key]=Motion(x,y,x,y)
        m=self.motions[key]
        px,py=m.advance(x,y,dt)
        return round(px*TILE+TILE/2),round(py*TILE+TILE/2),m
    def actor(self,identity,x,y,name,ghost,dt,weak=False,active=False):
        cx,cy,m=self.position(identity,x,y,dt)
        ellipse(self.scene,"#292735",cx-8,cy+5,16,6)
        if active:pg.draw.ellipse(self.scene,MINT if ghost else "#ddbb83",(cx-11,cy+2,22,11),1)
        if ghost:cy+=round(math.sin(self.time*4+len(name))*2)
        frame=(int(self.time*3)%2 if ghost else int(m.phase)%4 if m.moving else 0)
        sprite=self.get_sprite(name,ghost,m.direction,frame,weak)
        self.scene.blit(sprite,(cx-12,cy-25))
        return cx,cy
    def draw(self,w,dt=0.,target=None,goal=None):
        dt=max(0.,min(.15,dt));self.time+=dt
        if self.place!=w.place:self.place=w.place;self.reset_motion()
        self.load_map(w.place);self.scene.blit(self.maps[w.place],(0,0))
        labels=[];glows=[]
        if w.ghost_mode and w.anchor is not None:
            ax,ay=w.anchor;cx,cy=ax*TILE+12,ay*TILE+12
            radius=w.spirit.radius*TILE
            color="#b98979" if w.distance>w.spirit.radius else "#5b9d8b"
            points=[(cx-radius,cy),(cx,cy-radius),(cx+radius,cy),(cx,cy+radius)]
            for a,b in zip(points,points[1:]+points[:1]):
                for n in range(0,12,2):
                    start=tuple(round(a[i]+(b[i]-a[i])*n/12) for i in (0,1))
                    end=tuple(round(a[i]+(b[i]-a[i])*(n+1)/12) for i in (0,1))
                    line(self.scene,color,start,end)
            line(self.scene,color,(cx,cy),(w.gx*TILE+12,w.gy*TILE+12))
        items=[(o[1],0,k,o) for k,o in w.objects.items()]
        items.append((w.y,1,"human",None))
        if w.companion_present:items.append((w.gy,2,"companion",None))
        for _,layer,k,o in sorted(items,key=lambda row:(row[0],row[1])):
            if layer:
                ghost=layer==2
                name=w.active if ghost else "Tomás"
                x,y=(w.gx,w.gy) if ghost else (w.x,w.y)
                cx,cy=self.actor(k+name,x,y,name,ghost,dt,ghost and w.spirit.stability<40,w.ghost_mode==ghost)
                labels.append((cx,cy-29,name,ghost))
                if ghost:glows.append((cx,cy-5))
            else:
                x,y,name,kind=o;cx,cy=x*TILE+12,y*TILE+12
                if kind in ("npc","ghost"):
                    name=name.split(",")[0]
                    if k=="wish":
                        if w.active=="Brizna":
                            self.scene.blit(self.get_prop("home",k,False),(cx-16,cy-20));continue
                    cx,cy=self.actor(k,x,y,name,kind=="ghost",dt,k=="guest" and not w.guest_decision)
                    labels.append((cx,cy-29,name,kind=="ghost"))
                    if kind=="ghost":glows.append((cx,cy-5))
                else:
                    opened=(w.permissions.get(w.place,False) or w.distracted>0) if kind=="door" else False
                    self.scene.blit(self.get_prop(kind,k,opened),(cx-16,cy-20))
        # Lighting affects the whole scene, then supernatural emission adds glow.
        self.scene.blit(self.lights[w.place],(0,0),special_flags=pg.BLEND_RGB_MULT)
        for cx,cy in glows:
            self.scene.blit(self.aura,(cx-24,cy-24),special_flags=pg.BLEND_RGB_ADD)
            for i in range(3):
                x=round(cx+math.sin(self.time*1.8+i*2.1)*12)
                y=round(cy-5+math.cos(self.time*2+i*2.1)*9)
                rect(self.scene,MINT,x,y,1,2)
        if w.distracted and "radio" in w.objects:
            x,y,*_=w.objects["radio"];cx,cy=x*TILE+12,y*TILE+12
            self.scene.blit(self.lamp,(cx-38,cy-38),special_flags=pg.BLEND_RGB_ADD)
        # Readable names and interaction corners are not darkened.
        for cx,cy,name,ghost in labels:
            text=self.font.render(name,False,MINT if ghost else "#efdec3")
            p=text.get_rect(midbottom=(cx,max(11,cy)))
            rect(self.scene,"#292633",p.x-2,p.y-1,p.w+4,p.h+2)
            self.scene.blit(text,p)
        if goal in w.objects:
            x,y,*_=w.objects[goal];cx=x*TILE+12;cy=y*TILE+12
            py=cy-30+round(math.sin(self.time*5)*2)
            poly(self.scene,"#edc481",[(cx,py),(cx-5,py-7),(cx+5,py-7)])
        if target in w.objects:
            x,y,*_=w.objects[target]
            px,py=x*TILE+1,y*TILE+1
            for a,b in [((px,py+5),(px,py)),((px,py),(px+5,py)),((px+21,py),(px+16,py)),((px+21,py),(px+21,py+5)),((px,py+21),(px,py+16)),((px,py+21),(px+5,py+21)),((px+21,py+21),(px+16,py+21)),((px+21,py+21),(px+21,py+16))]:
                line(self.scene,"#d5f1c9",a,b,2)
        return self.scene
