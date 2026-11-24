"""Reglas independientes de la interfaz; portables a Godot."""
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

CLUES = {
    "E01": ("Nota de entrega", "La carta estaba en el escritorio antes de la disputa."),
    "E02": ("Registro de portería", "El hermano llegó a las 18:20."),
    "E03": ("Carta archivada", "Clara la guardó a las 18:05; conserva su firma."),
    "E04": ("Conversación", "Clara quería proteger la carta de una disputa familiar."),
    "T01": ("Acusación del cliente", "El espíritu cree que su hermano robó la carta. No es un hecho comprobado."),
}
OBJECTS = {
    "escritorio": (4, 3, "Nota oculta; requiere luz."),
    "lampara": (5, 3, "Encender/apagar: 7 de ectoplasma."),
    "radio": (13, 5, "Estática: 9 de ectoplasma; distrae a Julián."),
    "registro": (18, 3, "Consulta cuando Julián no vigila."),
    "armario": (18, 8, "Abierto durante el cambio de turno."),
    "cuadro": (15, 8, "Mirar el armario abierto desde aquí: 3 de ectoplasma."),
    "sofa": (5, 7, "Escuchar a Clara y Julián durante su reunión."),
    "archivo": (3, 10, "Copia de la nota de entrega; ruta alternativa."),
    "ancla1": (9, 9, "Recuperar 25, una vez por visita."),
    "ancla2": (20, 10, "Recuperar 25, una vez por visita."),
    "reloj": (7, 3, "Adelantar la alarma: 5 de ectoplasma; cambia la rutina."),
    "puerta": (11, 5, "Acceso entre habitaciones."),
}
VERDICTS = {
    "clara": "Clara archivó la carta antes de la llegada del hermano.",
    "hermano": "El hermano sustrajo la carta.",
    "incierto": "No hay evidencia suficiente para concluir.",
}

