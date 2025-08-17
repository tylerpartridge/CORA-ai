import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import SessionLocal, AnalyticsLog
from sqlalchemy import desc

db = SessionLocal()
try:
    latest = db.query(AnalyticsLog).order_by(desc(AnalyticsLog.timestamp)).first()
    if latest:
        print(f"ID: {latest.id}, User: {latest.user_id}, Time: {latest.timestamp}, Query: {latest.query}, Status: {latest.response_status}")
    else:
        print("No logs found")
finally:
    db.close()
