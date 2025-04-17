from fastapi import FastAPI
from .routers import delivery, dispatch, pricing
from .database import engine
from .models.db_models import Base

# Crée les tables si pas existantes
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IASERVICE Crowdshipping",
    description="Microservice IA pour la tarification et le dispatch.",
    version="1.0.0"
)

# Inclusion des routes
app.include_router(delivery.router, prefix="/delivery", tags=["Delivery"])
app.include_router(dispatch.router, prefix="/dispatch", tags=["Dispatch"])
app.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])

@app.get("/")
def read_root():
    return {"message": "IASERVICE is running. Check /docs."}
