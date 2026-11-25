# Agencia de espectros — prototipo Python 0.4

Prototipo de escritorio en Python 3.10+ y Pygame-ce. Se reemplaza la presentación anterior de Tkinter; no hay una segunda versión del juego. Godot será la plataforma final después de validar el diseño.

## Arrancar en Windows

Extrae el ZIP del repositorio. En la carpeta del proyecto, ejecuta una sola vez:

```powershell
py -m pip install -r requirements.txt
```

Luego abre Iniciar_demo.bat o ejecuta `py demo_python/main.py`. Si tu instalación utiliza python en vez de py, usa ese comando. No es necesario instalar Godot. Se recomienda un entorno virtual si ya tienes instalado pygame clásico, porque comparte el nombre del módulo.

## Campaña y hub

Tomás es un expolicía retirado que ve espíritus después de un accidente. Comienza en su despacho provisional. Acércate al tablón, abre E o TAB y acepta El último boleto. Allí conoce a Brizna, una criatura nacida de las emociones del cine, nunca humana. Un vínculo provisional le permite colaborar cerca de Tomás; el vínculo estable nace al resolver el caso. La agencia se consolida y desbloquea La maleta sin dueño. Mateo es un espíritu errante debilitado; al resolver su caso puede quedarse voluntariamente o despedirse.

- Oficina: refugio separado, sin radio de alcance ni penalización por distancia. Todos los aliados vinculados recuperan recursos. Se aceptan expedientes en el tablón y se selecciona equipo; no se entra a otro caso caminando directamente desde una misión.
- Misión: el único ancla espacial del compañero es Tomás. Fuera del radio cae la estabilidad, y agotarla obliga a regresar junto a él. Los fantasmas pueden leer y escuchar, pero no recuperar recuerdos ni leer mentes. No pueden extraer pruebas físicas de cajas cerradas.
- Regresar al despacho por la salida conserva las pistas; un expediente abierto puede continuarse. Brizna no abandona el cine hasta completar el primero. La conclusión se presenta durante la misión; en la oficina los expedientes son consultables.
- En la estación hay dos rutas para conseguir el número de casillero. Tomás debe conseguir acceso y recoger las pruebas físicas. La decisión de Mateo no bloquea el juego.

## Controles
| Tecla | Acción |
|---|---|
| WASD / flechas | Mover |
| E | Interactuar |
| Q | Alternar detective y compañero disponible |
| Espacio | Poder en misión |
| F | Cambiar objetivo cercano |
| R | Volver junto a Tomás (misiones) |
| TAB | Tablón en oficina / evidencias en misión |
| C | Seleccionar compañero en oficina |
| J / P | Invitar o despedir a Mateo tras resolver su caso |
| F5 / F9 | Guardar / cargar |
| F3 | Mostrar FPS |
| Esc | Cerrar panel |

Los paneles de selección y evidencias admiten ratón. Las teclas 1–2 seleccionan expedientes y 1–3 hipótesis; Enter presenta la conclusión.

## Motor visual

Mapa nativo de 480×264, tiles de 24×24, sprites de 24×38, escalado sin interpolación y ventana redimensionable con letterbox. Fondos, muebles, texturas, sprites y máscaras de luz generados en Python. Caché de recursos, iluminación ambiental coloreada y emisión espectral, sombras de contacto, profundidad por coordenada Y, animación por dirección e interpolación. Los muebles principales bloquean a Tomás, no a los espíritus. No se usan imágenes externas. Arte aún provisional: no equivale a sprites dibujados por un artista, ni a un motor 3D o GPU con sombras físicas.

## Guardado y pruebas

Se usa un nuevo archivo local .agencia_espectros_v3.json en la carpeta del usuario. El guardado v2 no se sobrescribe ni se carga automáticamente. La campaña y el render son módulos separados. Android y Godot todavía no están implementados.

```
python -m unittest discover -s demo_python -v
python demo_python/capturas.py
```

El segundo comando guarda capturas reales en capturas/. GitHub Actions usa SDL virtual y adjunta las capturas si las pruebas pasan. No mide el rendimiento de una PC concreta. 
