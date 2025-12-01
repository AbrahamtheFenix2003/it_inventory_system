from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import date, datetime

class Equipment(SQLModel, table=True):
    __tablename__ = "equipment"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    serial_number: str = Field(unique=True)
    type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    purchase_date: Optional[date] = None
    status: Optional[str] = Field(default="available")
    location: Optional[str] = None
    provider_id: Optional[int] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class EquipmentHistory(SQLModel, table=True):
    __tablename__ = "equipment_history"
    id: Optional[int] = Field(default=None, primary_key=True)
    equipment_id: int
    previous_location: Optional[str] = None
    new_location: Optional[str] = None
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    changed_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
