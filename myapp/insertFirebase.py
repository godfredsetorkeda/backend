import firebase_admin
import os
from firebase_admin import credentials, db
import random
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .extensions import dbA
from .models import User, Data, Plug

# Initialize Firebase Admin SDK
FIREBASE_PATH = os.environ("FIREBASE_PATH")
cred = credentials.Certificate(FIREBASE_PATH)
firebase_admin.initialize_app(cred, {"databaseURL": "https://gsk-smartplug-default-rtdb.firebaseio.com"})

# Set up PostgreSQL connection
DATABASE_URL = os.environ("DATABASE_URL")
#"postgresql://group3_backend_user:077oq8E0QGu2xpRT8jLA56NsRSViblhI@dpg-cj4li545kgrc739pljrg-a.oregon-postgres.render.com/group3_backend"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def insert_records():
    # Delete all records from the Data table
    Data.query.delete()
    session.commit()

    # Poll Data from Firebase
    root_ref = db.reference("/")
    readings_data = root_ref.child("readings").get()

    # Process and insert data into PostgreSQL
    for reading_id, reading_data in readings_data.items():
        # Extract relevant data from reading_data
        current = float(reading_data.get("current", 0))

        if reading_data.get("humidity") == 'NUL':
            humidity = float(0)
        else:
            humidity = float(reading_data.get("humidity", 0))
        
        voltage = float(reading_data.get("voltage", 0))
        timestamp = reading_data.get("timestamp", "")

        # Generate a random ambient temperature between 25 and 32
        ambient_temp = random.uniform(25, 32)

        # Convert the timestamp to a datetime object
        time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        client_id = 1

        if reading_data.get("temperature") == 'NUL':
            internal_temp = float(0)
        else:
            internal_temp = float(reading_data.get("humidity", 0))

        # Create a Data object and insert it into PostgreSQL
        data_entry = Data(
            client_id=client_id,
            current=current,
            humidity=humidity,
            internal_temp=internal_temp,
            voltage=voltage,
            time=timestamp,
            ambient_temp=ambient_temp
        )
        session.add(data_entry)

    # Commit the changes and close the session
    session.commit()
    session.close()
