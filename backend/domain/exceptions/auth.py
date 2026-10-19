class InvalidCredentialsError(Exception):
    """E-mail ou senha incorretos (sem dizer qual, para não revelar contas)"""


class NotAuthenticatedError(Exception):
    """Sem sessão, ou com token inválido, expirado ou de usuário removido"""
