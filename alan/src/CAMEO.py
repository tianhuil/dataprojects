class CAMEOCode():
    """A class for defining a CAMEOCode"""
    def __init__(self, code='', group='', description=''):
        """intializes the code, group, and description"""
        self.code = code
        self.group=group
        self.description=description
        return
    
    def __eq__(self, other):
        """define equality to be on the CAMEOCode"""
        if isinstance(other, self.__class__):
            return self.code == other.code
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    
