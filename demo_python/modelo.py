"""Reglas del juego. No depende de Tkinter ni del sistema operativo."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

WIDTH, HEIGHT = 20, 11
# x, y, nombre, tipo
MAPS = {
 "cine": {
  "client": (3,3,"Elena, acomodadora","ghost"),
  "brizna": (5,4,"Brizna","ghost"),
  "guard": (7,6,"Rafael, conserje","npc"),
  "poster": (3,2,"Cartel de la última función","paper"),
  "desk": (15,3,"Libro de entradas","paper"),
  "box": (16,7,"Caja de objetos perdidos","box"),
  "photo": (14,8,"Fotografía de la función","paper"),
  "radio": (8,3,"Radio antigua","device"),
  "door": (10,5,"Puerta de archivo","door"),
  "exit": (2,9,"Salida al despacho","exit")},
 "office": {
  "home": (4,3,"Mesa de Brizna","home"),
  "board": (8,3,"Archivo de expedientes","board"),
  "guest": (14,6,"Mateo, espíritu errante","ghost"),
  "station": (18,8,"Salir a la estación","exit"),
  "cinema": (2,8,"Regresar al cine","exit")},
 "station": {
  "client": (3,3,"Mateo","ghost"),
  "guard": (7,7,"Inés, encargada","npc"),
  "witness": (8,8,"Silvia, espíritu de la estación","ghost"),
  "schedule": (4,2,"Horario de trenes","paper"),
  "desk": (15,3,"Libro de incidencias","paper"),
  "box": (16,7,"Casillero de equipaje","box"),
  "photo": (14,8,"Etiqueta de equipaje","paper"),
  "radio": (8,3,"Campanilla de servicio","device"),
  "door": (10,5,"Puerta de equipajes","door"),
  "exit": (2,9,"Volver a la oficina","exit")}
}
CASES = {
 "cine": {
  "title":"El último boleto",
  "client":"Elena no descansa: cree que la última noche abandonó a una niña en el cine.",
  "clues":{
   "request":"Elena vio una butaca vacía y cree que dejó sola a la niña.",
   "poster":"La sesión terminó a las 21:00.",
   "heard":"Rafael dice que entregó una niña a su tía.",
   "desk":"El registro firmado indica entrega a las 20:55.",
   "photo":"Fotografía de la niña y su tía juntas a las 20:58.",
   "item":"Boleto con el nombre de la tía y número de asiento."},
  "choices":["Elena abandonó a la niña.","La tía recogió a la niña antes de terminar la función.","No se puede determinar."],
  "correct":1,
  "required":["desk","item"],
  "complete":["desk","item","photo"]},
 "station": {
  "title":"La maleta sin dueño",
  "client":"Mateo no recuerda bien sus días de errante. Cree que su hermano nunca recogió la maleta que le dejó.",
  "clues":{
   "request":"Mateo espera una respuesta sobre la maleta de su hermano.",
   "schedule":"El tren de las 18:40 fue cancelado.",
   "heard":"Inés vio al hermano volver tras el aviso de cancelación.",
   "witness":"Silvia oyó mencionar el casillero 4 durante el traslado; no vio quién retiró la maleta.",
   "desk":"El registro documenta el traslado de la maleta al casillero 4.",
   "photo":"Etiqueta fechada del casillero 4 con el apellido de Mateo.",
   "item":"Recibo firmado por el hermano: retiró las pertenencias al día siguiente."},
  "choices":["El hermano nunca regresó.","Inés se quedó con la maleta.","El hermano regresó y recogió la maleta al día siguiente."],
  "correct":2,
  "required":["desk","item","schedule"],
  "complete":["desk","item","schedule","photo"]}
}
WALLS = {(10,y) for y in range(1,10) if y!=5}

@dataclass
class Spirit:
    name: str
    origin: str
    bond: int = 0
    home: bool = False
    energy: float = 100
    stability: float = 100
    errant: bool = False
    power: str = "vibration"

    @property
    def radius(self):
        return min(6, 2 + self.bond) if self.bond else 3

    def update(self, distance, dt, at_home=False):
        if self.errant and not self.bond and not self.home:
            self.stability=max(0,self.stability-dt*0.4)
            self.energy=max(0,self.energy-dt*0.2)
            return
        if at_home and self.home:
            self.stability=min(100,self.stability+dt*14)
            self.energy=min(100,self.energy+dt*9)
        elif distance <= self.radius:
            self.stability=min(100,self.stability+dt*6)
            self.energy=min(100,self.energy+dt*2)
        else:
            self.stability=max(0,self.stability-dt*(6+3*(distance-self.radius)))

@dataclass
class World:
    place: str = "cine"
    x: int = 2
    y: int = 6
    gx: int = 5
    gy: int = 4
    ghost_mode: bool = False
    met: bool = False
    home_open: bool = False
    active: str = "Brizna"
    spirits: dict = field(default_factory=lambda: {"Brizna":Spirit("Brizna","cine")})
    facts: dict = field(default_factory=lambda: {"cine":{}, "station":{}})
    physical: dict = field(default_factory=lambda: {"cine":[], "station":[]})
    reports: dict = field(default_factory=dict)
    permissions: dict = field(default_factory=lambda: {"cine":False,"station":False})
    spoken: dict = field(default_factory=lambda: {"cine":False,"station":False})
    distracted: float = 0
    log: list = field(default_factory=list)
    wanderer: Spirit = field(default_factory=lambda: Spirit("Mateo","station",energy=30,stability=45,errant=True,power="sound"))
    guest_decision: str = ""
    guest_clock: float = 0

    @property
    def spirit(self):
        return self.spirits[self.active]

    @property
    def pos(self):
        return (self.gx,self.gy) if self.ghost_mode else (self.x,self.y)

    @property
    def anchor(self):
        if self.spirit.home and self.place=="office":
            return (4,3)
        if self.spirit.bond:
            return (self.x,self.y)
        return (5,4) if self.place==self.spirit.origin else (self.x,self.y)

    @property
    def distance(self):
        a,b=self.anchor
        return abs(self.gx-a)+abs(self.gy-b)

    @property
    def objects(self):
        result=dict(MAPS[self.place])
        if self.place=="cine" and self.met:result.pop("brizna",None)
        if self.place in CASES and self.reports.get(self.place)=="complete":result.pop("client",None)
        if self.place=="office":
            if self.guest_decision=="departed":result.pop("guest",None)
            elif self.guest_decision!="stayed":
                route=[(14,6),(15,6),(15,7),(14,7)]
                x,y=route[int(self.guest_clock//3)%len(route)]
                result["guest"]=(x,y,"Mateo, espíritu errante","ghost")
        return result

    @property
    def case(self):
        return CASES.get(self.place)

    def tell(self, msg):
        self.log.append(msg)
        self.log=self.log[-30:]
        return msg

    def tick(self,dt):
        dt=max(0,min(dt,2))
        self.distracted=max(0,self.distracted-dt)
        if self.home_open and not self.guest_decision:
            self.guest_clock+=dt
            self.wanderer.update(0,dt)
        if self.met:
            at_home=self.place=="office" and self.distance<=self.spirit.radius
            self.spirit.update(self.distance,dt,at_home)
            if not self.ghost_mode and self.spirit.bond and self.place!="office":
                self.gx,self.gy=self.x,self.y
            if self.spirit.stability<=0:
                self.gx,self.gy=self.anchor
                self.ghost_mode=False
                self.spirit.stability=20
                self.tell(self.active+" se debilitó y regresó a su ancla.")

    def move(self,dx,dy):
        if abs(dx)+abs(dy)!=1:return False
        x,y=self.pos
        x,y=x+dx,y+dy
        if not (1<=x<WIDTH-1 and 1<=y<HEIGHT-1):return False
        if self.ghost_mode:
            a,b=self.anchor
            new_dist=abs(x-a)+abs(y-b)
            if new_dist>self.spirit.radius+3 and new_dist>=self.distance:return False
            if self.spirit.stability<20 and new_dist>self.distance:return False
            self.gx,self.gy=x,y
        else:
            if self.place!="office":
                if (x,y) in WALLS:return False
                if (x,y)==(10,5) and not (self.permissions[self.place] or self.distracted>0):return False
            self.x,self.y=x,y
            if self.met and self.spirit.bond and self.place!="office":
                self.gx,self.gy=x,y
        return True

    def toggle(self):
        if not self.met:return self.tell("Primero conoce a Brizna en el cine.")
        self.ghost_mode=not self.ghost_mode
        return self.tell("Control: "+(self.active if self.ghost_mode else "Tomás"))

    def recall(self):
        if not self.met:return self.tell("Aún no tienes compañero.")
        self.gx,self.gy=self.anchor
        self.ghost_mode=False
        return self.tell(self.active+" regresó a su ancla.")

    def travel(self, destination):
        if self.ghost_mode:return self.tell("Tomás debe desplazarse físicamente.")
        if destination not in MAPS:return self.tell("Destino desconocido.")
        if not self.home_open:return self.tell("Primero termina el asunto de Elena en el cine.")
        self.place=destination
        self.x,self.y=(4,5) if destination=="office" else (2,6)
        self.gx,self.gy=(4,3) if destination=="office" else (self.x,self.y)
        self.distracted=0
        self.ghost_mode=False
        return self.tell("Llegaste a "+{"cine":"el cine","office":"la agencia","station":"la estación"}[destination]+".")

    def choose_spirit(self,name):
        if self.place!="office" or self.ghost_mode:return self.tell("Selecciona compañeros en la agencia como Tomás.")
        if name not in self.spirits:return self.tell("Ese espíritu no es compañero.")
        if not self.spirits[name].bond:return self.tell("Todavía no hay un vínculo.")
        self.active=name
        self.gx,self.gy=4,3
        return self.tell(name+" te acompañará en la siguiente investigación.")

    def nearby(self):
        x,y=self.pos
        objects=self.objects
        return sorted([k for k,o in objects.items() if abs(x-o[0])+abs(y-o[1])<=1],
                      key=lambda k:(abs(x-objects[k][0])+abs(y-objects[k][1]),k))

    def add_fact(self,key, physical=False):
        case=self.place
        if not self.case or key not in self.case["clues"]:return self.tell("No hay una pista aquí.")
        self.facts[case][key]=True
        if physical and key not in self.physical[case]:self.physical[case].append(key)
        return self.tell(self.case["clues"][key]+(" [Evidencia física]" if physical else ""))

    def act(self,key,power=False):
        if key not in self.nearby():return self.tell("Acércate primero.")
        ghost=self.ghost_mode
        if ghost and self.spirit.stability<20:return self.tell("Tu forma es demasiado débil; vuelve al ancla.")
        if power:
            if not ghost:return self.tell("Cambia al compañero para usar su poder.")
            if key!="radio":return self.tell("El poder no afecta a ese objeto.")
            cost=15 if self.spirit.power=="sound" else 20
            if self.spirit.energy<cost:return self.tell("No hay suficiente energía.")
            if self.place=="office":return self.tell("No es necesario aquí.")
            self.spirit.energy-=cost
            self.distracted=15 if self.spirit.power=="sound" else 10
            return self.tell(self.active+" activa el dispositivo. La puerta queda libre "+str(int(self.distracted))+" segundos.")
        if self.place=="office":
            if key=="home":
                self.spirit.home=True
                self.spirit.energy=100
                self.spirit.stability=100
                return self.tell("Este lugar se siente como un hogar. Ancla de la agencia restaurada.")
            if ghost:return self.tell("Tomás debe encargarse de esto.")
            if key=="guest":
                if "Mateo" in self.spirits:return self.tell("Mateo ya pertenece a la agencia.")
                if self.reports.get("station")=="complete":
                    return self.tell("Mateo: Gracias. Pulsa J para invitarme a quedarme o P para despedirnos.")
                return self.tell("Mateo: Llevo mucho tiempo vagando. Necesito saber qué pasó con mi maleta.")
            if key=="station":return self.travel("station")
            if key=="cinema":return self.travel("cine")
            return self.tell("Abre el tablero con TAB para revisar expedientes.")
        if key=="brizna":
            if ghost:return self.tell("Brizna está contigo.")
            self.met=True
            return self.tell("Brizna nació aquí, de las emociones del cine. Aún no puede irse lejos.")
        if key=="client":
            return self.add_fact("request")
        if key=="witness":
            if not ghost:return self.tell("Silvia teme a los vivos, incluso a quienes pueden verla. Deja que tu compañero hable con ella.")
            return self.add_fact("witness")
        if key=="guard":
            if ghost:
                return self.add_fact("heard")
            if "request" not in self.facts[self.place]:return self.tell("Antes de pedir acceso, habla con el espíritu que necesita ayuda.")
            if self.place=="station" and not ({"witness","desk"} & set(self.facts[self.place])):
                self.add_fact("heard")
                return self.tell("Inés necesita el número de casillero para identificar la maleta. Tu compañero puede averiguarlo hablando con Silvia o leyendo el registro.")
            self.spoken[self.place]=True
            self.permissions[self.place]=True
            self.add_fact("heard")
            return self.tell("El encargado te concede acceso al archivo tras escuchar tu explicación. "+self.case["clues"]["heard"])
        if key in ("poster","schedule","desk","photo"):
            return self.add_fact(key,not ghost)
        if key=="box":
            if ghost:return self.tell("Puedes ver la caja, pero no abrirla ni sacar su contenido.")
            if not self.spoken[self.place]:return self.tell("Necesitas la llave del encargado. Habla con él.")
            return self.add_fact("item",True)
        if key=="door":
            return self.tell("Acceso permitido." if self.permissions[self.place] or self.distracted>0 else "Cerrada. Habla con el encargado o usa una distracción.")
        if key=="exit":
            if ghost:return self.tell("Tomás debe salir contigo.")
            return self.travel("office")
        return self.tell("Dispositivo sencillo: el espíritu puede activarlo con ESPACIO.")

    def resolve(self,case,choice,selected):
        if self.ghost_mode:return self.tell("Tomás debe formular y presentar la conclusión.")
        if case not in CASES:return self.tell("Expediente desconocido.")
        if self.reports.get(case)=="complete":return self.tell("Este expediente ya quedó resuelto.")
        if case=="station" and not self.home_open:return self.tell("Expediente aún no disponible.")
        cfg=CASES[case]
        selected=set(selected)&set(self.facts[case])
        if choice!=cfg["correct"]:
            self.reports[case]="provisional"
            return self.tell("La explicación no convence al espíritu. Revisa tus pruebas; puedes rectificar.")
        if not set(cfg["required"])<=selected or "item" not in self.physical[case] or "desk" not in self.physical[case] or "request" not in self.facts[case]:
            self.reports[case]="incomplete"
            return self.tell("La hipótesis necesita documentos físicos, la versión del espíritu y las pruebas pertinentes.")
        if case=="cine" and not self.met:return self.tell("Conoce primero a Brizna.")
        self.reports[case]="complete"
        if case=="cine":
            self.spirits["Brizna"].bond=1
            self.home_open=True
            return self.tell("Elena conoce la verdad y decide descansar. Brizna se vincula contigo y ya puede salir del cine. Visita la agencia.")
        self.spirit.bond=min(4,self.spirit.bond+1)
        return self.tell("Mateo conoce la verdad. Puedes invitarlo a la agencia o respetar su decisión de partir.")

    def recruit(self):
        if self.place!="office" or self.ghost_mode or self.reports.get("station")!="complete" or "guest" not in self.nearby():
            return self.tell("Resuelve el expediente y acércate a Mateo en la agencia.")
        if self.guest_decision=="departed":return self.tell("Mateo ya descansó.")
        if "Mateo" not in self.spirits:
            self.spirits["Mateo"]=Spirit("Mateo","station",bond=1,home=True,energy=65,stability=70,power="sound")
            self.guest_decision="stayed"
            return self.tell("Mateo decide quedarse y ayudar. La agencia es su nueva ancla.")
        return self.tell("Mateo ya forma parte de la agencia.")

    def release_guest(self):
        if self.place!="office" or self.ghost_mode or self.reports.get("station")!="complete" or "guest" not in self.nearby() or self.guest_decision:
            return self.tell("La despedida se decide junto a Mateo tras resolver su caso.")
        self.guest_decision="departed"
        return self.tell("Mateo se despide agradecido. Eligió descansar en paz.")

    def save(self,path):
        path=Path(path)
        tmp=path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"version":2,"world":asdict(self)},ensure_ascii=False),encoding="utf-8")
        tmp.replace(path)

    @classmethod
    def load(cls,path):
        data=json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("version")!=2:raise ValueError("Guardado antiguo. Inicia una nueva partida.")
        d=data["world"]
        d["spirits"]={k:Spirit(**v) for k,v in d["spirits"].items()}
        d["wanderer"]=Spirit(**d["wanderer"])
        w=cls(**d)
        if w.place not in MAPS or w.active not in w.spirits:raise ValueError("Guardado inválido.")
        if any(not 0<=s.energy<=100 or not 0<=s.stability<=100 for s in w.spirits.values()):raise ValueError("Recursos inválidos.")
        return w
