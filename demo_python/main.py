"""Agencia de espectros 0.5.2 — prototipo Pygame-ce para validar antes de Godot."""
import os
import math
from pathlib import Path
import pygame as pg
from modelo import World, CASES
from campana import ORDER, DIALOGUES, EXTRA, NAMES
from motor_grafico import Motor, W, H, TILE
from arte import TitleArt

SIZE=(1280,720)
MAP_X,MAP_Y=16,64
MAP_SIZE=(W*2,H*2)
SIDE_X=992
BG="#191824"; PANEL="#292638"; BORDER="#51475c"; GOLD="#e9bc83"; MINT="#b2e6d1"; INK="#e6dbcd"; MUTED="#b2a6b8"
SAVE=Path.home()/".agencia_espectros_v5.json"

STATUS={"complete":"RESUELTO","provisional":"PROVISIONAL","incomplete":"INCOMPLETO"}

class Game:
    def __init__(self,screen=None):
        if not pg.get_init():pg.init()
        if not pg.font.get_init():pg.font.init()
        desktop=pg.display.get_desktop_sizes()[0]
        width=min(1280,max(640,desktop[0]-100));height=min(720,max(360,desktop[1]-100))
        self.screen=screen if screen is not None else pg.display.set_mode((width,height),pg.RESIZABLE)
        pg.display.set_caption("Agencia de espectros • El espíritu que nunca vivió")
        self.frame=pg.Surface(SIZE)
        self.motor=Motor()
        self.title_art=None
        self.title_font=pg.font.SysFont("georgia,dejavuserif,serif",49,bold=True)
        self.world=World.new_game()
        self.clock=pg.time.Clock()
        self.fonts={}
        self.buttons=[]
        self.choice=None
        self.modal="title"
        self.dialogue=[]
        self.dialogue_index=0
        self.after_dialogue=None
        self.dialogue_tag=None
        self.pending_interaction=None
        self.last_advance=0
        self.keys_down=set()
        self.community=None
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
        if self.choice not in options:
            goal=self.world.goal()[1]
            self.choice=goal if goal in options else options[0] if options else None
        return self.choice
    def autosave(self):
        try:self.world.save(SAVE)
        except OSError:self.world.tell("No se pudo guardar automáticamente.")

    def start_game(self):
        self.world=World.new_game();self.choice=None;self.motor.reset_motion()
        self.open_dialogue("accident",force=True)

    def open_dialogue(self,key,lines=None,after=None,force=False):
        tag="dialogue:"+key
        if not force and tag in self.world.visited:return False
        lines=lines or DIALOGUES.get(key)
        if not lines:return False
        self.dialogue_tag=tag
        self.dialogue=lines;self.dialogue_index=0;self.after_dialogue=after
        self.modal="dialogue";self.move_clock=0.
        return True

    def next_dialogue(self):
        if self.modal!="dialogue":return
        self.dialogue_index+=1
        if self.dialogue_index>=len(self.dialogue):
            after=self.after_dialogue;self.after_dialogue=None
            if self.dialogue_tag:self.world.mark(self.dialogue_tag)
            self.dialogue_tag=None
            pending=self.pending_interaction;self.pending_interaction=None
            self.close_modal()
            if pending:
                self.choice=pending
                self.interact(False,True)
            if after:self.modal=after
            self.autosave()

    def open_cases(self):
        if self.world.place=="office" and self.world.stage!="agency":
            self.world.tell("Sigue el objetivo de la introducción. El tablón se desbloquea al fundar la agencia.");return
        self.modal="cases";self.result="";self.move_clock=0.
    def open_evidence(self,case=None):
        self.review_case=case or self.world.place
        if self.review_case not in CASES:self.open_cases();return
        self.modal="evidence"
        self.selected=set(self.world.facts[self.review_case])
        self.hypothesis=None;self.result="";self.move_clock=0.
    def close_modal(self):
        self.modal=None;self.move_clock=0.;self.result=""
    def interact(self,power=False,commit=False):
        w=self.world;k=self.current_target()
        if k is None:return
        if not (w.power_action(k)[1] if power else w.interaction(k)[1]):return
        if not power and not commit and not w.ghost_mode:
            key=w.place+":"+k
            if key=="office:rafael" and w.stage=="dispatch":
                if "dialogue:"+key in w.visited:self.modal="rafael_choice"
                else:self.open_dialogue(key,after="rafael_choice")
                return
            if key in DIALOGUES and key!="cine:client" and not (key=="cine:guard" and "request" not in w.facts["cine"]):
                if "dialogue:"+key not in w.visited:
                    if self.open_dialogue(key):self.pending_interaction=k;return
            if key=="cine:client" and w.practice_done and "dialogue:"+key not in w.visited:
                if self.open_dialogue(key):self.pending_interaction=k;return
            if k.startswith("request_"):
                case=k[8:];lines=DIALOGUES.get("office:guest") if case=="station" else EXTRA[case]["intro"]
                if "dialogue:"+key not in w.visited and self.open_dialogue(key,lines):self.pending_interaction=k;return
        if w.place=="office" and w.stage=="agency" and k=="board" and not power and not w.ghost_mode:
            self.open_cases();return
        old=w.place;old_stage=w.stage;old_fact=set(w.facts.get(old,{}))
        obj=w.objects[k]
        result=w.act(k,power)
        if old!=w.place:self.choice=None;self.motor.reset_motion()
        if power:return
        key=old+":"+k
        lines=DIALOGUES.get(key)
        if old=="cine" and k=="client" and "request" not in w.facts[old]:lines=None
        if k=="witness" and old in CASES and "witness" not in w.facts[old]:lines=None
        if k=="client" and old in EXTRA and "request" in w.facts[old]:lines=EXTRA[old]["intro"]
        if k.startswith("request_") and not w.ghost_mode:
            case=k[len("request_"):]
            lines=DIALOGUES.get("office:guest") if case=="station" else EXTRA[case]["intro"]
        if k.startswith("guest_") and not w.ghost_mode:
            case=k[len("guest_"):]
            self.review_case=case
            name=obj[2].split(",")[0]
            lines=[(name,"Gracias por aclarar lo que pasó. Me gustaría decidir qué hacer ahora."),("Tomás","Aquí tienes un lugar si deseas colaborar. También puedes partir.")]
            self.open_dialogue(key,lines,after="ally",force=True);return
        if k=="wish" and "wish" in w.facts.get(old,{}):lines=[("Brizna","Quiero decidir qué hago después. No quiero que el cine decida por mí."),("Tomás","Te escucho.")]
        if k=="mora":lines=[("Brizna","Mora nos mira y mueve la cola hacia el archivo."),("Tomás","Veamos qué hay allí. No significa que ya sepamos la respuesta.")]
        if old=="office" and old_stage=="foundation" and w.stage=="agency":
            lines=[("Tomás","El tablón, la libreta y tu rincón están listos. Agencia de espectros."),("Brizna","¡Nuestra casa! ¿Podemos ayudar a otros?")]
        if old!=w.place and w.place=="office" and w.stage=="foundation":
            self.open_dialogue("foundation",force=False)
        elif lines:self.open_dialogue(key,lines)
        elif obj[3] in ("npc","ghost") and old in CASES and old_fact!=set(w.facts[old]):
            self.open_dialogue(key,[(obj[2].split(",")[0],result)])
        if old!=w.place or old_stage!=w.stage:self.autosave()

    def action(self,action):
        w=self.world
        if isinstance(action,tuple):
            kind,value=action
            if kind=="rafael":
                if value=="accept":w.accept_rafael();self.close_modal();self.autosave()
                elif value=="later":self.close_modal()
                elif value=="when":self.open_dialogue("rafael:when",[("Rafael","Comenzó hace varias noches. Primero pensé que era un fallo eléctrico.")],after="rafael_choice",force=True)
                elif value=="inside":self.open_dialogue("rafael:inside",[("Rafael","No hay visitantes autorizados. Yo tengo las llaves del vestíbulo.")],after="rafael_choice",force=True)
                return
            if kind=="ally":
                self.world.decide_ally(self.review_case,value);self.close_modal();self.autosave();return
            if kind=="community":self.community=value;return
            if kind=="ending" and self.community:
                w.choose_ending(self.community,value);self.close_modal();self.autosave();self.modal="credits";return
            if kind=="accept":
                old=w.place
                self.result=w.accept_case(value)
                if old!=w.place:self.close_modal();self.choice=None;self.motor.reset_motion();self.autosave()
            elif kind=="review":self.open_evidence(value)
            elif kind=="clue":
                if value in self.selected:self.selected.remove(value)
                else:self.selected.add(value)
            elif kind=="choice":self.hypothesis=value
            return
        if action=="new":self.start_game();return
        if action=="continue":
            try:
                self.world=World.load(SAVE);self.choice=None;self.motor.reset_motion();self.close_modal()
                if self.world.reports.get("final")=="complete" and not self.world.ending:self.modal="ending"
            except (OSError,ValueError,TypeError,KeyError) as ex:self.result="No se pudo cargar: "+str(ex)
            return
        if action=="quit":self.running=False;return
        if action=="options":self.modal="options";return
        if action=="window":
            self.screen=pg.display.set_mode((960,540),pg.RESIZABLE);return
        if action=="fullscreen":
            flag=0 if self.screen.get_flags() & pg.FULLSCREEN else pg.FULLSCREEN
            self.screen=pg.display.set_mode((0,0) if flag else (1120,630),flag or pg.RESIZABLE);return
        if action=="next_dialogue":
            now=pg.time.get_ticks()
            if now-self.last_advance>=180:self.last_advance=now;self.next_dialogue()
            return
        if action=="pause":self.modal="pause";return
        if action=="save_pause":self.autosave();self.result="Partida guardada.";return
        if action=="title":self.modal="title";return
        if action=="close":self.close_modal();return
        if action=="cases":self.open_cases();return
        if action=="submit":
            if self.hypothesis is None:self.result="Elige primero una hipótesis."
            else:
                case=self.review_case;before=w.reports.get(case)
                self.result=w.resolve(case,self.hypothesis,list(self.selected))
                if before!="complete" and w.reports.get(case)=="complete":
                    self.open_dialogue(case+":closing",DIALOGUES.get(case+":closing") or EXTRA[case]["closing"],after="ending" if case=="final" else None,force=True)
                    self.autosave()
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
            elif w.place in CASES:self.open_evidence()
            else:w.tell("Sigue el objetivo de la introducción.")
        elif action=="c":
            names=list(w.spirits)
            w.choose_spirit(names[(names.index(w.active)+1)%len(names)])
            self.motor.reset_motion()

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
                tx,ty=int((mx/2+self.motor.camera[0])//TILE),int((my/2+self.motor.camera[1])//TILE)
                for k,(x,y,*_) in self.world.objects.items():
                    if (tx,ty)==(x,y) and k in self.world.nearby():self.choice=k;return
    def event(self,e):
        if e.type==pg.QUIT:self.running=False;return
        if e.type==pg.VIDEORESIZE:
            self.screen=pg.display.set_mode((max(640,e.w),max(360,e.h)),pg.RESIZABLE);return
        if e.type==pg.MOUSEBUTTONDOWN and e.button==1:self.click(e.pos);return
        if e.type==pg.KEYUP:self.keys_down.discard(e.key);return
        if e.type==getattr(pg,"WINDOWFOCUSLOST",-1):self.keys_down.clear();return
        if e.type!=pg.KEYDOWN:return
        if e.key in self.keys_down:return
        self.keys_down.add(e.key)
        key=pg.key.name(e.key)
        if self.modal:
            if self.modal=="dialogue":
                if e.key in (pg.K_RETURN,pg.K_SPACE,pg.K_e):self.action("next_dialogue")
                return
            if self.modal=="title":
                if e.key==pg.K_RETURN:self.start_game()
                return
            if self.modal=="options":
                if e.key==pg.K_ESCAPE:self.modal="title"
                return
            if e.key in (pg.K_ESCAPE,pg.K_TAB) and self.modal not in ("ending","credits"):self.close_modal()
            elif self.modal=="cases" and pg.K_1<=e.key<=pg.K_6:
                self.action(("accept",ORDER[e.key-pg.K_1]))
            elif self.modal=="evidence" and e.key in (pg.K_1,pg.K_2,pg.K_3):
                self.action(("choice",e.key-pg.K_1))
            elif self.modal=="evidence" and e.key==pg.K_RETURN:self.action("submit")
            return
        if e.key==pg.K_ESCAPE:self.modal="pause";return
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
        if self.modal in ("title","options"):
            self.draw_title(dt);return self.frame
        self.text("AGENCIA DE ESPECTROS",18,15,29,GOLD,True)
        self.text("Agencia de espectros" if w.place=="office" and w.stage=="agency" else NAMES[w.place],438,18,23,MINT,True)
        self.text("REFUGIO" if w.place=="office" and w.stage=="agency" else "INVESTIGACIÓN" if w.place in CASES else "PRÓLOGO",994,20,20,MUTED)
        self.panel((12,60,MAP_SIZE[0]+8,MAP_SIZE[1]+8),"#292533")
        scene=self.motor.draw(w,0. if self.modal else dt,None if self.modal=="dialogue" else self.current_target(),None if self.modal=="dialogue" else w.goal()[1],native=True)
        self.frame.blit(scene,(MAP_X,MAP_Y))
        self.draw_hud()
        self.draw_log()
        if self.show_fps:self.text(f"FPS {self.fps:.1f}",20,42,16,MUTED)
        if self.modal:self.draw_modal()
        return self.frame

    def draw_hud(self):
        w=self.world;x=SIDE_X
        self.panel((x,64,272,528))
        self.text("OBJETIVO ACTUAL",x+15,79,20,GOLD,True)
        goal,target=w.goal()
        self.wrap(goal,x+15,106,242,23,INK,True,4)
        if target in w.objects:
            self.wrap("Busca: "+w.objects[target][2],x+15,201,240,19,MINT,limit=2)
        self.text("CONTROL · "+(w.active if w.ghost_mode else "Tomás"),x+15,251,22,GOLD,True)
        if w.companion_present:
            self.text(f"{w.active} · Vínculo {w.spirit.bond}",x+15,286,20,MINT,True)
            self.text(f"Energía {int(w.spirit.energy)}/100",x+15,312,19)
            self.bar(x+15,335,242,w.spirit.energy,"#76b9aa")
            self.text(f"Estabilidad {int(w.spirit.stability)}/100",x+15,351,19)
            self.bar(x+15,374,242,w.spirit.stability,"#b19bd2")
            state="Libre" if w.place=="office" else "Crítico" if w.spirit.stability<20 else "Inestable" if w.distance>w.spirit.radius else "Estable"
            self.panel((x+12,389,248,54),"#383344")
            self.text("Refugio sin límite" if w.place=="office" else f"Distancia {w.distance}/{w.spirit.radius}",x+22,395,21,MINT,True)
            self.text(state,x+22,420,18,"#e8ae8a" if state in ("Crítico","Inestable") else MINT)
        else:self.wrap("WASD o flechas: caminar. E: interacción.",x+15,292,237,21,MUTED,limit=3)
        if w.alert_enabled():
            npcs=[(abs(o[0]-w.x)+abs(o[1]-w.y),key,o) for key,o in w.objects.items() if o[3]=="npc"]
            if npcs:
                _,key,o=min(npcs);v=w.alert_value(key)
                state="Alarmado" if v>=75 else "Inquieto" if v>=50 else "Atento" if v>=25 else "Tranquilo"
                self.text("ALERTA · "+o[2].split(",")[0][:16],x+15,455,18,GOLD,True)
                self.text(state+f" · {int(v)}",x+15,478,18,INK)
                self.bar(x+15,503,242,v,"#e49e79" if v>=50 else "#a9c791")
        enabled=w.place in CASES or (w.place=="office" and w.stage=="agency")
        self.button((x+15,535,242,40),"TAB · EXPEDIENTES","tab",enabled,True)

    def draw_log(self):
        w=self.world;k=self.current_target()
        self.panel((16,605,960,99))
        self.text("INTERACCIÓN",29,614,18,GOLD,True)
        self.wrap(w.objects[k][2] if k else "Acércate al marcador dorado",29,636,280,20,INK,True,1)
        verb,enabled=w.interaction(k);power,valid=w.power_action(k)
        self.button((29,668,140,27),"E · "+verb.upper(),"e",enabled)
        self.button((176,668,140,27),"ESP · "+power.upper(),"space",valid)
        self.text("BITÁCORA",333,614,18,GOLD,True)
        if w.log:self.wrap(w.log[-1],333,636,625,20,INK,limit=3)
        self.panel((SIDE_X,605,272,99))
        self.text("WASD · Mover",SIDE_X+13,619,20)
        self.text("Esc · Ayuda y pausa",SIDE_X+13,650,20,MINT)
        self.text("F3 · FPS",SIDE_X+13,678,17,MUTED)

    def draw_title(self,dt):
        if self.title_art is None:self.title_art=TitleArt()
        self.frame.blit(pg.transform.scale(self.title_art.draw(dt),SIZE),(0,0))
        if self.modal=="options":
            self.text("OPCIONES",70,100,43,GOLD,True)
            self.button((70,185,360,48),"VENTANA 960 × 540","window")
            self.button((70,246,360,48),"PANTALLA COMPLETA","fullscreen")
            self.button((70,307,360,48),"VOLVER","title",accent=True)
            self.wrap("WASD o flechas: mover · E: interacción · Q: cambiar · R: regresar · TAB: cuaderno.",70,390,420,23,INK)
        else:
            self.text("SANTA BRUMA  /  EXPEDIENTE 001",72,76,20,MINT,True)
            for i,txt in enumerate(("AGENCIA DE","ESPECTROS")):
                im=self.title_font.render(txt,True,GOLD)
                self.frame.blit(im,(70,121+i*58))
            pg.draw.line(self.frame,"#bc9869",(73,248),(440,248),2)
            self.text("El espíritu que nunca vivió",73,268,29,INK)
            for i,(label,action,enabled) in enumerate((("NUEVA PARTIDA","new",True),("CONTINUAR","continue",SAVE.exists()),("OPCIONES","options",True),("SALIR","quit",True))):
                box=pg.Rect(73,330+i*57,345,45)
                self.button(box,label,action,enabled,i==0)
                if enabled and box.collidepoint(self.logical(pg.mouse.get_pos()) or (-1,-1)):
                    pg.draw.rect(self.frame,GOLD,box,2,border_radius=5)
            self.wrap("Algunos casos no terminan cuando muere la víctima.",73,581,390,23,"#d8c7b5",limit=2)
            if self.result:self.wrap(self.result,73,639,500,19,GOLD,limit=2)
        self.text("PROTOTIPO 0.5.2",73,689,17,"#b4b6b8")
        self.text("CINE AURORA  •  NOCHE",991,689,17,"#d9c9af")

    def draw_modal(self):
        overlay=pg.Surface(SIZE,pg.SRCALPHA);overlay.fill((10,9,17,85 if self.modal=="dialogue" else 205));self.frame.blit(overlay,(0,0))
        # Underlying buttons are not active while the modal is open.
        self.buttons.clear()
        if self.modal!="dialogue":self.panel((170,45,940,630),"#242232","#827186",10)
        if self.modal=="dialogue":
            self.panel((197,395,886,255),"#292738","#b39b87")
            speaker,line=self.dialogue[self.dialogue_index]
            isghost=speaker in ("Brizna","Elena","Mateo","Silvia","Nico","Clara","Mora","Silueta")
            if speaker!="Narrador":
                portrait=self.motor.get_sprite(speaker,isghost,"down",0,False)
                self.frame.blit(pg.transform.scale(portrait,(96,152)),(226,425))
            self.text(speaker,354,422,29,GOLD,True)
            self.wrap(line,354,467,674,27,INK,limit=4)
            self.text(f"{self.dialogue_index+1}/{len(self.dialogue)}",354,603,18,MUTED)
            self.button((804,595,247,40),"CONTINUAR · E / ENTER","next_dialogue",accent=True)
            return
        if self.modal=="rafael_choice":
            self.text("EL ENCARGO DE RAFAEL",640,130,38,GOLD,True,True)
            self.wrap("Tomás puede hacer preguntas antes de aceptar el encargo.",270,202,740,25,INK)
            for i,(label,value) in enumerate((("¿Desde cuándo sucede?","when"),("¿Hay alguien dentro?","inside"),("Iré a revisar","accept"),("Dame un momento","later"))):
                self.button((340,278+i*65,600,49),label,("rafael",value),True,value=="accept")
            return
        if self.modal=="pause":
            self.text("PAUSA",640,130,40,GOLD,True,True)
            self.button((470,220,340,45),"VOLVER AL JUEGO","close",accent=True)
            self.button((470,278,340,45),"GUARDAR PARTIDA","save_pause")
            self.button((470,336,340,45),"MENÚ PRINCIPAL","title")
            self.button((470,394,340,45),"SALIR","quit")
            self.wrap("WASD / flechas: mover · E: interactuar · Q: cambiar · Espacio: poder · R: volver · TAB: cuaderno · F: objetivo cercano",250,485,780,23,MUTED)
            if self.result:self.text(self.result,250,570,23,MINT)
            return
        if self.modal=="ally":
            name={"station":"Mateo","workshop":"Nico","ruiz":"Mora"}[self.review_case]
            self.text("UNA NUEVA ETAPA",640,150,40,GOLD,True,True)
            self.wrap(name+" puede elegir quedarse en el refugio o partir. No es una obligación ni una condición para seguir investigando.",280,220,720,29,INK)
            self.button((325,372,630,52),"OFRECERLE UN LUGAR EN LA AGENCIA",("ally",True),accent=True)
            self.button((325,444,630,52),"DESPEDIRNOS CON RESPETO",("ally",False))
            return
        if self.modal=="ending":
            self.text("EL FUTURO DEL CINE",194,63,34,GOLD,True)
            self.wrap("El informe demuestra que hay alternativas viables. Elige qué propuesta apoyar y escucha el futuro que Brizna desea.",194,113,875,25,INK)
            for i,name in enumerate(("centro cultural","archivo","traslado")):
                self.button((220+i*290,222,275,50),name.upper(),("community",name),True,self.community==name)
            self.text("Brizna quiere elegir...",194,322,28,MINT,True)
            for i,(label,value) in enumerate((("Quedarme con la agencia","agencia"),("Explorar nuevos lugares","explorar"),("Colaborar de otra manera","colaborar"))):
                self.button((365,371+i*65,550,49),label,("ending",value),self.community is not None,True)
            return
        if self.modal=="credits":
            self.text("EL ESPÍRITU QUE NUNCA VIVIÓ",640,145,40,GOLD,True,True)
            self.wrap("Seis expedientes resueltos. La comunidad apoya "+self.world.community_choice+". Brizna decide "+self.world.ending+".",275,230,730,28,INK)
            self.wrap("No necesita haber vivido antes para tener una historia propia.",275,350,730,28,MINT)
            self.button((450,485,380,50),"VOLVER AL JUEGO","close",accent=True)
            return
        self.button((982,62,110,31),"CERRAR","close")
        if self.modal=="cases":
            self.text("TABLÓN DE LA AGENCIA",194,63,31,GOLD,True)
            self.wrap("Habla con el cliente, elige tu compañero con C y acepta junto al tablón.",194,103,875,22,MUTED)
            for i,case in enumerate(ORDER):
                cfg=CASES[case];y=156+i*71
                enabled=self.world.available(case)
                complete=self.world.reports.get(case)=="complete"
                near=self.world.place=="office" and self.world.stage=="agency" and not self.world.ghost_mode and "board" in self.world.nearby()
                self.panel((194,y,892,64),"#312c40")
                self.text(f"0{i+1} / "+cfg["title"],208,y+8,25,INK,True)
                label="ARCHIVADO" if complete else "DISPONIBLE" if enabled and case in self.world.requests else "HABLA CON EL CLIENTE" if enabled else "BLOQUEADO"
                self.text(label,208,y+36,17,MINT if enabled else MUTED)
                self.button((665,y+13,190,36),"REVISAR",("review",case),enabled)
                self.button((865,y+13,207,36),("CONTINUAR" if case in self.world.accepted else "ACEPTAR"),("accept",case),enabled and not complete and near and case in self.world.requests,True)
            if self.result:self.wrap(self.result,194,594,875,21,GOLD,limit=2)
            else:self.text("Teclas 1–6: elegir · Esc: volver",194,603,21,MUTED)
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
        self.screen.blit(self.frame if v.size==SIZE else pg.transform.smoothscale(self.frame,v.size),v.topleft)
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
