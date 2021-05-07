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

def print_raw_comment_stats(comments):
    """
    Print hateful comment stats
    """
    possibly_hateful = len([c for c in comments if len(c["HATEFUL"]) > 0])
    hateful = len([c for c in comments if len(c["HATEFUL"]) >= 2])

    full_agreement = len([c for c in comments if len(c["HATEFUL"]) == 3])

    print("\n" + "="*80)
    print(f"Comentarios totales                             : {len(comments)}")
    print(f"Comentarios con >= 1 etiqueta de discriminación : {possibly_hateful}")
    print(f"Comentarios con >= 2 etiqueta de discriminación : {hateful}")
    print(f"Comentarios con >= 3 etiqueta de discriminación : {full_agreement}")
    print(f"Ratio de comentarios odiosos sobre totales = {hateful / len(comments):.2f}")
    print("="*80 + "\n")

def print_comment_stats(comments):
    """
    Print hateful comment stats
    """
    hateful = len([c for c in comments if c["HATEFUL"] > 0])


    print("\n" + "="*80)
    print(f"Comentarios totales                             : {len(comments)}")
    print(f"Comentarios con >= 2 etiqueta de discriminación : {hateful}")
    print(f"Ratio de comentarios odiosos sobre totales = {hateful / len(comments):.2f}")
    print("="*80 + "\n")



def generate_dataset(output_path, show_ids=False, raw=False):
    """
    Generates dataset

    Arguments:

    output_path: path
        Where to put the output

    show_ids: boolean (default False)
        True if you want tweet ids (no anonymization)

    raw: boolean (default False)
        True if you want the raw annotations
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

    serializer = CommentSerializer(anonymize=(not show_ids), raw=raw)
    article_serializer = ArticleSerializer()

    articles = []
    comments = []

    finished_articles = annotated_articles.filter(effective_labels=3).prefetch_related('comment_set', 'labels')

    for article in tqdm(finished_articles):
        serialized_article = article_serializer.serialize(article)

        serialized_article["comments"] = []
        for comment in article.comment_set.all():
            new_comment = serializer.serialize(comment)
            serialized_article["comments"].append(new_comment)
            comments.append(new_comment)

        articles.append(serialized_article)

    print(f"Ignoramos {serializer.ignored_labels} etiquetas (marcadas con OTROS)")

    if raw:
        print_raw_comment_stats(comments)
    else:
        print_comment_stats(comments)



    with open(output_path, "w+") as f:
        json.dump(articles, f, indent=4)
        print(f"{len(articles)} artículos guardados en {output_path}\n")

if __name__ == '__main__':
    fire.Fire(generate_dataset)
