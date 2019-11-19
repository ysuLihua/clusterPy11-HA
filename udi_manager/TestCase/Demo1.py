#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import InstallManager
import time
if __name__ == '__main__':
    hostsinfo = ["10.0.44.77,masternode,root,cloudos", "10.0.44.78,corenode,root,cloudos","10.0.44.79,corenode,root,cloudos"]
    master = "10.0.44.77,masternode,root,cloudos"
    im=InstallManager()
    im.set_cluster_hosts(hostsinfo)
    im.set_cluster_manager_ha(False)
    im.install_cluster_manager(master)
    while True:
        progress=im.get_cluster_manager_progress()
        print progress
        if progress=="0:manager install success":
            break
        elif progress=="1:manager install fail":
            break
        time.sleep(5)