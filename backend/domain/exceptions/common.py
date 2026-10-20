class ResourceNotFoundError(Exception):
    """O recurso não existe ou pertence a outro usuário. Os dois casos são
    tratados igual, para não revelar o que existe na conta de outra pessoa."""
