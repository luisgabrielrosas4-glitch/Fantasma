# Sprites reutilizables

Copia la subcarpeta del personaje o escenario que quieras llevar a otro juego. Las hojas PNG están a su resolución original y tienen fondo transparente. Usa escalado entero con filtro de vecino más próximo.

## Personajes

| Personaje | Celda | Contenido |
| --- | --- | --- |
| [Tomás](personajes/tomas/) | 24 × 32 px | Caminata en cuatro direcciones, cuatro cuadros por fila |
| [Brizna](personajes/brizna/) | 24 × 24 px | Flotación en cuatro direcciones, cuatro cuadros por fila y una quinta fila de expresiones |
| [Enfermera](personajes/enfermera/) | 24 × 32 px | Caminata en cuatro direcciones, cuatro cuadros por fila |

Las direcciones van de arriba abajo en este orden: abajo, derecha, arriba e izquierda.

## Escenarios

Cada carpeta de [escenarios](escenarios/) incluye un atlas `tiles.png` de 24 × 24 px por casilla y su `tiles.tsj`. Conserva juntos ambos archivos al importar en Tiled. El tileset del exterior del Cine Aurora incluye tres fotogramas de lluvia.

Los [mapas completos de Agencia de Espectros](../assets/escenarios/) se editan desde sus archivos `mapa.tmj`. Ahí están las capas y los puntos de la campaña.

## Objetos por capas

El [mobiliario del hospital](objetos/hospital/) está separado en PNG de sombra, base y detalle. Cada pieza también tiene un `sprite.png` ensamblado. La subcarpeta `accesorios/` contiene objetos independientes para colocar encima de una superficie.
