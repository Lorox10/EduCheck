import sys
sys.path.insert(0, '/d:\\LORENZO\\Escritorio\\Edu Check\\Backend')

from db import get_session
from sqlalchemy import update
from models import Student

with get_session() as session:
    session.execute(update(Student).values(telegram_id='5936924064'))
    session.commit()
    print("Actualizado!")
