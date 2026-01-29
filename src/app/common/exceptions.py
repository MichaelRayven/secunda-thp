class ModelNotFoundError(Exception):
    """Exception raised for missing data."""

    def __init__(self, message: str = 'Not found') -> None:
        self.message = message
        super().__init__(f'{self.message}')
