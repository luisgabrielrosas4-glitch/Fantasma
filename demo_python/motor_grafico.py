"""Motor visual 2D: resolución interna, mapas cacheados y sprites reutilizables.

El modelo conserva las coordenadas enteras y las reglas. El renderizador nunca
mueve personajes ni modifica evidencias, energía o permisos.
"""
import math
import random
import tkinter as tk
from dataclasses import dataclass
from modelo import WIDTH, HEIGHT, WALLS

TILE=32
SCALE=2
PIX=16
W,H=WIDTH*PIX,HEIGHT*PIX

def rgb(value):
    return tuple(int(value[i:i+2],16) for i in (1,3,5))

def mix(a,b,t):
    return tuple(round(x+(y-x)*t) for x,y in zip(a,b))

class Raster:
    """Superficie RGB de baja resolución; se escala sin interpolación."""
    def __init__(self,w=W,h=H,color="#201d2c"):
        self.w,self.h=w,h
        self.data=bytearray(bytes(rgb(color))*(w*h))
    def rect(self,x,y,w,h,color):
        color=rgb(color) if isinstance(color,str) else color
        left,right=max(0,x),min(self.w,x+w)
        if right<=left:return
        row=bytes(color)*(right-left)
        for j in range(max(0,y),min(self.h,y+h)):
            start=(j*self.w+left)*3
            self.data[start:start+len(row)]=row
    def light(self,lights,ambient):
        # Hornea luz de colores una sola vez por escenario.
        for y in range(self.h):
            for x in range(self.w):
                i=(y*self.w+x)*3
                r,g,b=self.data[i:i+3]
                shade=ambient
                add=[0.,0.,0.]
                for lx,ly,radius,tint in lights:
                    d2=(x-lx)**2+(y-ly)**2
                    if d2>=radius*radius:continue
                    f=(1-math.sqrt(d2)/radius)**1.5
                    shade+=f*.30
                    for c in range(3):add[c]+=tint[c]*f
                edge=min(1.,min(x,y,self.w-1-x,self.h-1-y)/18)
                self.data[i:i+3]=bytes(max(0,min(255,round(v*(shade*(.78+.22*edge))+a))) for v,a in zip((r,g,b),add))
    def ppm(self):
        return f"P6\n{self.w} {self.h}\n255\n".encode("ascii")+bytes(self.data)

PALETTES={
 "cine":("#51404b","#66505a","#352a3d","#8b666c"),
 "office":("#665344","#886e58","#3a3038","#a6886b"),
 "station":("#485a62","#62747b","#2c3845","#87979a"),
}
LIGHTS={
 "cine":[(65,36,83,(38,24,11)),(245,52,72,(35,22,14)),(80,68,36,(2,24,22))],
 "office":[(66,52,88,(43,28,10)),(210,76,90,(36,22,10)),(64,48,34,(0,25,18))],
 "station":[(65,46,76,(34,29,13)),(253,57,77,(34,26,12)),(126,128,55,(0,20,24))],
}

