from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    query = Column(String, nullable=False)
    response_status = Column(String, nullable=False)  # e.g., 'success', 'failure'
    variant = Column(String, nullable=True)
