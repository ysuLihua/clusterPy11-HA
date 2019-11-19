#!/usr/bin/python
# -*- coding: utf-8 -*-
import Logger
import re
import HostInfo
import os
import commands
class InstallManager(object):
    def __init__(self):
        self.__hostsInfo=[]
        self.__infos=""
        self.__ha=False
        self.path="./config"
        self.filename="DataEngineConfig" #生成配置文件的本地地址
        self.destfile="/etc/sysconfig/" #配置文件目的地址
        self.installScriptPath="/lihuatest/DataEngine-E0105-RHEL6-X86_64/silent_install.sh"  #远程净化安装脚本地址
        self.installLog="/lihuatest/DataEngine-E0105-RHEL6-X86_64/config/install.log" #远程安装产生日志的地址
        self.installLogPath="./logs" #获取日志文件到本地目录
        self.lastReadLine=0 #记录上一次读取日志文件的位置

    # hostsinfo=["ip,hostname,hosttype,username,password",....]
    def set_cluster_hosts(self,hostsinfo):
        hostsInfo=[]
        for hostinfo in hostsinfo:
            res=self.__checkHostinfo(hostinfo)
            if len(res)==1:
                return res
            else:
                if len(res)==4:
                    hostsInfo.append(HostInfo.HostInfo(res[0],' ',res[1],res[2],res[3]))
                else:
                    hostsInfo.append(HostInfo.HostInfo(res[0], res[1], res[2], res[3].res[4]))
        self.__hostsInfo=hostsInfo
        rightMsg="0:set_cluster_hosts is ok"
        print rightMsg
        Logger.info(rightMsg)
        return rightMsg

    def set_cluster_manager_ha(self,install):
        self.__ha=install
        return "0:set_cluster_manager_ha is ok"

    #master="ip,hostname,hosttype,username,password"
    def install_cluster_manager(self,master):
        self.__infos+="[IP-Config]\n"
        master_ips=[]
        core_ips=[]

        #1.构建infos
        for hostinfo in self.__hostsInfo:
            if hostinfo.getHosttype()=="masternode":
                master_ips.append(hostinfo.getIp())
            else:
                core_ips.append(hostinfo.getIp())
        ips=master_ips+core_ips
        res=self.__checkHostinfo(master)
        if len(res)==1:
            return res
        mhostinfo=''
        if len(res) == 4:
            mhostinfo=HostInfo.HostInfo(res[0], ' ', res[1], res[2], res[3])
        else:
            mhostinfo=HostInfo.HostInfo(res[0], res[1], res[2], res[3].res[4])

        self.__infos+="master_ips="+",".join(master_ips)+"\n"\
                      +"core_ips="+",".join(core_ips)+"\n"\
                      +"local_ip="+mhostinfo.getIp()+"\n"+\
                      "ips="+",".join(ips)+"\n"\
                      +"root_pwd="+mhostinfo.getIp()+"\n"\
                      +"[HA-Config]"+"\n"
        ha_conf = "off"
        if self.__ha:
            ha_conf = "on"
            self.__infos +="ha_conf="+ha_conf+"\n"+\
                           "master_ip="+master_ips[0]+"\n"\
                           +"virtual_ip=0.0.0.0"+"\n"
        else:
            self.__infos += "ha_conf=" + ha_conf + "\n"
        #2.infos写入到配置文件
        fres=self.__writeInfo2File(self.__infos,self.path,self.filename)
        if fres.find("1:")>-1:
            return fres
        #3.生成ansible hosts
        f=open("hosts.txt","w")
        f.write(mhostinfo.getIp()+" ansible_ssh_user="+mhostinfo.getUsername()+" ansible_ssh_pass="+mhostinfo.getPassword())
        f.close()
        #4.复制配置文件到远程主机/etc/sysconfig/下
        copyfile="ansible all -i hosts.txt -m copy -a 'src="+self.path+"/"+self.filename+" dest="+self.destfile+" backup=yes'"
        outputs=commands.getstatusoutput(copyfile)
        if outputs[0]!=0:
            errorMsg = "1:use ansible copy conf-file to destHost fail!"
            print errorMsg
            Logger.error(errorMsg)
            return errorMsg
        Logger.info(outputs)
        #5.触发远程主机执行安装脚本
        doinstall="ansible all -i hosts.txt -m shell -a 'sh " + self.installScriptPath+"'"
        outputs = commands.getstatusoutput(doinstall)
        if outputs[0] != 0:
            errorMsg = "1:use ansible to excute silent_install.sh in destHost fail!"
            print errorMsg
            Logger.error(errorMsg)
            return errorMsg
        Logger.info(outputs)
        rightMsg = "0:install_cluster_manager is ok. Begin Installing ......"
        Logger.info(rightMsg)
        return rightMsg



    def get_cluster_manager_progress(self):
        #1.拉取远程安装日志文件到本地
        fetchlog="ansible all -i hosts.txt -m fetch -a 'src="+self.installLog+" dest="+self.installLogPath+" force=yes backup=yes flat=yes'"
        outputs = commands.getstatusoutput(fetchlog)
        if outputs[0] != 0:
            errorMsg = "1:use ansible to fetch install.log from destHost fail!"
            print errorMsg
            Logger.error(errorMsg)
            return errorMsg
        Logger.info(outputs)

        #2.解析install.log文件
        try:
            fs=open(self.installLogPath+"/install.log","r")
            lines=fs.readlines()
            for lineIndex in range(self.lastReadLine,len(lines)):
                if lines[lineIndex].find("fail")>-1:
                    return "1:manager install fail"
                elif lines[lineIndex].find("Congratulations!")>-1:
                    return "0:manager installed successfully"
                else:
                    return "0:manager is installing"
        except Exception:
            Logger.error("open "+self.installLogPath+"/install.log fail!")
            print "open "+self.installLogPath+"/install.log fail!"
            return "1:get manager_install progress fail!"
        finally:
            fs.close()

    def __checkHostinfo(self,hostinfo):
        infos = hostinfo.split(",")
        if len(infos) <4 :
            errormsg="error: hostinfo must include [ip,hosttype,username,password]"
            print errormsg
            Logger.error(errormsg)
            return "1:"+errormsg
        else:
            # 判断IP是否合法
            compile_ip = re.compile(
                '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
            if compile_ip.match(infos[0]):
                pass
            else:
                errormsg=infos[0] + "ip format error"
                print errormsg
                Logger.error(errormsg)
                return "1:"+errormsg
        return infos

    def __writeInfo2File(self,infos,filepath,filename):
        try:
            isExists = os.path.exists(filepath)
            if not isExists:
                os.mkdir(filepath)
            fs = open(filepath+'/'+filename, 'w')
            fs.write(infos)
        except Exception:
            errorMsg="create file"+filepath+'/'+filename+" error！！！"
            print errorMsg
            Logger.error(errorMsg)
            return "1:"+errorMsg
        finally:
            fs.close()
        rightMsg="write infos to file :"+filepath+'/'+filename+" is ok！！！"
        Logger.info(rightMsg)
        return "0:"+rightMsg


# if __name__ == '__main__':
#     hostsinfo = ["10.0.44.71,masternode,root,cloudos", "10.0.44.72,corenode,root,cloudos","10.0.44.73,corenode,root,cloudos"]
#     master = "10.0.44.71,masternode,root,cloudos"
#     im=InstallManager()
#     im.set_cluster_hosts(hostsinfo)
#     im.set_cluster_manager_ha(False)
#     im.install_cluster_manager(master)