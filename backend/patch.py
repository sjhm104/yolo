from pathlib import Path
path = Path(r'D:\pyyolo\backend\app\api\v1\endpoints\detection.py')
text = path.read_text('utf-8')

old_snippet = '''record = DetectionRecord(
image_url=f"/{output_video_relpath}",
has_waste=has_waste,
latitude=None,
longitude=None,
)
db.add(record)
db.commit()
db.refresh(record)

if has_waste:
task = CleaningTask(
record_id=record.id,
status=CleaningTaskStatus.PENDING
)
db.add(task)
db.commit()

return VideoDetectionResponse('''

new_snippet = '''try:
record = DetectionRecord(
image_url=f"/{output_video_relpath}",
has_waste=has_waste,
latitude=None,
longitude=None,
)
db.add(record)
db.commit()
db.refresh(record)

if has_waste:
task = CleaningTask(
record_id=record.id,
status=CleaningTaskStatus.PENDING
)
db.add(task)
db.commit()
except Exception as e:
db.rollback()
print("DB Insert Error:", e)

return VideoDetectionResponse('''

text = text.replace(old_snippet, new_snippet)
path.write_text(text, 'utf-8')
print('Script patched')
