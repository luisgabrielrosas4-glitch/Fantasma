# Objetos del hospital

Los PNG de cada mueble se superponen desde la misma esquina superior izquierda. El orden de dibujo es `sombra.png`, `base.png` y `detalle.png`. La base dibuja la forma completa. El detalle añade reflejos, vetas, pliegues o indicadores. Usa `sprite.png` para importar la pieza ya compuesta en un motor que solo necesite una textura.

Los tres PNG de `accesorios/` se colocan encima de la base del mobiliario. El terminal, la bandeja y el portapapeles pueden moverse o cambiarse de forma independiente. Los lienzos son múltiplos de 24 px y `piezas.json` registra las medidas y rutas.

El [mapa del hospital](../../../assets/escenarios/hospital/mapa.tmj) tiene capas independientes para sombras, bases, detalles y accesorios. El tileset de mobiliario toma las celdas de estas mismas imágenes.

En `ventilacion/` están las rejillas empotradas en vista frontal y lateral. Se montan en la capa `Ventilación` del mapa, cada una sobre la pared que corresponde.