def build_map(place):
    """Arte procedural fijo: parquet, moqueta, azulejos, muebles y luces.
    Los muebles decorativos no añaden colisiones ni pistas al modelo.
    """
    a,b,c,d=PALETTES[place]
    r=Raster(color=c)
    rng=random.Random({"cine":21,"office":34,"station":55}[place])
    for y in range(1,HEIGHT-1):
        for x in range(1,WIDTH-1):
            px,py=x*PIX,y*PIX
            r.rect(px,py,PIX,PIX,mix(rgb(a),rgb(b),rng.uniform(.0,.36)))
            if place=="office":
                for j in (0,8):
                    r.rect(px,py+j,PIX,1,a)
                    joint=(x*7+y*3+j)%13
                    r.rect(px+joint,py+j,1,8,a)
                    r.rect(px+2,py+j+3,8,1,mix(rgb(a),rgb(b),.45))
            else:
                r.rect(px,py,PIX,1,c)
                r.rect(px,py,1,PIX,c)
                r.rect(px+1,py+1,PIX-2,1,b)
                for _ in range(2):
                    r.rect(px+rng.randrange(2,13),py+rng.randrange(3,14),2,1,a)
    # Back wall: dado, moulding and windows; outside grid is not playable.
    r.rect(0,0,W,16,c)
    r.rect(0,11,W,4,d);r.rect(0,15,W,2,a)
    for x in (24,87,191,265):
        r.rect(x,2,23,10,"#221f30")
        r.rect(x+2,3,19,7,"#777588" if place=="station" else "#967575")
        r.rect(x+11,3,1,8,c)
        r.rect(x+2,6,19,1,c)
    def rug(x,y,w,h,base,edge):
        r.rect(x+2,y+2,w,h,c);r.rect(x,y,w,h,edge)
        r.rect(x+2,y+2,w-4,h-4,base)
        r.rect(x+4,y+4,w-8,1,edge);r.rect(x+4,y+h-5,w-8,1,edge)
        for i in range(x+8,x+w-7,8):
            r.rect(i,y+5,2,2,edge);r.rect(i,y+h-7,2,2,edge)
    def shelf(x,y,w):
        r.rect(x+2,y+2,w,14,c);r.rect(x,y,w,13,"#79594c")
        r.rect(x+2,y+2,w-4,8,"#42313c")
        for i in range(x+3,x+w-4,4):
            ht=rng.randrange(4,8)
            r.rect(i,y+10-ht,3,ht,rng.choice(["#b38370","#7d9690","#a6a179","#8d6d92"]))
        r.rect(x,y+10,w,3,"#a17c60")
    if place=="cine":
        rug(17,65,100,69,"#754854","#b07d82")
        # Screen and stepped rows of velvet seats.
        r.rect(17,18,104,10,"#302b3a")
        r.rect(20,19,98,6,"#c3b1a3")
        r.rect(21,26,96,2,"#8a766e")
        for j in range(3):
            for i in range(3):
                x,y=25+i*23,78+j*16
                r.rect(x+1,y+2,17,12,"#3c2937")
                r.rect(x,y,17,10,"#824653")
                r.rect(x+2,y+1,13,3,"#b16d78")
                r.rect(x+2,y+7,13,2,"#633c4a")
                r.rect(x,y+3,2,7,"#a78176");r.rect(x+15,y+3,2,7,"#a78176")
        shelf(186,20,32);shelf(257,20,38)
        shelf(275,94,27)
    elif place=="office":
        rug(38,63,99,52,"#82665d","#c3a17f")
        shelf(20,19,31);shelf(95,19,25);shelf(215,19,57)
        r.rect(51,77,55,24,"#493a3f")
        r.rect(49,74,55,22,"#916e56")
        r.rect(51,76,51,17,"#aa8667")
        r.rect(58,78,12,8,"#e1ceb0")
        r.rect(88,79,8,6,"#53645c")
        for x in (148,165,182):
            r.rect(x,115,14,10,"#574755")
            r.rect(x+1,116,12,3,"#b99a85")
        for x in (18,285):
            r.rect(x,136,10,7,"#98674e")
            r.rect(x+3,129,5,9,"#6d967a")
            r.rect(x,128,5,4,"#84ad86");r.rect(x+5,126,6,6,"#779b79")
    else:
        for x in range(23,140,25):
            r.rect(x,96,18,9,"#354550")
            r.rect(x,94,18,4,"#8b9d9b")
            r.rect(x+2,100,14,3,"#687b80")
        shelf(190,19,35);shelf(260,19,36)
        r.rect(18,151,284,7,"#303c46")
        r.rect(18,152,284,1,"#c1ad7c")
        for x in range(18,302,8):r.rect(x,156,4,1,"#8a7f68")
    if place!="office":
        for x,y in sorted(WALLS):
            px,py=x*PIX,y*PIX
            r.rect(px+2,py,14,16,"#292534")
            r.rect(px,py,12,16,c)
            r.rect(px+1,py+1,10,5,b)
            r.rect(px+1,py+8,10,5,a)
            r.rect(px,py,2,16,d)
            r.rect(px+10,py,2,16,"#312a37")
    r.light(LIGHTS[place],.88)
    return r

