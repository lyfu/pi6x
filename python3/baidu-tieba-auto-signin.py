﻿#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- author: c8d8z8@gmail.com
'''
    百度贴吧自动签到
'''
# config logging
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('baidu-tieba')
logger.info('logging startup');

#python3 之后 configparser 模块 要小写
import configparser
config = configparser.ConfigParser()
config.readfp(open('baidu-tieba.ini'))
base_dir = config.get('global','base_dir')
name = config.get('global','name')
interval = config.get('global','interval')

import urllib.request
#import md5
import hashlib
import base64
import json
import time
import urllib.parse

# baidu login http request paramters
client_id='_client_id=wappc_1368589871859_564'
client_type='_client_type=2'
client_version='_client_version=2.0.3'
phone_imei='_phone_imei='
net_type='net_type=3'
vcode_md5='vcode_md5='
pn='pn=1'

def httpReady(url,data=None,cookie=None):
    logger.debug('-----request start-----')
    logger.debug('request url:'+url)
    #request url
    if data:
        logger.debug('request data:'+data)
        req=urllib.request.Request(url,data.encode('utf-8'))
    else:
        req=urllib.request.Request(url)
    #add cookie
    if cookie:
        logger.debug('request cookie:'+cookie)
        req.add_header('Cookie',cookie)    
    #emulate iphone 5s
    req.add_header('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X; en-us) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53')
    v=urllib.request.urlopen(req).read().decode('raw_unicode_escape')
    logger.debug('-response-')
    logger.debug(v)
    logger.debug('-----request end-----')
    return v

def bdussFile():
    if not base_dir:
        return 'load.bduss'
    return base_dir + '/' + 'load.bduss'

def baiduUtf(data):
    datagb=data#.decode("gbk")
    #return urllib.quote_plus(datagb.encode('UTF-8'))
    return urllib.parse.quote(datagb.encode('utf-8'))

def readbduss():
    #read bduss file
    try:
        flie=open(bdussFile(),'r')
        bduss=flie.read()
        flie.close()
        if islogin(bduss):
            return bduss
        else:
            logger.warning('没有发现bduss文件')
            nobduss()
            return
    except:
        return
        
def writebduss(bduss):
    # write bduss file
    file_object = open(bdussFile(), 'w')
    file_object.write(bduss)
    file_object.close()

def islogin(bduss):
    url='http://tieba.baidu.com/dc/common/tbs'
    data=httpReady(url,cookie=bduss)
    k=json.loads(data)
    if k["is_login"]==1:
        return True
    else:
        return False
def sign(bduss):
    # get tieba list
    url="http://c.tieba.baidu.com/c/f/forum/favolike"
    singbase= bduss +'&'+ client_id+'&'+ client_type+'&'+ client_version+'&'+ phone_imei+'&'+ net_type+'&'+ pn
    signmd5= bduss + client_id+ client_type+ client_version+ phone_imei+ net_type+ pn
    sign = '&sign=' + hashlib.md5((signmd5+'tiebaclient!!!').encode()).hexdigest()
    data=singbase+sign
    data=httpReady(url,data)
    tieba = []
    data=json.loads(data)
    list=data['forum_list']
    for x in list:
        tieba.append(x['name'].encode('gbk'))
    tbs='tbs='+data['anti']['tbs']
    
    
    url='http://c.tieba.baidu.com/c/c/forum/sign'
    for x in  tieba:
        kw='kw='+x.decode('gbk')
        sign='&sign='
        signmd5= bduss + kw + tbs + 'tiebaclient!!!'
        signbase= bduss +'&'+ kw + '&' + tbs
        sign=sign+hashlib.md5(signmd5.encode('utf-8')).hexdigest()
        data=signbase+sign
        data=httpReady(url,data)
        data=json.loads(data)
        if data['error_code']=='0':
            logger.info(x.decode('gbk') + '吧 签到成功！')
        else:
            logger.info(x.decode('gbk') + '吧 签到失败！ 失败原因:' + data['error_msg'])
        time.sleep(float(interval))
    return
    
def namepwd_login(user=None, password=None):
    # login paramters
    
    password='passwd='+base64.b64encode(password.encode('utf-8')).decode()
    un="un="+baiduUtf(user)
    signmd5= client_id+ client_type+ client_version+ phone_imei+password+un+ vcode_md5+"tiebaclient!!!"
    
    signbase= client_id+"&"+ client_type+'&'+ client_version+'&'+ phone_imei+'&'+password+'&'+un+'&'+ vcode_md5
    sign='&sign=' + hashlib.md5(signmd5.encode()).hexdigest()
    
    data=signbase+sign
    url='http://c.tieba.baidu.com/c/s/login'
    # start login
    data=httpReady(url,data)
    data=json.loads(data)
    
    if data['error_code']=='0':
        #login success & need save bduss
        bduss=data['user']['BDUSS'].encode('utf-8')
        bduss = 'BDUSS='+bduss.decode()
        writebduss(bduss)
        logger.info(data['user'])
    else:
        #login failed
        logger.info(data['error_msg'])
    return bduss
    
def auto_login():
    bduss=readbduss()
    if bduss:
        sign(bduss)
    else:
        if not name:
            user=input('请输入账号:')
        else:
            user = name
        password=input('请输入密码:')
        bduss = namepwd_login(user,password)
        sign(bduss)

auto_login()