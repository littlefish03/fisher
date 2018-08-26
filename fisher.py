#created by licw
# -*-coding=utf-8-*-
import config
from datetime import datetime,timedelta
import os
import sys
import time
import utils
import numpy as np
from scipy import stats as sci
from db.sqlalchemy import models as db

class StockData():
    def get_pagedata(self, df):
    # input dataframe
        redict = {}
        for i in range(len(df)):
            row = ''
            for j in range(df.columns.size):
                if j == 0:
                    continue
                if isinstance(df.iat[i,j],unicode):
                    row += ','+df.iat[i,j]
                else:
                    row += ','+str(df.iat[i,j])
            #key is company code and fill by zero to len 6
            key = str(df.iat[i,1]).zfill(6)
            redict[key] = row
        return redict

    def get_data_by_type(self, begin_date, code):
        redata = {}
        date_list = utils.get_daylist(begin_date)
        for d in date_list:
            url = config.gs_url%(code, d)
            data = utils.get_url_data(url)
            if len(data) == 0:
                continue
            df = data[0]
            redict = self.get_pagedata(df)
            for k,v in redict.items():
                if k not in redata.keys():
                    redata[k] = ''
                redata[k] += str(d)+' '+v+'\n'
            #print d
        return redata

    def get_percent(self, data_dir,dt_type, pos):
        redata = {}
        files = os.listdir(data_dir)
        if dt_type:
            dt_files = [f for f in files if dt_type in f]
        else:
            dt_files = files
        for f in dt_files:
            redict = self.calc_percent(os.path.join(data_dir,f),pos)
            for k,v in redict.items():
                redata[k] = v
        return redata
    
    def calc_percent(self, pathfile, pos):
        percent = {}
        vlist = []
        roe = 0
        end_date = datetime.strptime('2018-01-01','%Y-%M-%d')
        for line in open(pathfile, 'r'):
            vline = line.strip().split(',')
            cur_date = datetime.strptime(vline[0].strip(),'%Y-%M-%d')
            if cur_date>end_date:
                break
            try:
                pe = float(vline[12])
                pb = float(vline[13])
            except ValueError:
                continue
            roe = 100*pb/pe
            curr = float(vline[pos])
            last_value = curr
            hy_code = str(vline[1]).zfill(6)
            vlist.append(curr)
        #roe>10
        if roe < 10 or pe>50:
            return percent
        #at least two years
        if len(vlist)<100:
            return percent
        high = []
        low = []
        #20 data average
        for i in range(20):
            v = max(vlist)
            high.append(v)
            vlist.remove(v)
            v = min(vlist)
            low.append(v)
            vlist.remove(v)
        avg_high = sum(high)/len(high)
        avg_low = sum(low)/len(low)
        if avg_high<avg_low*3:
            return percent
        if avg_low > last_value:
            per = 0
        elif avg_high < last_value:
            per = 100
        else:
            per = 100*(last_value-avg_low)/(avg_high-avg_low)
        if per == 0:
            percent[hy_code] = 'hy:'+str(vline[7]).zfill(6)+' pb: '+str(pb)+' pe: '+str(pe)+' roe: '+str(roe)
            print hy_code+','+str(vline[7]).zfill(6)+','+str(pb)+','+str(pe)+','+str(roe)
        # print avg_high,avg_low,last_value,percent
        return percent

    def get_roe_by_code(self, data_dir, code_list,flag):
        for code in code_list:
            f = code.split(' ')[0]+'.txt'
            #from file
            redict = self.scrub_data(os.path.join(data_dir,f),flag)
            #from db
            #redict = self.scrub_data_from_db(code,flag)
            for k,v in redict.items():
                if flag=='roe':
                    std,mean,median,cv,skew,curr = self.calc_roe(v)
                    print 'company:',k,'mean:',mean,'std:',std,'cv:',cv,'skew:',skew,'count:',len(v),'curr:',curr
                else:
                    avg_high,avg_low,last_value,per = self.calc_pepb(v)
                    print 'company:',k,'high:',avg_high,'low:',avg_low,'cur:',last_value,'per:',per

    def calc_pepb(self, data):
        vlist = data
        if len(vlist)<100:
            return
        high = []
        low = []
        last_value = vlist[-1]
        #10 data average
        for i in range(10):
            v = max(vlist)
            high.append(v)
            vlist.remove(v)
            v = min(vlist)
            low.append(v)
            vlist.remove(v)
        avg_high = sum(high)/len(high)
        avg_low = sum(low)/len(low)
        if avg_low > last_value:
            per = 0
        elif avg_high < last_value:
            per = 100
        else:
            per = 100*(last_value-avg_low)/(avg_high-avg_low)
        return avg_high,avg_low,last_value,per

    def get_roe(self, data_dir,dt_type):
        stddict = {}
        meandict = {}
        meddict = {}
        cvdict = {}
        skewdict = {}
        countdict = {}
        currdict = {}
        files = os.listdir(data_dir)
        if dt_type:
            dt_files = [f for f in files if dt_type in f]
        else:
            dt_files = files
        for f in dt_files:
            redict = self.scrub_data(os.path.join(data_dir,f),'roe')
            for k,v in redict.items():
                std,mean,median,cv,skew,curr = self.calc_roe(v)
                stddict[k] = std
                meandict[k] = mean
                meddict[k] = median
                cvdict[k] = cv
                skewdict[k] = skew
                countdict[k] = len(v)
                currdict[k] = curr
        sortcv = sorted(cvdict.items(),key=lambda std:std[1])
        company = []
        for i in range(len(sortcv)):
            code = sortcv[i][0]
            if meandict[code]<15 or skewdict[code]>1:
                continue
            if sortcv[i][1]>15:
                break
            company.append(code)
            print code,'mean:',meandict[code],'median:',meddict[code],
            print 'cv:',cvdict[code],'std:',stddict[code],
            print 'skew:',skewdict[code],'count:',countdict[code],'curr:',currdict[code]
        return company

    def get_max_roe(self, data_dir,dt_type):
        stddict = {}                                                                     
        meandict = {}                                                                    
        meddict = {}                                                                     
        cvdict = {}                                                                      
        skewdict = {}                                                                    
        countdict = {}                                                                   
        currdict = {}                                                                    
        files = os.listdir(data_dir)                                                     
        if dt_type:                                                                      
            dt_files = [f for f in files if dt_type in f]                                
        else:                                                                            
            dt_files = files                                                             
        for f in dt_files:                                                               
            redict = self.scrub_data(os.path.join(data_dir,f),'roe')                     
            for k,v in redict.items():                                                   
                std,mean,median,cv,skew,curr = self.calc_roe(v)                          
                stddict[k] = std                                                         
                meandict[k] = mean                                                       
                meddict[k] = median                                                      
                cvdict[k] = cv                                                           
                skewdict[k] = skew                                                       
                countdict[k] = len(v)                                                    
                currdict[k] = curr                                                       
        sortroe = sorted(meandict.items(),key=lambda std:std[1],reverse=True)                            
        company = []                                                                     
        for i in range(len(sortroe)):                                                     
            code = sortroe[i][0]                                                          
            #if meandict[code]-stddict[code]<20:         
            if currdict[code]<15 or cvdict[code]>20 or skewdict[code]>1:                           
                continue                                                                 
            if sortroe[i][1]<15:                                                          
                break                                                                    
            company.append(code)                                                         
            print code,'mean:',meandict[code],'median:',meddict[code],                   
            print 'cv:',cvdict[code],'std:',stddict[code],                               
            print 'skew:',skewdict[code],'count:',countdict[code],'curr:',currdict[code] 
        return company                                                                   

    def get_max_roe_from_db(self, data_dir,dt_type):
        stddict = {}
        meandict = {}
        meddict = {}
        cvdict = {}
        skewdict = {}
        countdict = {}
        currdict = {}
        companies = db.get_company(None)
        for company in companies:
            redict = self.scrub_data_from_db(company.code,'roe')
            for k,v in redict.items():
                std,mean,median,cv,skew,curr = self.calc_roe(v)
                stddict[k] = std
                meandict[k] = mean
                meddict[k] = median
                cvdict[k] = cv
                skewdict[k] = skew
                countdict[k] = len(v)
                currdict[k] = curr
        sortroe = sorted(meandict.items(),key=lambda std:std[1],reverse=True)
        company = []
        for i in range(len(sortroe)):
            code = sortroe[i][0]
            #if meandict[code]-stddict[code]<20:
            if currdict[code]<15 or cvdict[code]>20 or skewdict[code]>1:
                continue
            if sortroe[i][1]<15:
                break
            company.append(code.split(' ')[0])
            print code,'mean:',meandict[code],'median:',meddict[code],
            print 'cv:',cvdict[code],'std:',stddict[code],
            print 'skew:',skewdict[code],'count:',countdict[code],'curr:',currdict[code]
        return company

    def scrub_data(self, pathfile,flag):
        vlist = []
        roe = 0
        #start_date = datetime.strptime('2017-12-15','%Y-%M-%d')-timedelta(days=5*365)
        start_date = datetime.now()-timedelta(days=5*365)
        end_date = datetime.strptime('2027-1-14','%Y-%M-%d')
        for line in open(pathfile, 'r'):
            vline = line.strip().split(',')
            cur_date = datetime.strptime(vline[0].strip(),'%Y-%M-%d')
            if cur_date<start_date:
                continue
            if cur_date>end_date:
                break
            try:
                pe = float(vline[12])
                pb = float(vline[13])
            except ValueError:
                # print vline
                continue
            roe = 100*pb/pe
            hy_code = str(vline[1]).zfill(6)+' '+vline[2]
            if flag=='roe':
                vlist.append(roe)
            elif flag=='pe':
                vlist.append(pe)
            else:
                vlist.append(pb)
        #at least two years
        if len(vlist)<100:
            return {}
        return {hy_code: vlist}

    def scrub_data_from_db(self, code, flag):
        vlist = []
        roe = 0
        #start_date = datetime.strptime('2017-12-15','%Y-%M-%d')-timedelta(days=5*365)
        start_date = datetime.now()-timedelta(days=5*365)
        end_date = datetime.strptime('2027-1-14','%Y-%M-%d')
        infos = db.get_info(code)
        comp = db.get_company(code)
        for info in infos:
            cur_date = datetime.strptime(info.date.strip(),'%Y-%M-%d')
            if cur_date<start_date or cur_date>end_date:
                continue
            if flag=='roe':
                vlist.append(info.roe)
            elif flag=='pe':
                vlist.append(info.pe_ttm)
            else:
                vlist.append(info.pb)
        #at least two years
        if len(vlist)<100:
            return {}
        return {code+' '+comp.name: vlist}

    def calc_roe(self, data):
        array = np.array(data)
        std = array.std()
        mean = array.mean()
        median = np.median(array)
        cv = 100*sci.variation(array)
        skew = sci.skew(array)
        last_value = data[-1]
        return std,mean,median,cv,skew,last_value

