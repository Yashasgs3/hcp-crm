from app.config.database import Base, engine

from app.models import *


def create_tables():
    Base.metadata.create_all(bind=engine)
