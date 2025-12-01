from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import date, datetime

class Maintenance(SQLModel, table=True):
    __tablename__ = "maintenance"
    id: Optional[int] = Field(default=None, primary_key=True)
    equipment_id: int
    type: str # preventive, corrective
    description: Optional[str] = None
    cost: Optional[float] = None
    date: date
    technician: Optional[str] = None
    status: Optional[str] = Field(default="scheduled") # scheduled, completed, cancelled
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
