#!/usr/bin/env python
# coding=utf8
# @author:weiyz

import os
import uuid
import threading
import tarfile
import shutil
import socket
import time
from filecmp import dircmp

### beg 20180111 重设系统编码为GBK保证可以读取中文字符 ###
import sys
reload(sys)
sys.setdefaultencoding('gbk')
### end 20180111 ###


def get_sub_dic(lst, key):
    for dic in lst:
        if not isinstance(dic, dict):
            continue
        if dic.has_key(key):
            return dic


def path2json(path, root_dir, res, type):
    simple_path = path.split(root_dir, 1)[1]
    info = simple_path.lstrip(os.sep).split(os.sep, 1)
    if len(info) > 1:
        nlv, rest = info
        sub_dic = get_sub_dic(res[root_dir], nlv)
        if sub_dic:
            path2json(simple_path, nlv, sub_dic, type)
        else:
            res[root_dir].append({nlv: []})
            path2json(simple_path, nlv, get_sub_dic(res[root_dir], nlv), type)
    else:
        # print type,path
        if type == 'f':
            res[root_dir].append(info[0])
        elif type == 'd':
            res[root_dir].append({info[0]: []})


class EnviromentCompare:
    def __init__(self, dir1, dir2, dir1_flag, dir2_flag):
        self.left_only_whole = []
        self.right_only_whole = []
        self.differing = []
        self.dir1 = dir1
        self.dir1_flag = dir1_flag
        self.dir2 = dir2
        self.dir2_flag = dir2_flag
        # print repr(dir1),repr(dir2)

    def getLeftOnly(self):
        res = {self.getLeftDir(): []}
        for item in self.left_only_whole:
            type = 'f' if os.path.isfile(item) else 'd'
            path2json(item, self.getLeftDir(), res, type)
        if self.dir1_flag:
            res[self.getFullLeftDir()] = res[self.getLeftDir()]
            del res[self.getLeftDir()]
        return res

    def getRightOnly(self):
        res = {self.getRightDir(): []}
        for item in self.right_only_whole:
            type = 'f' if os.path.isfile(item) else 'd'
            path2json(item, self.getRightDir(), res, type)
        if self.dir2_flag:
            res[self.getFullRightDir()] = res[self.getRightDir()]
            del res[self.getRightDir()]
        return res

    def getFormatDiffering(self):
        res = {self.getLeftDir(): []}
        for item, _ in self.differing:
            type = 'f' if os.path.isfile(item) else 'd'
            path2json(item, self.getLeftDir(), res, type)

        # path2json中含有递归的部分，不能传入绝对路径，所以先用相对路径完成计算，最后再把根节点名改成绝对路径即可
        if self.dir1_flag:
            res[self.getFullLeftDir()] = res[self.getLeftDir()]
            del res[self.getLeftDir()]
        elif self.dir2_flag:
            res[self.getFullRightDir()] = res[self.getLeftDir()]
            del res[self.getLeftDir()]
        else:
            pass

        return res

    def getDiffering(self):
        for item, _ in self.differing:
            # print item.split(self.getLeftDir())[1]
            yield item.split(self.getLeftDir())[1]

    def getLeftDir(self):
        return os.path.basename(self.dir1).encode('gbk')

    def getFullLeftDir(self):
        return self.dir1

    def getRightDir(self):
        return os.path.basename(self.dir2).encode('gbk')

    def getFullRightDir(self):
        return self.dir2

    def textResult(self):
        txt = u''
        txt += u'=============================\n只存在于%s中的文件/目录' % self.getLeftDir()
        if self.left_only_whole:
            for item in self.left_only_whole:
                txt += u'\n%s' % item
        else:
            txt += u'\n无。'

        txt += u'\n============================\n只存在于%s中的文件/目录' % self.getRightDir()
        if self.right_only_whole:
            for item in self.right_only_whole:
                try:
                    txt += u'\n%s' % item
                except Exception,e:
                    txt += u'\n%s' % repr(item)
        else:
            txt += u'\n无。'

        txt += u'\n=============================\n文件名相同内容不同的文件(不包括目录)'
        if self.getDiffering():
            for item in self.getDiffering():
                txt += u'\n%s' % item
        else:
            txt += u'\n无。'

        txt += u'\n\n\n============================================================'

        return txt

    def compare(self, dir1, dir2):
        dcmp = dircmp(dir1, dir2)

        if dcmp.left_only:
            for fi in dcmp.left_only:
                try:
                    self.left_only_whole.append(os.path.join(dir1, fi).encode('gbk'))
                except UnicodeEncodeError,e:
                    print repr(os.path.join(dir1,fi)) + u'编码格式复杂'
                    raise
                except Exception,e:
                    print repr(os.path.join(dir1,fi)) + u'出错'
                    raise

        if dcmp.right_only:
            for fi in dcmp.right_only:
                try:
                    self.right_only_whole.append(os.path.join(dir2, fi).encode('gbk'))
                except UnicodeEncodeError,e:
                    print repr(os.path.join(dir2,fi)) + u'编码格式复杂'
                except Exception,e:
                    print repr(os.path.join(dir2,fi)) + u'出错'
                    raise

        if dcmp.diff_files:
            for fi in dcmp.diff_files:
                try:
                    self.differing.append((os.path.join(dir1, fi).encode('gbk'), os.path.join(dir2, fi).encode('gbk')))
                except Exception,e:
                    print repr(os.path.join(dir1,fi)),repr(os.path.join(dir2,fi)) + u'出错'
                    raise

        if dcmp.common_dirs:
            for di in dcmp.common_dirs:
                try:
                    self.compare(os.path.join(dir1, di), os.path.join(dir2, di))
                except Exception,e:
                    # print repr(os.path.join(dir1,di)),repr(os.path.join(dir2,di))  # 错误信息打印在错的那个文件即可，以上的递归进去的目录没必要写
                    raise

