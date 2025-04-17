# Plus tard, on pourra implémenter un OAuth2 ou un apikey-check
from fastapi import Request, HTTPException

def check_api_key(request: Request):
    # Ex: lire l'entête X-API-KEY ?
    # if request.headers.get("X-API-KEY") != "secretkey":
    #     raise HTTPException(status_code=401, detail="Invalid API key")
    pass
