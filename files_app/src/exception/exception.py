class BibliographyAlreadyExistsException(Exception):
    pass


class AuthorAlreadyExistsException(Exception):
    pass


class AuthorNotFoundByIdException(Exception):
    pass


class BibliographyNotFoundByIdException(Exception):
    pass


class FileAlreadyExistsException(Exception):
    pass


class FileNotFoundByIdException(Exception):
    pass


class EmptyFilenameException(Exception):
    pass


class AuthorNotFoundByNamesException(Exception):
    pass
