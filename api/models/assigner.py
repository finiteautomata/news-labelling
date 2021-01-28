from django.db import transaction

class Assigner:
    """
    Objects responsible of assignment of articles to users

    """

    def assign_if_not_assigned(self, article, user):
        """
        Assign article to user if doesn't exist
        """
        if user.assignment_set.filter(article=article).exists():
            print(f"Assignment of '{article.title[:50]}' to {user.username} already exists -- skipping")
        else:
            return user.assignment_set.create(article=article)

    def assign(self, article, user, reassign=False, reassign_threshold=3):
        """
        Assign article to user

        Arguments:
        ----------

        article: an Article object
        user: an User
        reassign
        """
        num_assignments = article.assignment_set.count()

        times_annotated = article.labels.filter(is_interesting=True).count()

        users = [assignment.user for assignment in article.assignment_set.all()]

        if num_assignments <= 1:
            """
            If one or zero assignments, just assign if it is not already assigned
            """
            return self.assign_if_not_assigned(article, user)
        else:
            if user in users and reassign:
                # Should reassign
                assignment = article.assignment_set.get(user=user)

                return self._reassign(article, user, assignment, reassign_threshold)
            elif times_annotated == 2:
                # Article was annotated twice, but not by user
                return self._assign_only_hateful(article, user)

    def comments_labeled_as_hateful(self, article, user):
        """
        Return comments labeled as hateful by at least one annotator
        """
        article_labels = article.labels.exclude(
            user=user
        ).filter(is_interesting=True).prefetch_related('comment_labels', 'comment_labels__comment')

        return {comment_label.comment
            for article_label in article_labels
            for comment_label in article_label.comment_labels.all()
            if comment_label.is_hateful
        }
    def _assign_only_hateful(self, article, user):
        """
        Assign only comments labeled as hateful by any annotator
        """
        comments_to_assign = self.comments_labeled_as_hateful(article, user)

        if len(comments_to_assign) > 0:
            with transaction.atomic():
                assignment = user.assignment_set.create(
                    article=article,
                    skippable=False,
                )

                assignment.comments.set(comments_to_assign)
                return assignment



    def _reassign(self, article, user, assignment, reassign_threshold):
        """
        Reassign when skipped
        """

        if not assignment.done or assignment.article_label.is_interesting:
            raise ValueError("Should be a skipped assignment")

        other_labels = article.labels.exclude(user=user).filter(is_interesting=True)
        if not other_labels.exists():
            raise ValueError("Should reassign wrt an annotated assignment")

        with transaction.atomic():
            comments_to_reassign = self.comments_labeled_as_hateful(article, user)

            if len(comments_to_reassign) >= reassign_threshold:
                assignment.remove_label()
                assignment.skippable = False
                assignment.reassigned = True
                assignment.save(update_fields=["skippable", "reassigned"])

            assignment.refresh_from_db()
            return assignment
