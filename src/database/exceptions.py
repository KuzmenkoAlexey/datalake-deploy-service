class DBManagerException(Exception):
    pass


class ObjectAlreadyExists(DBManagerException):
    pass


class ObjectDoesntExist(DBManagerException):
    pass
