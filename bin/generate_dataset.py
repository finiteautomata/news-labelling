import os
import sys
import fire
import django
import json
from tqdm.auto import tqdm

sys.path.append(".")
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_labelling.settings'
django.setup()

from django.db.models import Count, Case, When, Value
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from api.models import Article
from dataset import CommentSerializer, ArticleSerializer

def print_comment_stats(comments):
    """
    Print hateful comment stats
    """
    possibly_hateful = len([c for c in comments if len(c['HATE']) > 0])
    hateful = len([c for c in comments if len(c['HATE']) >= 2])

    full_agreement = len([c for c in comments if len(c['HATE']) == 3])

    print("\n" + "="*80)
    print(f"Comentarios totales                             : {len(comments)}")
    print(f"Comentarios con >= 1 etiqueta de discriminación : {possibly_hateful}")
    print(f"Comentarios con >= 2 etiqueta de discriminación : {hateful}")
    print(f"Comentarios con >= 3 etiqueta de discriminación : {full_agreement}")
    print(f"Ratio de comentarios odiosos sobre totales = {hateful / len(comments):.2f}")
    print("="*80 + "\n")

def generate_dataset(comments_path, articles_path):
    """
    Generates dataset
    """

    annotated_articles = Article.objects.exclude(batch__name="training").annotate(
        num_labels=Count('labels'),
        effective_labels=Count(
            Case(When(labels__is_interesting=True, then=Value(1)))
        )
    )
    really_annotated_articles = annotated_articles.filter(effective_labels=3).count()

    skipped = 0

    for art in annotated_articles:
        if art.num_labels > art.effective_labels:
            skipped +=1


    print(f"Artículos totales: {Article.objects.count()}")
    print(f"Artículos con 3 anotaciones: {really_annotated_articles}")
    print(f"Artículos con alguna anotación: {annotated_articles.filter(num_labels__gte=1).count()}")
    print(f"Artículos que no pasaron a tercera anotación: {skipped}")

    serializer = CommentSerializer()
    article_serializer = ArticleSerializer()

    articles = []
    comments = []


    finished_articles = annotated_articles.filter(effective_labels=3).prefetch_related('comment_set', 'labels')

    for article in tqdm(finished_articles):
        articles.append(article_serializer.serialize(article))
        for comment in article.comment_set.all():
            new_comment = serializer.serialize(comment)
            comments.append(new_comment)

    print(f"Ignoramos {serializer.ignored_labels} etiquetas (marcadas con OTROS)")
    print_comment_stats(comments)

    with open(comments_path, "w+") as f:
        json.dump(comments, f, indent=4)
        print(f"{len(comments)} comentarios guardados en {comments_path}")

    with open(articles_path, "w+") as f:
        json.dump(articles, f, indent=4)
        print(f"{len(articles)} artículos guardados en {articles_path}\n")

if __name__ == '__main__':
    fire.Fire(generate_dataset)
