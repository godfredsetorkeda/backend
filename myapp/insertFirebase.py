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

cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "gsk-smartplug",
  "private_key_id": "cd6ccffd6647b65e9b754c824e1c19e6873c1adf",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCsww1FnBusdI6r\njb5QjRiD/X7HCEn5B/uAX+wQwdo6Ux0TH3qoJDMTGGApB0V37E0cAhaDf4K0xnOS\nVHjJnObAhpFY/Hiuxho+/Hl8+AObfHh55gjom9OPRcMHs22LjnBYK1Uy8ULWsuWS\n7fXWsvXWTN62c9RUZmWIhBwAsn/O3aJ5xxr1ghzLdIssMGtiLbjSnzB3MM/BoU++\nifnNkraDXuR4+Za+/F2IZLwHE5BhAr5K4Jg02xRE8aKKPKYFKtKSZr1y9f4J3+99\nM/450VOMzEa3wm1mJlPx+dBJXs9ykRd1dkJxRy2k30WlPZVO+Qcg5MSF/tLAP40D\nRVp3kRVbAgMBAAECggEAQs7U8Y/KVdjnGSlhqOW/Tr93SMGIVaDEHeM6N0q3uOlO\nK4h3VtFU3PQGr6cLsrHzKbsW+LgVFBJQPAylfxXJWDdRus87Xh7mpGffFTgVsQmj\nz0PpOwaTe+q23mIBIUAuarIrKt2Igt1AkR6rfGDNV5d3YqgNOqw0ZGPuLkjYyuZg\n2M0WJ3Sx/9EPA62RoKqJweI6HdDyEcYF/j3FOcdr1kyMLe1bwIQ4qh6IjurTljnC\nMBPupdyu4kU3aFIa5pamprhJPfXYwFN3AuK80y5EkKUzMInY9881G2at9X1vjZVq\n6g03q56aadAKqvjsk7KnJ6Nvrx2j3aT8X6QnQ0sZPQKBgQDSrRgvbQN5aaoqtMWp\nUY6/AKJIaAELXkqpdgXORyp6bk1OytKWaDzonhxEFQioYrz/B47r36locI1kTLlM\nFJ0oK8pXi3fvQMIk5cEeljSUmSCOtK1BgvkjXoLBD78QmR/Ri5UBaOJiPq304JkV\nK+mr9J/lKgPX89cXRA9e0RoYrQKBgQDR7diiKaF1IOEsAi0u3Nh3uPemF8rNOXFZ\nchxDprl49ca8JVyEBkgrcMnty/o0LlxeoaNLMQiNP6ui/UeFBkAQ0sZ65vYRbi2U\nyfzUJ6TuMjHQY48ZF6+WTJZIojPwnis7OMYpDJKnWAGFllPd/G4+S7Fm1MW9zz4w\n9iGA92//JwKBgFWZRu5eGL9IE3/umzFElf89PrK0r1fzI9revVUmzTeZgYe2GQJL\nsBPDyjBPa4kfNTNZ2tQzuB1bPde25MLozUH5KOmRHVX0te1P/Lt0xEBsRzI0bwDj\nOl8Ik4/l2ffgf3EgiZZdCz5nwT5x00Eq6nKXni/6dj1UMdyeJrCbvUKxAoGAWMOo\nKRFPStZnP5OABWOuSBk25c0DnHkge4CrgNN7czEBIkbt8okxdOTRDTKFjhDYT88q\n271U71yvt1A/MHkvF6337LnB7CbZMSOjOxW0QF+K/qFKPYLtZLDnjri/G4vVncno\nyCyfyhCFPDYPKjr1ZnPdBC0Nm6+IjW1VR1HY0lsCgYA+6XDFkBBn38cUdxcixhrz\nhTK6DjY3IhudDmhYf6k1e+R9FyaaVLck9L+bOk4gYDcVPAoFQ5l3XDlqOKmlz7oR\nWCC65X1avIMTIFAjMMFJJlSi7sDpBy1xWcY9BbcwXevKeX0cu6mFPMwMSO1CzChG\nBjNPHLpBPBrI4hM1zRtuow==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-96fyi@gsk-smartplug.iam.gserviceaccount.com",
  "client_id": "103388334598303328704",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-96fyi%40gsk-smartplug.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})

firebase_admin.initialize_app(cred, {"databaseURL": "https://gsk-smartplug-default-rtdb.firebaseio.com"})

# Set up PostgreSQL connection
DATABASE_URL = os.environ.get("DATABASE_URL")
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