def get_zy_data(df):
# input dataframe
    relist = []
    for i in range(0,len(df)):
        row = ''
        for j in range(0,df.columns.size):
            if j!=0:
                row += ','+str(df.iat[i,j])
        relist.append(row)
    return relist

def get_zy_by_type(date, zy_type):
    COUNT = 6
    cs_data = ['' for i in range(0,COUNT)]
    date_list = utils.get_daylist(begin_date)
    for d in date_list:
        time.sleep(1)
        url = config.cs_url%(zy_type, d)
        data = utils.get_url_data(url)
        if len(data) == 0:
            continue
        df = data[0]
        relist = get_zy_data(df)
        for i in range(0,COUNT):
            if i>=len(relist):
                continue
            cs_data[i] += str(d)+' '+relist[i]+'\n'
        print d
    return cs_data

def get_zy_all(date):
    TYPE_NUM = 4
    for i in range(0,TYPE_NUM):
        print config.zy_type[i]
        cs_data = get_zy_by_type(begin_date, config.zy_type[i])
        for j in range(0,len(cs_data)):
            filename = '/home/li/data/'+config.file_names[j]+'_'+config.d_type[i]+'.txt'
            f = open(filename, 'w')
            f.write(cs_data[j])
            f.close()

def get_zz_data(df):
# input dataframe
    redict = {}
    if df.iat[0,0] not in config.hy_code:
        return redict
    for i in range(0,len(df)):
        row = ''
        for j in range(0,df.columns.size):
            if isinstance(df.iat[i,j],unicode):
                row += ','+df.iat[i,j]
            else:
                row += ','+str(df.iat[i,j])
        redict[str(df.iat[0,0])] = row
    return redict

