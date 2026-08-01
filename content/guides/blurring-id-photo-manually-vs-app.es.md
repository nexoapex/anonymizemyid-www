---
title: "Difuminar tu DNI a mano o con una app dedicada"
subtitle: "Qué acierta la edición manual, qué se le escapa y cuándo cada opción es suficiente."
description: "Difuminar la foto de un documento con una app de marcado es mejor que nada, pero se le escapan cosas que una app de censura dedicada cubre por defecto."
date: 2026-07-20
lastmod: 2026-08-01
weight: 6
slug: "difuminar-el-dni-a-mano-o-con-app"
keywords:
  - "desenfoque"
  - "censurar"
  - "herramientas"
  - "cómo hacerlo"
answer: "Difuminar a mano es mejor que enviar una foto sin editar, pero tiene tres carencias reales: el desenfoque y el pixelado suave a veces se pueden revertir, es fácil olvidar un campo como la zona de lectura mecánica y no hay marca de agua que ate la copia a un único uso. Para todo lo que salga de tu control, usa censura opaca y aplanada."
takeaways:
  - "**Las cajas opacas eliminan los píxeles**; el desenfoque y el pixelado pierden información, pero no siempre la destruyen."
  - "**La MRZ es el campo que todo el mundo olvida**: si se escapa, echa por tierra el resto de la censura."
  - "El original sin censurar suele quedarse en el carrete junto a la versión editada, listo para enviarse por error."
  - "La edición manual es proporcionada para compartir algo de poco riesgo cuando sabes exactamente dónde se detiene la imagen."
faq:
  - q: "¿Es suficiente difuminar la foto de mi documento con la app de marcado del móvil?"
    a: "Es mejor que enviar una foto sin editar, pero tiene carencias reales: el desenfoque y el pixelado a veces se pueden revertir, es fácil pasar por alto un campo como la zona de lectura mecánica si no sabes que hay que taparlo, y no queda ninguna marca de agua que ligue la copia a un fin concreto."
  - q: "¿Se puede recuperar de verdad un texto difuminado?"
    a: "En las condiciones adecuadas, sí — el desenfoque ligero y el pixelado son técnicas con pérdida pero no siempre destructivas, y existe investigación documentada sobre reconstruir texto a partir de ambas. Una caja sólida y opaca elimina los píxeles por completo y no tiene ese problema."
  - q: "¿Qué hace distinto una app de censura dedicada?"
    a: "Está pensada específicamente para los campos que de verdad tiene un pasaporte o un DNI — incluidos los que se suelen olvidar, como la zona de lectura mecánica —, aplica por defecto una censura sólida y no reversible, añade una marca de agua y aplana el resultado para que no quede ninguna capa editable debajo."
  - q: "¿Cuándo es realmente suficiente la edición manual?"
    a: "Para compartir de muy bajo riesgo donde controlas los dos extremos — por ejemplo, mandarle por mensaje a un familiar una vista parcial que ya ha visto en persona. Para cualquier cosa que salga de tu control, las carencias anteriores empiezan a importar."
---

Tu móvil ya tiene una herramienta de marcado. Dibujas una caja negra o un desenfoque sobre el número de tu pasaporte, y parece que ya está. En general lo está — pero hay varias formas concretas en las que esto se queda corto respecto a lo que debería proteger de verdad una copia que va a salir de tus manos.

## Qué acierta la edición manual

Tapar el campo obvio — normalmente el número de documento — con una caja negra o un garabato grueso evita que una mirada superficial lo lea. Para situaciones de bajo riesgo donde confías exactamente en quién recibe la imagen y se queda con esa persona, muchas veces es de verdad suficiente.

## Dónde se queda corta

**El desenfoque y el pixelado no siempre son definitivos.** El desenfoque ligero y el pixelado de baja intensidad tienen pérdida, pero no son destructivos — en las condiciones adecuadas, el contenido original a veces se puede reconstruir. Y no es folclore: en [*Defeating Image Obfuscation with Deep Learning*](https://arxiv.org/abs/1609.00408), investigadores de Cornell Tech y la Universidad de Texas en Austin entrenaron redes neuronales para volver a leer caras, objetos y cifras en imágenes pixeladas y desenfocadas. Una **caja sólida y opaca** elimina los datos de los píxeles por completo y no tiene este problema; no todas las apps de marcado lo aplican por defecto.

**Es fácil pasar por alto un campo que no sabes que tienes que buscar.** La mayoría de la gente que censura un pasaporte a mano se acuerda del número. Muchas menos piensan en la **[zona de lectura mecánica]({{< relref "/guides/what-is-the-mrz-machine-readable-zone.md" >}})** — vuelve a codificar el número, la fecha de nacimiento y más, así que pasarla por alto anula el resto de la censura. La fecha de nacimiento y la firma también se olvidan, porque no parecen tan obviamente «sensibles» como un número de documento.

**No hay marca de agua.** Una foto difuminada a mano sigue siendo solo una foto — si se reenvía más allá de donde estaba pensada, nada en la imagen la liga a la solicitud concreta para la que se hizo.

**El original suele seguir existiendo al lado.** Las apps de marcado suelen editar un duplicado, pero la foto de origen — sin censurar — habitualmente se queda en el carrete, y es fácil coger y enviar la que no es bajo presión.

## Cara a cara

| | Herramienta de marcado manual | Flujo de censura dedicado |
| --- | --- | --- |
| **Reversibilidad** | El desenfoque y el pixelado suave pierden información, pero no siempre la destruyen | Cajas opacas por defecto: los píxeles desaparecen |
| **Zona de lectura mecánica** | Fácil de olvidar; no «parece» sensible | Tratada como un campo más que hay que tapar |
| **Marca de agua** | Ninguna | Se aplica automáticamente, con destinatario y fecha |
| **Capas editables** | El marcado puede sobrevivir como capa que se quita | Se aplana al exportar |
| **El original** | El original sin censurar suele quedarse en el carrete | Solo se exporta la copia censurada |
| **Proporcionado para** | Compartir de poco riesgo y bajo tu control | Todo lo que salga de tu control |

## Qué hace distinto un flujo de censura dedicado

Está construido alrededor de lo que de verdad tiene un pasaporte o un DNI: cajas sólidas y no reversibles por defecto (no desenfoque), avisos para los campos que se suelen olvidar, una marca de agua aplicada de forma automática y una exportación aplanada sin ninguna capa editable debajo que se pueda despegar después. [Anonymize my ID](/#get) hace exactamente esto, enteramente en el propio dispositivo — consulta [cómo censurar un pasaporte o DNI]({{< relref "/guides/how-to-redact-a-passport-or-id.md" >}}) para el método completo.

## Cuándo la edición manual es realmente suficiente

Si le mandas una vista parcial a alguien que ya ha visto el original en persona, y no sale nunca de esa conversación, una tapadura manual rápida es proporcionada. Las carencias anteriores importan sobre todo justo cuando una copia va a un sitio que no controlas del todo — que, para la mayoría de las peticiones de esta serie de guías, es exactamente la situación.
