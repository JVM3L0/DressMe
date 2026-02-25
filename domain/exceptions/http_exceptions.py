class BaseException(Exception):
    """Base para erros de negócio"""


class InvalidCredentialsError(BaseException):
    """Falha nas credenciais informadas"""


class UserAlreadyExistsError(BaseException):
    """Usuário já existente"""