def get_zz_by_type(date, zz_type):
    COUNT = len(config.hy_code)
    cs_data = {str(i):'' for i in config.hy_code}
    date_list = utils.get_daylist(begin_date)
    for d in date_list:
        # time.sleep(1)
        url = config.cs_url%(zz_type, d)
        hy_data = utils.get_url_data(url)
        if len(hy_data) < COUNT:
            continue
        for data in hy_data:
            redict = get_zz_data(data)
            for k in redict.keys():
                cs_data[k] += str(d)+' '+redict[k]+'\n'
                # print cs_data[k]
        print d
    return cs_data

def get_zz_all(date):
    TYPE_NUM = 4
    for i in range(2,TYPE_NUM):
        print config.zz_type[i]
        cs_data = get_zz_by_type(begin_date, config.zz_type[i])
        for k,v in cs_data.items():
            if len(v) == 0:
                continue
            filename = '/home/li/data/zz_'+config.d_type[i]+'_'+k+'.txt'
            f = open(filename, 'a')
            f.write(v.encode('utf-8'))
            f.close()

def find_value(date):
    TYPE_NUM = 2
    for i in range(1,TYPE_NUM):
        print config.zz_type[i]
        filename = '/home/li/data/'+config.d_type[i]+'_'+str(date)+'.txt'
        f = open(filename, 'w')
        cs_data = get_zz_by_type(begin_date, config.zz_type[i])
        for k,v in cs_data.items():
            if len(v) == 0:
                continue
            all_list = v.strip().split('\n')
            for sv in all_list:
                vlist = sv.strip().split(',')
                try:
                    curr = float(vlist[3])
                    mon1 = float(vlist[6])
                    mon3 = float(vlist[7])
                    mon6 = float(vlist[8])
                    mon12 = float(vlist[9])
                except ValueError:
                    continue
                if mon1>mon3 and mon6>mon1:
                    f.write(sv.encode('utf-8'))
                    f.write('\n')
        f.close()

