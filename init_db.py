from database import engine, Base
import models

print("Integrating Vision-led Database Schema...")
Base.metadata.create_all(bind=engine)
print("Database schema successfully generated at hosteva.db")
