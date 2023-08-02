from .extensions import db 

class Data(db.Model):
    db_id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)         # Timestamp of the data
    client_id = db.Column(db.Integer)     # ID of the client
    ambient_temp = db.Column(db.Float)    # Ambient temperature
    current = db.Column(db.Float)         # Current value
    internal_temp = db.Column(db.Float)   # Internal temperature
    humidity = db.Column(db.Float)        # Humidity value
    voltage = db.Column(db.Float)         # Voltage value

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75))  #name of candidate
    position = db.Column(db.String(150)) #admin, normal user
    password = db.Column(db.String(150))

class Plug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(75))  #name of candidate
    stateOfRelay = db.Column(db.String(150))
    
"""
# PostgreSQL database configuration for creating new tables
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://group3_backend_user:077oq8E0QGu2xpRT8jLA56NsRSViblhI@dpg-cj4li545kgrc739pljrg-a.oregon-postgres.render.com/group3_backend"  # Replace with your PostgreSQL credentials and database details
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Data(Base):
    __tablename__ = 'data'
    db_id = Column(Integer, primary_key=True)
    time = Column(DateTime)         # Timestamp of the data
    client_id = Column(Integer)     # ID of the client
    ambient_temp = Column(Float)    # Ambient temperature
    current = Column(Float)         # Current value
    internal_temp = Column(Float)   # Internal temperature
    humidity = Column(Float)        # Humidity value
    voltage = Column(Float)         # Voltage value

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(75))  #name of candidate
    position = Column(String(150)) #admin, normal user
    password = Column(String(150))

class Plug(Base):
    __tablename__ = 'plug'
    id = Column(Integer, primary_key=True)
    client_id = Column(String(75))  #name of candidate
    stateOfRelay = Column(String(150))

Base.metadata.create_all(engine)

"""
