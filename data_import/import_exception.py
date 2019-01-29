class ImportException(Exception):

    def __init__(self, message):
        super(ImportException, self).__init__(message)