@dataclass
class World:
    x: int = 3
    y: int = 8
    t: int = 0
    day: int = 1
    energy: int = 100
    suspicion: int = 0
    quiet: int = 0
    distraction: int = 0
    alarm: int = 0
    lamp: bool = False
    blocked: bool = False
    anchors: list = field(default_factory=list)
    clues: dict = field(default_factory=lambda: {"T01": 0})
    log: list = field(default_factory=list)
    report: str = ""
    trust: int = 0
    visits: int = 1

    @property
    def phase(self):
        return self.t % 40

    @property
    def julian(self):
        if self.distraction > 0:
            return (13, 6)
        p = (self.phase + self.alarm) % 40
        if p < 12:
            return (17, 4)
        if p < 26:
            return (6, 10)
        return (6, 7)

    @property
    def clara(self):
        if 14 <= self.phase < 26:
            return (18, 9)
        if 26 <= self.phase < 35:
            return (4, 7)
        return (8, 5)

    @property
    def cabinet_open(self):
        return 14 <= self.phase < 26

    def tell(self, message):
        self.log.append(message)
        self.log = self.log[-12:]
        return message

    def record(self, key):
        if key not in self.clues:
            self.clues[key] = self.t
            return self.tell("Nueva prueba: " + CLUES[key][0] + ".")
        return self.tell("Ya está documentada: " + CLUES[key][0] + ".")

    def tick(self):
        self.t += 1
        self.distraction = max(0, self.distraction - 1)
        self.quiet += 1
        if self.quiet >= 30 and self.quiet % 5 == 0:
            self.suspicion = max(0, self.suspicion - 1)

    def near(self, key):
        a, b, _ = OBJECTS[key]
        return abs(self.x-a) + abs(self.y-b) <= 2

    def move(self, dx, dy):
        if abs(dx) + abs(dy) != 1:
            return False
        x, y = self.x+dx, self.y+dy
        if not (1 <= x <= 20 and 2 <= y <= 11):
            return False
        # Los fantasmas atraviesan tabiques; una puerta protegida los rechaza.
        if x == 11 and y == 5 and self.blocked:
            return False
        self.x, self.y = x, y
        return True

    def event(self, key, amount):
        a, b, _ = OBJECTS[key]
        if any(abs(a-x)+abs(b-y) <= 8 for x,y in (self.julian, self.clara)):
            self.suspicion = min(100, self.suspicion + amount)
            self.quiet = 0
            if self.suspicion >= 75:
                self.blocked = True
                self.tell("Alerta: Julián protege el registro. Regresa al despacho o usa otra ruta.")

    def spend(self, cost):
        if self.energy < cost:
            self.tell("Ectoplasma insuficiente. Usa un ancla o vuelve al despacho.")
            return False
        self.energy -= cost
        return True

    def finish_action(self, message):
        self.tell(message)
        if self.energy == 0:
            self.return_office()
            return self.tell("Sin ectoplasma: regreso al despacho. Las pruebas se conservan.")
        return message

    def interact(self, key, power=False):
        if key not in OBJECTS or not self.near(key):
            return self.tell("Acércate al objeto.")
        if key == "escritorio":
            return self.record("E01") if self.lamp else self.tell("Está oscuro; usa la lámpara o consulta el archivo.")
        if key == "archivo":
            return self.record("E01")
        if key == "registro":
            guarded = self.julian == (17, 4)
            if self.blocked or guarded:
                return self.tell("Registro protegido. Espera, distrae a Julián o regresa otro día.")
            return self.record("E02")
        if key == "armario":
            return self.record("E03") if self.cabinet_open else self.tell("Cerrado. Clara lo abre durante el cambio de turno.")
        if key == "sofa":
            together = self.clara == (4, 7) and self.julian == (6, 7)
            return self.record("E04") if together else self.tell("Escucha aquí cuando Clara y Julián se reúnan al final del turno.")
        if key.startswith("ancla"):
            if key in self.anchors:
                return self.tell("Ancla agotada por esta visita.")
            if self.energy == 100:
                return self.tell("Energía completa. Guarda el ancla para después.")
            self.anchors.append(key)
            self.energy = min(100, self.energy+25)
            return self.tell("Ancla: energía recuperada.")
        if key == "puerta":
            return self.tell("Puerta protegida." if self.blocked else "Paso abierto.")
        if not power:
            return self.tell(OBJECTS[key][2] + " Pulsa ESPACIO para poseer.")
        if key == "lampara" and self.spend(7):
            self.lamp = not self.lamp
            self.event(key, 8)
            return self.finish_action("Lámpara encendida." if self.lamp else "Lámpara apagada.")
        if key == "radio" and self.spend(9):
            self.event(key, 18)
            self.distraction = 10
            return self.finish_action("Estática: Julián investiga la radio durante 10 segundos.")
        if key == "cuadro" and self.spend(3):
            if self.cabinet_open:
                self.record("E03")
            return self.finish_action("Vista desde el cuadro: " + ("carta visible." if self.cabinet_open else "armario cerrado."))
        if key == "reloj" and self.spend(5):
            self.alarm = (self.alarm + 12) % 40
            self.event(key, 8)
            return self.finish_action("Alarma alterada: cambia el horario de Julián.")
        return self.log[-1] if self.log else "Sin efecto."

    def return_office(self):
        self.x, self.y = 3, 10
        self.t += (40 - self.phase)
        self.day += 1
        self.visits += 1
        self.energy = 100
        self.suspicion = self.quiet = self.distraction = self.alarm = 0
        self.blocked = self.lamp = False
        self.anchors.clear()
        return self.tell("Nueva visita: energía y accesos restaurados. Pruebas conservadas.")

    def resolve(self, verdict, selected):
        if verdict not in VERDICTS:
            return self.tell("Elige una hipótesis.")
        # Solo pruebas documentadas pueden respaldar el informe.
        selected = set(selected) & set(self.clues)
        if verdict == "clara" and {"E02", "E03"} <= selected:
            self.report = "confirmado" if "E04" in selected else "confirmado_parcial"
            self.trust = 2 if "E04" in selected else 1
            return self.tell("Caso resuelto: Clara archivó la carta antes de que llegara el hermano." + (" Motivo comprobado." if "E04" in selected else " Motivo aún pendiente."))
        self.report = "erroneo" if verdict == "hermano" else "provisional"
        self.trust = -1 if verdict == "hermano" else 0
        return self.tell("Informe archivado como " + self.report + ". Puedes seguir investigando y rectificar.")

    def save(self, path):
        path = Path(path)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"version":1, "world":asdict(self)}, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data["version"] != 1:
            raise ValueError("Versión de guardado incompatible.")
        w = cls(**data["world"])
        if not (0 <= w.energy <= 100 and 0 <= w.suspicion <= 100 and 1 <= w.x <= 20 and 2 <= w.y <= 11 and set(w.clues) <= set(CLUES)):
            raise ValueError("Guardado inválido.")
        return w
