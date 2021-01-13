
class Completable:
    """
    Mixin for 'completable'
    """
    def complete(self):
        """
        Set as done
        """
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
