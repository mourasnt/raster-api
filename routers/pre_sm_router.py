from fastapi import APIRouter, Request, status, HTTPException
from typing import Dict, Any, List
from arq.jobs import Job
from models.pre_sm_models import PreSMRequest
from models.sm_model import SMRequest

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
        print(  "Request Dict:", request_dict)  # Log para depuração
        request_data_dict = {"PreSM": request_dict["PreSM"]}
        id_3zx = request_dict["id"]
        job = await arq_pool.enqueue_job('criar_pre_sm_task', request_data_dict)
        jobs_criados.append({"status": "accepted", "id": id_3zx ,"job_id": job.job_id, "type": "criar_pre_sm"})
    return jobs_criados

@router.post("/efetivar", status_code=status.HTTP_202_ACCEPTED)
async def efetivar_sm_endpoint(
    request_body: List[SMRequest],
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