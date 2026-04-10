from urllib import request

from fastapi import APIRouter, Request, status, HTTPException
from typing import Dict, Any, List
from arq.jobs import Job
from models.pre_sm_models import PreSMRequest, RefazerPreSMRequest, CancelarPreSMRequest
from models.viagem_models import StatusViagemRequest
from models.sm_model import EfetivarSMRequest, CancelarSMRequest, FinalizarSMRequest, RefazerSMRequest

router = APIRouter()

@router.post("/criar", status_code=status.HTTP_202_ACCEPTED)
async def criar_pre_sm_em_lote_endpoint(
    request_body: List[PreSMRequest],
    request: Request
) -> List[Dict[str, Any]]:
    arq_pool = request.app.state.arq_pool
    
    if not request_body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A lista de requisições não pode ser vazia.")

    jobs_criados = []
    for item in request_body:
        request_dict = item.dict()
        request_data_dict = {"PreSM": request_dict["PreSM"]}
        id_3zx = request_dict["id"]
        job = await arq_pool.enqueue_job('criar_pre_sm_task', request_data_dict)
        jobs_criados.append({"status": "accepted", "id": id_3zx ,"job_id": job.job_id, "type": "criar_pre_sm"})
    return jobs_criados

@router.post("/efetivar", status_code=status.HTTP_202_ACCEPTED)
async def efetivar_sm_endpoint(
    request_body: List[EfetivarSMRequest],
    request: Request
) -> List[Dict[str, Any]]:
    arq_pool = request.app.state.arq_pool
    
    if not request_body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O corpo da requisição não pode ser vazio.")
    
    jobs_criados = []
    for presm in request_body:
        if not presm or not presm.PreSM:
            continue
        
        job = await arq_pool.enqueue_job('efetivar_sm_task', presm.PreSM)
        jobs_criados.append({"status": "accepted", "job_id": job.job_id, "type": "efetivar_sm"})
    return jobs_criados

@router.post("/cancelar-pre-sm", status_code=status.HTTP_202_ACCEPTED)
async def cancelar_pre_sm_endpoint(
    request_body: CancelarPreSMRequest,
    request: Request
) -> Dict[str, Any]:
    arq_pool = request.app.state.arq_pool
    
    if not request_body.cod_pre_sm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O código da pré-solicitação é obrigatório.")
    
    job = await arq_pool.enqueue_job('cancelar_pre_sm_task', request_body.cod_pre_sm)
    return {"status": "accepted", "job_id": job.job_id, "type": "cancelar_pre_sm"}

@router.post("/cancelar-sm", status_code=status.HTTP_202_ACCEPTED)
async def cancelar_sm_endpoint(
    request_body: CancelarSMRequest,
    request: Request
) -> Dict[str, Any]:
    arq_pool = request.app.state.arq_pool
    
    if not request_body.cod_sm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O código da solicitação é obrigatório.")
    
    if not request_body.motivo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O motivo do cancelamento é obrigatório.")
    
    job_data = {"cod_sm": request_body.cod_sm, "motivo": request_body.motivo}
    job = await arq_pool.enqueue_job('cancelar_sm_task', job_data)
    return {"status": "accepted", "job_id": job.job_id, "type": "cancelar_sm"}

@router.post("/finalizar-sm", status_code=status.HTTP_202_ACCEPTED)
async def finalizar_sm_endpoint(
    request_body: FinalizarSMRequest,
    request: Request
) -> Dict[str, Any]:
    arq_pool = request.app.state.arq_pool
    
    if not request_body.cod_sm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O código da solicitação é obrigatório.")
    
    job = await arq_pool.enqueue_job('finalizar_sm_task', request_body.cod_sm)
    return {"status": "accepted", "job_id": job.job_id, "type": "finalizar_sm"}

@router.post("/refazer-pre-sm", status_code=status.HTTP_202_ACCEPTED)
async def refazer_pre_sm_endpoint(
    request_body: RefazerPreSMRequest,
    request: Request
) -> Dict[str, Any]:
    arq_pool = request.app.state.arq_pool
    
    if not request_body.cod_pre_sm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O código da pré-solicitação é obrigatório.")
    
    if not request_body.payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O payload para refazer a pré-solicitação é obrigatório.")
    
    request_dict = request_body.payload.dict()
    request_data_dict = {"PreSM": request_dict["PreSM"]}
    id_3zx = request_dict["id"]  
    job = await arq_pool.enqueue_job('refazer_pre_sm_task', request_body.cod_pre_sm, request_data_dict)
    
    return {"status": "accepted", "id": id_3zx ,"job_id": job.job_id, "type": "criar_pre_sm"}

@router.post("/refazer-sm", status_code=status.HTTP_202_ACCEPTED)
async def refazer_sm(
    request_body: RefazerSMRequest,
    request: Request
) -> Dict[str, Any]:
    arq_pool = request.app.state.arq_pool
    
    if not request_body.cod_sm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O código da solicitação é obrigatório.")
    
    if not request_body.payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O payload para refazer a solicitação é obrigatório.")
    
    job_data = {"cod_sm": request_body.cod_sm, "payload": request_body.payload}
    job = await arq_pool.enqueue_job('refazer_sm_task', job_data)
    return {"status": "accepted", "job_id": job.job_id, "type": "refazer_sm"}

@router.post("/statusViagem", status_code=status.HTTP_202_ACCEPTED)
async def status_viagem_endpoint(
    request_body: StatusViagemRequest,
    request: Request
) -> Dict[str, Any]:
    arq_pool = request.app.state.arq_pool

    if not request_body.cod_presm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O código da pré-solicitação é obrigatório.")

    job = await arq_pool.enqueue_job('status_viagem_task', request_body.cod_presm)
    return {"status": "accepted", "job_id": job.job_id, "type": "status_viagem"}

@router.get("/status/{job_id}", response_model=Dict[str, Any])
async def get_job_status(job_id: str, request: Request) -> Dict[str, Any]:
    """
    Verifica o status de uma tarefa enfileirada a partir do seu job_id.
    """
    arq_pool = request.app.state.arq_pool
    
    job_result_key = f"arq:result:{job_id}"

    if not await arq_pool.exists(job_result_key):
        job_definition_key = f"arq:job:{job_id}"
        if not await arq_pool.exists(job_definition_key):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Job with ID '{job_id}' not found or has expired.")
        else:
             return {
                "job_id": job_id,
                "status": "in_progress",
            }

    job = Job(job_id, arq_pool)
    status_job = await job.status()
    response = {
        "job_id": job_id,
        "status": status_job,
    }

    result = await job.result()
    if status_job == 'complete':
        response['result'] = result
    else:
        response['error_details'] = result

    return response