"""Datos de niveles independientes de Pygame, según parche 0.5.1.
Las posiciones de evidencia conservan sus IDs. Unidades: casillas."""
from dataclasses import dataclass
from functools import cached_property

DIRS=((1,0),(0,1),(-1,0),(0,-1))
def area(x,y,w,h):return {(i,j) for i in range(x,x+w) for j in range(y,y+h)}
def wall(x,y,w,h,holes=()):return area(x,y,w,h)-set(holes)

@dataclass
class Level:
    size:tuple
    spawn:tuple
    points:dict
    walls:set
    props:list
    restricted:set
    doors:set
    theme:str
    regions:list
    @cached_property
    def furniture(self):
        return set().union(*(area(*r[:4]) for r in self.props if r[5])) if self.props else set()
    def inside(self,p):return 0<p[0]<self.size[0]-1 and 0<p[1]<self.size[1]-1

# Prop: x,y,w,h, appearance, solid. Regions: x,y,w,h, name.
def make(size,spawn,points,walls=(),props=(),restricted=(),doors=(),theme="office",regions=()):
    return Level(size,spawn,points,set(walls),list(props),set(restricted),set(doors),theme,list(regions))

LEVELS={}
LEVELS["hospital"]=make((28,18),(3,4),{"nurse":(19,5),"patient":(8,12),"exit":(25,15)},
    wall(12,1,1,8,[(12,6)])|wall(1,9,11,1,[(6,9)]),
    [(3,2,3,2,"bed",True),(7,2,2,2,"monitor",True),(3,6,3,1,"curtain",False),(17,2,7,2,"counter",True),(4,13,3,1,"bench",True),(10,13,2,1,"plant",True)],
    theme="hospital",regions=[(1,1,11,8,"Habitación"),(13,1,14,8,"Enfermería"),(1,10,12,7,"Sala de espera"),(14,10,13,7,"Salida")])
LEVELS["house"]=make((22,18),(3,4),{"notebook":(15,4),"photo":(5,4),"coat":(17,14),"exit":(19,15)},
    wall(10,1,1,8,[(10,6)])|wall(1,9,20,1,[(5,9),(15,9)]),
    [(2,2,3,2,"bed",True),(7,2,2,2,"wardrobe",True),(13,2,5,1,"desk",True),(2,12,4,2,"sofa",True),(9,13,3,2,"table",True),(17,11,2,1,"coat",True)],
    theme="house",regions=[(1,1,9,8,"Dormitorio"),(11,1,10,8,"Estudio"),(1,10,12,7,"Sala"),(14,10,7,7,"Entrada")])
LEVELS["street"]=make((34,18),(3,14),{"rafael":(15,9),"poster":(20,5),"exit":(24,6)},
    area(1,1,32,4)|wall(1,5,32,1,[(20,5),(24,5)]),
    [(5,7,3,1,"bench",True),(8,7,1,1,"lamp",True),(28,7,1,1,"lamp",True),(11,12,6,2,"crosswalk",False)],
    theme="street",regions=[(1,1,32,5,"CINE AURORA"),(1,6,32,5,"Acera"),(1,11,32,6,"Calle")])
# Shared cinema geometry; final reuses it intentionally with an adjoining plaza.
cw=wall(25,1,1,15,[(25,9),(25,13)])|wall(26,6,11,1,[(31,6)])|wall(1,17,24,1,[(7,17),(18,17)])
cp=[(4,2,18,1,"screen",True),(4,5,7,1,"seats",True),(14,5,8,1,"seats",True),(4,8,7,1,"seats",True),(14,8,8,1,"seats",True),(4,11,7,1,"seats",True),(14,11,8,1,"seats",True),(4,14,7,1,"seats",True),(14,14,8,1,"seats",True),(28,2,7,2,"projector",True),(28,8,6,1,"shelf",True),(28,19,7,2,"counter",True),(4,21,4,1,"bench",True)]
cr=area(26,7,11,9)
LEVELS["cine"]=make((38,26),(5,22),{"exit":(2,23),"brizna":(12,19),"client":(12,13),"guard":(23,12),"poster":(5,19),"radio":(15,19),"door":(25,13),"desk":(30,10),"box":(33,13),"photo":(28,14)},cw,cp,cr,[(25,13),(25,9)],"cine",[(1,1,24,16,"Sala de proyección"),(26,1,11,5,"Cabina"),(26,7,11,9,"Archivo"),(1,18,24,7,"Vestíbulo"),(26,18,11,7,"Taquilla")])
LEVELS["office"]=make((30,22),(4,18),{"home":(23,4),"board":(5,4),"journal":(8,5),"rafael":(8,14),"exit":(3,19),"station":(3,19),"request":(12,15)},
    wall(15,1,1,13,[(15,5),(15,11)])|wall(1,10,14,1,[(8,10)])|wall(16,10,13,1,[(22,10)]),
    [(2,2,6,1,"shelf",True),(10,3,4,2,"desk",True),(21,2,4,1,"shelf",True),(20,14,6,2,"sofa",True),(22,18,3,2,"table",True),(4,12,4,1,"counter",True),(11,18,2,1,"plant",True)],
    theme="office",regions=[(1,1,14,9,"Archivo y tablón"),(16,1,13,9,"Rincón espectral"),(1,11,14,10,"Recepción"),(16,11,13,10,"Sala común")])
