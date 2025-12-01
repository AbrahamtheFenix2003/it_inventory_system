from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Provider

app = FastAPI()

@app.get("/providers", response_model=List[Provider])
def read_providers(session: Session = Depends(get_session)):
    providers = session.exec(select(Provider)).all()
    return providers

@app.post("/providers", response_model=Provider)
def create_provider(provider: Provider, session: Session = Depends(get_session)):
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider

@app.get("/providers/{provider_id}", response_model=Provider)
def read_provider(provider_id: int, session: Session = Depends(get_session)):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@app.put("/providers/{provider_id}", response_model=Provider)
def update_provider(provider_id: int, provider_data: Provider, session: Session = Depends(get_session)):
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Exclude id and created_at from update if present, or handle carefully
    provider_data_dict = provider_data.dict(exclude_unset=True)
    for key, value in provider_data_dict.items():
        if key not in ["id", "created_at"]:
            setattr(provider, key, value)
            
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider
