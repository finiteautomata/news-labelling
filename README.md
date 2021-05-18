# Hatespeech news labelling

![example workflow name](https://github.com/finiteautomata/news-labelling/workflows/run_tests/badge.svg)


Repositorio de etiquetador de discurso de odio en notas periodísticas

## Instrucciones

1. Instalar dependencias

```
pipenv shell
pipenv sync
```

2. Correr migraciones

```
./manage.py migrate
```

3. Crear superusuario

```
./manage.py createsuperuser
```

4. Cargar datos

```
python bin/load_articles.py <json>
```

5. Crear batches

```
python bin/load_batches.py --remove # Use --remove if need to remove previous batches
```

Para usar nuevos artículos


```
python bin/load_batches.py --remaining --batch_size 15
```


6. Asignar artículos

```
python bin/assign_batch.py <username> <batch_name>
```


7. Generar dataset

```
python bin/generate_dataset.py output/dataset.json --show_ids
# Crea dataset con tweet ids, sólo para uso interno
python bin/generate_dataset.py output/dataset.raw.json --show_ids --raw
```

## Running

```
uwsgi --http :8001 --module news_labelling.wsgi --logto logs/labelling.log
```



## Create demo database

```
python bin/clean_database.py
python bin/load_articles <json> --max_comments 10
python bin/load_batches

```
## Problemas?

Ante cualquier bug o consulta, usar el [issue tracker](https://github.com/finiteautomata/news-labelling/issues) de este repositorio haciendo una descripción del problema/mejora.


