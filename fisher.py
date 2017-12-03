#created by licw
import config
import os
import time
import utils

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
    datadir = '/home/li/data'
    get_position(datadir,'zz_dt_pe')
    print 'Next is PB'
    get_position(datadir,'zz_pb')