class DownloadThread(threading.Thread):
    def __init__(self, dir):
        threading.Thread.__init__(self)
        self.dir = dir
        self.id = str(uuid.uuid1())[:4]

    def setTrans(self,trans):
        self.trans = trans
        return self

    def setSftp(self, sftp):
        self.sftp = sftp
        return self

    def setSsh(self, ssh):
        self.ssh = ssh
        return self

    def setChannel(self,channel):
        self.channel = channel
        return self

    def run(self):
        ssh = self.ssh
        sftp = self.sftp
        basedir = os.path.basename(sftp.mydir)
        remoteTarName = '/tmp/%s@@%s.tar.gz' % (basedir, sftp.myip)
        with open(self.id, 'w') as f:
            f.write('正在打包...')
        relativedir, base = os.path.dirname(sftp.mydir), os.path.basename(sftp.mydir)
        # stdin, stdout, stderr = ssh.exec_command('cd %s;tar -cvzf \'%s\' %s' % (relativedir, remoteTarName, base),
        #                                          get_pty=True)
        # err = stderr.read()
        # if err != '':
        #     raise Exception(err)
        cmd = 'cd %s;tar -cvzf \'%s\' %s' % (relativedir, remoteTarName, base)
        self.channel.send(cmd+'\n')
        while 1:
            time.sleep(5)
            try:
                self.channel.recv(65535)
            except socket.timeout,e:
                break

        sftp.get(remoteTarName, os.path.join('Compare', os.path.basename(remoteTarName)), callback=self.writeProcess)
        ssh.exec_command('rm -f %s' % remoteTarName)

        # 进行解压
        with open(self.id, 'w') as f:
            f.write('正在解压...')
        if os.path.isdir(os.path.join('Compare',os.path.basename(remoteTarName).rsplit('.',2)[0])):
            shutil.rmtree(os.path.join('Compare',os.path.basename(remoteTarName).rsplit('.',2)[0]))
        os.mkdir(os.path.join('Compare',os.path.basename(remoteTarName).rsplit('.',2)[0]))
        tar = tarfile.open(os.path.join('Compare', os.path.basename(remoteTarName)))
        for fi in tar.getnames():
            ##### 20180201 解压时由于各种原因引起的解压错误处理，给出错误信息 begin #####
            try:
                tar.extract(fi, path=os.path.join('Compare',os.path.basename(remoteTarName).rsplit('.',2)[0]))
            except Exception,e:
                if os.path.splitext(fi)[1] in ('.txt','.doc','.docx'):
                    # 忽略这些说明类文件无法解压时报的错
                    continue
                with open(self.id,'w') as f:
                    f.write('EFF:解压文件%s失败: %s' % (repr(fi),str(e)))
                shutil.rmtree(os.path.join('Compare',os.path.basename(remoteTarName).rsplit('.',2)[0]))
                return
            ##### end #####
        self.ssh.close()
        self.channel.close()
        self.sftp.close()
        self.channel.close()
        with open(self.id, 'w') as f:
            f.write('EFF')

    def writeProcess(self, done, total):
        with open(self.id, 'w') as f:
            percent = '%.4s%%' % (float(done) * 100 / total)
            f.write(percent)
