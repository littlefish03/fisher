#created by licw
import config
import os
import time
import utils

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
            print d
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
        for line in open(pathfile, 'r'):
            vline = line.strip().split(',')
            try:
                pe = float(vline[12])
                pb = float(vline[13])
            except ValueError:
                continue
            curr = float(vline[pos])
            last_value = curr
            roe = 100*pb/pe
            hy_code = str(vline[1]).zfill(6)
            vlist.append(curr)
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
        if avg_low > last_value:
            per = 0
        elif avg_high < last_value:
            per = 100
        else:
            per = 100*(last_value-avg_low)/(avg_high-avg_low)
        if per == 0:
            percent[hy_code] = str(vline[7]).zfill(6)+' pb: '+str(pb)+' pe: '+str(pe)+' roe: '+str(roe)
            print avg_high,avg_low,last_value,percent
        # print avg_high,avg_low,last_value,percent
        return percent

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
    if 1:
        datadir = '/home/li/company'
        gs = StockData()
        print 'find the lowest PE'
        pe = gs.get_percent(datadir,None,12)
        print 'find the lowest PB'
        pb = gs.get_percent(datadir,None,13)
    if 0:
        gs = StockData()
        begin_date = '2017-12-08'
        for c in config.csrc_code:
            print c
            data = gs.get_data_by_type(begin_date, c)
            for k,v in data.items():
                filename = '/home/li/company/'+k+'.txt'
                with open(filename, 'a') as f:
                    f.write(v.encode('utf-8'))
