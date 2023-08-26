from .extensions import dbA 

class Data(dbA.Model):
    db_id = dbA.Column(dbA.Integer, primary_key=True)
    time = dbA.Column(dbA.DateTime)         # Timestamp of the data
    client_id = dbA.Column(dbA.Integer)     # ID of the client
    ambient_temp = dbA.Column(dbA.Float)    # Ambient temperature
    current = dbA.Column(dbA.Float)         # Current value
    internal_temp = dbA.Column(dbA.Float)   # Internal temperature
    humidity = dbA.Column(dbA.Float)        # Humidity value
    voltage = dbA.Column(dbA.Float)         # Voltage value

class User(dbA.Model):
    id = dbA.Column(dbA.Integer, primary_key=True)
    name = dbA.Column(dbA.String(75))  #name of candidate
    position = dbA.Column(dbA.String(150)) #admin, normal user
    password = dbA.Column(dbA.String(150))

class Plug(dbA.Model):
    id = dbA.Column(dbA.Integer, primary_key=True)
    client_id = dbA.Column(dbA.String(75))  #name of candidate
    stateOfRelay = dbA.Column(dbA.String(150))
    
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
