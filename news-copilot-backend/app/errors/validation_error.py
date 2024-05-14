class ValidationError(Exception):
    def __init__(self, field, message, code):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")
