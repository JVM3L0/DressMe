from enum import StrEnum


class GarmentCategory(StrEnum):
    """Categoria da peça pela região do corpo, que define a camada e a posição
    inicial no provador. Os rótulos em português ficam no frontend."""

    TOP = "top"  # parte de cima: camiseta, camisa, blusa, suéter
    OUTERWEAR = "outerwear"  # agasalho: jaqueta, casaco, blazer, cardigã
    BOTTOM = "bottom"  # parte de baixo: calça, short, saia
    ONE_PIECE = "one_piece"  # peça única: vestido, macacão
    FOOTWEAR = "footwear"  # calçado
    ACCESSORY = "accessory"  # bolsa, boné, óculos, cinto
