"""Reglas del juego. No depende de Tkinter ni del sistema operativo."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
from campana import ORDER, EXTRA, PROLOGUE_MAPS, DIALOGUES, NAMES

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
  "station": (18,8,"Puerta de la agencia","door")},
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
# Los capítulos nuevos conservan identificadores de evidencia, no respuestas mágicas.
for case,cfg in EXTRA.items():
    CASES[case]=cfg
    a,b,c,d=cfg["objects"]
    MAPS[case]={
        "client":(3,3,cfg["person"],cfg.get("client_kind","ghost")),
        "guard":(7,6,cfg["guard"],"npc"),
        "witness":(8,8,cfg["witness_name"],cfg["witness_kind"]),
        "schedule":(4,2,a,"paper"),"desk":(15,3,b,"paper"),
        "box":(16,7,c,"box"),"photo":(14,8,d,"paper"),
        "radio":(8,3,"Dispositivo de señal","device"),
        "door":(10,5,"Acceso al archivo","door"),
        "exit":(2,9,"Volver a la agencia","exit")}
MAPS["ruiz"]["mora"]=(6,4,"Mora, gata espectral","ghost")
MAPS["final"]["wish"]=(6,4,"Conversar con Brizna","ghost")
MAPS.update(PROLOGUE_MAPS)
WALLS = {(10,y) for y in range(1,10) if y!=5}
FURNITURE = {
    "cine": {(x,y) for x in (4,5,6) for y in (6,8)},
    "office": {(x,y) for x in (6,7,8) for y in (6,7)},
    "station": {(x,6) for x in (3,4,5)}
}
for place in MAPS:
    FURNITURE.setdefault(place,set())
def blocked(place,x,y,permission=False,distraction=0):
    if not (1<=x<WIDTH-1 and 1<=y<HEIGHT-1):return True
    if (x,y) in FURNITURE[place]:return True
    return place in CASES and ((x,y) in WALLS or ((x,y)==(10,5) and not (permission or distraction>0)))

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
    place: str = "office"
    x: int = 4
    y: int = 5
    gx: int = 4
    gy: int = 3
    ghost_mode: bool = False
    met: bool = False
    home_open: bool = False
    active: str = "Brizna"
    spirits: dict = field(default_factory=lambda: {"Brizna":Spirit("Brizna","cine")})
    facts: dict = field(default_factory=lambda: {k:{} for k in CASES})
    physical: dict = field(default_factory=lambda: {k:[] for k in CASES})
    reports: dict = field(default_factory=dict)
    permissions: dict = field(default_factory=lambda: {k:False for k in CASES})
    spoken: dict = field(default_factory=lambda: {k:False for k in CASES})
    distracted: float = 0
    log: list = field(default_factory=list)
    wanderer: Spirit = field(default_factory=lambda: Spirit("Mateo","station",energy=30,stability=45,errant=True,power="sound"))
    guest_decision: str = ""
    guest_clock: float = 0
    accepted: list = field(default_factory=list)
    stage: str = "dispatch"
    visited: list = field(default_factory=list)
    requests: list = field(default_factory=list)
    practice: list = field(default_factory=list)
    foundation: list = field(default_factory=list)
    decisions: dict = field(default_factory=dict)
    ending: str = ""
    community_choice: str = ""

    @classmethod
    def new_game(cls):
        return cls(place="hospital",x=3,y=6,stage="hospital")

    def mark(self,key):
        if key not in self.visited:self.visited.append(key)

    def next_case(self):
        return next((k for k in ORDER if self.reports.get(k)!="complete"),None)

    def goal(self):
        # El objetivo indica la acción y ubicación, nunca la solución del misterio.
        p=self.place
        if p=="hospital":return ("Habla con la enfermera (E).","nurse") if "hospital:nurse" not in self.visited else ("Ve a la salida del hospital.","exit")
        if p=="house":
            if len([k for k in self.visited if k.startswith("house:") and not k.endswith("exit")])<2:
                return ("Examina dos objetos de Tomás.",next(k for k in ("notebook","photo","coat") if "house:"+k not in self.visited))
            return ("Sal hacia el despacho.","exit")
        if p=="street":return ("Habla con Rafael antes de entrar.","rafael") if "street:rafael" not in self.visited else ("Entra al cine.","exit")
        if p=="office":
            if self.stage=="dispatch":return ("Habla con Rafael para aceptar su encargo.","rafael")
            if self.stage=="foundation":
                if "home" not in self.foundation:return ("Prepara el rincón de Brizna.","home")
                if "board" not in self.foundation:return ("Coloca el tablón de expedientes.","board")
                return ("Revisa la libreta para fundar la agencia.","journal")
            for case in ("station","workshop","ruiz"):
                if self.reports.get(case)=="complete" and case not in self.decisions:return ("Habla con el espíritu sobre su futuro.","guest_"+case)
            nxt=self.next_case()
            if nxt is None:return ("Campaña resuelta. Habla con tus compañeros o revisa el archivo.",None)
            if nxt not in self.requests:return ("Conoce al nuevo cliente en recepción.","request_"+nxt)
            return ("Abre el tablón y prepara el siguiente caso.","board")
        if p=="cine" and not self.met:return ("Acércate a la pequeña silueta y habla con ella.","brizna")
        if p=="cine" and not self.practice_done:
            if "power" not in self.practice:
                return (("Usa ESPACIO junto a la radio para probar la vibración." if self.ghost_mode else "Pulsa Q para controlar a Brizna y acércate a la radio."),"radio")
            return ("Pulsa R para volver junto a Tomás.",None)
        if self.reports.get(p)=="complete":return ("Regresa a la agencia por la salida.","exit")
        if "request" not in self.facts[p]:return ("Escucha al cliente.","client")
        if p=="station" and not ({"witness","desk"}&set(self.facts[p])):
            return ("Acércate a Silvia como espíritu o inspecciona el archivo con él.","witness")
        if not self.spoken[p]:return ("Habla con el responsable como Tomás para conseguir acceso.","guard")
        cfg=CASES[p]
        for key in cfg.get("physical_required",["desk","item"]):
            if key not in self.physical[p]:return ("Recupera las pruebas físicas con Tomás.","box" if key=="item" else key)
        for key in cfg["required"]:
            if key not in self.facts[p]:return ("Investiga la información que falta.","box" if key=="item" else key)
        if cfg.get("either") and not set(cfg["either"])&set(self.facts[p]):
            return ("Corrobora los datos con otro testigo o una inspección.","witness")
        return ("Abre el cuaderno (TAB) y formula una hipótesis.",None)

    @property
    def practice_done(self):
        return "power" in self.practice and "return" in self.practice

    def scene(self,destination,stage=None):
        self.place=destination;self.x,self.y=(3,6) if destination!="office" else (4,5)
        self.gx,self.gy=(self.x,self.y)
        self.ghost_mode=False;self.distracted=0
        if stage:self.stage=stage
        return self.tell("Llegaste a "+NAMES[destination]+".")

    @property
    def spirit(self):
        return self.spirits[self.active]

    @property
    def pos(self):
        return (self.gx,self.gy) if self.ghost_mode else (self.x,self.y)

    @property
    def companion_present(self):
        return self.met and (self.place in CASES or (self.place=="office" and self.spirit.bond>0))

    @property
    def anchor(self):
        # Solo las misiones tienen un ancla espacial. El hogar es toda la agencia.
        return (self.x,self.y) if self.place in CASES else None

    @property
    def distance(self):
        if self.anchor is None:return 0
        a,b=self.anchor
        return abs(self.gx-a)+abs(self.gy-b)

    def available(self,case):
        return case in CASES and all(self.reports.get(k)=="complete" for k in ORDER[:ORDER.index(case)])

    def accept_case(self,case):
        if self.place!="office" or self.ghost_mode or "board" not in self.nearby():
            return self.tell("Tomás debe aceptar el caso junto al tablón de la agencia.")
        if self.stage!="agency":return self.tell("Primero termina la introducción y funda la agencia.")
        if not self.available(case) or case not in self.requests:return self.tell("Habla con el cliente para registrar la solicitud.")
        if self.reports.get(case)=="complete":return self.tell("Este expediente está archivado.")
        if case not in self.accepted:self.accepted.append(case)
        return self.travel(case)

    @property
    def objects(self):
        result=dict(MAPS[self.place])
        if self.place=="cine" and self.met:result.pop("brizna",None)
        if self.place in CASES and self.reports.get(self.place)=="complete":result.pop("client",None)
        if self.place=="office":
            result.pop("guest",None)
            if self.stage=="dispatch":
                return {"rafael":(8,3,"Rafael, conserje","npc"),"home":(4,3,"Viejo escritorio","home")}
            if self.stage=="foundation":
                return {"home":(4,3,"Rincón de Brizna","home"),"board":(8,3,"Instalar tablón","board"),"journal":(11,3,"Libreta y letrero","paper")}
            next_case=self.next_case()
            if next_case and next_case!="cine":
                cfg=CASES[next_case];name=cfg.get("person","Mateo")
                result["request_"+next_case]=(13,4,name+", cliente",cfg.get("client_kind","ghost"))
            for i,case in enumerate(("station","workshop","ruiz")):
                if self.reports.get(case)=="complete" and case not in self.decisions:
                    name={"station":"Mateo","workshop":"Nico","ruiz":"Mora"}[case]
                    result["guest_"+case]=(13+i,7,name+", decisión","ghost")
            for i,(name,spirit) in enumerate(self.spirits.items()):
                if name!=self.active and spirit.bond:
                    result["ally_"+name]=(4+i*2,8,name+", aliado","ghost")
            result["journal"]=(11,3,"Archivo y libreta","paper")
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
            self.wanderer.stability=max(15,self.wanderer.stability)
            self.wanderer.energy=max(5,self.wanderer.energy)
        if self.place=="office":
            # Toda la oficina es un refugio, sin alcance, desgaste ni poderes de misión.
            for spirit in self.spirits.values():
                if spirit.bond:spirit.update(0,dt,True)
            return
        if not self.companion_present:return
        if not self.ghost_mode:self.gx,self.gy=self.x,self.y
        self.spirit.update(self.distance,dt)
        if self.spirit.stability<=0:
            self.gx,self.gy=self.anchor
            self.ghost_mode=False
            self.spirit.stability=20
            self.tell(self.active+" se debilitó y regresó junto a Tomás.")

    def move(self,dx,dy):
        if abs(dx)+abs(dy)!=1:return False
        x,y=self.pos
        x,y=x+dx,y+dy
        if not (1<=x<WIDTH-1 and 1<=y<HEIGHT-1):return False
        if self.ghost_mode:
            if not self.companion_present:return False
            if self.place!="office":
                a,b=self.anchor
                new_dist=abs(x-a)+abs(y-b)
                if new_dist>self.spirit.radius+3 and new_dist>=self.distance:return False
                if self.spirit.stability<20 and new_dist>self.distance:return False
            self.gx,self.gy=x,y
        else:
            if blocked(self.place,x,y,self.permissions.get(self.place,False),self.distracted):return False
            self.x,self.y=x,y
            if self.companion_present and self.place!="office":self.gx,self.gy=x,y
        return True

    def toggle(self):
        if not self.companion_present:return self.tell("Aún no tienes un compañero aquí.")
        self.ghost_mode=not self.ghost_mode
        if not self.ghost_mode and self.place!="office":self.gx,self.gy=self.x,self.y
        return self.tell("Control: "+(self.active if self.ghost_mode else "Tomás"))

    def recall(self):
        if not self.companion_present:return self.tell("Aún no tienes compañero aquí.")
        self.ghost_mode=False
        if self.place=="office":return self.tell("En la agencia los espíritus se mueven libremente.")
        if self.place=="cine" and "power" in self.practice and "return" not in self.practice:self.practice.append("return")
        self.gx,self.gy=self.anchor
        return self.tell(self.active+" regresó junto a Tomás.")

    def travel(self,destination):
        if self.ghost_mode:return self.tell("Tomás debe desplazarse físicamente.")
        if destination=="office":
            if self.place not in CASES or "exit" not in self.nearby():return self.tell("Usa la salida de la misión.")
            if self.place=="cine" and self.home_open and self.stage!="agency":
                for spirit in self.spirits.values():
                    if spirit.bond:spirit.home=True
                return self.scene("office","foundation")
            if self.place=="cine" and not self.home_open:return self.scene("office","dispatch")
            return self.scene("office")
        if self.place!="office" or self.stage!="agency" or destination not in self.accepted or not self.available(destination) or "board" not in self.nearby():
            return self.tell("Selecciona el expediente desde la agencia.")
        return self.scene(destination)

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
        if self.place in PROLOGUE_MAPS:
            if power:return self.tell("Todavía no puedes usar poderes.")
            if key!="exit":
                self.mark(self.place+":"+key)
                return self.tell(self.objects[key][2])
            if self.place=="hospital":
                if "hospital:nurse" not in self.visited:return self.tell("Habla primero con la enfermera.")
                return self.scene("house","house")
            if self.place=="house":
                if len([k for k in self.visited if k.startswith("house:")])<2:return self.tell("Examina dos recuerdos de tu vida anterior.")
                return self.scene("office","dispatch")
            if "street:rafael" not in self.visited:return self.tell("Habla primero con Rafael.")
            if "cine" not in self.accepted:self.accepted.append("cine")
            return self.scene("cine","first_case")
        if ghost and self.spirit.stability<20:return self.tell("Tu forma es demasiado débil; vuelve al ancla.")
        if power:
            if not ghost:return self.tell("Cambia al compañero para usar su poder.")
            if self.place not in CASES:return self.tell("En la agencia no hacen falta poderes de misión.")
            if self.spirit.power=="track":
                spirits=[(abs(x-self.gx)+abs(y-self.gy),name) for x,y,name,kind in self.objects.values() if kind=="ghost"]
                if not spirits:return self.tell("Mora no detecta ninguna presencia cercana.")
                if self.spirit.energy<10:return self.tell("Mora necesita descansar.")
                self.spirit.energy-=10
                return self.tell("Mora percibe una presencia a unas "+str(min(spirits)[0])+" casillas.")
            if key not in (("radio","door") if self.spirit.power=="mechanism" else ("radio",)):return self.tell("El poder no afecta a ese objeto.")
            cost={"sound":15,"mechanism":25}.get(self.spirit.power,20)
            if self.spirit.energy<cost:return self.tell("No hay suficiente energía.")
            if self.place=="office":return self.tell("No es necesario aquí.")
            self.spirit.energy-=cost
            if self.place=="cine" and "power" not in self.practice:self.practice.append("power")
            self.distracted=15 if self.spirit.power=="sound" else 10
            return self.tell(self.active+" activa el dispositivo. La puerta queda libre "+str(int(self.distracted))+" segundos.")
        if self.place=="office":
            if self.stage=="dispatch":
                if key=="rafael" and not ghost:
                    self.mark("office:rafael")
                    return self.scene("street","street")
                return self.tell("El despacho aún no es una agencia. Habla con Rafael.")
            if self.stage=="foundation":
                if key=="home":
                    if "home" not in self.foundation:self.foundation.append("home")
                    self.spirit.home=True
                    return self.tell("Colocaste el boleto de Brizna en su rincón.")
                if key=="board":
                    if "home" not in self.foundation:return self.tell("Prepara primero el rincón de Brizna.")
                    if "board" not in self.foundation:self.foundation.append("board")
                    return self.tell("Instalaste el tablón de solicitudes.")
                if key=="journal":
                    if not {"home","board"}<=set(self.foundation):return self.tell("Prepara el rincón y el tablón primero.")
                    self.stage="agency"
                    return self.tell("Agencia de espectros fundada. Un nuevo cliente espera en recepción.")
            if key=="home":
                self.spirit.energy=self.spirit.stability=100
                return self.tell("La agencia es un hogar, no un límite de distancia.")
            if ghost:return self.tell("Tomás debe hablar con el cliente.")
            if key.startswith("request_"):
                case=key[len("request_"):]
                if case not in self.requests:self.requests.append(case)
                return self.tell("Solicitud registrada: "+CASES[case]["title"])
            if key.startswith("guest_"):return self.tell(self.objects[key][2]+": quiero hablar de lo que haré después.")
            if key.startswith("ally_"):return self.tell(self.objects[key][2]+": me alegra tener un hogar.")
            return self.tell("Consulta el tablón de solicitudes y prepara el equipo.")
        if key=="brizna":
            if ghost:return self.tell("Brizna está contigo.")
            self.met=True
            self.gx,self.gy=self.x,self.y
            return self.tell("Brizna nació de las emociones del cine. Te acompaña gracias a un vínculo provisional.")
        if key=="client":
            if self.place=="cine" and not self.practice_done:return self.tell("Primero practica el vínculo con Brizna y la radio.")
            return self.add_fact("request")
        if key=="witness":
            kind=self.objects[key][3]
            if kind=="ghost" and not ghost:return self.tell("Este espíritu desconfía de Tomás. Deja que tu compañero se presente.")
            return self.add_fact("witness")
        if key=="mora":return self.add_fact("mora")
        if key=="wish":
            if ghost:return self.tell("Tomás debe conversar con Brizna.")
            return self.add_fact("wish")
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
        if self.place!=case or case not in self.accepted:return self.tell("Presenta la conclusión durante la investigación activa.")
        if self.reports.get(case)=="complete":return self.tell("Este expediente ya quedó resuelto.")
        if not self.available(case):return self.tell("Expediente aún no disponible.")
        cfg=CASES[case]
        selected=set(selected)&set(self.facts[case])
        if choice!=cfg["correct"]:
            self.reports[case]="provisional"
            return self.tell("La explicación no convence al espíritu. Revisa tus pruebas; puedes rectificar.")
        required=set(cfg["required"])|{"request"}
        if not required<=selected or not set(cfg.get("physical_required",["item","desk"]))<=set(self.physical[case]) or (cfg.get("either") and not set(cfg["either"])&selected):
            self.reports[case]="incomplete"
            return self.tell("La hipótesis necesita documentos físicos, la versión del espíritu y las pruebas pertinentes.")
        if case=="cine" and not self.met:return self.tell("Conoce primero a Brizna.")
        self.reports[case]="complete"
        if case=="cine":
            self.spirits["Brizna"].bond=1
            self.home_open=True
            return self.tell("Elena conoce la verdad y decide descansar. Brizna se vincula contigo y ya puede salir del cine. Visita la agencia.")
        self.spirit.bond=min(4,self.spirit.bond+1)
        if case=="final":return self.tell("El informe es coherente. Elige una alternativa comunitaria viable y escucha la decisión de Brizna.")
        return self.tell("Expediente resuelto: "+cfg["title"]+". Regresa a la agencia.")

    def decide_ally(self,case,stay):
        if self.place!="office" or self.ghost_mode or case not in ("station","workshop","ruiz") or self.reports.get(case)!="complete" or "guest_"+case not in self.nearby() or case in self.decisions:
            return self.tell("Habla con el espíritu en la agencia tras resolver su caso.")
        name,power={"station":("Mateo","sound"),"workshop":("Nico","mechanism"),"ruiz":("Mora","track")}[case]
        self.decisions[case]="stayed" if stay else "departed"
        if case=="station":self.guest_decision=self.decisions[case]
        if stay:
            self.spirits[name]=Spirit(name,case,bond=1,home=True,energy=65,stability=70,power=power)
            return self.tell(name+" elige quedarse y colaborar.")
        return self.tell(name+" elige su propio camino. Su despedida queda en la libreta.")

    def recruit(self):return self.decide_ally("station",True)
    def release_guest(self):return self.decide_ally("station",False)

    def choose_ending(self,community,ending):
        if self.reports.get("final")!="complete":return self.tell("Presenta primero el informe final.")
        if community not in ("centro cultural","archivo","traslado") or ending not in ("agencia","explorar","colaborar"):
            return self.tell("Elige una alternativa viable.")
        self.community_choice=community;self.ending=ending
        return self.tell("La comunidad elige "+community+". Brizna decide "+ending+". Su historia continúa.")

    def save(self,path):
        path=Path(path)
        tmp=path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"version":4,"world":asdict(self)},ensure_ascii=False),encoding="utf-8")
        tmp.replace(path)

    @classmethod
    def load(cls,path):
        data=json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("version")!=4:raise ValueError("Guardado anterior. Inicia una partida de esta versión.")
        d=data["world"]
        d["spirits"]={k:Spirit(**v) for k,v in d["spirits"].items()}
        d["wanderer"]=Spirit(**d["wanderer"])
        w=cls(**d)
        if w.place not in MAPS or w.active not in w.spirits:raise ValueError("Guardado inválido.")
        if any(not 0<=s.energy<=100 or not 0<=s.stability<=100 for s in w.spirits.values()):raise ValueError("Recursos inválidos.")
        return w