LEVELS["station"]=make((42,22),(3,12),{"exit":(2,14),"client":(8,12),"schedule":(12,5),"witness":(17,13),"guard":(27,13),"radio":(25,11),"door":(29,14),"desk":(32,14),"box":(35,18),"photo":(37,15)},
    area(1,1,40,2)|wall(29,8,1,13,[(29,14)])|wall(30,8,11,1),
    [(3,5,5,1,"bench",True),(16,5,5,1,"bench",True),(25,5,5,1,"bench",True),(5,9,5,2,"counter",True),(12,16,5,1,"lockers",True),(32,10,7,1,"lockers",True),(32,19,7,1,"shelf",True),(1,1,40,2,"tracks",False)],
    area(30,9,11,12),[(29,14)],"station",[(1,3,40,5,"Andén"),(1,8,28,13,"Vestíbulo"),(30,9,11,12,"Equipaje")])
LEVELS["workshop"]=make((32,24),(27,20),{"exit":(29,21),"client":(7,10),"schedule":(5,5),"guard":(6,17),"witness":(12,6),"radio":(17,14),"door":(22,10),"desk":(26,7),"box":(27,12),"photo":(16,6)},
    wall(22,1,1,16,[(22,10)])|wall(23,16,8,1)|wall(1,14,11,1,[(8,14)]),
    [(3,3,6,1,"tools",True),(3,8,3,1,"machine",True),(10,9,4,3,"machine",True),(16,3,4,2,"tools",True),(16,18,4,2,"pallet",True),(25,3,4,1,"shelf",True),(4,19,4,2,"desk",True)],
    area(23,1,8,15),[(22,10)],"workshop",[(1,1,21,13,"Taller"),(23,1,8,15,"Depósito"),(1,15,11,8,"Oficina"),(13,17,18,6,"Patio de carga")])
LEVELS["ruiz"]=make((30,28),(3,24),{"exit":(2,25),"client":(5,5),"schedule":(6,8),"guard":(20,23),"witness":(23,5),"mora":(11,13),"radio":(20,17),"door":(21,20),"desk":(24,23),"box":(26,24),"photo":(24,25)},
    wall(16,1,1,9,[(16,6)])|wall(1,10,10,1,[(6,10)])|wall(20,19,1,8,[(20,23)])|wall(21,19,8,1,[(21,19)])|wall(21,20,1,1,[(21,20)]),
    [(3,2,5,2,"sofa",True),(6,6,4,1,"table",True),(22,2,4,2,"bed",True),(9,12,9,7,"garden",False),(12,14,3,3,"fountain",True),(3,19,3,2,"wardrobe",True),(25,21,3,1,"shelf",True)],
    area(21,20,8,7),[(21,20)],"ruiz",[(1,1,15,9,"Sala"),(17,1,12,9,"Habitación"),(8,11,11,9,"Patio"),(21,20,8,7,"Correspondencia")])
# The correspondence access is a real aperture from the north, surrounded by walls.
LEVELS["ruiz"].walls |= wall(21,19,8,1,[(21,19)])
LEVELS["archive"]=make((40,26),(3,4),{"exit":(2,3),"client":(7,5),"schedule":(14,4),"guard":(27,13),"witness":(18,14),"radio":(26,11),"door":(30,15),"desk":(33,12),"box":(35,19),"photo":(14,22)},
    wall(30,6,1,19,[(30,15)])|wall(31,6,8,1),
    [(4,8,2,10,"shelf",True),(9,8,2,10,"shelf",True),(14,8,2,10,"shelf",True),(21,7,2,10,"shelf",True),(25,19,3,2,"cart",True),(33,8,5,2,"shelf",True),(9,20,4,1,"table",True)],
    area(31,7,8,18),[(30,15)],"archive",[(1,1,29,6,"Consulta"),(1,7,29,12,"Estantes"),(1,19,29,6,"Cotejo"),(31,7,8,18,"Depósito")])
LEVELS["final"]=make((38,36),(5,32),{"exit":(2,33),"client":(10,30),"schedule":(15,30),"guard":(23,12),"witness":(23,30),"radio":(15,19),"door":(25,13),"desk":(30,10),"box":(30,30),"photo":(28,14),"wish":(12,19)},
    cw|wall(1,25,36,1,[(7,25),(18,25)]),
    cp+[(8,28,6,1,"table",True),(20,28,6,1,"table",True),(29,27,5,1,"bench",True),(26,2,1,4,"tape",False)],cr,[(25,13),(25,9)],"cine",[(1,1,24,16,"Sala segura"),(26,7,11,9,"Archivo"),(1,18,36,7,"Vestíbulo"),(1,26,36,9,"Plaza comunitaria")])

def distance(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])
def occupied(objects):return {(o[0],o[1]) for o in objects.values() if o[3] in ("npc","ghost")}
def sight(level,a,b,closed=True):
    # Supercover-ish samples along line; shelves/solid furniture occlude.
    n=max(abs(a[0]-b[0]),abs(a[1]-b[1]),1)
    opaque=level.walls|level.furniture|(level.doors if closed else set())
    return not any((round(a[0]+(b[0]-a[0])*i/n),round(a[1]+(b[1]-a[1])*i/n)) in opaque for i in range(1,n))
