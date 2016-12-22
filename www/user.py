#!/usr/bin/evn python3
#-*-coding:utf-8-*-
from sqlalchemy.orm import StringField,IntegerField
import database_connector

Base = declarative_base()
class User(Base):
	__table__ = "users"
	id = IntegerField(primary_key = True)
	name =StringField()
user = User(id = 123,nmae="Michael long")
user.insert()
users=User.findAll()

