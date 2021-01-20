from django.db import transaction

class Completable:
    """
    Mixin for 'completable'
    """
    def complete(self):
        """
        Set as done
        """
        with transaction.atomic():
            if self.done:
                # Raise if already completed
                raise ValueError("Assignment already completed")
            self.done = True
            self.save()

            self.after_complete()

    def undo(self):
        """
        Undo!
        """
        with transaction.atomic():
            if not self.done:
                # Raise if already completed
                raise ValueError("Assignment not done")
            self.done = False
            self.save()

            self.after_undo()

    def after_complete(self):
        """
        Abstract method. Override!
        """
        pass


    def after_undo(self):
        """
        Abstract method, override!
        """
        pass
