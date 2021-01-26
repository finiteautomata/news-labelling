from .factories import CommentLabelFactory

def label_article(user, article, is_interesting, comments=None):
    """
    Label article
    """
    article_label = user.article_labels.create(article=article, is_interesting=is_interesting)

    if is_interesting:
        if not comments or len(comments) != article.comment_set.count():
            raise ValueError("comments argument must be same size of comments")

        for label_args, comment in zip(comments, article.comment_set.all()):
            CommentLabelFactory(comment=comment, article_label=article_label, **label_args)

    return article.assignment_set.get(user=user)
