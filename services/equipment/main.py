from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Equipment, EquipmentHistory

app = FastAPI()

@app.get("/equipment", response_model=List[Equipment])
def read_equipment(session: Session = Depends(get_session)):
    equipment = session.exec(select(Equipment)).all()
    return equipment

@app.post("/equipment", response_model=Equipment)
def create_equipment(equipment: Equipment, session: Session = Depends(get_session)):
    session.add(equipment)
    session.commit()
    session.refresh(equipment)
    return equipment

@app.get("/equipment/{equipment_id}", response_model=Equipment)
def read_single_equipment(equipment_id: int, session: Session = Depends(get_session)):
    equipment = session.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@app.put("/equipment/{equipment_id}", response_model=Equipment)
def update_equipment(equipment_id: int, equipment_data: Equipment, session: Session = Depends(get_session)):
    equipment = session.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Track changes
    prev_location = equipment.location
    prev_status = equipment.status
    
    equipment_data_dict = equipment_data.dict(exclude_unset=True)
    for key, value in equipment_data_dict.items():
        if key not in ["id", "created_at"]:
            setattr(equipment, key, value)
            
    # If location or status changed, add history
    if equipment.location != prev_location or equipment.status != prev_status:
        history = EquipmentHistory(
            equipment_id=equipment.id,
            previous_location=prev_location,
            new_location=equipment.location,
            previous_status=prev_status,
            new_status=equipment.status
        )
        session.add(history)
        
    session.add(equipment)
    session.commit()
    session.refresh(equipment)
    return equipment

@app.get("/equipment/{equipment_id}/history", response_model=List[EquipmentHistory])
def read_equipment_history(equipment_id: int, session: Session = Depends(get_session)):
    history = session.exec(select(EquipmentHistory).where(EquipmentHistory.equipment_id == equipment_id).order_by(EquipmentHistory.changed_at.desc())).all()
    return history
