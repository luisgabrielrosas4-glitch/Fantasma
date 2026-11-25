"""Contenido narrativo del GDD 0.4. Identificadores estables para futura migración."""
ORDER=("cine","station","workshop","ruiz","archive","final")
NAMES={"office":"Despacho de Tomás","cine":"Cine Aurora","station":"Estación del barrio","hospital":"Hospital","house":"Casa de Tomás","street":"Exterior del Cine Aurora","workshop":"Taller de Nico","ruiz":"Casa de los Ruiz","archive":"Archivo comunitario","final":"Cine Aurora · reunión"}
THEMES={"hospital":"station","house":"office","street":"cine","workshop":"office","ruiz":"office","archive":"station","final":"cine"}
PROLOGUE_MAPS={
 "hospital":{"nurse":(5,4,"Enfermera","npc"),"patient":(9,3,"Silueta junto a la silla","ghost"),"exit":(18,8,"Alta médica · salida","exit")},
 "house":{"notebook":(5,3,"Libreta policial","paper"),"photo":(8,3,"Fotografías familiares","paper"),"coat":(12,6,"Abrigo","box"),"exit":(18,8,"Salir al despacho","exit")},
 "street":{"rafael":(5,4,"Rafael, conserje","npc"),"poster":(9,3,"Marquesina del Cine Aurora","paper"),"exit":(18,8,"Entrar al cine","exit")}
}
EXTRA={
 "workshop":{
 "title":"La llave prometida","client":"Nico prometió dejarle a su sobrina la llave del taller, pero cree que el propietario la retuvo.",
 "person":"Nico","guard":"Propietario del taller","witness_name":"Sobrina de Nico","witness_kind":"npc",
 "objects":("Orden de copia","Registro de cerrajería","Recibo de depósito","Cerradura del taller"),
 "clues":{"request":"Nico vio su llave original en el cajón; no vio que le negaran acceso a su sobrina.","schedule":"La sobrina solicitó una copia antes del cierre.","heard":"El propietario explica el protocolo de depósito y autoriza consultar el registro.","witness":"La sobrina muestra su propia llave y confirma que usa el taller.","desk":"El registro de cerrajería acredita la entrega de una copia a la sobrina.","item":"Recibo firmado: el original quedó bajo custodia por seguridad.","photo":"La copia abre el acceso normal; prueba realizada con autorización."},
 "choices":["El propietario retuvo toda llave.","La sobrina recibió una copia autorizada; el original quedó en depósito.","Nico nunca hizo la promesa."],
 "correct":1,"required":["request","desk","item"],"physical_required":["desk","item"],"either":["witness","photo"],
 "intro":[("Nico","Esa puerta tenía que abrirse para ella, no para mí."),("Tomás","¿Vio que le negaran la llave?"),("Nico","No. Vi que la mía seguía en el cajón.")],
 "closing":[("Nico","Entonces sí pudo abrir su taller. Cumplí mi promesa."),("Brizna","¡Una llave puede abrir más de una historia!")],
 "ally":["Nico","mechanism"]},
 "ruiz":{
 "title":"La casa de los Ruiz","client":"Clara Ruiz cree que su hijo nunca respondió su carta. Mora, una gata espectral, ronda el archivo.",
 "person":"Clara","guard":"Conserje de los Ruiz","witness_name":"Familiar de Clara","witness_kind":"npc",
 "objects":("Carta original","Libro de correspondencia","Sobre archivado","Fotografía y firma"),
 "clues":{"request":"Clara quería saber si su hijo la había perdonado.","schedule":"Carta original con dirección, destinatario y fecha.","heard":"El conserje admite que pudo archivar la respuesta con otro apellido.","witness":"El familiar confirma el apellido abreviado y la letra del hijo.","desk":"Libro de correspondencia: entrada bajo un apellido abreviado.","item":"Sobre archivado: respuesta firmada que coincide con la carta original.","photo":"La firma coincide con las muestras familiares.","mora":"Mora señala el rincón del archivo; no revela el contenido de la carta."},
 "choices":["El hijo nunca respondió.","Mora escondió la carta.","El hijo respondió; la carta quedó archivada con otro apellido."],
 "correct":2,"required":["request","schedule","desk","item"],"physical_required":["schedule","desk","item"],"either":["heard","witness"],
 "intro":[("Clara","No necesitaba que volviera. Solo quería saber si me había perdonado."),("Tomás","Buscaremos si hubo una respuesta. No voy a prometer lo que todavía no sé."),("Brizna","Mora insiste en ese rincón. ¿Nos estará pidiendo algo?")],
 "closing":[("Clara","Ahora sé que me escuchó. Gracias."),("Brizna","Mora... ¿quieres venir a conocer nuestra casa?")],
 "ally":["Mora","track"]},
 "archive":{
 "title":"El archivo ausente","client":"Sara, archivista viva, teme que varias piezas del cine hayan sido vendidas.",
 "person":"Sara","client_kind":"npc","guard":"Responsable del depósito","witness_name":"Testigo del traslado","witness_kind":"ghost",
 "objects":("Inventario antiguo","Acta de filtración","Copia de recepción","Inventario actualizado"),
 "clues":{"request":"Sara pide aclarar la desaparición aparente de las piezas del inventario.","schedule":"Inventario antiguo: números de las piezas antes del traslado.","heard":"El responsable explica el retraso en actualizar el inventario.","witness":"Un espíritu vio cajas trasladadas, no ventas.","desk":"Acta de filtración: traslado preventivo autorizado.","item":"Copia de recepción: cajas identificadas en depósito comunitario.","photo":"Inventario actualizado: coinciden los números de las piezas."},
 "choices":["Las piezas fueron vendidas.","Las piezas se trasladaron por la filtración y faltaba actualizar una copia.","Los espíritus destruyeron el archivo."],
 "correct":1,"required":["request","schedule","desk","item","photo"],"physical_required":["schedule","desk","item","photo"],
 "intro":[("Sara","Una copia parece decir que vendieron las piezas. No quiero acusar sin estar segura."),("Tomás","Comparemos las versiones y las fechas antes de señalar a nadie.")],
 "closing":[("Sara","Los números coinciden. Podemos preservar el inventario."),("Brizna","Guardar objetos no es lo mismo que guardar personas. ¿Verdad?")]},
 "final":{
 "title":"El lugar que recuerda","client":"La comunidad decide qué hacer con el Cine Aurora. Brizna teme desaparecer si el cine cambia.",
 "person":"Sara","client_kind":"npc","guard":"Responsable municipal","witness_name":"Representante vecinal","witness_kind":"npc",
 "objects":("Actas de propiedad","Informe técnico","Propuesta de conservación","Inventario verificado"),
 "clues":{"request":"Sara convoca una reunión para decidir el futuro del cine.","schedule":"Actas de propiedad y permisos: determinan quién puede decidir.","heard":"Responsable municipal: no se puede ocupar la parte insegura sin obras.","witness":"La comunidad contempla centro cultural, archivo o traslado.","desk":"Informe técnico: zonas seguras y restricciones estructurales.","item":"Propuestas documentadas: centro cultural en zona segura, archivo o traslado autorizado.","photo":"Inventario verificado y evaluación de piezas del caso 5.","wish":"Brizna quiere elegir su futuro; no necesita conservar cada objeto en su sitio."},
 "choices":["Solo conservar todo en su sitio puede salvar a Brizna.","Existen alternativas viables; conservar la memoria no exige mantener todo en su lugar.","No hace falta consultar a nadie."],
 "correct":1,"required":["request","schedule","desk","item","photo","wish"],"physical_required":["schedule","desk","item","photo"],
 "intro":[("Sara","Hay varias propuestas, pero necesitamos saber qué podemos conservar con seguridad."),("Brizna","Si cambian el cine, ¿yo voy a cambiar también?"),("Tomás","Probablemente. Cambiar no es lo mismo que desaparecer.")],
 "closing":[("Brizna","Entonces quiero elegir qué hago después."),("Tomás","Esa decisión es tuya. No tienes que demostrar nada a nadie.")]}
}
DIALOGUES={
 "accident":[("Narrador","Lluvia. Un frenazo. Después, silencio."),("Tomás","¿Dónde estoy?")],
 "hospital:nurse":[("Enfermera","¿Se encuentra bien? Lleva un rato mirando esa silla."),("Tomás","¿El señor que estaba sentado ahí ya se fue?"),("Enfermera","No ha entrado nadie más desde que llegó."),("Tomás","...Claro. Debe ser el cansancio.")],
 "hospital:patient":[("Silueta","No todos los que esperan aquí están esperando el alta."),("Tomás","¿Me está hablando a mí?")],
 "house:notebook":[("Tomás","Mi vieja libreta policial. Ya no tengo placa, pero todavía sé hacer preguntas.")],
 "house:photo":[("Tomás","Necesito volver a mi vida. Si es que sigue siendo la misma.")],
 "house:coat":[("Tomás","El abrigo de siempre. Me vendrá bien salir un poco.")],
 "office:rafael":[("Rafael","Tomás, hay ruidos en el cine. La radio suena incluso sin corriente."),("Tomás","No prometo nada, pero iré a echar un vistazo.")],
 "street:rafael":[("Rafael","La marquesina lleva años apagada. Puedes pasar."),("Tomás","Gracias. Voy a comprobarlo.")],
 "cine:brizna":[("Tomás","Tranquilo. No pienso hacerte daño. ¿Tienes nombre?"),("Brizna","¿Nombre? Tengo boletos. ¿Sirven?"),("Tomás","No exactamente. ¿Desde cuándo estás aquí?"),("Brizna","Desde que sé que estoy aquí. Antes no había un antes."),("Tomás","¿Nunca saliste del cine?"),("Brizna","Lo intento, pero me cuesta seguir siendo yo."),("Tomás","Entonces probemos juntos. Si te incomoda, paramos.")],
 "cine:client":[("Brizna","Elena, mira. Él también me ve."),("Elena","¿Y qué puede hacer por nosotros un hombre que todavía respira?"),("Tomás","Escucharla, para empezar. ¿Qué le preocupa?"),("Elena","La niña de la última función. Su asiento estaba vacío. Nunca supe si hice bien."),("Tomás","¿La vio salir o solo vio el asiento vacío?"),("Elena","Solo el asiento. Eso es lo que no me deja tranquila.")],
 "cine:guard":[("Rafael","¿Encontraste algo?"),("Tomás","Necesito consultar el registro de la última función."),("Rafael","Si me explicas qué buscas, puedo dejarte pasar.")],
 "cine:closing":[("Elena","Siempre creí que tenía que quedarme para encontrarla."),("Brizna","¿Y ahora adónde vas?"),("Elena","A donde me toque. Tú todavía tienes mucho por conocer.")],
 "foundation":[("Brizna","¿También puedo estar aquí? No se parece a mi cine."),("Tomás","Si quieres, podemos arreglar este lugar."),("Brizna","¿Y si llegan otros como yo?"),("Tomás","Entonces tendremos que poner otro asiento."),("Brizna","¿Eso es un hogar?"),("Tomás","Puede llegar a serlo.")],
 "office:guest":[("Mateo","¿Este lugar... es para gente como yo?"),("Brizna","¡Sí! Bueno, estamos aprendiendo qué clase de lugar es."),("Tomás","¿Cómo se llama? No hace falta que recuerde todo."),("Mateo","Mateo. Dejé una maleta para mi hermano en la estación. No sé si volvió por ella."),("Tomás","¿Qué detalles recuerda de cuando la dejó?"),("Mateo","Una etiqueta. El apellido. Y el tren que no salió.")],
 "station:client":[("Mateo","Aquí fue. La etiqueta y el tren cancelado son lo único que tengo claro."),("Tomás","Vamos a comprobar qué pasó.")],
 "station:guard":[("Inés","Protejo los registros de esta estación. ¿Qué necesita?"),("Tomás","Localizar una maleta antigua. Necesito contrastar los datos.")],
 "station:witness":[("Brizna","Hola. Soy Brizna. ¿Viste dónde llevaron aquella maleta?"),("Silvia","Oí casillero cuatro. No vi quién la retiró. No me hagas decir más de lo que sé.")],
 "station:closing":[("Mateo","Mi hermano sí volvió. Pensé que me había olvidado."),("Brizna","Ahora ya lo sabes.")],
 "office:home":[("Brizna","Aquí están mis boletos. Creo que este lugar también es mío."),("Tomás","Y no tienes que quedarte pegado a mí dentro de la oficina.")],
}
