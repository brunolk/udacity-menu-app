import sys

# This will come in handy when writing our mapper code
from sqlalchemy import Column, ForeignKey, Integer, String

# This will be used in the configuration and class code
from sqlalchemy.ext.declarative import declarative_base

# This will be used to create our foreign key relationships
# in our mapper code
from sqlalchemy.orm import relationship

# This will be used in our configuration code
# at the end of file
from sqlalchemy import create_engine

# Create an instance of the declarative_base class
Base = declarative_base()


# Object-oriented representation of user table in our database
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Object-oriented representation of restaurant table in our database
class Restaurant(Base):
    __tablename__ = 'restaurant'

    # Declare restaurant table columns (mapper)
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in json format
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
        }


# Object-oriented representation of menu_item table in our database
class MenuItem(Base):
    __tablename__ = 'menu_item'

    # Declare menu_item table columns (mapper)
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in json format
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
            'user_id': self.user_id
        }

# Create an instance of the create_engine class and
# point to the database we will use
engine = create_engine('sqlite:///restaurantmenu.db')

# Goes into the database and adds the classes
# we will soon create as new tables in our database
Base.metadata.create_all(engine)
