from fastapi import FastAPI
from app.routers import pricing, dispatch


# Routers (endpoints)
from .routers import pricing, dispatch

app = FastAPI(
    title="Module IA - Crowdshipping",
    description="Tarification dynamique et dispatching intelligent pour crowdshipping",
    version="1.0.0"
)

# Inclure les routers
app.include_router(pricing.router, prefix="/pricing", tags=["pricing"])
app.include_router(dispatch.router, prefix="/dispatch", tags=["dispatch"])

@app.get("/")
def root():
    return {"message": "Bienvenue dans le Module IA de Crowdshipping !"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
