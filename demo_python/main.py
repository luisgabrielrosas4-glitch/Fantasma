"""Agencia de espectros 0.4 — prototipo Pygame-ce para validar antes de Godot."""
import os
import math
from pathlib import Path
import pygame as pg
from modelo import World, CASES
from motor_grafico import Motor, W, H, TILE

SIZE=(1280,720)
MAP_X,MAP_Y=16,64
MAP_SIZE=(W*2,H*2)
SIDE_X=992
BG="#191824"; PANEL="#292638"; BORDER="#51475c"; GOLD="#e9bc83"; MINT="#b2e6d1"; INK="#e6dbcd"; MUTED="#b2a6b8"
SAVE=Path.home()/".agencia_espectros_v3.json"
NAMES={"office":"Agencia de espectros","cine":"Cine Aurora","station":"Estación del barrio"}
STATUS={"complete":"RESUELTO","provisional":"PROVISIONAL","incomplete":"INCOMPLETO"}

class Game:
    def __init__(self,screen=None):
        if not pg.get_init():pg.init()
        if not pg.font.get_init():pg.font.init()
        self.screen=screen if screen is not None else pg.display.set_mode((1280,720),pg.RESIZABLE)
        pg.display.set_caption("Agencia de espectros • El espíritu que nunca vivió")
        self.frame=pg.Surface(SIZE)
        self.motor=Motor()
        self.world=World()
        self.world.tell("Después del accidente, Tomás oye voces que otros no pueden escuchar. Acércate al tablón para aceptar El último boleto.")
        self.clock=pg.time.Clock()
        self.fonts={}
        self.buttons=[]
        self.choice=None
        self.modal=None
        self.review_case=None
        self.selected=set()
        self.hypothesis=None
        self.result=""
        self.move_clock=0.
        self.running=True
        self.fps=0.
        self.show_fps=False

    def font(self,size,bold=False):
        key=(size,bold)
        if key not in self.fonts:
            f=pg.font.Font(None,size);f.set_bold(bold);self.fonts[key]=f
        return self.fonts[key]
    def text(self,value,x,y,size=22,color=INK,bold=False,center=False):
        im=self.font(size,bold).render(str(value),True,color)
        self.frame.blit(im,im.get_rect(center=(x,y)) if center else (x,y))
        return im.get_height()
    def wrap(self,value,x,y,width,size=21,color=INK,bold=False,limit=None):
        f=self.font(size,bold);lines=[]
        for paragraph in str(value).split("\n"):
            current=""
            for word in paragraph.split():
                test=(current+" "+word).strip()
                if current and f.size(test)[0]>width:lines.append(current);current=word
                else:current=test
            lines.append(current)
        if limit and len(lines)>limit:
            lines=lines[:limit]
            while f.size(lines[-1]+"...")[0]>width and lines[-1]:lines[-1]=lines[-1][:-1]
            lines[-1]+="..."
        for l in lines:
            self.text(l,x,y,size,color,bold);y+=f.get_height()+3
        return y
    def panel(self,box,fill=PANEL,edge=BORDER,radius=8):
        pg.draw.rect(self.frame,fill,box,border_radius=radius)
        pg.draw.rect(self.frame,edge,box,width=1,border_radius=radius)
    def button(self,box,label,action,enabled=True,accent=False):
        box=pg.Rect(box)
        self.panel(box,"#455d55" if accent and enabled else "#3e394d" if enabled else "#302d3b", "#789a87" if accent and enabled else BORDER,5)
        self.text(label,box.centerx,box.centery,19,MINT if enabled else "#756f80",True,True)
        if enabled:self.buttons.append((box,action))
    def bar(self,x,y,w,value,color):
        pg.draw.rect(self.frame,"#40394b",(x,y,w,8),border_radius=4)
        if value>0:pg.draw.rect(self.frame,color,(x,y,max(1,round(w*min(100,value)/100)),8),border_radius=4)
    def current_target(self):
        options=self.world.nearby()
        if self.choice not in options:self.choice=options[0] if options else None
        return self.choice
    def open_cases(self):
        self.modal="cases";self.result="";self.move_clock=0.
    def open_evidence(self,case=None):
        self.review_case=case or self.world.place
        if self.review_case not in CASES:self.open_cases();return
        self.modal="evidence"
        self.selected=set(self.world.facts[self.review_case])
        self.hypothesis=None;self.result="";self.move_clock=0.
    def close_modal(self):
        self.modal=None;self.move_clock=0.;self.result=""
    def interact(self,power=False):
        w=self.world;k=self.current_target()
        if k is None:w.tell("Acércate a un objeto o a un personaje.");return
        if w.place=="office" and k=="board" and not power and not w.ghost_mode:
            self.open_cases();return
        old=w.place
        w.act(k,power)
        if old!=w.place:self.choice=None;self.motor.reset_motion()
    def action(self,action):
        w=self.world
        if isinstance(action,tuple):
            kind,value=action
            if kind=="accept":
                old=w.place
                self.result=w.accept_case(value)
                if old!=w.place:self.close_modal();self.choice=None;self.motor.reset_motion()
            elif kind=="review":self.open_evidence(value)
            elif kind=="clue":
                if value in self.selected:self.selected.remove(value)
                else:self.selected.add(value)
            elif kind=="choice":self.hypothesis=value
            return
        if action=="close":self.close_modal();return
        if action=="cases":self.open_cases();return
        if action=="submit":
            if self.hypothesis is None:self.result="Elige primero una hipótesis."
            else:self.result=w.resolve(self.review_case,self.hypothesis,list(self.selected))
            return
        if self.modal:return
        if action=="e":self.interact()
        elif action=="space":self.interact(True)
        elif action=="q":w.toggle();self.choice=None
        elif action=="r":w.recall();self.choice=None;self.motor.reset_motion()
        elif action=="f":
            cs=w.nearby();k=self.current_target()
            if cs:self.choice=cs[(cs.index(k)+1)%len(cs)]
        elif action=="tab":
            if w.place=="office":self.open_cases()
            else:self.open_evidence()
        elif action=="c":
            names=list(w.spirits)
            w.choose_spirit(names[(names.index(w.active)+1)%len(names)])
            self.motor.reset_motion()
        elif action=="j":w.recruit()
        elif action=="p":w.release_guest()
        elif action=="f5":
            try:w.save(SAVE);w.tell("Partida guardada.")
            except OSError as e:w.tell("No se pudo guardar: "+str(e))
        elif action=="f9":
            try:self.world=World.load(SAVE);self.world.tell("Partida cargada.");self.choice=None;self.motor.reset_motion()
            except (OSError,ValueError,TypeError,KeyError) as e:w.tell("No se pudo cargar: "+str(e))
        elif action=="f3":self.show_fps=not self.show_fps

    def viewport(self):
        sw,sh=self.screen.get_size()
        ratio=min(sw/SIZE[0],sh/SIZE[1])
        nw,nh=max(1,round(SIZE[0]*ratio)),max(1,round(SIZE[1]*ratio))
        return pg.Rect((sw-nw)//2,(sh-nh)//2,nw,nh)
    def logical(self,pos):
        v=self.viewport()
        if not v.collidepoint(pos):return None
        return ((pos[0]-v.x)*SIZE[0]/v.w,(pos[1]-v.y)*SIZE[1]/v.h)
    def click(self,pos):
        point=self.logical(pos)
        if point is None:return
        for box,action in reversed(self.buttons):
            if box.collidepoint(point):self.action(action);return
        if not self.modal:
            mx,my=point[0]-MAP_X,point[1]-MAP_Y
            if 0<=mx<MAP_SIZE[0] and 0<=my<MAP_SIZE[1]:
                tx,ty=int(mx//(TILE*2)),int(my//(TILE*2))
                for k,(x,y,*_) in self.world.objects.items():
                    if (tx,ty)==(x,y) and k in self.world.nearby():self.choice=k;return
    def event(self,e):
        if e.type==pg.QUIT:self.running=False;return
        if e.type==pg.VIDEORESIZE:
            self.screen=pg.display.set_mode((max(640,e.w),max(360,e.h)),pg.RESIZABLE);return
        if e.type==pg.MOUSEBUTTONDOWN and e.button==1:self.click(e.pos);return
        if e.type!=pg.KEYDOWN:return
        key=pg.key.name(e.key)
        if self.modal:
            if e.key in (pg.K_ESCAPE,pg.K_TAB):self.close_modal()
            elif self.modal=="cases" and e.key in (pg.K_1,pg.K_2):
                self.action(("accept",("cine","station")[e.key-pg.K_1]))
            elif self.modal=="evidence" and e.key in (pg.K_1,pg.K_2,pg.K_3):
                self.action(("choice",e.key-pg.K_1))
            elif self.modal=="evidence" and e.key==pg.K_RETURN:self.action("submit")
            return
        if e.key==pg.K_ESCAPE:self.open_cases() if self.world.place=="office" else self.open_evidence();return
        self.action(key)

    def update(self,dt,keys=None):
        if self.modal:return
        dt=max(0.,min(.15,dt))
        self.move_clock+=dt
        keys=pg.key.get_pressed() if keys is None else keys
        if self.move_clock>=.125:
            self.move_clock-=.125
            for a,b,dx,dy in ((pg.K_w,pg.K_UP,0,-1),(pg.K_s,pg.K_DOWN,0,1),(pg.K_a,pg.K_LEFT,-1,0),(pg.K_d,pg.K_RIGHT,1,0)):
                if keys[a] or keys[b]:
                    self.world.move(dx,dy);self.choice=None;break
        self.world.tick(dt)

    def draw(self,dt=0.):
        w=self.world
        self.buttons.clear();self.frame.fill(BG)
        self.text("AGENCIA DE ESPECTROS",18,15,29,GOLD,True)
        self.text(NAMES[w.place],438,18,23,MINT,True)
        self.text("REFUGIO / PREPARACIÓN" if w.place=="office" else "INVESTIGACIÓN ACTIVA",994,20,20,MUTED)
        self.panel((12,60,MAP_SIZE[0]+8,MAP_SIZE[1]+8),"#292533")
        scene=self.motor.draw(w,0. if self.modal else dt,self.current_target())
        self.frame.blit(pg.transform.scale(scene,MAP_SIZE),(MAP_X,MAP_Y))
        self.draw_hud()
        self.draw_log()
        if self.show_fps:self.text(f"FPS {self.fps:.1f}",20,42,16,MUTED)
        if self.modal:self.draw_modal()
        return self.frame

    def draw_hud(self):
        w=self.world;x=SIDE_X
        self.panel((x,64,272,528))
        self.text("CONTROL",x+15,79,19,GOLD,True)
        portrait=self.motor.get_sprite(w.active if w.ghost_mode else "Tomás",w.ghost_mode,"down",0,False)
        self.frame.blit(pg.transform.scale(portrait,(48,76)),(x+12,100))
        self.text(w.active if w.ghost_mode else "Tomás",x+70,109,27,INK,True)
        self.text("Espíritu" if w.ghost_mode else "Detective",x+70,138,20,MUTED)
        if w.companion_present:
            self.text(f"{w.active}  ·  Vínculo {w.spirit.bond}",x+15,185,22,MINT,True)
            self.text(f"Energía {int(w.spirit.energy)}/100",x+15,210,18)
            self.bar(x+15,231,242,w.spirit.energy,"#76b9aa")
            self.text(f"Estabilidad {int(w.spirit.stability)}/100",x+15,248,18)
            self.bar(x+15,269,242,w.spirit.stability,"#b19bd2")
            if w.place=="office":self.text("Refugio: sin límite de distancia",x+15,286,18,MINT)
            else:
                color="#edb68c" if w.distance>w.spirit.radius else MINT
                self.text(f"Distancia {w.distance} / {w.spirit.radius} casillas",x+15,286,18,color)
        else:self.wrap("Sin compañero disponible aquí. El primer expediente te espera.",x+15,184,240,20,MUTED,limit=4)
        pg.draw.line(self.frame,BORDER,(x+15,316),(x+257,316))
        if w.place=="office":
            self.text("CENTRO DE OPERACIONES",x+15,330,18,GOLD,True)
            self.wrap("Acércate al tablón para aceptar una misión. Descansa, prepara y elige compañeros aquí.",x+15,353,240,19,INK,limit=4)
            self.text("Equipo: "+", ".join(n for n,s in w.spirits.items() if s.bond) if w.home_open else "Agencia en preparación",x+15,443,17,MINT)
            if w.reports.get("station")=="complete" and not w.guest_decision:self.wrap("J: invitar a Mateo / P: despedirse",x+15,468,240,17,MUTED,limit=2)
        else:
            self.text("EXPEDIENTE ACTIVO",x+15,330,18,GOLD,True)
            self.wrap(w.case["title"],x+15,354,240,24,INK,True,2)
            self.text(f"{len(w.facts[w.place])} pistas · {len(w.physical[w.place])} físicas",x+15,405,19,MINT)
            self.text(STATUS.get(w.reports.get(w.place),"ABIERTO"),x+15,431,18,GOLD)
            self.wrap("Reúne pruebas y abre el tablero para formular tu conclusión.",x+15,455,240,19,MUTED,limit=3)
        self.button((x+15,535,242,40),"TAB · EXPEDIENTES","tab",accent=True)
    def draw_log(self):
        w=self.world;k=self.current_target()
        self.panel((16,605,960,99))
        self.text("INTERACCIÓN",29,614,18,GOLD,True)
        self.wrap(w.objects[k][2] if k else "Acércate a un objeto o personaje",29,636,263,23,INK,True,2)
        self.button((29,668,112,27),"E · USAR","e")
        self.button((148,668,143,27),"ESP · PODER","space",w.place!="office" and w.companion_present)
        self.text("BITÁCORA",312,614,18,GOLD,True)
        for i,msg in enumerate(w.log[-2:]):
            self.wrap(msg,312,636+i*31,650,19,INK if i==len(w.log[-2:])-1 else MUTED,limit=1)
        self.panel((SIDE_X,605,272,99))
        self.text("WASD · Mover   Q · Cambiar",SIDE_X+11,615,18)
        self.text("F · Objetivo   R · Regresar",SIDE_X+11,638,18)
        self.text("C · Equipo   F5/F9 · Guardar",SIDE_X+11,661,17,MUTED)
        self.text("F3 · FPS",SIDE_X+11,682,16,MUTED)
    def draw_modal(self):
        overlay=pg.Surface(SIZE,pg.SRCALPHA);overlay.fill((10,9,17,205));self.frame.blit(overlay,(0,0))
        # Underlying buttons are not active while the modal is open.
        self.buttons.clear()
        self.panel((170,45,940,630),"#242232","#827186",10)
        self.button((982,62,110,31),"CERRAR","close")
        if self.modal=="cases":
            self.text("TABLÓN DE LA AGENCIA",194,63,31,GOLD,True)
            self.wrap("Selecciona una investigación disponible. Para salir a una misión, Tomás debe estar junto al tablón.",194,103,875,22,MUTED)
            for i,(case,cfg) in enumerate(CASES.items()):
                y=169+i*176
                enabled=self.world.available(case)
                complete=self.world.reports.get(case)=="complete"
                near=self.world.place=="office" and not self.world.ghost_mode and "board" in self.world.nearby()
                self.panel((194,y,892,151),"#312c40")
                self.text(f"0{i+1} / "+cfg["title"],212,y+13,29,INK,True)
                self.text("ARCHIVADO" if complete else "DISPONIBLE" if enabled else "BLOQUEADO",212,y+46,18,MINT if enabled else MUTED,True)
                self.wrap(cfg["client"] if enabled else "Resuelve el primer expediente para desbloquearlo.",212,y+70,560,22,INK,limit=3)
                self.button((806,y+23,258,40),"REVISAR EXPEDIENTE",("review",case),enabled)
                self.button((806,y+79,258,40),("CONTINUAR" if case in self.world.accepted else "ACEPTAR CASO"),("accept",case),enabled and not complete and near,True)
            if self.result:self.wrap(self.result,194,541,875,22,GOLD,limit=3)
            else:self.wrap("1 / 2: elegir caso disponible · Esc: volver. Los expedientes sin resolver conservan sus pruebas cuando regresas.",194,541,875,22,MUTED,limit=3)
            return
        case=self.review_case;cfg=CASES[case];w=self.world
        self.text(cfg["title"].upper(),194,63,31,GOLD,True)
        self.wrap(cfg["client"],194,103,870,22,MUTED,limit=2)
        self.text("EVIDENCIAS",194,161,21,MINT,True)
        y=190
        for key,clue in cfg["clues"].items():
            known=key in w.facts[case]
            if not known:continue
            physical=key in w.physical[case]
            box=pg.Rect(194,y,492,48)
            self.panel(box,"#38374a" if key in self.selected else "#2c2939")
            self.text("[x]" if key in self.selected else "[ ]",204,y+8,19,MINT if physical else INK,True)
            self.wrap(clue,240,y+6,434,19,INK,limit=2)
            self.buttons.append((box,("clue",key)));y+=53
        if y==190:self.wrap("Aún no hay pistas documentadas.",194,y,475,22,MUTED)
        self.text("HIPÓTESIS",710,161,21,MINT,True)
        for i,label in enumerate(cfg["choices"]):
            box=pg.Rect(710,190+i*81,375,70)
            self.panel(box,"#4a5450" if self.hypothesis==i else "#322e40")
            self.text(f"{i+1}.",720,box.y+8,20,GOLD,True)
            self.wrap(label,751,box.y+8,320,21,INK,limit=3)
            self.buttons.append((box,("choice",i)))
        allowed=w.place==case and not w.ghost_mode and w.reports.get(case)!="complete"
        self.button((710,443,375,42),"PRESENTAR CONCLUSIÓN","submit",allowed,True)
        if not allowed:self.wrap("Consulta de expediente. Tomás presenta conclusiones durante la misión.",710,496,375,19,MUTED,limit=3)
        if self.result:self.wrap(self.result,710,548,375,20,GOLD,limit=4)
        self.text("Las observaciones espectrales no sustituyen pruebas físicas.",194,624,19,MUTED)
        if w.place=="office":self.button((982,615,110,32),"TABLÓN","cases")
    def present(self):
        v=self.viewport()
        self.screen.fill("#101019")
        self.screen.blit(pg.transform.scale(self.frame,v.size),v.topleft)
        pg.display.flip()
    def run(self):
        while self.running:
            dt=self.clock.tick(60)/1000.
            for event in pg.event.get():self.event(event)
            self.update(dt);self.fps=self.clock.get_fps();self.draw(dt);self.present()
        pg.quit()

def main():
    Game().run()
if __name__=="__main__":main()
