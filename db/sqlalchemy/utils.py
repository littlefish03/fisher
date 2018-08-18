#!/usr/bin/env python
# -*-coding=utf-8-*-

import models as db
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def create_company():
    datadir = '/home/li/company'
    files = os.listdir(datadir)
    for fname in files:
        with open(os.path.join(datadir,fname),'r') as f:
           # read file end
           f.seek(2)
           data = f.readline().strip('\n')
           data = data.strip().split(',')
           print data[1], data[2]
           company = db.Company()
           company.code = str(data[1]).zfill(6)
           company.name = str(data[2]).decode('utf-8')
           company.zz1code = str(data[3]).zfill(2)
           company.zz1name = str(data[4]).decode('utf-8')
           company.zz2code = str(data[5]).zfill(4)
           company.zz2name = str(data[6]).decode('utf-8')
           company.zz3code = str(data[7]).zfill(6)
           company.zz3name = str(data[8]).decode('utf-8')
           company.zz4code = str(data[9]).zfill(8)
           company.zz4name = str(data[10]).decode('utf-8')
           if not db.get_company(company.code):
               db.add_data([company])


def create_info():
    datadir = '/home/li/company'
    files = os.listdir(datadir)
    for fname in files:
        print fname
        for line in open(os.path.join(datadir,fname),'r'):
           data = line.strip().split(',')
           # print data[1], data[2]
           info = db.Info()
           info.code = str(data[1]).zfill(6)
           info.date = str(data[0])
           try:
               info.pe = float(data[11])
               info.pe_ttm = float(data[12])
               info.pb = float(data[13])
               info.dyr = float(data[14])
           except ValueError:
               continue
           info.roe = 100*info.pb/info.pe_ttm
           db.add_data([info])

#create_company()
#create_info()