def get_position(data_dir,dt_type):
    files = os.listdir(data_dir)
    dt_files = [f for f in files if dt_type in f]
    for f in dt_files:
        find_percent(os.path.join(data_dir,f))

def find_percent(pathfile):
    percent = {}
    vlist = []
    for line in open(pathfile, 'r'):
        vline = line.strip().split(',')
        try:
            curr = float(vline[3])
        except ValueError:
            continue
        last_value = curr
        hy_code = vline[1]
        vlist.append(curr)
    if len(vlist)<50:
        return percent
    high = []
    low = []
    for i in range(10):
        v = max(vlist)
        high.append(v)
        vlist.remove(v)
        v = min(vlist)
        low.append(v)
        vlist.remove(v)
    avg_high = sum(high)/len(high)
    avg_low = sum(low)/len(low)
    if avg_low > last_value:
        percent[hy_code] = 0
    elif avg_high < last_value:
        percent[hy_code] = 100
    else:
        percent[hy_code] = 100*(last_value-avg_low)/(avg_high-avg_low)
    print avg_high,avg_low,last_value,percent
    return percent

if __name__ == '__main__':
    #begin_date = config.cs_main_begin_date
    #begin_date = '2017-11-24'
    #find_value(begin_date)
    #get_zz_all(begin_date)
    # get_zy_all(begin_date)
    #datadir = '/home/li/data'
    #get_position(datadir,'zz_dt_pe')
    #print 'Next is PB'
    #get_position(datadir,'zz_pb')
    if len(sys.argv) == 1:
        print 'Usage: Input roe for stocks roe'
        print 'Input data  for download data'
        print 'Input company for finding max roe companies'
        exit()
    datadir = '/home/li/company'
    if sys.argv[1] == 'roe':
        hold_codes = ['601928','600305','002507','300124','600350',
                      '600823','000900','002275','600048','600612',
                      '601186','000625','002150','600271','600763',
                      '000915','002585','002294','601339','002029',
                      '300357','000726','600611','600757']
        xq = ['600519','002304','000895','600886','600036',
              '600016','002294','002415','600196','600763',
              '300003','601318','000651','002508','002241',
              '002572','600340','600900','600004','600660',
              '600276','002236','002104','002701']
        low_pb = ['600350','600611','000625','000708','000726',
                  '000552','600757','600308','600449','600894',
                  '600585','600019','600649','000667','600126',
                  '000550','000719','000898','002187','601188',
                  '600016','600036']
        high_gx = ['000895','600011','601988','601288','601328',
                   '601158','600066','000726','601088','002411']
        company = config.hold_stocks
        gs = StockData()
        print 'roe'
        gs.get_roe_by_code(datadir,company,'roe')
        print 'pe'
        gs.get_roe_by_code(datadir,company,'pe')
        print 'pb'
        gs.get_roe_by_code(datadir,company,'pb')
    #find max roe company
    if sys.argv[1] == 'company':
        datadir = '/home/li/company'
        gs = StockData()
        company = gs.get_max_roe(datadir,None)
        #company = gs.get_max_roe_from_db(datadir,None)
        print 'pe'
        gs.get_roe_by_code(datadir,company,'pe')
        print 'pb'
        gs.get_roe_by_code(datadir,company,'pb')
    if 0:
        datadir = '/home/li/company'
        gs = StockData()
        print 'find the lowest PE'
        pe = gs.get_percent(datadir,None,12)
        print 'find the lowest PB'
        pb = gs.get_percent(datadir,None,13)
    #download company info
    if sys.argv[1] == 'data':
        gs = StockData()
        with open('/home/li/date.txt','r+') as f:
            begin_date = f.readline().strip('\n') ##'2018-2-14'
            curr_date = datetime.now()+timedelta(days=1)
            f.seek(0)
            f.write(curr_date.strftime('%Y-%m-%d'))
        for c in config.csrc_code:
            print c
            codes = db.get_company_by_zzcode(c)
            for code in codes:
                data = gs.get_data_by_type(begin_date, code)
                for k,v in data.items():
                    #write db info
                    db.add_info(v)
                    filename = '/home/li/company/'+k+'.txt'
                    with open(filename, 'a') as f:
                        f.write(v.encode('utf-8'))
