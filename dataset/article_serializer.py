from datetime import datetime

class ArticleSerializer:
    """
    Serializer for articles
    """
    def serialize(self, article):
        date = datetime.strftime(article.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        ret = {
            "tweet_id": article.tweet_id,
            "title": article.title,
            "tweet_text": article.text,
            "body": article.body,
            "news": article.user,
            "date": date,
        }

        return ret
