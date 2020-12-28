
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

    def undo(self):
        """
        Undo!
        """
        if not self.done:
            # Raise if already completed
            raise ValueError("Assignment not done")
        self.done = False
        self.save()