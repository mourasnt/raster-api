from pydantic import BaseModel

class SMRequest(BaseModel):
    """ Modelo principal que a API espera receber no corpo da requisição. """
    id: str
    PreSM: int