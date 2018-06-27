#!/usr/bin/env python
# coding=utf8
# @author:weiyz

import paramiko
import json
import os
import chardet
import time
import traceback
import warnings
import webbrowser
from difflib import HtmlDiff,IS_LINE_JUNK
from flask import Flask
from flask import render_template, url_for, request
from flask_bootstrap import Bootstrap
from EnvCmp import EnviromentCompare,DownloadThread

### beg 20180111 重设系统编码为GBK保证可以读取中文字符 ###
import sys
reload(sys)
sys.setdefaultencoding('gbk')
### end 20180111 ###

WORKSPACE = os.getcwd()
app = Flask(__name__,template_folder=os.path.join(WORKSPACE,'templates'),static_folder=os.path.join(WORKSPACE,'static'))

bootstrap = Bootstrap()
bootstrap.init_app(app)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/local', methods=['GET', 'POST'])
def local_cmp():
    if request.method == 'GET':
        lst = os.listdir(os.path.join(WORKSPACE, 'Compare'))
        for item in lst:
            if not os.path.isdir(os.path.join(WORKSPACE,'Compare',item)):
                del lst[lst.index(item)]
        return render_template('local.html', lst_a=lst, lst_b=lst)

@app.route('/remote/download',methods=['GET','POST'])
def remote_cmp():
    if request.method == 'GET':
        return render_template('remote.html')
    elif request.method == 'POST':
        form = request.form
        host,port,user,password,dir = form.get(u'host'),int(form.get(u'port')),form.get(u'u'),form.get(u'p'),form.get(u'dir')

        # print repr(host),repr(user),repr(password),repr(dir)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host,port,user,password)

        trans = paramiko.Transport((host,port))
        trans.connect(username=user,password=password)
        sftp = paramiko.SFTPClient.from_transport(trans)
        sftp.mydir = dir
        sftp.myip = host
        channel = trans.open_session()
        channel.get_pty()
        channel.invoke_shell()
        channel.settimeout(3)

        downloadThread = DownloadThread(dir)
        downloadThread.setTrans(trans).setSftp(sftp).setSsh(ssh).setChannel(channel)
        thread_id = downloadThread.id

        downloadThread.start()
        return json.dumps({'code':'200','id':thread_id})




@app.route('/remote/help',methods=['GET'])
def remote_help():
    ope = request.args.get(u'ope')

    # 检查IP的请求
    if ope == 'checkIp':
        host = request.args.get(u'host')
        port = int(request.args.get(u'port'))
        import socket
        sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sk.settimeout(0.5)
        try:
            sk.connect((host,port))
        except Exception as e:
            return json.dumps({'code':'201','msg':str(e)})
        else:
            return json.dumps({'code':'200'})
        finally:
            sk.close()

    # 检查目录的请求
    elif ope == 'checkDir':
        host = request.args.get(u'host')
        port = int(request.args.get(u'port'))
        dir = request.args.get(u'dir')
        user = request.args.get(u'u')
        password = request.args.get(u'p')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host,port,username=user,password=password)
        except paramiko.AuthenticationException,e:
            return json.dumps({'code':'203','msg':'Bad Username or Password'})
        stdin,stdout,stderr = ssh.exec_command('if [ -d %s ];then echo True;else echo False;fi' % dir)
        out,err = stdout.read(),stderr.read()
        if err.strip() != '':
            return json.dumps({'code':'204','msg':err})
        if out.strip() == str(True):
            return json.dumps({'code':'200'})
        else:
            return json.dumps({'code':'202','msg':'Directory %s not Found' % dir})

@app.route('/remote/help/pq')
def process_query():
    time.sleep(1)
    id = request.args.get(u't').encode('gbk')
    if id.startswith('__EFF__'):
        # print repr(id)
        # 确定已经下载完成后删除记录文件
        id = id.replace('__EFF__','')
        os.remove(id)
        return json.dumps({'pr':'__Done__'})
    with open(id,'r') as f:
        content = f.read().strip()
    return json.dumps({'pr':content})


