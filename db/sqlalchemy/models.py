#!/usr/bin/env python
# -*-coding=utf-8-*-

from sqlalchemy import Column, Integer
from sqlalchemy import String, Float, create_engine
from sqlalchemy.orm import sessionmaker, exc
from sqlalchemy import exc as sqlexc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint

# 创建对象的基类:
Base = declarative_base()

# 定义company对象:
class Company(Base):
    # 表的名字:
    __tablename__ = 'companies'
    __table_args__ = (
        UniqueConstraint('code', name='uniq_companies0name'),
    )
    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(6),  nullable=False)
    name = Column(String(16), nullable=False)
    zz1code = Column(String(2), nullable=True)
    zz1name = Column(String(16), nullable=True)
    zz2code = Column(String(4), nullable=True)
    zz2name = Column(String(16), nullable=True)
    zz3code = Column(String(6), nullable=True)
    zz3name = Column(String(48), nullable=True)
    zz4code = Column(String(8), nullable=True)
    zz4name = Column(String(48), nullable=True)

class Info(Base):
     # 表的名字:
     __tablename__ = 'infos'
     __table_args__ = (
        UniqueConstraint('code', 'date', name='uniq_infos0code0date'),
     )
     # 表的结构:
     id = Column(Integer, primary_key=True, autoincrement=True)
     code = Column(String(6), nullable=False)
     date = Column(String(10), nullable=False)
     pe = Column(Float, nullable=True)
     pe_ttm = Column(Float, nullable=True)
     pb = Column(Float, nullable=True)
     dyr = Column(Float, nullable=True)
     roe = Column(Float, nullable=True)

# 初始化数据库连接:
engine = create_engine('sqlite:////home/code/fisher/stocks.db')
Base.metadata.create_all(engine)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

def add_data(records):
    # 创建session对象:
    session = DBSession()
    for record in records:
        # 添加到session:
        session.add(record)
    # 提交即保存到数据库:
    try:
        session.commit()
    except sqlexc.IntegrityError:
        print 'exist...'
    # 关闭session:
    session.close()

def get_company(code):
    # 创建Session:
    session = DBSession()
    # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
    try:
        if code:
            company = session.query(Company).filter(Company.code==code).one()
        else:
            company = session.query(Company).filter().all()
        #print 'company name:', company.name
    except exc.NoResultFound:
        company = None
    finally:
        # 关闭Session:
        session.close()
    return company

def get_company_by_zzcode(code):
    codes = []
    # 创建Session:
    session = DBSession()
    # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
    try:
        company = session.query(Company).filter(Company.zz1code==code).all()
    except exc.NoResultFound:
        company = None
    finally:
        # 关闭Session:
        session.close()
    for c in company:
        codes.append(c.code)
    return codes

def get_info(code):
    # 创建Session:
    session = DBSession()
    # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
    infos = session.query(Info).filter(Info.code==code).all()
    #print('comany infos num:', len(infos))
    # 关闭Session:
    session.close()
    return infos

def add_info(lines):
    for line in lines.split('\n'):
       data = line.strip().split(',')
       if len(data) < 10:
           continue
       #print data
       info = Info()
       info.code = str(data[1]).zfill(6)
       info.date = str(data[0])
       try:
           info.pe = float(data[11])
           info.pe_ttm = float(data[12])
           info.pb = float(data[13])
       except ValueError:
           continue
       # 股息率没有不影响，单独计算
       try:
           info.dyr = float(data[14])
       except ValueError:
           info.dyr = 0
       info.roe = 100*info.pb/info.pe_ttm
       #print info.code, info.date, info.pe
       add_data([info])
