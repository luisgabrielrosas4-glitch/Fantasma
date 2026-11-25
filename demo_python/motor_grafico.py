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
from niveles import LEVELS, occupied
from arte import character

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

def paint_prop(s,x,y,w,h,kind):
    x,y,w,h=x*TILE,y*TILE,w*TILE,h*TILE
    if kind=="seats":
        for px in range(x,x+w,TILE):seat(s,px,y)
    elif kind=="bench":
        wood(s,x+2,y+3,w-4,h-6,"#68838a")
        for px in range(x+5,x+w-5,12):rect(s,"#9fb0aa",px,y+4,2,h-9)
    elif kind=="bed":
        rect(s,"#344452",x+2,y+3,w-4,h-4)
        rect(s,"#9cbdc0",x+5,y+2,w-10,h-7)
        rect(s,"#e4e5d4",x+7,y+4,w-14,10)
        rect(s,"#597d91",x+7,y+16,w-14,h-24)
        for px in range(x+7,x+w-7,7):rect(s,"#7597a5",px,y+17,1,h-27)
        rect(s,"#d0d7cc",x+2,y+1,w-4,3)
    elif kind=="monitor":
        wood(s,x+5,y+4,w-10,h-8,"#8ea8a4")
        rect(s,"#243c46",x+8,y+6,w-16,h-20)
        pts=[(x+9,y+19),(x+15,y+19),(x+20,y+12),(x+24,y+25),(x+30,y+19),(x+w-10,y+19)]
        pg.draw.lines(s,"#a8e4ad",False,pts,1)
    elif kind=="curtain":
        rect(s,"#90b6bb",x,y+4,w,6)
        for px in range(x,x+w,6):rect(s,"#d0ddd7",px,y+4,2,6)
    elif kind in ("shelf","lockers","wardrobe"):
        if kind=="shelf":
            for py in range(y,y+h,TILE):shelf(s,x+1,py+1,w-2,py+x)
        else:
            wood(s,x+1,y+1,w-2,h-2,"#748c89" if kind=="lockers" else "#93715e")
            for px in range(x+4,x+w-4,10):
                rect(s,"#4b505a",px,y+4,1,h-9);rect(s,"#c9bb96",px+3,y+h//2,3,2)
    elif kind in ("desk","table","counter","tools","projector","machine","pallet","cart"):
        color={"machine":"#6d8585","tools":"#8d7961","projector":"#666578","counter":"#a3b2ae","pallet":"#9c7b59","cart":"#6b777e"}.get(kind,"#aa8464")
        wood(s,x+1,y+1,w-2,h-2,color)
        for i in range(x+6,x+w-5,18):
            if kind=="machine":
                ellipse(s,"#293d45",i,y+5,13,12);ellipse(s,"#a1b1a4",i+3,y+8,7,6)
            elif kind=="tools":
                line(s,"#d4c6ab",(i,y+6),(i+9,y+13),2);ellipse(s,"#49555a",i,y+4,6,5)
            elif kind=="projector":
                rect(s,"#343644",i,y+5,13,10);ellipse(s,"#9aaca8",i+9,y+7,6,5)
            else:
                rect(s,"#d5c4a5",i,y+5,9,6);line(s,"#907660",(i+1,y+8),(i+7,y+8))
    elif kind=="sofa":
        rect(s,"#513c47",x+1,y+1,w-2,h-2);rect(s,"#a16a70",x+4,y+3,w-8,h-7)
        rect(s,"#c08b87",x+4,y+3,w-8,5)
        for px in range(x+8,x+w-5,18):line(s,"#704b59",(px,y+9),(px,y+h-6))
    elif kind=="screen":
        rect(s,"#2d2735",x,y,w,h)
        rect(s,"#e0d6c4",x+4,y+3,w-8,h-7)
        rect(s,"#845063",x,y,4,h);rect(s,"#845063",x+w-4,y,4,h)
    elif kind=="garden":
        rect(s,"#536e59",x,y,w,h)
        for py in range(y+3,y+h-3,11):
            for px in range(x+4,x+w-3,13):rect(s,"#78966a",px,py,3,2)
    elif kind=="fountain":
        ellipse(s,"#b4aaa0",x+3,y+3,w-6,h-6);ellipse(s,"#709fa4",x+8,y+8,w-16,h-16)
        ellipse(s,"#ccd8c9",x+w//2-6,y+h//2-6,12,12)
    elif kind=="plant":
        rect(s,"#ae7655",x+w//2-5,y+h-11,10,8)
        poly(s,"#729e72",[(x+w//2,y+2),(x+3,y+8),(x+w//2-3,y+h-8),(x+w-3,y+7)])
    elif kind=="coat":
        line(s,"#bba288",(x+w//2,y+2),(x+w//2,y+h-2),2)
        poly(s,"#997c62",[(x+6,y+5),(x+w-6,y+5),(x+w-4,y+h-3),(x+4,y+h-3)])
    elif kind=="lamp":
        rect(s,"#676b70",x+11,y,3,h);ellipse(s,"#e5cb8d",x+6,y+1,14,7)
    elif kind=="crosswalk":
        for px in range(x+2,x+w-2,13):rect(s,"#92928e",px,y+4,7,h-8)
    elif kind=="tracks":
        for py in (y+6,y+h-8):rect(s,"#9e9990",x,py,w,3)
        for px in range(x,x+w,13):rect(s,"#786b60",px,y+2,4,h-4)
    elif kind=="tape":
        for py in range(y,y+h,6):rect(s,"#d6b65d",x+6,py,12,3)

def build_map(place):
    l=LEVELS[place];mw,mh=l.size;ww,hh=mw*TILE,mh*TILE
    s=pg.Surface((ww,hh));theme=l.theme
    colors={"hospital":("#617e88","#a4b2b0","#394f5a"),"house":("#856a54","#b39170","#51424a"),
            "street":("#424b57","#727e86","#563d42"),"cine":("#624453","#a06972","#382b3c"),
            "office":("#80674f","#b39a76","#493846"),"station":("#5a7078","#91a39e","#364652"),
            "workshop":("#69746e","#a4a28e","#45494d"),"ruiz":("#8c7560","#b9a182","#57464b"),
            "archive":("#6c5e53","#a99a7c","#3c3544")}
    floor,hi,wall=colors[theme];rng=random.Random(place);s.fill(wall)
    for y in range(1,mh-1):
        for x in range(1,mw-1):
            px,py=x*TILE,y*TILE
            c=blend(floor,hi,rng.random()*.24)
            if theme=="street":c=blend("#333c48" if y>=11 else "#747981",hi,rng.random()*.08)
            rect(s,c,px,py,TILE,TILE)
            if theme in ("house","office"):
                for yy in (0,8,16):
                    line(s,wall,(px,py+yy),(px+23,py+yy))
                    line(s,blend(floor,hi,.4),(px+2,py+yy+2),(px+20,py+yy+2))
            else:
                line(s,blend(floor,wall,.36),(px,py),(px+23,py))
                line(s,blend(floor,wall,.36),(px,py),(px,py+23))
            for _ in range(2):rect(s,blend(floor,hi,.19),px+rng.randrange(2,21),py+rng.randrange(2,21),2,1)
    # El trazado de muros, no la paleta, determina la arquitectura.
    for x,y in sorted(l.walls):
        px,py=x*TILE,y*TILE
        rect(s,"#282735",px,py,TILE,TILE)
        rect(s,wall,px+1,py+1,TILE-3,TILE-4)
        rect(s,hi,px+1,py+1,TILE-3,2)
        if theme=="street":
            for yy in (6,12,18):
                line(s,"#372c38",(px,py+yy),(px+23,py+yy))
                line(s,"#372c38",(px+(x+y+yy)%17,py+yy-5),(px+(x+y+yy)%17,py+yy))
    if theme=="street":
        rect(s,"#302734",10*TILE,2*TILE,17*TILE,2*TILE)
        rect(s,"#b89a70",10*TILE+4,2*TILE+4,17*TILE-8,2*TILE-8)
        font=pg.font.Font(None,34)
        s.blit(font.render("CINE AURORA",True,"#523943"),(15*TILE,2*TILE+10))
        for x in (4,7,29):rect(s,"#3c4650",x*TILE,4*TILE,2*TILE,2*TILE)
        line(s,"#c2b8a0",(TILE,11*TILE),(ww-TILE,11*TILE),2)
    for prop in l.props:paint_prop(s,*prop[:5])
    if place=="final":
        for x in range(26,36):
            rect(s,"#d0b15f",x*TILE,6*TILE+5,12,3)
    # Señalética pequeña, diferente por habitación.
    font=pg.font.Font(None,16)
    for x,y,w,h,name in l.regions:
        if theme=="street" and y==1:continue
        label=font.render(name,False,"#e2d7c1")
        p=label.get_rect(topleft=(x*TILE+5,y*TILE+3))
        rect(s,"#32343b",p.x-2,p.y-1,p.w+4,p.h+2);s.blit(label,p)
    for x,y in l.doors:
        rect(s,"#b99c75",x*TILE,y*TILE,TILE,2)
    return s

def light_mask(place):
    l=LEVELS[place];ww,hh=l.size[0]*TILE,l.size[1]*TILE
    small=pg.Surface((max(1,ww//8),max(1,hh//8)))
    lights=[((x+w/2)*TILE,(y+h/2)*TILE,max(w,h)*TILE*.72) for x,y,w,h,_ in l.regions]
    ambient=150 if l.theme in ("hospital","house","office") else 122
    for y in range(small.get_height()):
        for x in range(small.get_width()):
            val=ambient
            for lx,ly,r in lights:
                d=math.hypot(x*8-lx,y*8-ly)
                if d<r:val+=65*(1-d/r)
            v=min(255,int(val));small.set_at((x,y),(v,min(255,v+4),min(255,v+12)))
    return pg.transform.smoothscale(small,(ww,hh))

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
    return character(name,ghost,direction,frame,weak)

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

class PairMotion:
    """Interpolación visual de un paso. El intercambio usa un rodeo lateral."""
    def __init__(self):
        self.last=None;self.old=None;self.new=None;self.elapsed=0.;self.side=0
    def update(self,w,dt):
        if not w.companion_present or w.ghost_mode or w.place=="office":
            self.last=None
            return {}
        pair=((w.x,w.y),(w.gx,w.gy))
        if self.last is None or dt==0:
            self.last=pair;self.old=self.new=pair;self.elapsed=.12
        elif pair!=self.last:
            self.old,self.new=self.last,pair;self.last=pair;self.elapsed=0.
            self.side=0
            h,g=self.old;nh,ng=self.new
            if nh==g and ng==h:
                dx,dy=nh[0]-h[0],nh[1]-h[1]
                l=LEVELS[w.place];taken=occupied(w.objects)
                for side in (1,-1):
                    offset=(-dy*side,dx*side)
                    cells=[(p[0]+offset[0],p[1]+offset[1]) for p in (h,nh)]
                    if all(l.inside(p) and p not in taken for p in cells):
                        self.side=side;break
            if abs(nh[0]-h[0])+abs(nh[1]-h[1])>1 or abs(ng[0]-g[0])+abs(ng[1]-g[1])>2:
                self.old=self.new;self.elapsed=.12
        self.elapsed=min(.12,self.elapsed+dt)
        t=self.elapsed/.12
        h,g=self.old;nh,ng=self.new
        pos=lambda a,b:tuple(a[i]+(b[i]-a[i])*t for i in (0,1))
        hx,hy=pos(h,nh);gx,gy=pos(g,ng)
        alpha=255
        if nh==g and ng==h and h!=nh:
            dx,dy=nh[0]-h[0],nh[1]-h[1]
            arc=math.sin(math.pi*t)
            if self.side:
                gx-=dy*self.side*arc;gy+=dx*self.side*arc
                alpha=round(255-55*arc)
            else:alpha=round(255*(1-arc))
        return {"human":(hx,hy,255),"companion":(gx,gy,alpha)}

class Motor:
    def __init__(self):
        self.maps={};self.lights={};self.sprites={};self.props={};self.motions={}
        self.place=None;self.time=0.;self.background_builds=0
        self.scene=pg.Surface((W,H))
        self.camera=(0.,0.)
        self.view=pg.Surface((W,H))
        self.route_key=None;self.route=[]
        self.aura=glow(24,(20,61,48))
        self.lamp=glow(38,(55,36,12))
        self.font=pg.font.Font(None,14)
        self.name_font=pg.font.Font(None,24)
        self.pair=PairMotion();self.pair_positions={};self.native_actors=[]
        self.native=False
        self.actor_scaled={}
        self.label_rects=[]
    def reset_motion(self):self.motions.clear();self.pair=PairMotion()
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
        # La posición de dibujo nunca queda en la casilla liberada de otra entidad.
        px,py=x,y
        return round(px*TILE+TILE/2),round(py*TILE+TILE/2),m
    def actor(self,identity,x,y,name,ghost,dt,weak=False,active=False):
        cx,cy,m=self.position(identity,x,y,dt)
        alpha=255
        slot="human" if identity.startswith("human") else "companion" if identity.startswith("companion") else None
        if slot in self.pair_positions:
            px,py,alpha=self.pair_positions[slot];cx,cy=round(px*TILE+12),round(py*TILE+12)
        ellipse(self.scene,"#292735",cx-8,cy+5,16,6)
        if active:pg.draw.ellipse(self.scene,MINT if ghost else "#ddbb83",(cx-11,cy+2,22,11),1)
        if ghost:cy+=round(math.sin(self.time*4+len(name))*2)
        frame=(int(self.time*3)%2 if ghost else int(m.phase)%4 if m.moving else 0)
        sprite=self.get_sprite(name,ghost,m.direction,frame,weak)
        if self.native:self.native_actors.append((cx,cy,sprite,ghost,name,alpha))
        else:self.scene.blit(pg.transform.scale(sprite,(20,30)),(cx-10,cy-23))
        return cx,cy
    def draw(self,w,dt=0.,target=None,goal=None,native=False):
        dt=max(0.,min(.15,dt));self.time+=dt
        changed=self.place!=w.place
        if changed:self.place=w.place;self.reset_motion()
        self.native=native;self.native_actors=[];self.label_rects=[]
        self.pair_positions=self.pair.update(w,dt)
        self.load_map(w.place)
        bg=self.maps[w.place]
        if self.scene.get_size()!=bg.get_size():self.scene=pg.Surface(bg.get_size())
        self.scene.blit(bg,(0,0))
        maxx,maxy=max(0,bg.get_width()-W),max(0,bg.get_height()-H)
        cx=min(maxx,max(0,w.pos[0]*TILE+12-W/2));cy=min(maxy,max(0,w.pos[1]*TILE+12-H/2))
        if changed or dt==0:self.camera=(cx,cy)
        else:self.camera=tuple(v+(t-v)*min(1,dt*12) for v,t in zip(self.camera,(cx,cy)))
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
                if w.ghost_mode==ghost:labels.append((cx,cy-26,name,ghost))
                if ghost:glows.append((cx,cy-5))
            else:
                x,y,name,kind=o;cx,cy=x*TILE+12,y*TILE+12
                if kind in ("npc","ghost"):
                    name=name.split(",")[0]
                    if k=="wish":
                        if w.active=="Brizna":
                            self.scene.blit(self.get_prop("home",k,False),(cx-16,cy-20));continue
                    cx,cy=self.actor(k,x,y,name,kind=="ghost",dt,k=="guest" and not w.guest_decision)
                    if k==target or k==goal:labels.append((cx,cy-32 if k==goal else cy-26,name,kind=="ghost"))
                    if kind=="npc" and w.alert_value(k)>=25:
                        c="#ed9c7b" if w.alert_value(k)>=75 else "#e3c175"
                        rect(self.scene,c,cx-7,cy+10,round(14*w.alert_value(k)/100),2)
                    if kind=="ghost":glows.append((cx,cy-5))
                else:
                    opened=(w.access() or w.distracted>0) if kind=="door" else False
                    self.scene.blit(self.get_prop(kind,k,opened),(cx-16,cy-20))
        # Puertas adicionales comparten la misma regla y su aspecto visible.
        for dx,dy in LEVELS[w.place].doors:
            if w.objects.get("door",(-1,-1))[:2]==(dx,dy):continue
            self.scene.blit(self.get_prop("door","extra",w.access() or w.distracted>0),(dx*TILE-4,dy*TILE-8))
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
        placed=[]
        for cx,cy,name,ghost in ([] if native else labels):
            text=self.font.render(name,False,MINT if ghost else "#efdec3")
            p=text.get_rect(midbottom=(cx,max(11,cy)))
            while any(p.inflate(4,4).colliderect(q) for q in placed):p.y-=text.get_height()+4
            if p.top<0:continue
            placed.append(p.copy())
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
        if goal in w.objects:
            key=(w.place,w.pos,goal,w.ghost_mode,w.anchor,w.access(),w.distracted>0,tuple((k,o[:2]) for k,o in w.objects.items()))
            if key!=self.route_key:self.route_key=key;self.route=w.route_to(goal)
            for x,y in self.route[1:]:
                pg.draw.circle(self.scene,"#c8aa73",(x*TILE+12,y*TILE+12),2)
        self.view.fill("#282633")
        ox,oy=map(round,self.camera)
        self.view.blit(self.scene,(0,0),pg.Rect(ox,oy,W,H))
        if goal in w.objects:
            gx,gy=w.objects[goal][:2];px,py=gx*TILE+12-ox,gy*TILE+12-oy
            if not (12<=px<W-12 and 12<=py<H-12):
                ex,ey=max(12,min(W-12,px)),max(12,min(H-12,py))
                pg.draw.circle(self.view,"#e8c589",(round(ex),round(ey)),7)
                pg.draw.circle(self.view,"#584333",(round(ex),round(ey)),3)
        if not native:return self.view
        # Los sprites y nombres se componen después de ampliar los tiles.
        output=pg.transform.scale(self.view,(W*2,H*2))
        for cx,cy,sprite,ghost,name,alpha in self.native_actors:
            size=(36,54) if ghost else (42,63)
            k=(id(sprite),size)
            if k not in self.actor_scaled:self.actor_scaled[k]=pg.transform.scale(sprite,size)
            im=self.actor_scaled[k].copy()
            if not ghost:
                lx=max(0,min(self.lights[w.place].get_width()-1,cx))
                ly=max(0,min(self.lights[w.place].get_height()-1,cy))
                light=self.lights[w.place].get_at((lx,ly))
                im.fill(tuple(min(255,int(v*.55+115)) for v in light[:3])+(255,),special_flags=pg.BLEND_RGBA_MULT)
            if alpha<255:im.set_alpha(alpha)
            px,py=(cx-ox)*2,(cy-oy)*2
            output.blit(im,(px-size[0]//2,py-size[1]+12))
        for cx,cy,name,ghost in labels:
            px,py=(cx-ox)*2,(cy-oy)*2
            if not (0<=px<W*2 and -8<=py<H*2):continue
            im=self.name_font.render(name,True,MINT if ghost else "#f4e4ce")
            r=im.get_rect(midbottom=(px,py))
            r.x=max(4,min(W*2-r.w-4,r.x))
            while any(r.inflate(10,6).colliderect(q) for q in self.label_rects):r.y-=r.h+7
            if r.top<4:continue
            self.label_rects.append(r.copy())
            bg=pg.Surface((r.w+10,r.h+6),pg.SRCALPHA)
            pg.draw.rect(bg,(25,25,37,220),bg.get_rect(),border_radius=5)
            output.blit(bg,(r.x-5,r.y-3));output.blit(im,r)
        return output
