# Agencia de espectros — prototipo 0.5.1

Python 3.10+ / Pygame-ce. Rama principal; Godot se utilizará más adelante.

## Instalar
```powershell
py -m pip install -r requirements.txt
```
Después ejecuta Iniciar_demo.bat. El nuevo guardado .agencia_espectros_v5.json no sobrescribe el anterior. Por el cambio de geometría se recomienda Nueva partida; la versión 0.5 no se migra automáticamente.

## Parche
- Diez niveles con geometría propia (niveles.py), dimensiones variables, mobiliario, zonas de acceso, colisiones y cámara. El último caso conecta el cine con una plaza en un mismo mapa.
- Personajes no comparten casillas; compañero sigue a Tomás a una casilla cuando es posible, retorno a posición adyacente. La agencia sigue siendo refugio libre.
- E contextual (hablar, leer, examinar, abrir, entrar, salir, preparar, ver casos); Espacio muestra habilidad si es válida. Objetivo, camino orientativo, diálogo modal y HUD redistribuido.
- Rafael tiene diálogo ampliado, preguntas, decisión de aceptar/posponer y salida explícita.
- Alerta por NPC: visión, sonido, infracción, umbrales, espera, explicación y suspensión recuperable de permisos. El primer ejercicio no suma alerta. No hay perturbación espiritual en este parche.
- Se mantienen seis expedientes y decisiones de aliados. Arte y valores de alerta provisionales. Las rutinas son locales, no una simulación avanzada; las rutas y el equilibrio necesitan prueba humana.

## Controles
WASD/flechas, E interacción, Q cambio, Espacio poder, R retorno, F objetivo, TAB cuaderno, C equipo en agencia, F5/F9 guardado/carga, Esc pausa/ayuda, F3 FPS.

## Pruebas
```
python -m unittest discover -s demo_python -v
python demo_python/capturas.py
```
Las capturas son imágenes del juego y de los mapas generadas por Pygame. GitHub Actions prueba SDL virtual. No se afirma rendimiento real ni validación artística solo por aprobar pruebas.
