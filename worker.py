import logging
from fastapi import HTTPException
from services import pre_sm_service
from clients import raster_api_client
from arq.connections import RedisSettings
from config import settings

async def criar_pre_sm_task(ctx, request_data: dict):
    """
    Tarefa assíncrona que executa o fluxo de criação da Pré-SM.
    'ctx' é o dicionário de contexto do worker, 'request_data' são os dados da API.
    """
    job_id = ctx.get('job_id', 'unknown_job')
    logging.info(f"Worker (job_id: {job_id}): Iniciando processamento da Pré-SM com os dados recebidos.")
    
    if not isinstance(request_data, dict):
        error_msg = f"Erro crítico: O dado recebido pelo worker não é um dicionário. Valor recebido: {request_data}"
        logging.error(f"Worker (job_id: {job_id}): {error_msg}")
        return {"sucesso": False, "erro": error_msg}

    try:
        # --- A lógica de negócio principal fica dentro do bloco try ---
        codigo_rota_fornecido = request_data.get("PreSM", {}).get("Rota", {}).get("CodRota")

        if not codigo_rota_fornecido or codigo_rota_fornecido == 0:
            logging.info(f"Worker (job_id: {job_id}): Buscando rota por IBGE.")
            detalhamento = request_data["PreSM"]["Detalhamento"]
            ibge_origem, ibge_destino = pre_sm_service._extrair_ibge_origem_destino(detalhamento)
            
            if not ibge_origem or not ibge_destino:
                raise ValueError("Não foi possível extrair IBGEs de origem/destino.")

            codigo_rota_buscado = raster_api_client.get_rota(ibge_origem, ibge_destino)
            if not codigo_rota_buscado:
                raise ValueError(f"Rota não encontrada para {ibge_origem}->{ibge_destino}.")
            
            request_data["PreSM"]["Rota"]["CodRota"] = int(codigo_rota_buscado)
        else:
            logging.info(f"Worker (job_id: {job_id}): Usando rota fornecida: {codigo_rota_fornecido}.")
        
        resultado = raster_api_client.set_pre_sm(request_data)
        logging.info(f"Worker (job_id: {job_id}): Pré-SM criada com sucesso! Resultado: {resultado}")
        
        # Retorna um dicionário simples em caso de sucesso
        return {"sucesso": True, "resultado": resultado}

    # --- Bloco de captura de exceções ---
    except HTTPException as e:
        logging.error(f"Worker (job_id: {job_id}): Erro de negócio da API Raster: {e.detail}")
        return {"sucesso": False, "erro": e.detail}
    except Exception as e:
        logging.error(f"Worker (job_id: {job_id}): Ocorreu um erro inesperado: {e}", exc_info=True)
        return {"sucesso": False, "erro": f"Erro inesperado no worker: {str(e)}"}
    
async def efetivar_sm_task(ctx, presm: dict):
    """
    Tarefa assíncrona que executa o fluxo de efetivação da SM.
    'ctx' é o dicionário de contexto do worker, 'presm' são os dados da Pré-SM a serem efetivados.
    """
    job_id = ctx.get('job_id', 'unknown_job')
    logging.info(f"Worker (job_id: {job_id}): Iniciando efetivação da SM com os dados recebidos.")
    
    try:
        resultado = raster_api_client.efetivar_sm(presm)
        logging.info(f"Worker (job_id: {job_id}): SM efetivada com sucesso! Resultado: {resultado}")
        return {"sucesso": True, "resultado": resultado}
    except HTTPException as e:
        logging.error(f"Worker (job_id: {job_id}): Erro de negócio da API Raster durante efetivação: {e.detail}")
        return {"sucesso": False, "erro": e.detail}
    except Exception as e:
        logging.error(f"Worker (job_id: {job_id}): Ocorreu um erro inesperado durante efetivação: {e}", exc_info=True)
        return {"sucesso": False, "erro": f"Erro inesperado no worker durante efetivação: {str(e)}"}
    
async def cancelar_pre_sm_task(ctx, cod_pre_solicitacao: str):
    job_id = ctx.get('job_id', 'unknown_job')
    logging.info(f"Worker (job_id: {job_id}): Iniciando cancelamento da Pré-SM com código: {cod_pre_solicitacao}")
    
    try:
        resultado = raster_api_client.cancelar_pre_sm(cod_pre_solicitacao)
        logging.info(f"Worker (job_id: {job_id}): Pré-SM cancelada com sucesso! Resultado: {resultado}")
        return {"sucesso": True, "resultado": resultado}
    except HTTPException as e:
        logging.error(f"Worker (job_id: {job_id}): Erro de negócio da API Raster durante cancelamento de Pré-SM: {e.detail}")
        return {"sucesso": False, "erro": e.detail}
    except Exception as e:
        logging.error(f"Worker (job_id: {job_id}): Ocorreu um erro inesperado durante cancelamento de Pré-SM: {e}", exc_info=True)
        return {"sucesso": False, "erro": f"Erro inesperado no worker durante cancelamento de Pré-SM: {str(e)}"}
    
