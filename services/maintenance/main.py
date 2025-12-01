from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Maintenance

app = FastAPI()

@app.get("/maintenance", response_model=List[Maintenance])
def read_maintenance(session: Session = Depends(get_session)):
    maintenance = session.exec(select(Maintenance)).all()
    return maintenance

@app.post("/maintenance", response_model=Maintenance)
def create_maintenance(maintenance: Maintenance, session: Session = Depends(get_session)):
    session.add(maintenance)
    session.commit()
    session.refresh(maintenance)
    return maintenance

@app.get("/maintenance/equipment/{equipment_id}", response_model=List[Maintenance])
def read_maintenance_by_equipment(equipment_id: int, session: Session = Depends(get_session)):
    maintenance = session.exec(select(Maintenance).where(Maintenance.equipment_id == equipment_id)).all()
    return maintenance

@app.put("/maintenance/{maintenance_id}", response_model=Maintenance)
def update_maintenance(maintenance_id: int, maintenance_data: Maintenance, session: Session = Depends(get_session)):
    maintenance = session.get(Maintenance, maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance not found")
    
    maintenance_data_dict = maintenance_data.dict(exclude_unset=True)
    for key, value in maintenance_data_dict.items():
        if key not in ["id", "created_at"]:
            setattr(maintenance, key, value)
            
    session.add(maintenance)
    session.commit()
    session.refresh(maintenance)
    return maintenance
