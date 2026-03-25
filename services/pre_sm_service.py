from typing import Dict, Any, Tuple, Optional

def _extrair_ibge_origem_destino(detalhamento: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Função auxiliar para extrair códigos IBGE."""
    coletas_entregas = detalhamento.get("ColetasEntregas", [])
    ibge_origem = next((str(item.get("CodIBGECidade")) for item in coletas_entregas if item.get("Tipo") == "COLETA"), None)
    ibge_destino = next((str(item.get("CodIBGECidade")) for item in reversed(coletas_entregas) if item.get("Tipo") == "ENTREGA"), None)
    return ibge_origem, ibge_destino