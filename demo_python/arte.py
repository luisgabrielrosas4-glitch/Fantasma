"""Arte original procedural de Agencia de espectros.
Sprites 48x72 y portada 640x360. No requiere recursos externos."""
import math
import random
import pygame as pg

def rect(s,c,x,y,w,h):
    if w>0 and h>0:pg.draw.rect(s,c,(int(x),int(y),int(w),int(h)))
def poly(s,c,pts):pg.draw.polygon(s,c,pts)
def line(s,c,a,b,w=1):pg.draw.line(s,c,a,b,w)
def ell(s,c,x,y,w,h):pg.draw.ellipse(s,c,(x,y,w,h))
def mix(a,b,t):
    a,b=pg.Color(a),pg.Color(b)
    return tuple(round(x+(y-x)*t) for x,y in zip(a[:3],b[:3]))

def spirit(name,direction,frame,weak):
    s=pg.Surface((48,72),pg.SRCALPHA)
    shift=frame%2
    if name=="Brizna":
        # A living flame rather than a miniature human ghost.
        outline="#397f79";base="#72c9b3";mid="#a2e3c6";hi="#e0ffe5"
        poly(s,outline,[(11,49),(7,39),(8,27),(15,18),(19,10),(24,17),(31,5),(32,19),(39,26),(42,38),(38,49),(31,54),(24,52+shift),(17,57)])
        poly(s,base,[(13,48),(10,37),(12,27),(20,19),(24,22),(30,12),(30,23),(37,29),(39,39),(35,48),(29,51),(23,49+shift),(17,53)])
        poly(s,mid,[(15,29),(23,23),(31,25),(36,34),(34,44),(27,48),(18,46),(13,39)])
        poly(s,hi,[(17,27),(22,25),(20,31),(16,36),(14,35)])
        poly(s,"#c6f4d5",[(13,51),(18,49),(21,51),(16,55)])
        if direction!="up":
            eyes=(17,27) if direction=="left" else (21,31) if direction=="right" else (18,29)
            for x in eyes:
                rect(s,"#27545b",x,34,4,7);rect(s,hi,x,34,1,2)
            rect(s,"#458b82",23,44,4,2)
            rect(s,"#d1b9ae",14,42,3,1);rect(s,"#d1b9ae",33,42,3,1)
        else:poly(s,hi,[(19,30),(26,26),(30,29),(25,31)])
        rect(s,hi,30,14,2,4)
        rect(s,"#b6f0d8",7,21,2,2);rect(s,"#9ad9c7",39,15+shift,2,2)
    elif name=="Mora":
        poly(s,"#477b83",[(8,51),(7,36),(11,23),(10,12),(20,23),(29,23),(38,12),(37,29),(41,40),(37,53),(30,58),(17,56)])
        poly(s,"#8fc5c4",[(11,49),(11,35),(14,20),(20,28),(29,27),(35,20),(36,34),(38,40),(34,51),(28,55),(18,53)])
        poly(s,"#c4e9dc",[(13,34),(17,28),(20,31),(16,43),(13,45)])
        line(s,"#72aab0",(34,51),(44,43),5);line(s,"#9bd4ce",(44,43),(42,31+shift),4)
        for x in (17,29):rect(s,"#294d58",x,35,4,5);rect(s,"#e5f5d5",x,35,1,1)
        rect(s,"#456e79",23,43,3,2)
        for x in (7,32):line(s,"#b8e3dd",(x,45),(x+9,43))
    else:
        # Human spirits retain clothing and recognizable silhouettes.
        colors={"Elena":("#6c6599","#b0a4d3","#e3d8f3"),"Mateo":("#526f99","#8daed1","#d9ebf9"),"Nico":("#728b80","#a9c0a4","#e6ecd2"),"Clara":("#8e718e","#c1a2c7","#f1d8e8"),"Silvia":("#547e92","#9bc9dc","#e4f4f4")}
        dark,mid,hi=colors.get(name,("#677e99","#a2bed5","#dcecf2"))
        poly(s,dark,[(11,21),(12,12),(19,7),(29,7),(36,13),(37,23),(42,33),(39,49),(34,58),(28,54+shift),(22,62),(15,54),(8,48),(7,33)])
        poly(s,mid,[(14,23),(14,13),(20,10),(29,10),(34,15),(34,24),(39,34),(36,48),(32,54),(28,50+shift),(22,57),(16,50),(11,47),(10,34)])
        poly(s,hi,[(14,15),(19,10),(28,10),(24,13),(18,15),(16,22),(13,23)])
        if name in ("Elena","Clara","Silvia"):
            poly(s,dark,[(12,15),(14,10),(20,6),(31,8),(37,15),(36,35),(31,30),(30,18),(18,18),(16,33),(11,29)])
            if name=="Elena":rect(s,hi,14,14,20,3);poly(s,hi,[(14,33),(24,41),(34,33),(29,46),(19,46)])
            elif name=="Clara":poly(s,hi,[(12,32),(24,38),(35,32),(33,44),(16,44)])
            else:line(s,hi,(16,17),(32,13),2)
        else:
            rect(s,dark,14,11,20,7);rect(s,hi,17,12,11,2)
            if name=="Nico":
                rect(s,dark,12,30,24,4);rect(s,dark,16,34,4,15);rect(s,dark,29,34,4,15)
                rect(s,hi,19,39,11,8)
                rect(s,dark,15,22,18,2);rect(s,dark,16,22,2,6);rect(s,dark,30,22,2,6)
            else:
                poly(s,hi,[(15,31),(23,39),(32,31),(30,44),(19,44)])
                rect(s,dark,13,39,7,9);rect(s,hi,15,40,4,5)
        if direction!="up":
            for x in (18,28):
                rect(s,"#39465d",x,22,3,4);rect(s,hi,x,22,1,1)
            rect(s,dark,22,29,5,1)
        else:rect(s,dark,15,14,19,13)
        line(s,hi,(12,37),(10,43),2);line(s,hi,(36,37),(38,42),2)
    if weak:s.fill((165,180,190,220),special_flags=pg.BLEND_RGBA_MULT)
    return s

