# py -m pip install python-dateutil
# py -m pip install mongoengine
from datetime import date

from dateutil.relativedelta import relativedelta
from mongoengine import Document, DateTimeField, StringField

class User(Document):
    fullname: StringField(require=True)
    username: StringField(require=True)
    password: StringField(require=True)
    email: StringField(require=True)
    birth_date: DateTimeField(require=True)
    gender: StringField(require=False)
    phone_number: StringField(require=False)

    def __init__(self, fullname, username, password, email, birth_date, gender=None, phone_number=None):
        self.fullname = fullname
        self.username = username
        self.password = password
        self.email = email
        self.birth_date = birth_date
        self.gender = gender
        self.phone_number = phone_number

    @property
    def age(self):
        return relativedelta(date.today(), self.birth_date).years
      
    @property
    def is_birthday(self):
      today = date.today()
      return self.birth_date.day == today.day and self.birth_date.month == today.month