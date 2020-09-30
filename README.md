# Hatespeech news labelling

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

5. Asignar artículos

```
python bin/assign_articles_to_user.py <username> --ids_file <json>

o

python bin/assign_articles_to_user.py <username> --number_of_articles 50
```

La primera opción asigna los artículos listados en el json. En el segundo caso asigna 50 artículos al azar de todos los disponibles

## Problemas?

Ante cualquier bug o consulta, usar el [issue tracker](https://github.com/finiteautomata/news-labelling/issues) de este repositorio haciendo una descripción del problema/mejora.
