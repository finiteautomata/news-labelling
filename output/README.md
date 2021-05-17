# Dataset contextualizado de Hate Speech

Tenemos dos versiones del dataset

- `dataset.raw.json`: dataset con anotaciones crudas, sin procesar
- `dataset.json`: dataset ya "asignado"; es decir, con etiquetas binarias

## dataset.raw.json

Este archivo contiene una array de `JSON`. Cada elemento de este array representa un "artículoes un objeto JSON con los siguientes atributos:

- `tweet_id`: string que representa el id del tweet
- `tweet_text`: Texto del tweet
- `title`: Título del Artículo
- `body`: Cuerpo completo del artículo
- `news`: Nombre del medio (en nuestro caso, es uno de los siguientes: `infobae`, `clarincom`, `perfilcom`, `lanacion`, `cronica`)
- `date`: Fecha en formato ISO
- `comments`: Lista de comentarios. Cada comentario tiene los siguientes:
    - `id`: Identificador interno de comentarios
    - `text`: Texto del comentario
    - `article_id`: Tweet id del artículo (redundante)
    - `tweet_id`: Tweet id del comentario (**USO INTERNO - Luego va a sacarse esto**)
    - `annotators`: Nombres anonimizados de los anotadores
    - `HATEFUL`: Anotadores que marcaron el comentario como odioso
    - `CALLS`: Anotadores que marcaron el comentario como un llamado a la acción
    - `WOMEN`: Anotadores que marcaron "MUJER" como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
    - `LGBTI`: Anotadores que marcaron `LGBTI` como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
    - `RACISM`: Anotadores que marcaron `RACISMO` como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
    - `CLASS`: Anotadores que marcaron `POBREZA` como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
    - `POLITICS`: Anotadores que marcaron `POLITICA` como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
    - `DISABLED`: Anotadores que marcaron `DISCAPACIDAD` como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
    - `APPEARANCE`: Anotadores que marcaron `APARIENCIA` como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
    - `CRIMINAL`: Anotadores que marcaron `CRIMINAL` como característica atacada en el tweet (sólo para quienes marcaron HATEFUL)
