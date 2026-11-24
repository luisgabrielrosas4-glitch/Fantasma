# Agencia de espectros — prototipo Python 0.2

La versión anterior ha sido reemplazada en main. Sigue siendo un prototipo de escritorio con Tkinter y no una aplicación Android. No requiere dependencias de pip. Python 3.10+ con Tcl/Tk.

## Iniciar
Descarga el ZIP de main, extráelo y abre Iniciar_demo.bat en Windows, o ejecuta:
```
python demo_python/main.py
```

## Campaña inicial
Tomás es un expolicía retirado que, tras sobrevivir a un accidente, ve espíritus. En el Cine Aurora conoce a Brizna, un espíritu nacido de las emociones del lugar, nunca humano. Ayuda a Elena a descubrir qué sucedió en la última función. La resolución crea el vínculo con Tomás y permite salir del cine. Visita la agencia, establece el ancla del hogar junto a su mesa y explora el segundo expediente en la estación. Mateo es un espíritu errante debilitado; al resolver su caso puedes invitarlo o despedirte.

## Controles
| Tecla | Acción |
|---|---|
| WASD o flechas | Mover |
| E | Interactuar |
| Q | Cambiar entre Tomás y el compañero |
| Espacio | Poder del espíritu |
| F | Cambiar objetivo cercano |
| R | Regresar al ancla |
| TAB | Tablero de evidencias (pausa) |
| C | Seleccionar compañero en la oficina |
| J / P | Invitar a Mateo / despedirse de él, junto a él tras su caso |
| F5 / F9 | Guardar / cargar |

## Reglas
Los fantasmas leen documentos visibles y escuchan; no recuperan recuerdos ni leen mentes. No extraen objetos de cajas cerradas. El detective dialoga, consigue acceso y recupera pruebas físicas. Un vínculo amplía el radio de exploración; la estabilidad cae al salir de él y provoca el regreso al agotarse. La energía es distinta y financia los poderes. El radio tiene un límite exterior adicional de tres casillas. La oficina puede convertirse en hogar/ancla; Tomás es ancla móvil cuando existe vínculo. Un errante sin ancla pierde recursos gradualmente. No se bloquea la campaña por dejar descansar a Mateo.

El tablero distingue observaciones y evidencias físicas; no basta adivinar la hipótesis. En el segundo caso el compañero averigua el casillero por dos rutas: hablar con Silvia o leer el libro detrás de la puerta. Tomás debe recuperar las pruebas. Los poderes de Brizna y Mateo tienen costes y duraciones diferentes, todavía provisionales.

## Estado y pruebas
Dos casos, tres mapas, arte dibujado mediante código, rutinas simples, progreso y guardado JSON local (v2, incompatible con el guardado antiguo; no lo borra). No incluye todavía campaña completa, assets finales, audio, exportación Android ni gestión avanzada. La lógica está separada de Tkinter para su futura adaptación a Godot.

```
python -m unittest discover -s demo_python -v
```
Pruebas de campaña, reclutamiento y despedida, alcance, recuperación, lectura, evidencias, guardado, simulación de 10 000 acciones y arranque gráfico. CI existente con Xvfb.
