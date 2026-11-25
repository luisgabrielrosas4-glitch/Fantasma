# Agencia de espectros — prototipo Python 0.5

Implementación inicial del plan integral GDD 0.4. Prototipo de escritorio Python 3.10+ / Pygame-ce; Godot será la plataforma final. El código anterior se sustituye en main.

## Instalar y jugar

En la carpeta extraída:
```powershell
py -m pip install -r requirements.txt
```
Abre `Iniciar_demo.bat` o ejecuta `py demo_python/main.py`. Si no tienes el comando py usa python.

## Primeros pasos

1. Nueva partida. Avanza el diálogo inicial con E, Enter o el botón.
2. Sigue el objetivo del panel derecho. El marcador dorado indica la ubicación; acércate y pulsa E.
3. Hospital, casa, despacho, encargo de Rafael y exterior del cine preceden al encuentro con Brizna.
4. Practica Q (control de Brizna), camina hacia la radio, usa Espacio y R para volver. Después habla con Elena.
5. Investiga como Tomás, recoge pruebas físicas y abre TAB. Elige una hipótesis y las evidencias que la respaldan.
6. Tras resolver, vuelve por la salida y funda la agencia: rincón, tablón, libreta.
7. Conoce al siguiente cliente, elige compañero con C y acepta en el tablón. Los seis expedientes se desbloquean en orden.

## Controles
WASD/flechas: caminar. E: interactuar. Q: cambiar personaje. Espacio: poder en misión. R: volver junto a Tomás. F: elegir objetivo cercano. TAB: cuaderno/tablón. C: equipo en agencia. F5/F9: guardar/cargar. Esc: pausa. F3: FPS. Ratón para botones y selección de objetos cercanos.

## Contenido y alcance

- Prólogo y diálogo de encuentro, tutorial de vínculo, despedida de Elena y fundación de agencia.
- El último boleto, La maleta sin dueño, La llave prometida, La casa de los Ruiz, El archivo ausente, El lugar que recuerda.
- Casos con evidencias y requisitos físicos, hipótesis revisables, desbloqueos y decisiones de reclutamiento de Mateo/Nico/Mora. Tres alternativas comunitarias y tres desenlaces de Brizna.
- En misión Tomás es el ancla móvil; la oficina es un refugio separado. Los fantasmas leen y escuchan, no recuperan recuerdos ni descubren automáticamente culpables.
- Guardado v4 separado de los anteriores; automático al cambiar escenas y terminar diálogos. No se borran guardados antiguos.

La implementación es una primera pasada jugable del GDD, no el acabado final. Los mapas nuevos reutilizan temas visuales, el arte es procedural, las conversaciones aún son mayormente lineales y los sistemas de herramientas, economía, rutinas, confianza, música, accesibilidad avanzada, alternativas complejas de investigación, exportación de assets, Android y migración a Godot requieren trabajo adicional. El final presenta decisiones narrativas; no simula todas sus consecuencias en juego libre.

## Verificación
```
python -m unittest discover -s demo_python -v
python demo_python/capturas.py
```
GitHub Actions ejecuta pruebas con SDL virtual y genera capturas del juego.
