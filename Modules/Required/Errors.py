class InsufficientParameterException(Exception):
    """Insufficient Parameters given for Command"""
    def init(self, command):
        self.command = command

    def __str__(self):
        return "Command %s called with insufficient Parameters" % command
