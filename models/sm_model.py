from pydantic import BaseModel

class EfetivarSMRequest(BaseModel):
    """ Modelo principal que a API espera receber no corpo da requisição. """
    id: str
    PreSM: int

class CancelarSMRequest(BaseModel):
    cod_sm: str
    motivo: str

class FinalizarSMRequest(BaseModel):
    cod_sm: str

class RefazerSMRequest(BaseModel):
    cod_sm: str
    payload: dict