# 16 x 24 sprites, painted pixel by pixel. Each symbol is a palette index.
HUMAN=[
"................",".....HHHHHH.....","....HHHHHHHH....","...HHHHHHHHHH...",
"...HHSSSSSSHH...","...HSSSSSSSSH...","...HSKSSSSKSH...","....SSSSSSSS....",
"....SSDDDDSS....",".....SSSSSS.....",".....CCCCCC.....","...CCBLLBCC.....",
"..CCCBLLBCCC....","..CCCBLLBCCC....","..SCCBLLBCCS....","..SCCBBBBCCS....",
"...CCBBBBCC.....","...CCBBBBCC.....","...CCBBBBCC.....","....PP..PP......",
"....PP..PP......","....PP..PP......","...KKK..KKK.....","................"]
GHOST=[
"................","........G.......",".......GGG......","......GAG.......",
".....GGAGGG.....","....GAAAAAAG....","...GAAAAAAAA G..".replace(" ",""),
"..GAAAAAAAAAAG..","..GAAAAAAAAAAG..",".GAAKAAAAKAAAAG.",".GAAKAAAAKAAAAG.",
".GAAAAAAAAAAAAG.",".GAAAAKKAAAAAAG.",".GAAAAAAAAAAAAG.",".GAAAAAAAAAAAAG.",
"..GAAAAAAAGAGG..","..GAAAAAGG.G....","...GGAGGG.......",".....GG.........",
"................","................","................","................"]
HUMAN_P={"H":"#473b46","S":"#e2b89c","K":"#2c2a38","D":"#9b7369","C":"#ad8868","B":"#6a534f","L":"#e4d6bb","P":"#42495c"}
GHOST_P={"G":"#477e79","A":"#b8efdc","K":"#365361"}

def sprite_pixels(name,ghost,direction,frame,weak=False):
    rows=[list(row.ljust(16,".")[:16]) for row in (GHOST if ghost else HUMAN)]
    palette=dict(GHOST_P if ghost else HUMAN_P)
    if ghost:
        if name!="Brizna":
            rows[1:4]=[list("."*16) for _ in range(3)]
            palette["A"]="#a9c6ed" if name=="Mateo" else "#ccbfed"
        if weak:palette={k:"#"+''.join(f"{v:02x}" for v in mix(rgb(c),rgb("#59636c"),.48)) for k,c in palette.items()}
        if frame%2:
            rows[16]=list("...GAAAAAGGG....")
            rows[17]=list("....GGGGG.......")
    else:
        if name!="Tomás":palette["C"]="#74949c" if name in ("Rafael","Inés") else "#93798c"
        if name=="Tomás":palette["H"]="#3c3342"
        if direction=="up":
            for y in range(4,9):
                rows[y]=list("...HHHHHHHHHH...")
        elif direction in ("left","right"):
            rows[6]=list("...HSKSSSSSSH..." if direction=="left" else "...HSSSSSSKSH...")
        if frame==1:
            rows[21]=list("...PPP...PP.....");rows[22]=list("..KKKK...KKK....")
        elif frame==2:
            rows[21]=list("....PP..PPP.....");rows[22]=list("...KKK..KKKK....")
    return rows,palette

@dataclass
class Motion:
    x: float
    y: float
    tx: int
    ty: int
    direction: str="down"
    phase: float=0.
    moving: bool=False

    def advance(self,x,y,dt):
        dx,dy=x-self.tx,y-self.ty
        if abs(dx)+abs(dy)>1:
            self.x,self.y=float(x),float(y)
            self.phase=0.
        elif dx or dy:
            self.direction=("right" if dx>0 else "left") if dx else ("down" if dy>0 else "up")
        self.tx,self.ty=x,y
        distance=math.hypot(x-self.x,y-self.y)
        self.moving=distance>.005
        if self.moving:
            amount=min(1.,dt*9/max(distance,.001))
            self.x+=(x-self.x)*amount;self.y+=(y-self.y)*amount
            self.phase+=dt*9
        else:self.x,self.y=float(x),float(y);self.phase=0.
        return self.x,self.y

