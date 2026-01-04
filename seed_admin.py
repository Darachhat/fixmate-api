import asyncio
import sys
import os

# Ensure root fixmate_project is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine, Base
from modules.auth.models import User
from modules.auth.service import get_user_by_email, create_user
from modules.auth.schemas import UserCreate
from shared.enums import UserRole
from core.security import get_password_hash

async def seed_admin():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        admin_email = "admin@fixmate.com"
        admin_pass = "admin123"
        
        user = await get_user_by_email(db, admin_email)
        if user:
            print(f"Admin user already exists: {admin_email}")
            return

        print(f"Creating admin user: {admin_email}")
        # Manually create to force role since schema might default to CUSTOMER
        # actually create_user uses UserCreate which has role field if we updated it, 
        # but let's check schema. usually create_user takes UserCreate.
        # UserCreate schema has role? Let's check. 
        # If not, we create model directly.
        
        # Checking schema: class UserCreate(UserBase): password: str; role: UserRole = UserRole.CUSTOMER
        # So we can pass role.
        
        user_in = UserCreate(
            email=admin_email,
            password=admin_pass,
            role=UserRole.ADMIN,
            full_name="Super Admin",
            phone_number="0000000000"
        )
        
        # create_user hashes password and saves
        user = await create_user(db, user_in)
        print(f"Admin created successfully. Login with: {admin_email} / {admin_pass}")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(seed_admin())
    except Exception as e:
        print(f"Error: {e}")
