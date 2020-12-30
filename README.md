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


6. Asignar artículos

```
python bin/assign_batch.py <username> <batch_name>
```


## Running

```
uwsgi --http :8001 --module news_labelling.wsgi --logto logs/labelling.log
```
## Problemas?

Ante cualquier bug o consulta, usar el [issue tracker](https://github.com/finiteautomata/news-labelling/issues) de este repositorio haciendo una descripción del problema/mejora.
