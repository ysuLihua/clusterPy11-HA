#!/usr/bin/python
# -*- coding: utf-8 -*-
class HostInfo(object):
    def __init__(self,ip,hostname,hosttype,username,password):
        self.__ip=ip
        self.__hostname=hostname
        self.__hosttype=hosttype
        self.__username=username
        self.__password=password
    def getIp(self):
        return self.__ip
    def getHostname(self):
        return self.__hostname
    def getHosttype(self):
        return self.__hosttype
    def getUsername(self):
        return self.__username
    def getPassword(self):
        return self.__password