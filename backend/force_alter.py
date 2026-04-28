
import sys
from app.db.session import SessionLocal
from sqlalchemy import text
import traceback

try:
    db = SessionLocal()
    db.execute(text('ALTER TABLE detection_records MODIFY COLUMN latitude DECIMAL(10,7) NULL'))
    db.execute(text('ALTER TABLE detection_records MODIFY COLUMN longitude DECIMAL(10,7) NULL'))
    db.execute(text('ALTER TABLE cleaning_tasks MODIFY record_id INTEGER UNSIGNED NULL'))
    db.commit()
    print('DB Altered Success')
except Exception as e:
    print('DB Alter Failed!')
    traceback.print_exc()