@app.route('/res', methods=['GET', 'POST'])
def show_res():
    if request.method == 'POST':
        dir1 = request.form.get('da')
        dir1_flag = request.form.get('asdf') == u'true'
        dir2 = request.form.get('db')
        dir2_flag = request.form.get('bsdf') == u'true'
        dir1 = dir1 if dir1_flag else os.path.join(os.getcwd(),'Compare', dir1)
        dir2 = dir2 if dir2_flag else os.path.join(os.getcwd(),'Compare', dir2)
        for dir in (dir1,dir2):
            if not os.path.isdir(dir):
                return json.dumps({'msg':u'不存在目录%s，请检查是否输入有误' % dir}),400
        try:
            cmp = EnviromentCompare(dir1, dir2, dir1_flag, dir2_flag)
            cmp.compare(dir1,dir2)
        except Exception,e:
            print traceback.format_exc()
            return json.dumps({'msg': u'比对错误，请查看控制台信息: %s' % unicode(e)}),400

        try:
            textResult = cmp.textResult()
            with open(os.path.join('static','tmp','result.txt'),'w') as f:
                f.write(textResult.encode('gb18030'))
        except Exception,e:
            print traceback.format_exc()
            print u'生成文本结果失败，跳过生成'

        try:
            # print repr(cmp.getLeftOnly())
            return render_template('res.html', cmp=cmp, lsdf=dir1_flag, rsdf=dir2_flag)
        except Exception,e:
            print traceback.format_exc()
            return json.dumps({'msg': u'比对结果页面生成失败，请查看控制台信息: %s' % unicode(e)}),400

@app.route('/filediffer',methods=['POST'])
def file_differ():
    filea = request.form.get('fa')
    asdf = request.form.get('asdf') == u'true'
    fileb = request.form.get('fb')
    bsdf = request.form.get('bsdf') == u'true'
    wrap_column = int(request.form.get('sw'))
    is_context = True if request.form.get('isc') == u'true' else False
    is_detailed = True if request.form.get('isd') == u'true' else False
    response = {}
    codecs = {}
    try:
        if asdf:
            with open(filea,'r') as f:
                contenta = f.read()
        else:
            with open(os.path.join('Compare',filea),'r') as f:
                contenta = f.read()
        if bsdf:
            with open(fileb,'r') as f:
                contentb = f.read()
        else:
            with open(os.path.join('Compare',fileb),'r') as f:
                contentb = f.read()

        if is_detailed:
            char_detect = chardet.detect(contenta)
            if char_detect.get('confidence') >= 0.9:
                codecs['a'] = char_detect.get('encoding')
            else:
                codecs['a'] = 'not sure'

            char_detect = chardet.detect(contentb)
            if char_detect.get('confidence') >= 0.9:
                codecs['b'] = char_detect.get('encoding')
            else:
                codecs['b'] = 'not sure'

            codeca,codecb = codecs['a'],codecs['b']
            if codeca != codecb and 'not sure' not in (codeca,codecb):
                try:
                    raw_contenta = contenta.decode(codeca)
                    raw_contentb = contentb.decode(codecb)
                    if raw_contenta == raw_contentb:
                        response['code'] = '201'
                        response['codeca'] = codeca
                        response['codecb'] = codecb
                        return json.dumps(response)
                except Exception:
                    response['msg'] = 'Fail to decode content'

            if '\r\n' in contenta:
                contenta = contenta.replace('\r\n','\n')
            if '\r\n' in contentb:
                contentb = contentb.replace('\r\n','\n')

            if contenta == contentb:
                # 不同换行符导致不同
                response['code'] = '202'
                return json.dumps(response)
            else:
                longer,shorter = (contenta,contentb) if len(contenta) >= len(contentb) else (contentb,contenta)
                if len(longer) - len(shorter) == 1 and longer[-1] == '\n':
                    response['code'] = '203'
                    return json.dumps(response)
    except Exception,e:
        response['code'] = '400'
        response['msg'] = repr(unicode(e))
        return json.dumps(response)
    htmlDiff = HtmlDiff(tabsize=2,wrapcolumn=wrap_column,linejunk=IS_LINE_JUNK)
    fromdesc = filea.split('/',1)[0].encode('utf8')
    todesc = fileb.split('/',1)[0].encode('utf8')
    with open(os.path.join('static','tmp','tmp.html'),'w') as f:
        f.write(htmlDiff.make_file(contenta.splitlines(),contentb.splitlines(),fromdesc=fromdesc,todesc=todesc,context=is_context))
    webbrowser.open_new_tab(os.path.join('static','tmp','tmp.html'))
    response['code'] = '200'
    return json.dumps(response)

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception,e:
        warnings.warn('Invalid Input of port number. Will use default value 5050.')
        port = 5050
    app.run(debug=True, port=port, threaded=True)