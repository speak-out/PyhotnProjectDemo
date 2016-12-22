#!/usr/bin/evn python3
#-*-coding:utf-8-*-
#ORM
#

__author__="Michael long"#作者

import asyncio,logging

import aiomysql

def log(sql,args=()):  #log打印
	logging.info('SQL :%s' %sql)

#mysql数据库连接池
@asyncio.coroutine
def create_pool(loop,**kw):
	logging.info("Create database connection pool.....")
	global __pool
	__pool = yield from aiomysql.create_pool(
		host = kw.get('host','localhost'),#主机地址
		port = kw.get('port',3306),#端口号
		user =kw['user'],#获取用户名称
		password = kw['password'],#数据密码
		db = kw['db'],#h还不知道是不是数据库名称
		charset=kw.get('charset','utf8'),#默认编码utf8
		autocommit=kw.get('autocommit',True),#是否自动提交，是
		maxsize=kw.get('maxsize',10),#最大链接数
		minsize=kw.get('minsize',1),
		loop = loop
		)
#要执行SELECT语句，我们用select函数执行，需要传入SQL语句和SQL参数
@asyncio.coroutine
def select(sql,args,size=None):
	log(sql,args)
	global __pool
	with (yield from __pool) as conn:
		cur = yield from conn.cursor(aiomysql.DictCursor)
		yield from cur.execute(sql.replace('?','%s'),args or ())
		if size:
			rs = yield from cur.fechtmany(size)
		else:
			rs = yield from cur.fetchall()
		yield from cur.fetchall()
		logging.info("rows returned :%s" %len(rs))
		return rs

#要执行INSERT、UPDATE、DELETE语句，可以定义一个通用的execute()函数，
#因为这3种SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数：
#Insert 、Update、Delete
def execute(sql,args):
	log(sql)
	with (yield from __pool) as conn:
		try:
			cur = yield from conn.cursor()  #获取练级的cursor
			yield from cur.execute(sql.replace('?','%s'),args)
			affected = cur.rowcount  #影响的行数
			yield from cur.close()  #关闭链接
		except BaseException as e:
			raise
		else:
			pass
		finally:
			pass
		return affected
def create_args_string(num):
	L=[]
	for x in xrange(num):
		L.append('?')
	return ','.join(L)

class Field(object):
	def __init__(self,name,column_type,primary_key,default):
		self.name = name
		self.column_type=column_type
		self.primary_key =primary_key
		self.default = default

	def __str__(self):
		return '<%s,%s:%s>' %(self.__class__.__name__,self.column_type,self.name)

class StringField(Field):
	def __init__(self,name=Name,primary_key=False,default=None,ddl='varchar(100)'):
		super().__init__(name,ddl,primary_key,default)

class BooleanField(Field):
	def __init__(self,name=None,default=False):
		super().__init__(name,'boolean',False，default)

class IntegerField(Field):
	def __init__(self,name=None,primary_key=False,default=0):
		super.__init__(name,'bigint',primary_key,default)

class FloatField(Field):
	def __init__(self,name=None,primary_key=False,default=0):
		super().__init__(name,'real',primary_key,default)

class TextField(Field):
	def __init__(self,name=None,default=None):
		super().__init__(name,'text',False,default)

class ModelMetaclass(type):
	def __new__(cls,name,bases,attrs):
		if name=='Model':
			return type.__new__(cls,name,bases,attrs)
		tableName=attrs.get('__table__',None) or name
		logging.info('found model:%s (table:%s)' %(name,tableName))
		mapppings=dict()
		fields=[]
		 primarykey=None
		 for k,v in attrs.items():
		 	if isinstance(v,Field):
		 		logging.info('Found mapping :  %s ==>%s',%(k,v))
		 		mappings[k]=v
		 		if v.primary_key:
		 			#找到主键
		 			if  primarykey:
		 				raise StandarError("Duplicate primary key for field:%s" %k)
		 			primarykey = k
		 		else:
		 			fields.append(k)

		 if not primarykey:
		 	raise StandarError('primarykey key not found')

		 for x in mappings.keys():
		 	attrs.pop(k)
		 escaped_fields = list(map(lambda f:''%s'' %f,fields))
		 asyncio['__mappings__']=mappings
		 attrs['__table__']=tableName
		 attrs['__primary_key__']=primarykey#主键属性名
		 attrs['__fields__']=fields
		 attrs['__select__']='select %s,%s from %s' %(primarykey,','.join(escaped_fields),tableName)

		 
