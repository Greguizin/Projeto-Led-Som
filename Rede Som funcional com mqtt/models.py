from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class LdrReading(Base):
    __tablename__ = 'ldr_readings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    red = Column(Float, nullable=False)
    green = Column(Float, nullable=False)
    blue = Column(Float, nullable=False)
   

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return f"<LdrReading(id={self.id}, red={self.red}, green={self.green}, blue={self.blue})>"
