import enum


class Docs(enum.Enum):

    HELPDOC = 'docs/helpdoc.pdf'

    def __str__(self):
        return str(self.value)

