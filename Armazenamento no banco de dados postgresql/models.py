from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float

Base = declarative_base()

class LdrReading(Base):
    __tablename__ = 'ldr_readings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    red = Column(Float, nullable=False)
    green = Column(Float, nullable=False)
    blue = Column(Float, nullable=False)
