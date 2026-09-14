from app import app, db, User
from werkzeug.security import generate_password_hash


with app.app_context():

    admin = User.query.filter_by(
        email="mallesh@gmail.com"
    ).first()

    if admin:

        admin.role = "admin"

        db.session.commit()

        print("Admin already exists.")
        print("Admin role updated.")

    else:

        admin = User(
            name="Mallesh",
            email="mallesh@gmail.com",
            password=generate_password_hash("mallesh@123"),
            role="admin",
            phone="9014844812"
        )

        db.session.add(admin)

        db.session.commit()

        print("================================")
        print("Admin account created")
        print("================================")
        print("Email    : mallesh@gmail.com")
        print("Password : mallesh@123")
        print("Role     : admin")