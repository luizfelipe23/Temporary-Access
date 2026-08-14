from fastapi import FastAPI

app = FastAPI(
    title="Temporary Access API",
    version="0.1.0",
)

# só verifica se a aplicação está rodando
@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "service": "temporary-access-api",
    }