from app.person import Person


class Fellow(Person):

    """ Hold the information of a fellow
    Acts as an object for Fellow. Inherit from Person

    Methods:
        want_accomodation - return the true/false base on fellow choice

    """

    def __init__(self, name, gender, want_accom="N"):
        super().__init__(name, gender)
        self.want_accom = want_accom

    def wants_accomodation(self):
        """ return value base on the value of want_accom"""
        if self.want_accom == "Y":
            return True
        else:
            return False
