from dependencies.database import engine, Base
from models.user import User
from models.expense import Expense

print('Creating database tables...')
Base.metadata.create_all(bind=engine)
