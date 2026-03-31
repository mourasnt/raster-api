from typing import List, Optional
from pydantic import BaseModel

# As classes Produto, Cliente, ColetaEntrega, etc., continuam as mesmas...
class Produto(BaseModel):
    CodProduto: str
    Produto: str
    Valor: float

class Cliente(BaseModel):
    Codigo: int
    Razao: str
    Fantasia: str
    CNPJ: str
    Endereco: str
    Numero: str
    Complemento: Optional[str] = ""
    Bairro: str
    CodIBGECidade: int
    Cidade: str
    Latitude: str
    Longitude: str

class ColetaEntrega(BaseModel):
    Tipo: str
    CodIBGECidade: int
    Cliente: Cliente
    DataHoraChegada: str
    DataHoraSaida: str
    Observacao: str
    Produtos: List[Produto]
    
class Detalhamento(BaseModel):
    ColetasEntregas: List[ColetaEntrega]

class Engate(BaseModel):
    CodFilial: str
    PlacaVeiculo: str
    VincVeiculo: str
    CodPerfilSeguranca: int
    CPFMotorista1: str
    VincMotorista1: str
    PlacaCarreta1: Optional[str] = None
    VincCarreta1: Optional[str] = None

class Rota(BaseModel):
    CodRota: Optional[int] = 0

class LiberacaoEngate(BaseModel):
    SolicitarPesquisa: str

class PreSMBody(BaseModel):
    Engate: Engate
    Detalhamento: Detalhamento
    Rota: Rota
    LiberacaoEngate: LiberacaoEngate

class PreSMRequest(BaseModel):
    """ Modelo principal que a API espera receber no corpo da requisição. """
    id: str
    PreSM: PreSMBody

class CodPreSMRequest(BaseModel):
    cod_pre_sm: str

class CancelarPreSMRequest(BaseModel):
    cod_pre_sm: str

class RefazerPreSMRequest(BaseModel):
    cod_pre_sm: str
    payload: PreSMRequest