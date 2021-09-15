import enum


class Docs(enum.Enum):
    """
    Help files
    TODO: replace with html files.
    """

    HELPDOC = 'docs/helpdoc.pdf'

    def __str__(self):
        return str(self.value)
