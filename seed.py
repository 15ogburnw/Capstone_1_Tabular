from models import db, User
from app import app

db.drop_all()
db.create_all()

User.query.delete()


user1 = User.register(username='HockeyLover445', password='password123',
                      email='hockeylover445@gmail.com', first_name='Garrett', last_name='Smith')
user2 = User.register(username='c_Taylor', password='i<3mydog',
                      email='ctaylor1994@gmail.com', first_name='Chad', last_name='Taylor')

db.session.add(user1)
db.session.add(user2)
db.session.commit()
