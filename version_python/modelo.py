from dataclasses import dataclass, field
import json
from pathlib import Path

POINTS = {
 "cine": {"Brizna": (3,4), "Elena": (7,7), "cartel": (5,2), "registro": (15,3), "boleto": (16,7), "radio": (13,6), "Mateo": (15,5), "salida": (2,9)},
 "oficina": {"mesa": (5,4), "Brizna": (7,4), "salida": (2,9)}
}
CLUES = {"cartel":"La última función fue cancelada a las 20:00.",
 "registro":"Mateo recibió el boleto de Elena a las 19:45.",
 "boleto":"Boleto firmado por Elena: cambio de función solicitado.",
 "Elena":"Elena cree que su hijo nunca recibió el boleto.",
 "Mateo":"Mateo confirma que entregó el boleto al hijo antes de la cancelación."}
def dist(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

@dataclass
class Game:
    room: str = "cine"
    human: tuple = (2,8)
    ghost: tuple = (3,4)
    active: str = "human"
    bond: bool = False
    home: bool = False
    energy: int = 100
    stability: int = 100
    clues: list = field(default_factory=list)
    resolved: bool = False
    distraction: int = 0
    message: str = "Tomás: ¿Quién eres? Acércate a Brizna y pulsa E."
    def anchor(self):
        return self.human if self.bond and self.room=="cine" else ((7,4) if self.room=="oficina" else (3,4))
    def tell(self,s):
        self.message=s
        return s
    def move(self,dx,dy):
        if abs(dx)+abs(dy)!=1: return False
        p=self.human if self.active=="human" else self.ghost
        q=(p[0]+dx,p[1]+dy)
        if not (1<=q[0]<=18 and 1<=q[1]<=10): return False
        if self.active=="human":
            if self.room=="cine" and q[0]==10 and q[1]!=8: return False
            self.human=q
        else:
            self.ghost=q
        return True
    def tick(self):
        self.distraction=max(0,self.distraction-1)
        if dist(self.ghost,self.anchor())>5:
            self.stability=max(0,self.stability-8)
        else:
            self.stability=min(100,self.stability+5)
            self.energy=min(100,self.energy+2)
        if not self.stability:
            self.ghost=self.anchor()
            self.active="human"
            self.stability=50
            self.tell("Brizna perdió estabilidad y regresó a su ancla.")
    def switch(self):
        self.active="ghost" if self.active=="human" else "human"
    def record(self,key):
        if key not in self.clues: self.clues.append(key)
        return self.tell(CLUES[key])
    def interact(self,key,power=False):
        p=self.human if self.active=="human" else self.ghost
        if key not in POINTS[self.room] or dist(p,POINTS[self.room][key])>1:
            return self.tell("Acércate al objetivo.")
        if power:
            if self.active!="ghost" or key!="radio" or self.energy<20:
                return self.tell("Solo Brizna puede interferir con la radio; cuesta 20 de energía.")
            self.energy-=20
            self.distraction=12
            return self.tell("La radio distrae a Mateo durante 12 segundos.")
        if key=="Brizna":
            if self.active!="human": return self.tell("Brizna: quiero conocer a ese humano.")
            if not self.bond:
                self.bond=True
                self.ghost=self.human
                return self.tell("Brizna: ¡puedo acompañarte! Nuestro vínculo me sostiene.")
            return self.tell("Brizna: quiero entender por qué Elena sigue esperando.")
        if key=="salida":
            if self.active!="human": return self.tell("Tomás debe acompañarte.")
            if not self.bond: return self.tell("Primero habla con Brizna.")
            self.room="oficina" if self.room=="cine" else "cine"
            self.human=(2,8)
            self.ghost=(7,4) if self.room=="oficina" else self.human
            self.energy=self.stability=100
            self.home=self.home or self.resolved
            return self.tell("La oficina es nuestro refugio." if self.room=="oficina" else "De vuelta al cine.")
        if key=="mesa": return self.tell("Abre el tablero con B para revisar el expediente.")
        if key=="Mateo" and self.active!="human":
            return self.tell("Puedes escuchar, pero Mateo no responde a los espíritus.")
        if key=="registro" and not self.distraction and self.active=="human" and "Mateo" not in self.clues:
            return self.tell("Mateo protege el registro. Habla con él o usa la radio.")
        if key=="boleto" and self.active!="human":
            return self.tell("Ves un boleto firmado. Tomás debe recogerlo y verificarlo.")
        if key in CLUES: return self.record(key)
        return self.tell("Radio antigua. Brizna puede interferir con ella.")
    def resolve(self,answer):
        if self.active!="human": return self.tell("Tomás debe formular el informe.")
        if answer!=2 or not {"registro","boleto","Mateo","Elena"}<=set(self.clues):
            return self.tell("Hipótesis sin respaldo suficiente. Sigue investigando.")
        self.resolved=True
        return self.tell("Elena conoce la verdad y decide descansar. Brizna quiere seguir ayudando.")
    def save(self,path):
        from dataclasses import asdict
        Path(path).write_text(json.dumps(asdict(self),ensure_ascii=False),encoding="utf8")
    @classmethod
    def load(cls,path):
        d=json.loads(Path(path).read_text(encoding="utf8"))
        d["human"]=tuple(d["human"]); d["ghost"]=tuple(d["ghost"])
        return cls(**d)
