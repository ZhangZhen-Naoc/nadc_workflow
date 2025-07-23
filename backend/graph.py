from app.models import *
from wsgi import app

with app.app_context():
    entity: Entity = Entity.query.get(8)
    print(entity.generated_by)
