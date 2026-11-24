# Agencia de espectros — demo Python

Prototipo gráfico independiente para evaluar el caso **El reloj del conserje**, antes de construir el juego en Godot. No es la versión definitiva ni una exportación Android.

## Abrir en Windows

Instala Python 3.10 o posterior desde https://www.python.org/downloads/ (con Tcl/Tk, incluido en el instalador habitual). Descarga el repositorio, descomprime y abre una terminal en la carpeta Fantasma.

```powershell
py demo_python/main.py
```

También puedes ejecutar `Iniciar_demo.bat`. No se necesita instalar pygame ni ninguna otra dependencia de pip. En Linux puede hacer falta python3-tk.

## Controles

| Tecla | Acción |
|---|---|
| WASD / flechas | Mover al detective |
| E | Observar, documentar o usar anclas |
| Espacio | Poseer el objeto seleccionado |
| Q | Cambiar objetivo cercano (también clic) |
| Tab / B | Tablero, pausa e informe |
| R | Regresar al despacho y comenzar otra visita conservando pruebas |
| F5 / F9 | Guardar / cargar |

Explora la casa y la portería; observa las rutinas, consigue pruebas y comprueba tu hipótesis. La radio distrae al conserje, el reloj altera su rutina y el cuadro permite ver el interior del armario cuando está abierto. Las acciones consumen ectoplasma y pueden levantar sospechas. No necesitas poseer objetos para resolver el caso. El tablero permite archivar conclusiones equivocadas y rectificarlas.

## Alcance

Un expediente, dos rutas, dos NPC con rutinas discretas, cuatro evidencias materiales o testimoniales más la acusación inicial, escenario 2D, arte provisional dibujado mediante código, guardado JSON local. Los NPC cambian de posición por fases; no hay navegación animada, mundo completo, audio, ni campaña. La interfaz Tkinter es solo para validar en PC: las reglas de modelo.py están separadas para reimplementarlas en Godot/GDScript y hacer una interfaz táctil independiente. Android no está implementado.

## Pruebas

```powershell
py -m unittest discover -s demo_python -v
```

En Linux sin pantalla, la prueba gráfica se omite; con Xvfb se puede ejecutar mediante `xvfb-run -a python3 -m unittest discover -s demo_python -v`. Incluye rutas de paciencia e intervención, bloqueo, recuperación, informe incorrecto, guardado y 10 000 acciones simuladas. La diversión y legibilidad requieren prueba humana.

## Archivos

- demo_python/modelo.py: reglas y persistencia.
- demo_python/main.py: vista, entradas y tablero.
- demo_python/test_demo.py: pruebas.
- Iniciar_demo.bat: acceso para Windows.
