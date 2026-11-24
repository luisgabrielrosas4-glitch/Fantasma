"""Agencia de espectros v0.2: interfaz de escritorio sin dependencias externas."""
import tkinter as tk
from pathlib import Path
import time
from motor_grafico import Motor
from modelo import World, CASES, WALLS, WIDTH, HEIGHT

T=32
MW=WIDTH*T
H=600
BG="#181825"
INK="#e8e0d5"
MINT="#afe1ce"
GOLD="#dfb57e"
SAVE=Path.home()/".agencia_espectros_v2.json"
NAMES={"cine":"Cine Aurora","office":"Agencia de espectros","station":"Estación del barrio"}
COLORS={"cine":("#594552","#725764","#382f40"),"office":("#675447","#866e58","#413747"),"station":("#465962","#5c7279","#2c3945")}

class Game:
    def __init__(self,root):
        self.root=root
        self.world=World()
        self.held=set()
        self.choice=None
        self.paused=False
        self.board=None
        self.frame=0
        self.last_time=time.monotonic()
        self.move_clock=0.0
        self.hud_signature=None
        self.frame_dt=0.0
        self.buttons=[]
        root.title("Agencia de espectros | El espíritu que nunca vivió")
        root.resizable(False,False)
        self.cv=tk.Canvas(root,width=960,height=H,bg=BG,highlightthickness=0)
        self.cv.pack()
        self.motor=Motor(self.cv)
        root.bind("<KeyPress>",self.press)
        root.bind("<KeyRelease>",lambda e:self.held.discard(e.keysym.lower()))
        root.bind("<FocusOut>",lambda e:self.held.clear())
        self.cv.bind("<Button-1>",self.click)
        self.world.tell("Tras sobrevivir a un accidente, Tomás escucha voces en el cine cerrado. Busca a Elena y Brizna.")
        self.render()
        root.after(33,self.loop)

    def rect(self,x,y,w,h,fill,outline="",width=1):
        self.cv.create_rectangle(x,y,x+w,y+h,fill=fill,outline=outline,width=width)
    def line(self,*p,fill,width=1,dash=None):
        self.cv.create_line(*p,fill=fill,width=width,dash=dash)
    def oval(self,x,y,w,h,fill,outline=""):
        self.cv.create_oval(x,y,x+w,y+h,fill=fill,outline=outline)
    def poly(self,*p,fill,outline=""):
        self.cv.create_polygon(*p,fill=fill,outline=outline)
    def text(self,x,y,s,size=10,color=INK,anchor="nw",width=0,bold=False):
        self.cv.create_text(x,y,text=s,fill=color,font=("Segoe UI",size,"bold" if bold else "normal"),anchor=anchor,width=width)
    def bar(self,x,y,w,value,color):
        self.rect(x,y,w,8,"#3c3648")
        self.rect(x,y,int(w*max(0,min(100,value))/100),8,color)
    def button(self,x,y,w,h,title,key):
        self.rect(x,y,w,h,"#3e3a4f","#655d74")
        self.text(x+w/2,y+h/2,title,10,MINT,"center",bold=True)
        self.buttons.append((x,y,w,h,key))

    def actor(self,x,y,name,ghost=False,active=False,weak=False,identity=None):
        self.motor.actor(x,y,name,ghost,active,weak,identity)

    def prop(self,key,obj):
        x,y,name,kind=obj
        w=self.world
        cx,cy=x*T+16,y*T+16
        if kind in ("npc","ghost"):
            if key=="brizna" and w.met:return
            if key=="client" and w.reports.get(w.place)=="complete":return
            if key=="guest" and w.guest_decision=="stayed" and w.active=="Mateo":return
            self.actor(x,y,name.split(",")[0],kind=="ghost",weak=key=="guest" and not w.guest_decision,identity="npc:"+key)
        elif kind=="paper":
            self.rect(cx-15,cy-8,30,21,"#654f46","#322a36")
            self.rect(cx-15,cy-9,30,6,"#a38268")
            self.rect(cx-8,cy-12,16,13,"#e0cda6","#78685c")
            self.line(cx-5,cy-8,cx+5,cy-8,fill="#886e5d")
            self.line(cx-5,cy-4,cx+3,cy-4,fill="#886e5d")
        elif kind=="box":
            self.rect(cx-14,cy-12,28,26,"#76604f","#352e38")
            self.rect(cx-12,cy-10,24,9,"#ac8a67")
            self.rect(cx-4,cy,8,7,"#d1b68a","#5e4c46")
        elif kind=="device":
            self.rect(cx-13,cy-9,26,21,"#9c7960","#322c39")
            self.rect(cx-9,cy-5,13,11,"#45404c")
            for i in range(3):self.line(cx-7,cy-2+i*3,cx+1,cy-2+i*3,fill="#b8a69b")
            self.oval(cx+5,cy-3,5,5,GOLD)
            if w.distracted:self.text(cx,cy-16,"♪",14,MINT,"center")
        elif kind=="door":
            self.rect(cx-15,cy-15,30,30,"#809d8c" if w.permissions[w.place] or w.distracted>0 else "#996f60","#3b3341")
            self.rect(cx+6,cy-2,5,5,GOLD)
        elif kind=="home":
            self.rect(cx-15,cy-8,30,23,"#79604f","#41384b")
            self.oval(cx-8,cy-17,16,17,"#84bdad","#dcdfb0")
        elif kind=="board":
            self.rect(cx-14,cy-17,29,30,"#514553","#c9ac8b",2)
            for dx,dy in [(-9,-11),(3,-8),(-7,4)]:self.rect(cx+dx,cy+dy,8,7,"#e6d5b8")
            self.line(cx-5,cy-8,cx+7,cy-5,cx-3,cy+7,fill="#d28d86")
        else:
            self.rect(cx-14,cy-14,28,28,"#4d625d","#a9b995")
            self.text(cx,cy,"↗",17,MINT,"center",bold=True)

    def target(self):
        cs=self.world.nearby()
        if self.choice not in cs:self.choice=cs[0] if cs else None
        return self.choice

    def render(self):
        w=self.world
        self.motor.begin(w.place,self.frame_dt)
        self.frame_dt=0.
        before=set(self.cv.find_all())
        if w.ghost_mode:self.motor.anchor(w)
        # Orden Y: los personajes pueden aparecer por delante o detrás de muebles.
        items=[(o[1],0,k,o) for k,o in w.objects.items()]
        items.append((w.y,1,"human",None))
        if w.met:items.append((w.gy,2,"companion",None))
        for _,layer,k,o in sorted(items,key=lambda e:(e[0],e[1])):
            if layer==0:self.prop(k,o)
            elif layer==1:self.actor(w.x,w.y,"Tomás",active=not w.ghost_mode,identity="human")
            else:self.actor(w.gx,w.gy,w.active,True,w.ghost_mode,w.spirit.stability<40,identity="companion:"+w.active)
        k=self.target()
        if k:
            x,y,*_=w.objects[k]
            self.rect(x*T+1,y*T+1,30,30,"",MINT,2)
        self.motor.finish(before)
        # El HUD solo se reconstruye si cambian los datos que muestra.
        signature=(w.place,w.met,w.ghost_mode,w.active,int(w.spirit.energy),
                   int(w.spirit.stability),w.spirit.bond,w.spirit.home,
                   tuple(w.reports.items()),w.home_open,
                   tuple((key,tuple(value)) for key,value in w.facts.items()),
                   tuple((key,tuple(value)) for key,value in w.physical.items()),
                   tuple(w.spirits),w.guest_decision,int(w.wanderer.stability),
                   k,w.objects[k][2] if k else "",tuple(w.log[-2:]))
        if signature==self.hud_signature:return
        self.hud_signature=signature
        self.cv.delete("hud");self.buttons.clear()
        before=set(self.cv.find_all())
        self.rect(0,0,MW,30,BG)
        self.text(11,5,NAMES[w.place],13,GOLD,bold=True)
        self.text(MW-10,8,"MOTOR 0.3",9,MINT,"ne")
        self.rect(MW,0,320,H,"#282536")
        self.text(654,13,"AGENCIA DE ESPECTROS",14,MINT,bold=True)
        self.text(654,43,"Control: "+(w.active if w.ghost_mode else "Tomás"),11,GOLD)
        if w.met:
            self.text(654,72,f"{w.active} · Energía {int(w.spirit.energy)}",10)
            self.bar(654,92,290,w.spirit.energy,"#70b9ac")
            self.text(654,110,f"Estabilidad {int(w.spirit.stability)} · Vínculo {w.spirit.bond}",10)
            self.bar(654,131,290,w.spirit.stability,"#b3a1d5")
            anchor="Agencia" if w.place=="office" and w.spirit.home else ("Tomás" if w.spirit.bond else "Cine")
            self.text(654,147,f"Ancla: {anchor} · Alcance: {w.spirit.radius}",10,MINT)
        else:self.text(654,72,"Encuentra a Brizna en el cine.",10,MINT)
        self.text(654,181,"EXPEDIENTES",11,GOLD,bold=True)
        for i,(case,cfg) in enumerate(CASES.items()):
            report=w.reports.get(case,"abierto")
            if case=="station" and not w.home_open:report="bloqueado"
            label={"complete":"resuelto","incomplete":"incompleto","provisional":"provisional"}.get(report,report)
            self.text(654,206+i*24,cfg["title"]+" · "+label,10)
        if w.case:
            self.text(654,261,"PISTAS DEL LUGAR",10,GOLD,bold=True)
            for i,key in enumerate(w.facts[w.place]):
                physical=key in w.physical[w.place]
                clue=w.case["clues"][key]
                self.text(654,283+i*17,("◆ " if physical else "◇ ")+clue[:39]+("…" if len(clue)>39 else ""),9,MINT if physical else INK)
        else:
            self.text(654,262,"COMPAÑEROS",11,GOLD,bold=True)
            self.text(654,287," / ".join(w.spirits),10,MINT)
            if not w.guest_decision:self.text(654,310,f"Mateo errante · estabilidad {int(w.wanderer.stability)}",10)
            self.text(654,334,"C: cambiar compañero",10)
            if w.reports.get("station")=="complete" and not w.guest_decision:self.text(654,355,"J: invitar / P: despedirse (junto a Mateo)",9)
        self.button(654,405,290,36,"TAB · TABLERO DE EVIDENCIAS","tab")
        self.button(654,450,140,35,"CAMBIAR [Q]","q")
        self.button(804,450,140,35,"ANCLA [R]","r")
        self.button(654,496,140,35,"GUARDAR [F5]","f5")
        self.button(804,496,140,35,"CARGAR [F9]","f9")
        self.text(654,550,"◇ Observado   ◆ Evidencia física",10,"#aaa0b2")
        self.rect(0,HEIGHT*T,MW,H-HEIGHT*T,BG)
        self.text(12,363,"WASD / Flechas: mover · E: interactuar · ESPACIO: poder · F: objetivo",10,MINT)
        self.text(12,391,"OBJETO: "+(w.objects[k][2] if k else "Acércate a uno"),12,GOLD,bold=True)
        self.button(12,420,140,34,"INTERACTUAR E","e")
        self.button(160,420,140,34,"PODER ESPACIO","space")
        self.button(308,420,125,34,"OBJETIVO F","f")
        self.rect(12,469,616,118,"#2d293a","#51485d")
        self.text(22,480,"BITÁCORA",10,GOLD,bold=True)
        for i,msg in enumerate(w.log[-2:]):self.text(22,502+i*38,msg,10,INK,width=590)
        self.motor.capture("hud",before)
        self.cv.tag_raise("hud")

    def command(self,key):
        w=self.world
        if key in ("e","space"):
            k=self.target()
            if k:w.act(k,key=="space")
            else:w.tell("No hay objeto al alcance.")
        elif key=="q":w.toggle();self.choice=None
        elif key=="r":w.recall();self.choice=None;self.motor.reset_motion()
        elif key=="f":
            cs=w.nearby();k=self.target()
            if cs:self.choice=cs[(cs.index(k)+1)%len(cs)]
        elif key=="c":
            names=list(w.spirits)
            w.choose_spirit(names[(names.index(w.active)+1)%len(names)])
        elif key=="j":w.recruit()
        elif key=="p":w.release_guest()
        elif key=="f5":
            try:w.save(SAVE);w.tell("Partida guardada.")
            except OSError as ex:w.tell("No se pudo guardar: "+str(ex))
        elif key=="f9":
            try:self.world=World.load(SAVE);self.world.tell("Partida cargada.");self.choice=None;self.motor.reset_motion()
            except (OSError,ValueError,TypeError,KeyError) as ex:w.tell("No se pudo cargar: "+str(ex))
        elif key=="tab":self.open_board();return
        self.render()

    def press(self,e):
        if self.paused:return
        key=e.keysym.lower()
        if key in ("w","a","s","d","up","down","left","right"):self.held.add(key);return
        self.command(key)
        if key=="tab":return "break"

    def loop(self):
        now=time.monotonic()
        dt=min(.15,max(0.,now-self.last_time))
        self.last_time=now
        if not self.paused:
            self.move_clock+=dt
            # La lógica sigue avanzando en casillas a ~8 pasos/s.
            if self.move_clock>=.125:
                self.move_clock-=.125
                for key,dx,dy in [("w",0,-1),("up",0,-1),("s",0,1),("down",0,1),("a",-1,0),("left",-1,0),("d",1,0),("right",1,0)]:
                    if key in self.held:self.world.move(dx,dy);self.choice=None;break
            self.world.tick(dt)
            self.frame_dt=dt
            self.frame+=1
            self.render()
        else:self.move_clock=0.
        self.root.after(33,self.loop)

    def click(self,e):
        if self.paused:return
        for x,y,w,h,key in self.buttons:
            if x<=e.x<=x+w and y<=e.y<=y+h:self.command(key);return
        for key,(x,y,_,_) in self.world.objects.items():
            if (e.x//T,e.y//T)==(x,y) and key in self.world.nearby():self.choice=key;self.render();return

    def open_board(self):
        if self.board:return
        self.paused=True;self.held.clear()
        top=tk.Toplevel(self.root);self.board=top
        top.title("Expedientes");top.configure(bg=BG)
        top.geometry("740x650");top.transient(self.root);top.grab_set()
        def close():
            top.grab_release();top.destroy();self.board=None;self.paused=False;self.last_time=time.monotonic();self.render()
        top.protocol("WM_DELETE_WINDOW",close);top.bind("<Escape>",lambda e:close())
        case=tk.StringVar(value=self.world.place if self.world.place in CASES else ("station" if self.world.home_open else "cine"))
        header=tk.Frame(top,bg=BG);header.pack(fill="x",padx=14,pady=12)
        body=tk.Frame(top,bg=BG);body.pack(fill="both",expand=True,padx=18)
        def lab(s,color=INK,size=11):
            tk.Label(body,text=s,bg=BG,fg=color,font=("Segoe UI",size),wraplength=680,justify="left").pack(anchor="w",pady=4)
        def build():
            for widget in body.winfo_children():widget.destroy()
            k=case.get();cfg=CASES[k];w=self.world
            lab(cfg["title"],GOLD,18);lab(cfg["client"])
            lab("Selecciona las evidencias que respaldan tu hipótesis.",MINT)
            flags={}
            for key,clue in cfg["clues"].items():
                if key not in w.facts[k]:continue
                v=tk.BooleanVar(value=True);flags[key]=v
                label=("◆ " if key in w.physical[k] else "◇ ")+clue
                tk.Checkbutton(body,text=label,variable=v,bg=BG,fg=INK,activebackground=BG,activeforeground=MINT,selectcolor="#302d40",wraplength=665,justify="left").pack(anchor="w")
            lab("HIPÓTESIS",GOLD)
            choice=tk.IntVar(value=-1)
            for i,label in enumerate(cfg["choices"]):
                tk.Radiobutton(body,text=label,value=i,variable=choice,bg=BG,fg=INK,selectcolor="#302d40",activebackground=BG,activeforeground=MINT,wraplength=665,justify="left").pack(anchor="w")
            result=tk.Label(body,text="",bg=BG,fg=GOLD,wraplength=670,justify="left");result.pack(anchor="w",pady=10)
            def submit():
                if choice.get()<0:result.config(text="Selecciona una hipótesis.");return
                result.config(text=w.resolve(k,choice.get(),[key for key,v in flags.items() if v.get()]))
            tk.Button(body,text="Presentar conclusión",command=submit,bg="#506d65",fg="white").pack(anchor="w")
        for k in CASES:
            if k=="station" and not self.world.home_open:continue
            tk.Radiobutton(header,text=CASES[k]["title"],variable=case,value=k,bg=BG,fg=MINT,selectcolor="#3c344b",activebackground=BG,activeforeground=MINT,command=build).pack(side="left",padx=12)
        build()
        tk.Button(top,text="Volver a investigar",command=close,bg="#51435c",fg="white",padx=12,pady=6).pack(pady=10)

def main():
    root=tk.Tk()
    Game(root)
    root.mainloop()

if __name__=="__main__":main()
