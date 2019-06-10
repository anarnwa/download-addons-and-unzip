import os
import re
import sys
import zipfile

import requests


def getnewversion(url:str)->str:#获取最新版本号
    data=str(requests.get(url).content)
    return data.split('<td class="project-file__name" title="')[1].split('">')[0]


def getdownloadurl(url:str)->str: #解析下载地址
    url=url+"/download"
    r = requests.get(url).content 
    d=re.search('<a class="download__link" href=".+">here',str(r))
    d="https://www.curseforge.com"+re.sub('">here',"",d.group(0).lstrip('<a class="download__link" href="'))
    return d

def getfilename(url:str)->str: #获取文件名
    filename=re.sub("https://www.curseforge.com/wow/addons/","",url)
    return filename+"  "+getnewversion(url+"/files")

def downloadfile(url:str,filename:str,Display_percent=True): #下载文件
    downloadurl=getdownloadurl(url)
    r = requests.get(downloadurl, stream=True)
    if Display_percent:
        total_size = int(r.headers['Content-Length'])  #总长度
        temp_size = 0 #当前进度
        with open(filename+".zip", "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    f.write(chunk)                    
                    done = int(20 * temp_size / total_size)
                    sys.stdout.write("\r%s[%s%s] %d%%" % (filename,'█' * done, ' ' * (20 - done), 100 * temp_size / total_size))       
        print()  #换行
    else:
         with open(filename+".zip", "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)



def unzip(filename:str,targetpath:str): #解压文件
    fz = zipfile.ZipFile(filename, 'r')
    for file in fz.namelist():
        fz.extract(file,targetpath)

def deletefile(filename:str): #删除文件
    if os.path.exists(filename):
        os.remove(filename)

def readdownloadtxt(): #读取1.TXT  获取下载链接
     File = open("1.txt")
     while 1:
        url = File.readline()
        if not url:
            break
        url=url.strip("\n")  #读出一行并去除尾部换行符
        #----------------------------#
        #调用以上函数进行处理        
        filename=getfilename(url) 
        downloadfile(url,filename,True)
        unzip(filename+".zip","./addons")
        deletefile(filename+".zip")
        #----------------------------#

def gettoc(path:str)->list:#找出toc文件
    l=[]
    for files in os.listdir(path):
        for fn in os.listdir(path+"/"+files):
            if os.path.splitext(fn)[1]==".toc":
                l.append(path+"/"+files+"/"+fn)
    return l

def getnowversion(path:str)->dict: #获取当前已安装的版本号
    d={}
    toc=gettoc(path)
    for i in toc:
        f=open(i,'r', encoding='UTF-8')
        read=f.read()
        try:
            if "## Version" in read:
                Version=re.sub("Version:","",re.search("Version: .+\n",read).group(0)).strip("\n")
                d[os.path.splitext(os.path.split(i)[1])[0]]=Version
        except:
            print(i)
    return d


if __name__=="__main__":
    readdownloadtxt()
