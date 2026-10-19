from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(examples=["joao@example.com"])]
    # Sem as regras do cadastro: elas só valem para senhas novas. O limite
    # evita corpos enormes; senhas acima de 72 bytes nunca conferem.
    password: Annotated[str, Field(min_length=1, max_length=1024)]
