

class ChangeRequestException(Exception):
    """
    This class really to add more context to the
    404 error returned by the API. For certain
    actions like Commit Status CRUD operations
    a 404 error is returned if your token
    does not have correct scope of privileges.
    """
    def __init__(self, message=None, exc=None):

        if hasattr(exc, 'status'):
            if exc.status == 404:
                super().__init__("The PR/Commit doesn't exist or your token doesn't have proper permissions.")
