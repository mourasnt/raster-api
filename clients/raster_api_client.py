import requests
from typing import Dict, Any, Optional
from fastapi import HTTPException
from config import settings # Importa as configurações

# Não precisa mais receber login e senha como parâmetros
def get_rota(ibge_origem: str, ibge_destino: str) -> Optional[str]:
    """Faz a chamada para o endpoint 'getRotas' da API Raster."""
    url = f'{settings.RASTER_BASE_URL}/%22getRotas%22/'
    payload = {
        "Ambiente": settings.RASTER_AMBIENTE,
        "Login": settings.RASTER_LOGIN,
        "Senha": settings.RASTER_SENHA,
        "TipoRetorno": settings.RASTER_TIPO_RETORNO,
        "CodIBGECidadeOrigem": ibge_origem,
        "CodIBGECidadeDestino": ibge_destino,
        "DevolverKML": "N",
        "DetalharRota": "S",
        "CriarSeNaoExistir": "N"
    }

    try:
        response = requests.post(url, json=payload, timeout=240)
        response.raise_for_status()
        data = response.json()
        
        rotas = data.get("result", [{}])[0].get("Rotas")
        if rotas:
            codigo_rota = rotas[0].get("Codigo")
            if codigo_rota is not None:
                return str(codigo_rota)
        return None
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro de comunicação com o serviço de rotas: {e}")
    except (KeyError, IndexError, ValueError):
        raise HTTPException(status_code=500, detail="Resposta inesperada do serviço de rotas.")

def set_pre_sm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Faz a chamada para o endpoint 'setPreSM' da API Raster."""
    url = f'{settings.RASTER_BASE_URL}/%22setPreSM%22/'

    payload["PreSM"]["Codigo"] = 0
    
    # Monta o payload final aqui, adicionando as credenciais
    final_payload = {
        "Ambiente": settings.RASTER_AMBIENTE,
        "Login": settings.RASTER_LOGIN,
        "Senha": settings.RASTER_SENHA,
        "TipoRetorno": settings.RASTER_TIPO_RETORNO,
        "PreSM": payload["PreSM"] # Adiciona o corpo da PreSM recebido
    }
    
    try:
        response = requests.post(url, json=final_payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", [{}])[0]

        if "MsgErro" in result and result["MsgErro"]:
            raise HTTPException(status_code=400, detail=f"Erro retornado pela API da Raster: {result['MsgErro']}")
        
        return result
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro de comunicação com o serviço de criação de SM: {e}")
    
def efetivar_sm(preSM):
    """Faz a chamada para o endpoint 'efetivarSM' da API Raster."""
    url = f'{settings.RASTER_BASE_URL}/%22setEfetivaPreSM%22/'
    payload = {
        "Ambiente": settings.RASTER_AMBIENTE,
        "Login": settings.RASTER_LOGIN,
        "Senha": settings.RASTER_SENHA,
        "TipoRetorno": settings.RASTER_TIPO_RETORNO,
        "CodPreSolicitacao": preSM,
        "JaPassouRaioOrigem": "N"
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", [{}])[0]

        if "MsgErro" in result and result["MsgErro"]:
            raise HTTPException(status_code=400, detail=f"Erro retornado pela API da Raster: {result['MsgErro']}")
        
        return result
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro de comunicação com o serviço de efetivação de SM: {e}")