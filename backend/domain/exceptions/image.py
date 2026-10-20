class ImageTooLargeError(Exception):
    """A imagem passa do limite de tamanho"""


class InvalidImageError(Exception):
    """O arquivo não é uma imagem aceita (JPEG ou PNG) ou está corrompido"""
