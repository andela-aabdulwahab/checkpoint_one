class Error(Exception):
    """Base class for all other exception."""

    pass


class RoomIsFullError(Error):
    """Raise when person is added to a room which is full."""

    pass


class PersonNotInRoomError(Error):
    """Raise when person not in room is accessed."""

    pass


class PersonNotFellowError(Error):
    """Raise when A Fellow Action is performed on Person Not a Fellow."""

    pass


class RoomGenderDiffError(Error):
    """Raise when room and person Gender don't match."""

    pass


class PersonInRoomError(Error):
    """Person already in Room."""

    pass


class NoRoomError(Error):
    """Raise when there is no available room ro assign to person."""

    pass


class PersonAllocatedError(Error):
    """Raise when person already allocated is allocated again."""

    pass


class SameNameRoomError(Error):
    """Raise when a room with name already in amity is added."""

    pass
