import sys
from app.db.session import SessionLocal
from app.db.base import DetectionRecord, CleaningTask
try:
  db = SessionLocal()
  print('A: ', db.query(DetectionRecord).count())
except Exception as e:
  import traceback
  traceback.print_exc()
