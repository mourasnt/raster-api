import logging # Adicione esta importação
from fastapi import FastAPI
from arq import create_pool
from routers import sm_router
from worker import WorkerSettings
import uvicorn

# O resto do arquivo...
app = FastAPI(
    title="API de Integração Raster",
    description="Orquestra chamadas para a API da Raster de forma assíncrona.",
    version="3.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Cria o pool de conexões do ARQ ao iniciar a API."""
    logging.info("Tentando conectar ao Redis para criar o pool do ARQ...")
    try:
        arq_pool = await create_pool(WorkerSettings.redis_settings)
        app.state.arq_pool = arq_pool
        logging.info("✅ Conexão com o Redis estabelecida e pool do ARQ criado com sucesso!")
    except Exception as e:
        # Se falhar, o log vai te dizer exatamente o porquê!
        logging.error(f"❌ Falha ao conectar com o Redis e criar o pool do ARQ: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Fecha o pool de conexões do ARQ ao desligar a API."""
    if hasattr(app.state, 'arq_pool'):
        await app.state.arq_pool.close()
        logging.info("Pool de conexões do ARQ fechado.")

app.include_router(sm_router.router, prefix="/sm", tags=["SM"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API de Integração Raster no ar!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)