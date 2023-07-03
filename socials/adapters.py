class PostAdapter:
    def authenticate(self, *args, **kwargs):
        raise NotImplementedError('Subclasses must implement this method')

    def post(self, message, **kwargs):
        raise NotImplementedError('Subclasses must implement this method')