class Motor:
    """Cache de mapas y sprites por instancia; capas mundo/HUD separadas."""
    def __init__(self,canvas):
        self.cv=canvas
        self.maps={}
        self.sprites={}
        self.motions={}
        self.place=None
        self.dt=0.
        self.elapsed=0.
        self.background_builds=0

    def reset_motion(self):
        self.motions.clear()

    def begin(self,place,dt):
        self.dt=max(0.,min(.15,dt))
        self.elapsed+=self.dt
        self.cv.delete("world")
        if self.place!=place or not self.cv.find_withtag("background"):
            self.cv.delete("background")
            self.place=place;self.reset_motion()
            if place not in self.maps:
                image=tk.PhotoImage(master=self.cv,data=build_map(place).ppm(),format="PPM")
                self.maps[place]=image.zoom(SCALE,SCALE)
                self.background_builds+=1
            self.cv.create_image(0,0,anchor="nw",image=self.maps[place],tags=("background",))
            self.cv.tag_lower("background")

    def capture(self,tag,before):
        for item in self.cv.find_all():
            if item not in before:self.cv.addtag_withtag(tag,item)

    def finish(self,before):
        self.capture("world",before)
        self.cv.tag_raise("hud")

    def image(self,name,ghost,direction,frame,weak):
        key=(name,ghost,direction if not ghost else "down",frame,weak)
        if key not in self.sprites:
            rows,palette=sprite_pixels(name,ghost,direction,frame,weak)
            img=tk.PhotoImage(master=self.cv,width=16,height=24)
            for y,row in enumerate(rows):
                for x,char in enumerate(row):
                    if char in palette:img.put(palette[char],(x,y))
            self.sprites[key]=img.zoom(SCALE,SCALE)
        return self.sprites[key]

    def position(self,identity,x,y):
        if identity not in self.motions:self.motions[identity]=Motion(x,y,x,y)
        motion=self.motions[identity]
        px,py=motion.advance(x,y,self.dt)
        return px*TILE+16,py*TILE+16,motion

    def actor(self,x,y,name,ghost=False,active=False,weak=False,identity=None):
        cx,cy,m=self.position(identity or name,x,y)
        cv=self.cv
        cv.create_oval(cx-11,cy+9,cx+11,cy+15,fill="#312b38",outline="")
        if active:
            cv.create_oval(cx-14,cy+5,cx+14,cy+18,outline="#9cd7bf" if ghost else "#e3bd88",width=2)
        if ghost:
            bob=round(math.sin(self.elapsed*4+len(name))*2)
            cy+=bob
            frame=int(self.elapsed*3)%2
            # Small animated particles communicate supernatural presence.
            for i in range(3):
                px=cx+math.sin(self.elapsed*1.8+i*2.1)*15
                py=cy-9+math.cos(self.elapsed*2+i*2.1)*8
                cv.create_rectangle(px,py,px+2,py+2,fill="#82b8a8" if weak else "#a6e7d0",outline="")
        else:frame=(1,0,2,0)[int(m.phase)%4] if m.moving else 0
        image=self.image(name,ghost,m.direction,frame,weak)
        cv.create_image(round(cx),round(cy-8),image=image)
        cv.create_text(round(cx),round(cy-33),text=name,font=("Segoe UI",8,"bold"),fill="#b3e6d5" if ghost else "#f4dfc2")

    def anchor(self,w):
        ax,ay=w.anchor
        cx,cy=ax*TILE+16,ay*TILE+16
        r=w.spirit.radius*TILE
        points=(cx-r,cy,cx,cy-r,cx+r,cy,cx,cy+r,cx-r,cy)
        self.cv.create_line(*points,fill="#d1a58b" if w.distance>w.spirit.radius else "#8dd0bc",dash=(5,5),width=2)
        gx,gy=w.gx*TILE+16,w.gy*TILE+16
        self.cv.create_line(cx,cy,gx,gy,fill="#cfa589" if w.distance>w.spirit.radius else "#6da99c",dash=(2,6))
        self.cv.create_oval(cx-5,cy-5,cx+5,cy+5,outline="#bde9d1",width=2)
