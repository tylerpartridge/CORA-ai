from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

class PredictionFeedback(Base):
    __tablename__ = "prediction_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_id = Column(String, nullable=False)
    action_taken = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, default=func.now(), nullable=False)