async def cancelar_sm_task(ctx, cod_solicitacao: str):
    job_id = ctx.get('job_id', 'unknown_job')
    logging.info(f"Worker (job_id: {job_id}): Iniciando cancelamento da SM com código: {cod_solicitacao}")
    
    try:
        resultado = raster_api_client.cancelar_sm(cod_solicitacao)
        logging.info(f"Worker (job_id: {job_id}): SM cancelada com sucesso! Resultado: {resultado}")
        return {"sucesso": True, "resultado": resultado}
    except HTTPException as e:
        logging.error(f"Worker (job_id: {job_id}): Erro de negócio da API Raster durante cancelamento de SM: {e.detail}")
        return {"sucesso": False, "erro": e.detail}
    except Exception as e:
        logging.error(f"Worker (job_id: {job_id}): Ocorreu um erro inesperado durante cancelamento de SM: {e}", exc_info=True)
        return {"sucesso": False, "erro": f"Erro inesperado no worker durante cancelamento de SM: {str(e)}"}
    
async def finalizar_sm_task(ctx, cod_solicitacao: str):
    job_id = ctx.get('job_id', 'unknown_job')
    logging.info(f"Worker (job_id: {job_id}): Iniciando finalização da SM com código: {cod_solicitacao}")
    
    try:
        resultado = raster_api_client.finalizar_sm(cod_solicitacao)
        logging.info(f"Worker (job_id: {job_id}): SM finalizada com sucesso! Resultado: {resultado}")
        return {"sucesso": True, "resultado": resultado}
    except HTTPException as e:
        logging.error(f"Worker (job_id: {job_id}): Erro de negócio da API Raster durante finalização de SM: {e.detail}")
        return {"sucesso": False, "erro": e.detail}
    except Exception as e:
        logging.error(f"Worker (job_id: {job_id}): Ocorreu um erro inesperado durante finalização de SM: {e}", exc_info=True)
        return {"sucesso": False, "erro": f"Erro inesperado no worker durante finalização de SM: {str(e)}"}
    
async def refazer_pre_sm_task(ctx, cod_pre_solicitacao: str, payload: dict):
    job_id = ctx.get('job_id', 'unknown_job')
    logging.info(f"Worker (job_id: {job_id}): Iniciando refação da Pré-SM com código: {cod_pre_solicitacao}")
    
    try:
        resultado = raster_api_client.refazer_pre_sm(cod_pre_solicitacao, payload)
        logging.info(f"Worker (job_id: {job_id}): Pré-SM refeita com sucesso! Resultado: {resultado}")
        return {"sucesso": True, "resultado": resultado}
    except HTTPException as e:
        logging.error(f"Worker (job_id: {job_id}): Erro de negócio da API Raster durante refação de Pré-SM: {e.detail}")
        return {"sucesso": False, "erro": e.detail}
    except Exception as e:
        logging.error(f"Worker (job_id: {job_id}): Ocorreu um erro inesperado durante refação de Pré-SM: {e}", exc_info=True)
        return {"sucesso": False, "erro": f"Erro inesperado no worker durante refação de Pré-SM: {str(e)}"}

async def refazer_sm_task(ctx, cod_solicitacao: str, payload: dict):
    job_id = ctx.get('job_id', 'unknown_job')
    logging.info(f"Worker (job_id: {job_id}): Iniciando refação da SM com código: {cod_solicitacao}")
    
    try:
        resultado = raster_api_client.refazer_sm(cod_solicitacao, payload)
        logging.info(f"Worker (job_id: {job_id}): SM refeita com sucesso! Resultado: {resultado}")
        return {"sucesso": True, "resultado": resultado}
    except HTTPException as e:
        logging.error(f"Worker (job_id: {job_id}): Erro de negócio da API Raster durante refação de SM: {e.detail}")
        return {"sucesso": False, "erro": e.detail}
    except Exception as e:
        logging.error(f"Worker (job_id: {job_id}): Ocorreu um erro inesperado durante refação de SM: {e}", exc_info=True)
        return {"sucesso": False, "erro": f"Erro inesperado no worker durante refação de SM: {str(e)}"}


class WorkerSettings:
    functions = [criar_pre_sm_task, efetivar_sm_task, cancelar_pre_sm_task, cancelar_sm_task, finalizar_sm_task, refazer_pre_sm_task, refazer_sm_task]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=6379, database=0)

    # 3 tentativas significa que ele executará no total até 4 vezes (1 original + 3 retries).
    job_retry = 3
    job_retry_delay = 60 # Espera 1 minuto antes da próxima tentativa