def human(name,direction,frame):
    s=pg.Surface((48,72),pg.SRCALPHA)
    tom=name=="Tomás";nurse=name=="Enfermera";rafael=name=="Rafael"
    palette={"Tomás":"#b18a61","Enfermera":"#d4dfd9","Rafael":"#687b8a","Inés":"#719a93","Sara":"#97788e"}
    coat=palette.get(name,"#8a91a0");shadow=mix(coat,"#302a38",.48);hi=mix(coat,"#f2d7b5",.36)
    ink="#292735";skin="#dcb194";skinshadow="#a77666";hair="#514047" if not tom else "#4b4448"
    step=(0,-3,0,3)[frame%4]
    # Legs and arms, individually articulated.
    for x,offset in ((15,max(0,step)),(26,max(0,-step))):
        rect(s,ink,x,53+offset,9,13-offset);rect(s,"#535967",x+2,54+offset,5,10-offset)
        rect(s,"#777987",x+2,54+offset,1,7-offset)
        rect(s,ink,x-2,65+offset//2,12,4);rect(s,"#65544c",x-1,65+offset//2,9,1)
    poly(s,ink,[(10,31),(16,26),(32,26),(38,31),(43,49),(36,54),(36,60),(12,60),(12,54),(5,49)])
    poly(s,coat,[(12,32),(17,28),(31,28),(36,32),(40,48),(34,50),(34,58),(14,58),(14,50),(8,48)])
    poly(s,shadow,[(12,34),(15,37),(15,54),(14,58),(20,58),(19,34)])
    poly(s,shadow,[(34,34),(31,40),(31,56),(34,57),(35,49),(40,48)])
    line(s,hi,(13,32),(17,29),2);line(s,hi,(32,29),(35,32),2)
    if direction!="up":
        poly(s,"#e5dac5",[(19,28),(29,28),(24,44)])
        poly(s,shadow,[(17,30),(23,42),(18,47),(19,36)])
        poly(s,shadow,[(31,30),(25,42),(31,47),(29,36)])
        if tom:poly(s,"#6b4e48",[(23,31),(26,31),(27,40),(24,44),(22,40)])
        rect(s,shadow,23,44,2,13)
        for y in (46,51,56):rect(s,"#dfc49a",26,y,2,2)
        rect(s,shadow,16,47,6,2);rect(s,hi,16,46,6,1)
        if rafael:
            rect(s,"#d9bf7e",31,46,2,7);rect(s,"#d9bf7e",33,51,4,2)
            pg.draw.circle(s,"#d9bf7e",(32,46),3,1)
        if nurse:rect(s,"#719e9d",29,36,5,7);rect(s,"#e5f1e4",30,37,3,2)
    else:
        line(s,shadow,(24,30),(24,57),2);line(s,hi,(16,31),(31,31))
        if tom:rect(s,shadow,16,45,16,3);rect(s,hi,20,45,7,2)
    rect(s,skinshadow,7,48,6,5);rect(s,skin,8,48,4,3)
    rect(s,skinshadow,35,48,6,5);rect(s,skin,36,48,4,3)
    # Neck, asymmetric hair, eyebrows and facial features.
    rect(s,skinshadow,20,24,9,6)
    poly(s,ink,[(12,10),(17,4),(30,4),(36,9),(37,21),(31,28),(17,28),(11,22)])
    poly(s,skin,[(15,11),(33,11),(34,21),(29,26),(19,26),(14,21)])
    rect(s,skinshadow,17,24,13,2);rect(s,"#efc4a1",17,12,5,3)
    poly(s,hair,[(13,9),(18,5),(30,5),(35,10),(34,15),(28,12),(19,13),(14,17)])
    line(s,"#8b6b61",(18,7),(30,7),2)
    if tom:
        rect(s,"#a8a095",13,14,3,6);rect(s,"#a8a095",32,14,3,6)
        rect(s,"#ae8674",19,23,10,1)
    if nurse:
        poly(s,"#dce6da",[(13,9),(15,3),(33,3),(36,9)])
        rect(s,"#b66b74",23,4,3,6);rect(s,"#b66b74",21,6,7,2)
    if rafael:
        rect(s,"#50606d",13,5,22,5);rect(s,"#788b96",16,5,16,2);rect(s,ink,12,10,25,2)
    if direction=="up":
        rect(s,hair,14,11,21,13);line(s,"#82685d",(18,12),(30,12),2)
    else:
        eyes=(17,26) if direction=="left" else (22,31) if direction=="right" else (18,29)
        for x in eyes:
            rect(s,"#6c514c",x,15,4,1);rect(s,ink,x,17,3,3);rect(s,"#f2dac3",x,17,1,1)
        rect(s,skinshadow,23,20,3,2);rect(s,"#845e59",22,23,6,1)
    return s

def character(name,ghost,direction="down",frame=0,weak=False):
    return spirit(name,direction,frame,weak) if ghost else human(name,direction,frame)

def title_scene():
    """Illustrated pixel-art facade, perspective pavement and rainy atmosphere."""
    s=pg.Surface((640,360));rng=random.Random(412)
    for y in range(360):
        c=mix("#121929","#40545e",min(1,y/300))
        line(s,c,(0,y),(639,y))
    ell(s,"#a1a5a0",520,23,35,35);ell(s,"#344351",531,18,35,35)
    for x in range(0,640,30):
        h=rng.randrange(30,100);rect(s,"#202d3a",x,132-h,28,h+100)
        for y in range(140-h,145,13):
            if rng.random()>.5:rect(s,"#67645f",x+5,y,4,6)
    # Main theater is deliberately on the right; menu occupies the left.
    poly(s,"#2b2634",[(252,75),(575,75),(616,110),(616,278),(252,278)])
    rect(s,"#694d51",255,81,320,190)
    for y in range(83,270,9):
        line(s,"#493842",(255,y),(575,y))
        for x in range(255+(y%2)*9,575,18):line(s,"#493842",(x,y),(x,y+8))
    poly(s,"#4b3b47",[(575,81),(616,111),(616,270),(575,270)])
    for x in (261,365,472,568):
        rect(s,"#98716a",x,86,7,184);rect(s,"#c39577",x,86,2,180)
    rect(s,"#332a37",249,73,332,11);rect(s,"#a47b69",249,73,332,3)
    for x in (281,381,489):
        rect(s,"#272b39",x,96,55,36);rect(s,"#67838b",x+4,100,47,27)
        line(s,"#34434f",(x+27,99),(x+27,128),2)
        line(s,"#34434f",(x+3,114),(x+51,114),2)
        rect(s,"#b59880",x-2,129,59,3)
    # Marquee and warm entrance.
    poly(s,"#392b36",[(264,141),(570,141),(590,164),(252,164)])
    rect(s,"#d9b78a",257,145,321,30);rect(s,"#a87567",257,172,321,4)
    font=pg.font.Font(None,32);font.set_bold(True)
    im=font.render("CINE AURORA",False,"#5b3940")
    s.blit(im,im.get_rect(center=(417,159)))
    for x in range(265,574,9):rect(s,"#ffe3a6",x,173,3,2)
    rect(s,"#352b37",353,183,139,88);rect(s,"#9c7462",358,185,129,83)
    for x in (363,403,443):
        rect(s,"#322f3a",x,190,37,76);rect(s,"#a17f61",x+3,193,31,41)
        rect(s,"#d9ad73",x+5,195,27,36);rect(s,"#8c6b55",x+18,194,2,40)
        rect(s,"#d7bd8a",x+27,241,3,7)
    for x in (281,514):
        rect(s,"#372d3a",x,189,40,63);rect(s,"#c2a27f",x+3,192,34,55)
        rect(s,"#586a74",x+6,196,28,31);poly(s,"#a06c71",[(x+8,226),(x+19,202),(x+32,226)])
        for y in (232,236,240):rect(s,"#876c63",x+7,y,25,1)
    rect(s,"#aaa08e",247,270,372,6)
    poly(s,"#535a60",[(0,281),(640,276),(640,360),(0,360)])
    for y in (286,304,331,357):line(s,"#3c4855",(0,y),(639,y-4))
    for x in range(0,640,47):line(s,"#3e4854",(x,360),(int(420+(x-420)*.60),278))
    for _ in range(110):
        x=rng.randrange(0,640);y=rng.randrange(284,360)
        c=rng.choice(["#76818a","#a58b70","#596d77","#6a6467"])
        rect(s,c,x,y,rng.randrange(2,13),1)
    # Lamp and its pool of light.
    ell(s,"#6f6b65",557,286,73,10);rect(s,"#34343e",591,199,5,92)
    poly(s,"#3e3c46",[(581,190),(606,190),(601,205),(587,205)])
    rect(s,"#f2cf87",589,193,10,8)
    for y in range(280,332):
        if y%3==0:line(s,"#8b8171",(380+(y-280)//2,y),(465-(y-280)//2,y))
    # Foreground detective, facing the entrance; small spectral companion.
    detective=pg.transform.scale(character("Tomás",False,"up"),(58,87))
    ell(s,"#30323d",435,324,60,10);s.blit(detective,(435,247))
    brizna=pg.transform.scale(character("Brizna",True,"left"),(37,55))
    s.blit(brizna,(503,267))
    # Dark reading area fades into the illustration.
    shade=pg.Surface(s.get_size(),pg.SRCALPHA)
    for x in range(640):
        alpha=round(224*max(0,1-x/375)**1.25)
        line(shade,(14,18,30,alpha),(x,0),(x,359))
    s.blit(shade,(0,0))
    return s

class TitleArt:
    def __init__(self):
        self.base=title_scene()
        self.time=0.
        rng=random.Random(31)
        self.rain=[(rng.randrange(640),rng.randrange(360),rng.uniform(45,100)) for _ in range(85)]
    def draw(self,dt):
        self.time+=max(0,min(.15,dt))
        s=self.base.copy()
        overlay=pg.Surface(s.get_size(),pg.SRCALPHA)
        for x,y,speed in self.rain:
            yy=int((y+self.time*speed)%370)-8;xx=int((x-self.time*speed*.22)%640)
            line(overlay,(155,184,193,75),(xx,yy),(xx-2,yy+7))
        for i in range(7):
            x=522+int(math.sin(self.time*.8+i*2.1)*23)
            y=292+int(math.cos(self.time+i)*16)
            rect(overlay,(160,240,206,145),x,y,1,2)
        if int(self.time*2)%9==0:rect(overlay,(57,35,45,80),257,145,65,29)
        s.blit(overlay,(0,0))
        return s
