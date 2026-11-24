import pygame as pg
from pathlib import Path
from modelo import Game, POINTS, CLUES, dist

def main():
    pg.init()
    screen=pg.display.set_mode((960,640),pg.RESIZABLE)
    pg.display.set_caption("Agencia de espectros | El último boleto")
    canvas=pg.Surface((480,320))
    font=pg.font.SysFont("consolas",10)
    big=pg.font.SysFont("consolas",15,bold=True)
    clock=pg.time.Clock()
    game=Game()
    board=False
    elapsed=0
    movement=0
    save=Path.home()/".agencia_v1.json"
    def txt(s,x,y,color="#e9dfcf",large=False):
        canvas.blit((big if large else font).render(s,True,color),(x,y))
    def rect(c,x,y,w,h): pg.draw.rect(canvas,c,(x,y,w,h))
    def pos(p): return (p[0]*16+8,p[1]*16+24)
    def wrap(s,x,y,width=450):
        line=""
        for word in s.split():
            candidate=(line+" "+word).strip()
            if font.size(candidate)[0]>width:
                txt(line,x,y); y+=13; line=word
            else: line=candidate
        txt(line,x,y)
    def target():
        p=game.human if game.active=="human" else game.ghost
        return min(POINTS[game.room],key=lambda k:dist(p,POINTS[game.room][k]))
    running=True
    while running:
        dt=clock.tick(60)
        for e in pg.event.get():
            if e.type==pg.QUIT: running=False
            if e.type==pg.KEYDOWN:
                if e.key==pg.K_ESCAPE: board=False
                elif e.key==pg.K_b: board=not board
                elif board and e.key in (pg.K_1,pg.K_2,pg.K_3):
                    game.resolve(e.key-pg.K_0); board=False
                elif not board:
                    if e.key==pg.K_TAB: game.switch()
                    elif e.key==pg.K_e: game.interact(target())
                    elif e.key==pg.K_SPACE: game.interact(target(),True)
                    elif e.key==pg.K_F5:
                        try: game.save(save); game.tell("Guardado.")
                        except OSError: game.tell("No se pudo guardar.")
                    elif e.key==pg.K_F9:
                        try: game=Game.load(save)
                        except (OSError,ValueError,TypeError,KeyError): game.tell("No se pudo cargar.")
        if not board:
            elapsed+=dt; movement+=dt
            if elapsed>=1000: game.tick(); elapsed-=1000
            if movement>=120:
                movement=0; k=pg.key.get_pressed()
                for keys,dx,dy in [((pg.K_w,pg.K_UP),0,-1),((pg.K_s,pg.K_DOWN),0,1),((pg.K_a,pg.K_LEFT),-1,0),((pg.K_d,pg.K_RIGHT),1,0)]:
                    if any(k[a] for a in keys): game.move(dx,dy); break
        canvas.fill("#201d2b")
        txt("AGENCIA DE ESPECTROS",8,4,"#b2e4d2",True)
        for y in range(1,11):
            for x in range(1,19):
                px,py=pos((x,y))
                rect("#554951" if (x+y)%2 else "#51454d",px-8,py-8,16,16)
        if game.room=="cine":
            for y in range(1,11):
                if y!=8:
                    x,z=pos((10,y)); rect("#302b3d",x-8,z-8,16,16)
            for y in (3,5,7):
                for x in (2,3,4):
                    px,py=pos((x,y)); rect("#784b58",px-6,py-4,12,7)
        for name,p in POINTS[game.room].items():
            if name=="Brizna": continue
            x,y=pos(p)
            rect("#9b785c" if name not in ("Elena","Mateo") else "#827ba0",x-6,y-6,12,12)
            txt(name,x-10,y+7,"#f0cf9c")
        for p,ghost in [(game.human,False),(game.ghost,True)]:
            x,y=pos(p)
            if ghost:
                pg.draw.polygon(canvas,"#a6e5d3",[(x-7,y+7),(x-7,y-4),(x-4,y-8),(x+4,y-8),(x+7,y-4),(x+7,y+7),(x,y+4)])
                rect("#34464d",x-4,y-3,2,3); rect("#34464d",x+2,y-3,2,3)
            else:
                rect("#4c3c38",x-5,y-9,10,5); rect("#d7ac89",x-4,y-4,8,6)
                rect("#b18d65",x-6,y+2,12,8); rect("#343443",x-5,y+10,4,4); rect("#343443",x+1,y+10,4,4)
            if (game.active=="ghost")==ghost: pg.draw.circle(canvas,"#f0d49b",(x,y),11,1)
        txt(game.room.upper(),326,28,"#f0cf9c",True)
        txt("Control: "+("Brizna" if game.active=="ghost" else "Tomás"),326,49)
        txt("Energía: "+str(game.energy),326,68)
        txt("Estabilidad: "+str(game.stability),326,84)
        txt("Vínculo: "+("sí" if game.bond else "no"),326,100)
        txt("Pruebas: "+str(len(game.clues)),326,116)
        txt("Caso: "+("resuelto" if game.resolved else "abierto"),326,132)
        txt("Objetivo: "+target(),326,150)
        txt("WASD mover | TAB cambiar | E hablar/leer | ESP poder",8,207)
        txt("B tablero | F5 guardar | F9 cargar",8,221)
        wrap(game.message,8,245)
        if board:
            rect("#30293c",10,20,460,290)
            txt("EXPEDIENTE: EL ÚLTIMO BOLETO",20,28,"#f0cf9c",True)
            for i,key in enumerate(game.clues): wrap(CLUES[key],20,53+i*26,430)
            txt("1. Mateo robó el boleto.",20,200)
            txt("2. El boleto fue entregado antes de la cancelación.",20,216)
            txt("3. Elena nunca compró el boleto.",20,232)
            txt("Elige 1-3 | B o ESC cerrar",20,270,"#a6e5d3")
        screen.blit(pg.transform.scale(canvas,screen.get_size()),(0,0))
        pg.display.flip()
    pg.quit()

if __name__=="__main__": main()
