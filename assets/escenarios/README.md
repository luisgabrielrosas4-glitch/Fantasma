# Escenarios de Agencia de Espectros

Abre `mapa.tmj` de cualquier carpeta en Tiled. Cada mapa usa su propio `tiles.tsj` y atlas PNG de **24 × 24 px por casilla**. Mantén los tres archivos juntos al mover un escenario. Usa un factor entero y el filtro de vecino más próximo para ampliar los PNG.

| Carpeta | Escenario | Elementos principales |
| --- | --- | --- |
| `hospital` | Hospital | Habitación, enfermería, espera, pasillos y señalización de salida |
| `house` | Casa de Tomás | Dormitorio, estudio y sala con suelos de madera y alfombra |
| `street` | Exterior del Cine Aurora | Fachada art déco, marquesina, taquilla, banquetas, luminarias, charcos y lluvia |
| `cine` | Interior del Cine Aurora | Vestíbulo, pasillos, proyección, butacas, cabina, radio, puertas y trastienda |
| `office` | Agencia | Recepción, escritorio, archivadores, tablón, sofá, perchero y rincón espectral |
| `station` | Estación ferroviaria | Vías, andén, ventanilla y consigna |
| `workshop` | Taller | Herramientas, maquinaria, oficina, depósito y patio de carga |
| `ruiz` | Casa de los Ruiz | Sala, dormitorio, patio con fuente y correspondencia |
| `archive` | Archivo comunitario | Consulta, estantes de documentos, cotejo y depósito |
| `final` | Cine y plaza comunitaria | Cine conectado a la plaza, mobiliario y puestos para la reunión |
| `deposito` | Depósito | Mostrador, estanterías, armarios y custodia |
| `patio` | Patio de carga | Maniobras, tarimas, equipo de carga y descanso |

El suelo, la arquitectura, los detalles, el mobiliario y la lluvia están en capas separadas. La lluvia del exterior usa tres fotogramas de 100 ms en el tileset. Actívala u ocúltala desde la capa `Lluvia`.

Las capas de objetos incluyen colisiones, puertas, zonas restringidas, sectores y puntos de la campaña. Los diez mapas del prototipo conservan las casillas y los identificadores de `demo_python/niveles.py`. Depósito y patio también tienen ejemplos autónomos para reutilizar sus tilesets. El prototipo en Python todavía dibuja sus mapas con el renderizador actual.