### Ejemplo de objeto crudo
```json
 {
        "tweet_id": "1241486782178435072",
        "title": "Coronavirus en Argentina: Cristina Kirchner vuelve de Cuba junto a su hija Florencia y permanecerá aislada por 14 días",
        "tweet_text": "Coronavirus en Argentina: Cristina Kirchner vuelve de Cuba junto a su hija Florencia y permanecerá aislada por 14 días https://t.co/ltgNhDGTlZ",
        "body": "En plena cuarentena, la vicepresidenta Cristina Fernández de Kirchner llegará este domingo de Cuba junto a su hija Florencia, quien vuelve a la Argentina tras un año de tratamientos médicos en ese país. Tal como anunció en sus redes sociales, la ex mandataria se mantendrá durante dos semanas en aislamiento.\n\n\"Si bien Cuba no es un país de riesgo, al llegar cumpliré con los 14 días de aislamiento\", escribió el viernes en cuenta de Twitter.\n\nEn su entorno confirmaron que, aunque por su carácter de vicepresidenta de la Nación está exceptuada de la cuarentena obligatoria decretada para todo el país, se mantendrá resguardada por precaución.\n\n\n\nLa exmandataria llegará en el vuelo semanal de Cubana de Aviación -la aerolínea oficial de ese país- con su hija Florencia, quien estuvo en tratamiento durante un año y días en el Centro de Investigaciones Médicas Quirúrgicas (CIMEQ) de La Habana.\n\nDurante ese periodo la presidenta del Senado hizo diez vuelos a a ese país para visitarla y asistirla. \"Flor me pidió que la venga a buscar para ayudarla... sentía que sola no iba a poder\", contó.\n\nSin embargo, en su entorno señalaron que lo más probable es que el aislamiento lo cumplan por separado y que la vicepresidenta se quede en su departamento en Recoleta.\n\nEn el Senado -que congeló su actividad hasta fin de mes- no tiene tareas programadas y con el presiente Alberto Fernández, ​aseguran, mantiene contactos diarios por teléfono.\n\nEn marzo de 2019 Florencia Kirchner fue diagnosticada en Cuba con \"trastorno de estrés postraumático\", \"síndrome purpúrico\", \"polineuropatía sensitiva desmielinizante de etiología desconocida\", \"amenorrea\", \"bajo peso corporal\" y \"linfederma ligero de miembros inferiores de etiología no precisada\".\n\n\"Llegué con las piernas llenas de hematomas, dolores incesables. Pesando menos que el aire. Tan poco me movía y con tanto miedo lo hacía. Venía de ver médicos sin parar, pero La Cosa que me pasaba era nada. Molestias de nena para muchos profesionales. Llegué acá mirando mal a los médicos y me la fui dando -la mente- contra los cajones, porque después de mucho tiempo se me trataba como persona\", escribió en su cuenta de Instagram antes de volar hacia Buenos Aires.\n\nEn el texto, en el que aseguró que no sabe \"cómo decirle gracias\" a Cuba\" y que se va de ese país llorando, también apuntó contra el gobierno de Mauricio Macri.\n\n\"Me fui de una Argentina sin ministerio de Salud, regreso a una que lo tiene. Solo pienso en qué hubiese sucedido de haber esto ocurrido con el anterior Gobierno\", planteó en alusión a la crisis por la pandemia del coronavirus. \"Llegaré y, por supuesto, estaré en casa\".\n\nFlorencia Kirchner irá a juicio oral junto a su madre y su hermano Máximo Kirchner en dos causas: es investigada por la Justicia por la causa del hotel Hotesur -es dueña del hotel en un 50% de las acciones- y la inmobiliaria Los Sauces, donde tiene el 22,5% de las acciones. Florencia ya suma 900 millones de pesos en embargos de las dos causas.\n\nPJB",
        "news": "clarincom",
        "date": "2020-03-22T01:08:09.000000Z",
        "comments": [
            {
                "id": 327916,
                "text": "@usuario Momento oportuno para hacer esa movida!!!!..ahora que la JUSTICIA está en veda sanitaria..!!!!..",
                "article_id": "1241486782178435072",
                "annotators": [
                    "annotator_5",
                    "annotator_2"
                ],
                "HATEFUL": [],
                "CALLS": [],
                "WOMEN": [],
                "LGBTI": [],
                "RACISM": [],
                "CLASS": [],
                "POLITICS": [],
                "DISABLED": [],
                "APPEARANCE": [],
                "CRIMINAL": [],
                "tweet_id": "1241513939499876354"
            },
            {
                "id": 327917,
                "text": "@usuario vienen medicos cubanos... ahhh pero no veo ninguna ayuda norteamericana, quienes ni siquiera les importa, seguro que ellos generaron esto, lacras de mierda",
                "article_id": "1241486782178435072",
                "annotators": [
                    "annotator_5",
                    "annotator_2",
                    "annotator_1"
                ],
                "HATEFUL": [
                    "annotator_2"
                ],
                "CALLS": [],
                "WOMEN": [],
                "LGBTI": [],
                "RACISM": [
                    "annotator_2"
                ],
                "CLASS": [],
                "POLITICS": [],
                "DISABLED": [],
                "APPEARANCE": [],
                "CRIMINAL": [],
                "tweet_id": "1241524087773593600"
            }
        ]
 }
```

## dataset.json

El dataset anterior, sólo que reemplazando los nombres de los anotadores por etiquetas binarias. Si un comentario tiene dos o más etiquetas de `HATEFUL`, entonces tiene un `1`; caso contrario, un 0. Igual tratamiento tiene `CALLS`; en el caso de las características protegidas, se marcan con `1` todas las que al menos un etiquetador haya marcado.

Ilustramos con ejemplos de cómo quedan los comentarios:

```json
    {
        "id": 327933,
        "text": "@usuario Que se queden toda la vida encerrada!!!",
        "article_id": "1241486782178435072",
        "annotators": [
            "annotator_5",
            "annotator_2"
        ],
        "HATEFUL": 0,
        "CALLS": 0,
        "WOMEN": 0,
        "LGBTI": 0,
        "RACISM": 0,
        "CLASS": 0,
        "POLITICS": 0,
        "DISABLED": 0,
        "APPEARANCE": 0,
        "CRIMINAL": 0,
        "tweet_id": "1241692765865627651"
    },
    {
        "id": 327934,
        "text": "@usuario Que cirujeada esta la supuesta enfermita!  Hipocritas.",
        "article_id": "1241486782178435072",
        "annotators": [
            "annotator_5",
            "annotator_2",
            "annotator_1"
        ],
        "HATEFUL": 1,
        "CALLS": 0,
        "WOMEN": 1,
        "LGBTI": 0,
        "RACISM": 0,
        "CLASS": 0,
        "POLITICS": 0,
        "DISABLED": 0,
        "APPEARANCE": 1,
        "CRIMINAL": 0,
        "tweet_id": "1241492662084980736"
    }
```
