from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com")

session.add(User1)
session.commit()

# Menu for UrbanBurger
category1 = Category(user_id=1, name="Soccer")

session.add(category1)
session.commit()

category2 = Category(user_id=1, name="Basketball")

session.add(category2)
session.commit()

category3 = Category(user_id=1, name="Baseball")

session.add(category3)
session.commit()

category4 = Category(user_id=1, name="frisbee")

session.add(category4)
session.commit()

category5 = Category(user_id=1, name="Snowboarding")

session.add(category5)
session.commit()

category6 = Category(user_id=1, name="Rock Climbing")

session.add(category6)
session.commit()

category7 = Category(user_id=1, name="Foosball")

session.add(category7)
session.commit()

category8 = Category(user_id=1, name="Skating")

session.add(category8)
session.commit()

category9 = Category(user_id=1, name="Hockey")

session.add(category9)
session.commit()


categoryItem1 = CategoryItem(user_id=1, title="Stick",
                             description="Juicy grilled veggie patty"
                             " with tomato mayo and lettuce",
                             category=category9)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(user_id=1, title="Goggles",
                             description="Juicy grilled veggie patty"
                             " with tomato mayo and lettuce",
                             category=category5)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, title="Snowboard",
                             description="Juicy grilled veggie "
                                         "patty with tomato mayo and lettuce",
                             category=category5)

session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(user_id=1, title="Two shinguards",
                             description="Juicy grilled veggie patty"
                             " with tomato mayo and lettuce",
                             category=category1)

session.add(categoryItem4)
session.commit()


categoryItem5 = CategoryItem(user_id=1, title="Shinguards",
                             description="Juicy grilled veggie "
                                         "patty with tomato mayo and lettuce",
                             category=category1)

session.add(categoryItem5)
session.commit()


categoryItem6 = CategoryItem(user_id=1, title="Frisbee",
                             description="Juicy grilled veggie "
                             "patty with tomato mayo and lettuce",
                             category=category4)

session.add(categoryItem6)
session.commit()


categoryItem7 = CategoryItem(user_id=1, title="Bat",
                             description="Juicy grilled veggie",
                             category=category3)

session.add(categoryItem7)
session.commit()


categoryItem8 = CategoryItem(user_id=1, title="Jersey",
                             description="Juicy grilled veggie patty"
                             " with tomato mayo and lettuce",
                             category=category1)

session.add(categoryItem8)
session.commit()

categoryItem9 = CategoryItem(user_id=1, title="Soccer Cleats",
                             description="Juicy grilled veggie patty"
                             " with tomato mayo and lettuce",
                             category=category1)

session.add(categoryItem9)
session.commit()


print "added category items!"
