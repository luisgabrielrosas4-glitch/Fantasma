"""Demo gráfica de Agencia de espectros (Python 3, Tkinter)."""
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import math
import random
from modelo import World, OBJECTS, CLUES, VERDICTS

W,H,T = 960,610,32
MW,MH = 704,416
BG = "#181525"
INK = "#dfd5d2"
MINT = "#a8e8d3"
GOLD = "#e7b67d"
SAVE = Path.home()/".agencia_espectros_demo.json"
LABELS = {"lampara":"Lámpara", "radio":"Radio", "registro":"Registro", "armario":"Armario",
          "cuadro":"Cuadro", "sofa":"Sofá", "archivo":"Archivo", "escritorio":"Escritorio",
          "ancla1":"Ancla", "ancla2":"Ancla", "reloj":"Reloj", "puerta":"Puerta"}

class Game:
    def __init__(self, root):
        self.root=root
        self.world=World()
        self.root.title("Agencia de espectros | El reloj del conserje")
        self.root.resizable(False, False)
        self.cv=tk.Canvas(root,width=W,height=H,bg=BG,highlightthickness=0)
        self.cv.pack()
        self.choice=None
        self.held=set()
        self.paused=False
        self.board=None
        self.frame=0
        self.root.bind("<KeyPress>", self.press)
        self.root.bind("<KeyRelease>", self.release)
        self.root.bind("<FocusOut>", lambda e:self.held.clear())
        self.cv.bind("<Button-1>",self.click)
        self.world.tell("Un espíritu acusa a su hermano de robar una carta. Investiga antes de acusar.")
        self.render()
        self.root.after(100,self.motion)
        self.root.after(1000,self.tick)

    def rect(self,x,y,w,h,fill,outline="",width=1):
        return self.cv.create_rectangle(x,y,x+w,y+h,fill=fill,outline=outline,width=width)
    def line(self,*coords,fill,width=1):
        self.cv.create_line(*coords,fill=fill,width=width)
    def text(self,x,y,s,size=10,color=INK,anchor="nw",width=0,bold=False):
        self.cv.create_text(x,y,text=s,fill=color,font=("Consolas",size,"bold" if bold else "normal"),anchor=anchor,width=width)
    def ellipse(self,x,y,w,h,color,outline=""):
        self.cv.create_oval(x,y,x+w,y+h,fill=color,outline=outline)
    def poly(self,*pts,fill,outline=""):
        self.cv.create_polygon(*pts,fill=fill,outline=outline)
    def bar(self,x,y,w,value,color):
        self.rect(x,y,w,8,"#312a42")
        self.rect(x,y,max(0,int(w*value/100)),8,color)

    def floor(self):
        colors = ["#473c48","#4c414b","#50434c","#493e48"]
        rng=random.Random(7)
        for y in range(2,12):
            for x in range(1,21):
                c=colors[rng.randrange(len(colors))]
                if y>=9 and x<=10: c=["#46504b","#49574e","#414b45"][rng.randrange(3)]
                self.rect(x*T,y*T,T,T,c,"#3c3540")
                if rng.randrange(4)==0:
                    self.line(x*T+5,y*T+24,x*T+12,y*T+24,fill="#5a4b51")
        # Exterior, room partitions and doorways. Spectral movement crosses interior walls.
        for x,y,w,h in [(0,32,704,32),(0,64,32,320),(672,64,32,320),(0,384,704,32),
                        (352,64,32,96),(352,192,32,128),(352,352,32,32)]:
            self.rect(x,y,w,h,"#33293b","#221d2d")
            for i in range(x,x+w,32):
                for j in range(y,y+h,16):
                    self.rect(i+2,j+2,27,11,"#403347","#514154")
        self.rect(32,32,320,27,"#583c4c")
        self.rect(384,32,288,27,"#433849")
        self.text(44,38,"CASA DE LOS RUIZ",11,GOLD,bold=True)
        self.text(395,38,"PORTERÍA",11,GOLD,bold=True)
        self.text(39,365,"PATIO / ARCHIVO",9,"#b1bca1")
        # carpet and courtyard
        self.rect(80,139,220,112,"#664151","#916178",2)
        self.rect(87,146,206,98,"#795063","#5b3b4b",2)
        for x in range(100,280,24):
            self.poly(x,151,x+5,157,x,163,x-5,157,fill="#b38a83")
            self.poly(x,229,x+5,235,x,241,x-5,235,fill="#b38a83")
        self.rect(400,125,244,3,"#77615f")
        for x in [52,331,409,634]:
            self.rect(x,70,22,34,"#29293a","#ac8173")
            self.rect(x+4,74,14,26,"#a56d77")
            self.line(x+11,74,x+11,100,fill="#453646")
            self.line(x+4,87,x+18,87,fill="#453646")
        for x,y in [(38,268),(317,273),(648,320)]:
            self.rect(x,y+17,19,11,"#9e664e")
            self.poly(x+9,y+22,x+2,y+4,x+8,y+10,x+12,y,x+14,y+11,x+20,y+6,fill="#78967a")
        if self.world.blocked:
            self.rect(352,160,32,32,"#9d485a","#f1b0ab")
            self.text(368,176,"×",15,"#ffe2ce","center",bold=True)
        else:
            self.rect(352,160,32,32,"#927260","#654e49")

    def furniture(self,key,px,py):
        x,y=px-14,py-12
        r=self.rect
        if key in ("escritorio","registro","archivo"):
            r(x-3,y,34,23,"#503846","#2b2433")
            r(x-3,y,34,7,"#9f705d")
            r(x+2,y+9,10,7,"#765348")
            r(x+15,y+9,10,7,"#765348")
            r(x+8,y-2,13,9,"#e5c6a0")
            self.line(x+10,y+1,x+18,y+1,fill="#95766a")
            if key=="escritorio" and not self.world.lamp:
                r(x+8,y-2,13,9,"#67535b")
        elif key=="lampara":
            if self.world.lamp:
                self.ellipse(px-25,py-23,50,46,"#887052")
            r(x+13,y+10,3,11,"#bb9e76")
            r(x+6,y+20,17,4,"#7b594b")
            self.poly(x+8,y,x+22,y,x+27,y+13,x+3,y+13,fill="#ebc17b" if self.world.lamp else "#a18b83",outline="#423340")
        elif key=="radio":
            r(x,y+2,29,21,"#926b59","#352a38")
            r(x+4,y+5,14,13,"#40313e")
            for a in range(3): self.line(x+7,y+8+a*4,x+15,y+8+a*4,fill="#ad8a78")
            self.ellipse(x+20,y+6,5,5,GOLD)
            self.line(x+20,y+1,x+26,y-8,fill="#bca5a1")
            if self.world.distraction: self.text(px,py-20,"♪",13,MINT,"center")
        elif key=="armario":
            r(x-4,y-12,36,40,"#583e49","#292530")
            r(x-2,y-9,15,33,"#926657")
            r(x+16,y-9,14,33,"#926657")
            if self.world.cabinet_open:
                r(x+1,y-8,27,30,"#362c3e")
                r(x+3,y+7,24,3,"#ab8068")
                r(x+10,y-2,12,8,"#e4c59e")
            else:
                r(x+12,y+6,3,5,GOLD);r(x+18,y+6,3,5,GOLD)
        elif key=="cuadro":
            r(x,y-6,28,29,"#b58762","#332b38",2)
            r(x+4,y-2,20,21,"#554b63")
            self.poly(x+5,y+16,x+13,y+4,x+18,y+10,x+23,y+1,x+23,y+18,fill="#819580")
        elif key=="sofa":
            r(x-15,y-2,55,28,"#443345","#2f2636")
            r(x-11,y+2,47,13,"#996477")
            r(x-11,y+16,47,7,"#775165")
            r(x-14,y+7,7,17,"#ab7884");r(x+31,y+7,7,17,"#ab7884")
        elif key.startswith("ancla"):
            self.poly(px,py-13,px+9,py,px,py+13,px-9,py,fill="#6eaea2" if key not in self.world.anchors else "#5b5360",outline="#bfdfc9")
            r(px-4,py-4,8,8,MINT if key not in self.world.anchors else "#7a707b")
        elif key=="reloj":
            self.ellipse(x+3,y-2,23,23,"#a98066","#30283a")
            self.ellipse(x+7,y+2,15,15,"#dcc7aa")
            self.line(px,py-2,px+4,py+2,fill="#4b3642")
            self.line(px,py-2,px,py-8,fill="#4b3642")

    def sprite(self,x,y,who):
        cx,cy=x*T+16,y*T+16
        self.ellipse(cx-10,cy+10,20,7,"#312938")
        if who=="ghost":
            off=(self.frame//2)%3-1
            cy+=off
            self.poly(cx-10,cy-2,cx-8,cy-13,cx+8,cy-13,cx+11,cy-2,cx+10,cy+10,cx+4,cy+8,cx,cy+13,cx-5,cy+9,cx-11,cy+12,fill="#a6e1d0",outline="#263b42")
            self.rect(cx-7,cy-17,14,6,"#42364d")
            self.rect(cx-13,cy-12,26,4,"#594259")
            self.rect(cx-6,cy-5,4,5,"#2d3443")
            self.rect(cx+3,cy-5,4,5,"#2d3443")
            self.poly(cx-9,cy+2,cx-4,cy+2,cx,cy+8,cx+6,cy+2,cx+10,cy+3,cx+8,cy+11,cx-8,cy+11,fill="#5e4a68")
        else:
            color="#7593ac" if who=="Julián" else "#aa788b"
            self.rect(cx-7,cy-12,14,11,"#d9ab8d","#392d38")
            self.rect(cx-9,cy-15,18,5,"#51404a")
            self.rect(cx-8,cy-1,16,12,color,"#392d38")
            self.rect(cx-6,cy+11,5,6,"#403448");self.rect(cx+2,cy+11,5,6,"#403448")
            self.rect(cx-4,cy-7,2,2,"#3a303a");self.rect(cx+3,cy-7,2,2,"#3a303a")
            self.text(cx,cy-20,who,8,"#f4d7bd","center")

    def candidates(self):
        w=self.world
        return sorted((k for k in OBJECTS if w.near(k)),key=lambda k: (abs(w.x-OBJECTS[k][0])+abs(w.y-OBJECTS[k][1]),k))
    def target(self):
        choices=self.candidates()
        if self.choice not in choices: self.choice=choices[0] if choices else None
        return self.choice

    def render(self):
        c=self.cv; w=self.world; c.delete("all")
        self.floor()
        for key,(x,y,_) in OBJECTS.items():
            self.furniture(key,x*T+16,y*T+16)
        self.sprite(*w.julian,"Julián");self.sprite(*w.clara,"Clara")
        key=self.target()
        if key:
            x,y,_=OBJECTS[key]
            self.rect(x*T+1,y*T+1,30,30,"",MINT,2)
        self.sprite(w.x,w.y,"ghost")
        self.rect(0,0,MW,32,BG)
        self.text(12,7,"AGENCIA DE ESPECTROS",13,MINT,bold=True)
        self.text(360,8,"CASO 01 · EL RELOJ DEL CONSERJE",10,GOLD)
        self.rect(MW,0,W-MW,H,"#252033")
        self.text(720,13,"EXPEDIENTE 01",12,GOLD,bold=True)
        self.text(720,40,"Visita "+str(w.visits)+"  |  Día "+str(w.day),10)
        self.text(720,61,"Hora de investigación: "+str(w.phase).zfill(2)+"/40",9)
        self.text(720,87,"Ectoplasma "+str(w.energy)+"/100",10,MINT)
        self.bar(720,107,220,w.energy,"#70bda9")
        self.text(720,123,"Sospecha "+str(w.suspicion)+"/100",10)
        self.bar(720,143,220,w.suspicion,"#d98489")
        self.text(720,166,"RUTINAS",10,GOLD,bold=True)
        status="Protección" if w.blocked else ("Alerta" if w.suspicion>=50 else "Curioso" if w.suspicion>=25 else "Normal")
        self.text(720,186,"Julián: "+status,10)
        self.text(720,204,"Armario: "+("abierto" if w.cabinet_open else "cerrado"),10)
        self.text(720,235,"PRUEBAS "+str(len(w.clues)-1)+"/4",10,GOLD,bold=True)
        for i,(id,(name,_)) in enumerate(CLUES.items()):
            self.text(720,260+i*23,("■ " if id in w.clues else "□ ")+name,9,MINT if id in w.clues else "#877b8e")
        self.rect(718,386,224,38,"#483953","#77617f")
        self.text(830,405,"TAB  ·  TABLERO",11,MINT,"center",bold=True)
        self.text(720,442,"R  Nueva visita\nF5 Guardar   F9 Cargar\nQ  Cambiar objetivo",10,"#b7a9bc")
        self.text(720,509,"Informe: "+(w.report or "sin cerrar").replace("_"," "),10,GOLD,width=220)
        self.text(720,558,"Demo 0.1  ·  PC",9,"#84788b")
        self.rect(0,416,MW,194,BG)
        self.text(12,429,"WASD / Flechas: mover    E: observar    ESPACIO: poseer",11,MINT)
        self.text(12,453,"OBJETO: "+(LABELS[key] if key else "Acércate a uno"),11,GOLD,bold=True)
        if key: self.text(12,476,OBJECTS[key][2],10,INK,width=680)
        self.rect(12,509,680,87,"#292337","#45374d")
        self.text(22,519,"BITÁCORA",9,GOLD,bold=True)
        for i,msg in enumerate(w.log[-2:]):
            self.text(22,540+i*24,msg,10,INK,width=660)

    def press(self,e):
        if self.paused: return
        key=e.keysym.lower()
        if key in ("w","a","s","d","up","down","left","right"):
            self.held.add(key);return
        if key in ("e","space"):
            k=self.target()
            if k:self.world.interact(k,key=="space")
            else:self.world.tell("No hay objetos al alcance.")
        elif key=="q":
            cs=self.candidates(); k=self.target()
            if cs:self.choice=cs[(cs.index(k)+1)%len(cs)]
        elif key in ("tab","b"):
            self.open_board();return "break"
        elif key=="r":self.world.return_office()
        elif key=="f5":
            try:self.world.save(SAVE);self.world.tell("Partida guardada.")
            except OSError as ex:self.world.tell("No se pudo guardar: "+str(ex))
        elif key=="f9":
            try:self.world=World.load(SAVE);self.world.tell("Partida cargada.")
            except (OSError,ValueError,TypeError,KeyError) as ex:self.world.tell("No se pudo cargar: "+str(ex))
        self.render()

    def release(self,e):self.held.discard(e.keysym.lower())
    def motion(self):
        if not self.paused:
            for key,dx,dy in [("w",0,-1),("up",0,-1),("s",0,1),("down",0,1),("a",-1,0),("left",-1,0),("d",1,0),("right",1,0)]:
                if key in self.held:
                    self.world.move(dx,dy);self.choice=None;break
            self.frame+=1
            self.render()
        self.root.after(100,self.motion)
    def tick(self):
        if not self.paused:self.world.tick()
        self.root.after(1000,self.tick)
    def click(self,e):
        if self.paused:return
        if 718<=e.x<=942 and 386<=e.y<=424:
            self.open_board();return
        for k,(x,y,_) in OBJECTS.items():
            if (e.x//T,e.y//T)==(x,y) and self.world.near(k):
                self.choice=k;self.render();return

    def open_board(self):
        if self.board:return
        self.paused=True;self.held.clear()
        top=tk.Toplevel(self.root);self.board=top
        top.title("Tablero de evidencias");top.configure(bg=BG)
        top.geometry("690x590");top.resizable(False,False)
        top.transient(self.root);top.grab_set()
        def close():
            top.grab_release();top.destroy();self.board=None;self.paused=False;self.render()
        top.protocol("WM_DELETE_WINDOW",close)
        top.bind("<Escape>",lambda e:close())
        def lab(s,color=INK,size=11):
            tk.Label(top,text=s,bg=BG,fg=color,font=("Segoe UI",size),wraplength=640,justify="left").pack(anchor="w",padx=18,pady=4)
        lab("EL RELOJ DEL CONSERJE",GOLD,17)
        lab("Selecciona las pruebas que respaldan tu conclusión. El tiempo queda detenido.")
        flags={}
        for ident,(title,description) in CLUES.items():
            if ident not in self.world.clues:continue
            v=tk.BooleanVar(value=True);flags[ident]=v
            tk.Checkbutton(top,text=title+": "+description,variable=v,bg=BG,fg=MINT,activebackground=BG,activeforeground=MINT,selectcolor="#30283d",wraplength=620,justify="left",font=("Segoe UI",10)).pack(anchor="w",padx=18)
        lab("HIPÓTESIS",GOLD,12)
        verdict=tk.StringVar(value="incierto")
        for ident,label in VERDICTS.items():
            tk.Radiobutton(top,text=label,variable=verdict,value=ident,bg=BG,fg=INK,activebackground=BG,activeforeground=MINT,selectcolor="#30283d",font=("Segoe UI",10),wraplength=620,justify="left").pack(anchor="w",padx=18)
        result=tk.Label(top,text="",bg=BG,fg=GOLD,wraplength=630,justify="left",font=("Segoe UI",11))
        result.pack(anchor="w",padx=18,pady=12)
        def submit():
            if verdict.get()!="clara" or not {"E02","E03"} <= {k for k,v in flags.items() if v.get()}:
                if not messagebox.askyesno("Informe provisional","Puedes cerrar con dudas o una conclusión errónea. ¿Continuar?",parent=top):return
            result.config(text=self.world.resolve(verdict.get(),[k for k,v in flags.items() if v.get()]))
        buttons=tk.Frame(top,bg=BG);buttons.pack(pady=8)
        tk.Button(buttons,text="Presentar informe",command=submit,bg="#49655f",fg="white",padx=12,pady=6).pack(side="left",padx=8)
        tk.Button(buttons,text="Volver a investigar",command=close,bg="#59445e",fg="white",padx=12,pady=6).pack(side="left",padx=8)

def main():
    root=tk.Tk()
    Game(root)
    root.mainloop()

if __name__=="__main__":
    main()
