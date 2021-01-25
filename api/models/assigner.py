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

    def assign(self, article, user, reassign=False):
        """
        Assign article to user

        Arguments:
        ----------

        article: an Article object
        user: an User
        reassign
        """
        num_assignments = article.assignment_set.count()

        users = [assignment.user for assignment in article.assignment_set.all()]

        if num_assignments <= 1:
            """
            If one or zero assignments, just assign if it is not already assigned
            """
            return self.assign_if_not_assigned(article, user)
        elif num_assignments == 2:
            if user in users and reassign:
                # Should reassign
                assignment = article.assignment_set.get(user=user)
                another_assignment = article.assignment_set.exclude(user=user)[0]

                return self._reassign(assignment, another_assignment)




    def _reassign(self, assignment, another_assignment):
        """
        Reassign when skipped
        """

        if not assignment.done or assignment.article_label.is_interesting:
            raise ValueError("Should be a skipped assignment")

        if not another_assignment.done or not another_assignment.article_label.is_interesting:
            raise ValueError("Should reassign wrt an annotated assignment")

        with transaction.atomic():
            annotated_label = another_assignment.article_label
            comments_to_reassign = [
                comment_label.comment
                for comment_label in annotated_label.comment_labels.all()
                if comment_label.is_hateful
            ]

            if len(comments_to_reassign) > 0:
                assignment.remove_label()
                assignment.skippable = False
                assignment.save(update_fields=["skippable"])
                assignment.comments.set(comments_to_reassign)
        return assignment.refresh_from_db()
