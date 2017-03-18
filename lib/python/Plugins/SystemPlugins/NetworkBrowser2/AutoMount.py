import os
from enigma import eTimer
from Components.Console import Console
from Components.Harddisk import harddiskmanager
from xml.etree.cElementTree import parse as cet_parse
XML_FSTAB = '/etc/enigma2/automounts.xml'

def rm_rf(d):
    try:
        for path in (os.path.joindf for f in os.listdir(d)):
            if os.path.isdir(path):
                rm_rf(path)
            else:
                os.unlink(path)

        os.rmdir(d)
    except Exception as ex:
        print 'AutoMount failed to remove',
        print d,
        print 'Error:',
        print ex



class AutoMount():

    def __init__(self):
        self.automounts = {}
        self.restartConsole = Console()
        self.MountConsole = Console()
        self.removeConsole = Console()
        self.activeMountsCounter = 0
        self.callback = None
        self.timer = eTimer()
        self.timer.callback.append(self.mountTimeout)
        self.getAutoMountPoints()



    def getAutoMountPoints(self, callback = None):
        automounts = []
        self.automounts = {}
        self.activeMountsCounter = 0
        if not os.path.exists(XML_FSTAB):
            return 
        file = open(XML_FSTAB, 'r')
        tree = cet_parse(file).getroot()
        file.close()

        def getValue(definitions, default):
            ret = ''
            Len = len(definitions)
            return Len > 0 and definitions[(Len - 1)].text or default


        mountusing = 0
        for fstab in tree.findall('fstab'):
            mountusing = 1
            for nfs in fstab.findall('nfs'):
                for mount in nfs.findall('mount'):
                    data = {'isMounted': False,
                     'mountusing': False,
                     'active': False,
                     'ip': False,
                     'sharename': False,
                     'sharedir': False,
                     'username': False,
                     'password': False,
                     'mounttype': False,
                     'options': False,
                     'hdd_replacement': False}
                    try:
                        data['mountusing'] = 'fstab'.encode('UTF-8')
                        data['mounttype'] = 'nfs'.encode('UTF-8')
                        data['active'] = getValue(mount.findall('active'), False).encode('UTF-8')
                        if data['active'] == 'True' or data['active'] == True:
                            self.activeMountsCounter += 1
                        data['hdd_replacement'] = getValue(mount.findall('hdd_replacement'), 'False').encode('UTF-8')
                        data['ip'] = getValue(mount.findall('ip'), '192.168.0.0').encode('UTF-8')
                        data['sharedir'] = getValue(mount.findall('sharedir'), '/exports/').encode('UTF-8')
                        data['sharename'] = getValue(mount.findall('sharename'), 'MEDIA').encode('UTF-8')
                        data['options'] = getValue(mount.findall('options'), 'rw,nolock,tcp,utf8').encode('UTF-8')
                        self.automounts[data['sharename']] = data
                    except Exception as e:
                        print '[MountManager] Error reading Mounts:',
                        print e


            for cifs in fstab.findall('cifs'):
                for mount in cifs.findall('mount'):
                    data = {'isMounted': False,
                     'mountusing': False,
                     'active': False,
                     'ip': False,
                     'sharename': False,
                     'sharedir': False,
                     'username': False,
                     'password': False,
                     'mounttype': False,
                     'options': False,
                     'hdd_replacement': False}
                    try:
                        data['mountusing'] = 'fstab'.encode('UTF-8')
                        data['mounttype'] = 'cifs'.encode('UTF-8')
                        data['active'] = getValue(mount.findall('active'), False).encode('UTF-8')
                        if data['active'] == 'True' or data['active'] == True:
                            self.activeMountsCounter += 1
                        data['hdd_replacement'] = getValue(mount.findall('hdd_replacement'), 'False').encode('UTF-8')
                        data['ip'] = getValue(mount.findall('ip'), '192.168.0.0').encode('UTF-8')
                        data['sharedir'] = getValue(mount.findall('sharedir'), '/exports/').encode('UTF-8')
                        data['sharename'] = getValue(mount.findall('sharename'), 'MEDIA').encode('UTF-8')
                        data['options'] = getValue(mount.findall('options'), 'rw,utf8').encode('UTF-8')
                        data['username'] = getValue(mount.findall('username'), 'guest').encode('UTF-8')
                        data['password'] = getValue(mount.findall('password'), '').encode('UTF-8')
                        self.automounts[data['sharename']] = data
                    except Exception as e:
                        print '[MountManager] Error reading Mounts:',
                        print e



        for enigma2 in tree.findall('enigma2'):
            mountusing = 2
            for nfs in enigma2.findall('nfs'):
                for mount in nfs.findall('mount'):
                    data = {'isMounted': False,
                     'mountusing': False,
                     'active': False,
                     'ip': False,
                     'sharename': False,
                     'sharedir': False,
                     'username': False,
                     'password': False,
                     'mounttype': False,
                     'options': False,
                     'hdd_replacement': False}
                    try:
                        data['mountusing'] = 'enigma2'.encode('UTF-8')
                        data['mounttype'] = 'nfs'.encode('UTF-8')
                        data['active'] = getValue(mount.findall('active'), False).encode('UTF-8')
                        if data['active'] == 'True' or data['active'] == True:
                            self.activeMountsCounter += 1
                        data['hdd_replacement'] = getValue(mount.findall('hdd_replacement'), 'False').encode('UTF-8')
                        data['ip'] = getValue(mount.findall('ip'), '192.168.0.0').encode('UTF-8')
                        data['sharedir'] = getValue(mount.findall('sharedir'), '/exports/').encode('UTF-8')
                        data['sharename'] = getValue(mount.findall('sharename'), 'MEDIA').encode('UTF-8')
                        data['options'] = getValue(mount.findall('options'), 'rw,nolock,tcp,utf8').encode('UTF-8')
                        self.automounts[data['sharename']] = data
                    except Exception as e:
                        print '[MountManager] Error reading Mounts:',
                        print e


            for cifs in enigma2.findall('cifs'):
                for mount in cifs.findall('mount'):
                    data = {'isMounted': False,
                     'mountusing': False,
                     'active': False,
                     'ip': False,
                     'sharename': False,
                     'sharedir': False,
                     'username': False,
                     'password': False,
                     'mounttype': False,
                     'options': False,
                     'hdd_replacement': False}
                    try:
                        data['mountusing'] = 'enigma2'.encode('UTF-8')
                        data['mounttype'] = 'cifs'.encode('UTF-8')
                        data['active'] = getValue(mount.findall('active'), False).encode('UTF-8')
                        if data['active'] == 'True' or data['active'] == True:
                            self.activeMountsCounter += 1
                        data['hdd_replacement'] = getValue(mount.findall('hdd_replacement'), 'False').encode('UTF-8')
                        data['ip'] = getValue(mount.findall('ip'), '192.168.0.0').encode('UTF-8')
                        data['sharedir'] = getValue(mount.findall('sharedir'), '/exports/').encode('UTF-8')
                        data['sharename'] = getValue(mount.findall('sharename'), 'MEDIA').encode('UTF-8')
                        data['options'] = getValue(mount.findall('options'), 'rw,utf8').encode('UTF-8')
                        data['username'] = getValue(mount.findall('username'), 'guest').encode('UTF-8')
                        data['password'] = getValue(mount.findall('password'), '').encode('UTF-8')
                        self.automounts[data['sharename']] = data
                    except Exception as e:
                        print '[MountManager] Error reading Mounts:',
                        print e



        if mountusing == 0:
            for nfs in tree.findall('nfs'):
                for mount in nfs.findall('mount'):
                    data = {'isMounted': False,
                     'mountusing': False,
                     'active': False,
                     'ip': False,
                     'sharename': False,
                     'sharedir': False,
                     'username': False,
                     'password': False,
                     'mounttype': False,
                     'options': False,
                     'hdd_replacement': False}
                    try:
                        data['mountusing'] = 'old_enigma2'.encode('UTF-8')
                        data['mounttype'] = 'nfs'.encode('UTF-8')
                        data['active'] = getValue(mount.findall('active'), False).encode('UTF-8')
                        if data['active'] == 'True' or data['active'] == True:
                            self.activeMountsCounter += 1
                        data['hdd_replacement'] = getValue(mount.findall('hdd_replacement'), 'False').encode('UTF-8')
                        data['ip'] = getValue(mount.findall('ip'), '192.168.0.0').encode('UTF-8')
                        data['sharedir'] = getValue(mount.findall('sharedir'), '/exports/').encode('UTF-8')
                        data['sharename'] = getValue(mount.findall('sharename'), 'MEDIA').encode('UTF-8')
                        data['options'] = getValue(mount.findall('options'), 'rw,nolock,tcp,utf8').encode('UTF-8')
                        self.automounts[data['sharename']] = data
                    except Exception as e:
                        print '[MountManager] Error reading Mounts:',
                        print e


            for cifs in tree.findall('cifs'):
                for mount in cifs.findall('mount'):
                    data = {'isMounted': False,
                     'mountusing': False,
                     'active': False,
                     'ip': False,
                     'sharename': False,
                     'sharedir': False,
                     'username': False,
                     'password': False,
                     'mounttype': False,
                     'options': False,
                     'hdd_replacement': False}
                    try:
                        data['mountusing'] = 'old_enigma2'.encode('UTF-8')
                        data['mounttype'] = 'cifs'.encode('UTF-8')
                        data['active'] = getValue(mount.findall('active'), False).encode('UTF-8')
                        if data['active'] == 'True' or data['active'] == True:
                            self.activeMountsCounter += 1
                        data['hdd_replacement'] = getValue(mount.findall('hdd_replacement'), 'False').encode('UTF-8')
                        data['ip'] = getValue(mount.findall('ip'), '192.168.0.0').encode('UTF-8')
                        data['sharedir'] = getValue(mount.findall('sharedir'), '/exports/').encode('UTF-8')
                        data['sharename'] = getValue(mount.findall('sharename'), 'MEDIA').encode('UTF-8')
                        data['options'] = getValue(mount.findall('options'), 'rw,utf8').encode('UTF-8')
                        data['username'] = getValue(mount.findall('username'), 'guest').encode('UTF-8')
                        data['password'] = getValue(mount.findall('password'), '').encode('UTF-8')
                        self.automounts[data['sharename']] = data
                    except Exception as e:
                        print '[MountManager] Error reading Mounts:',
                        print e


        self.checkList = self.automounts.keys()
        if not self.checkList:
            print '[NetworkBrowser] self.automounts without mounts',
            print self.automounts
            if callback is not None:
                callback(True)
        else:
            self.CheckMountPoint(self.checkList.pop(), callback)



    def sanitizeOptions(self, origOptions, cifs = False, fstab = False):
        options = origOptions.strip()
        if not fstab:
            if not options:
                options = 'rw,rsize=32768,wsize=32768'
                if not cifs:
                    options += ',proto=tcp'
            elif not cifs:
                if 'rsize' not in options:
                    options += ',rsize=32768'
                if 'wsize' not in options:
                    options += ',wsize=32768'
                if not cifs and 'tcp' not in options and 'udp' not in options:
                    options += ',tcp'
        elif not options:
            options = 'rw'
            if not cifs:
                options += ',nfsvers=3,rsize=32768,wsize=32768,proto=tcp'
        elif not cifs:
            options += ',nfsvers=3'
            if 'rsize' not in options:
                options += ',rsize=32768'
            if 'wsize' not in options:
                options += ',wsize=32768'
            if 'tcp' not in options and 'udp' not in options:
                options += ',tcp'
            options = options + ',timeo=14,fg,soft,intr'
        options = options.replace('tcp', 'proto=tcp')
        options = options.replace('udp', 'proto=udp')
        options = options.replace('utf8', 'iocharset=utf8')
        return options



    def CheckMountPoint(self, item, callback):
        data = self.automounts[item]
        if not self.MountConsole:
            self.MountConsole = Console()
        self.command = []
        self.mountcommand = None
        self.unmountcommand = None
        if data['hdd_replacement'] == 'True' or data['hdd_replacement'] is True:
            path = os.path.join('/media/hdd')
            sharepath = os.path.join('/media/net', data['sharename'])
        else:
            path = os.path.join('/media/net', data['sharename'])
            sharepath = ''
        if os.path.ismount(path):
            self.unmountcommand = 'umount -fl ' + path
        if sharepath and os.path.ismount(sharepath):
            self.unmountcommand = self.unmountcommand + ' && umount -fl ' + sharepath
        if self.activeMountsCounter != 0:
            if data['active'] == 'True' or data['active'] is True:
                if data['mountusing'] == 'fstab':
                    if data['mounttype'] == 'nfs':
                        tmpcmd = 'mount ' + data['ip'] + ':/' + data['sharedir']
                    elif data['mounttype'] == 'cifs':
                        tmpcmd = 'mount //' + data['ip'] + '/' + data['sharedir']
                    self.mountcommand = tmpcmd.encode('UTF-8')
                elif data['mountusing'] == 'enigma2' or data['mountusing'] == 'old_enigma2':
                    tmpsharedir = data['sharedir'].replace(' ', '\\ ')
                    if tmpsharedir[-1:] == '$':
                        tmpdir = tmpsharedir.replace('$', '\\$')
                        tmpsharedir = tmpdir
                    if data['mounttype'] == 'nfs':
                        if not os.path.ismount(path):
                            tmpcmd = 'mount -t nfs -o ' + self.sanitizeOptions(data['options']) + ' ' + data['ip'] + ':/' + tmpsharedir + ' ' + path
                            print 'MOUNT CMD',
                            print tmpcmd
                            self.mountcommand = tmpcmd.encode('UTF-8')
                    elif data['mounttype'] == 'cifs':
                        if not os.path.ismount(path):
                            tmpusername = data['username'].replace(' ', '\\ ')
                            tmpcmd = 'mount -t cifs -o ' + self.sanitizeOptions(data['options'], cifs=True) + ',noatime,noserverino,username=' + tmpusername + ',password=' + data['password'] + ' //' + data['ip'] + '/' + tmpsharedir + ' ' + path
                            self.mountcommand = tmpcmd.encode('UTF-8')
        if self.unmountcommand is not None or self.mountcommand is not None:
            if self.unmountcommand is not None:
                self.command.append(self.unmountcommand)
            if self.mountcommand is not None:
                if not os.path.exists(path):
                    self.command.append('mkdir -p ' + path)
                self.command.append(self.mountcommand)
            self.MountConsole.eBatch(self.command, self.CheckMountPointFinished, [data, callback], debug=True)
        else:
            self.CheckMountPointFinished([data, callback])



    def CheckMountPointFinished(self, extra_args):
        (data, callback,) = extra_args
        if data['hdd_replacement'] == 'True' or data['hdd_replacement'] is True:
            path = os.path.join('/media/hdd')
            sharepath = os.path.join('/media/net', data['sharename'])
        else:
            path = os.path.join('/media/net', data['sharename'])
            sharepath = ''
        if os.path.exists(path):
            if os.path.ismount(path):
                if self.automounts.has_key(data['sharename']):
                    self.automounts[data['sharename']]['isMounted'] = True
                    desc = data['sharename']
                    harddiskmanager.addMountedPartition(path, desc)
            else:
                if self.automounts.has_key(data['sharename']):
                    self.automounts[data['sharename']]['isMounted'] = False
                if os.path.exists(path):
                    if not os.path.ismount(path):
                        try:
                            os.rmdir(path)
                            harddiskmanager.removeMountedPartition(path)
                        except Exception as ex:
                            print 'Failed to remove',
                            print path,
                            print 'Error:',
                            print ex
        if self.checkList:
            self.CheckMountPoint(self.checkList.pop(), callback)
        if self.MountConsole:
            if len(self.MountConsole.appContainers) == 0:
                if callback is not None:
                    self.callback = callback
                    self.timer.startLongTimer(1)



    def mountTimeout(self):
        self.timer.stop()
        if self.MountConsole:
            if len(self.MountConsole.appContainers) == 0:
                if self.callback is not None:
                    self.callback(True)
        elif self.removeConsole:
            if len(self.removeConsole.appContainers) == 0:
                if self.callback is not None:
                    self.callback(True)



    def getMountsList(self):
        return self.automounts



    def getMountsAttribute(self, mountpoint, attribute):
        if self.automounts.has_key(mountpoint):
            if self.automounts[mountpoint].has_key(attribute):
                return self.automounts[mountpoint][attribute]



    def setMountsAttribute(self, mountpoint, attribute, value):
        if self.automounts.has_key(mountpoint):
            self.automounts[mountpoint][attribute] = value



    def writeMountsConfig(self):
        list = ['<?xml version="1.0" ?>\n<mountmanager>\n']
        for (sharename, sharedata,) in self.automounts.items():
            if sharedata['hdd_replacement'] == 'True' or sharedata['hdd_replacement'] is True:
                path = os.path.join('/media/hdd')
                sharepath = os.path.join('/media/net', sharedata['sharename'])
            else:
                path = os.path.join('/media/net', sharedata['sharename'])
                sharepath = ''
            if sharedata['mountusing'] == 'fstab':
                sharetemp = sharedata['ip'] + ':/' + sharedata['sharedir'] + ' '
                tmpfile = open('/etc/fstab.tmp', 'w')
                file = open('/etc/fstab')
                tmpfile.writelines([ l for l in file.readlines() if sharetemp not in l ])
                tmpfile.close()
                file.close()
                os.rename('/etc/fstab.tmp', '/etc/fstab')
                mtype = sharedata['mounttype']
                list.append('<fstab>\n')
                list.append(' <' + mtype + '>\n')
                list.append('  <mount>\n')
                list.append('   <active>' + str(sharedata['active']) + '</active>\n')
                list.append('   <hdd_replacement>' + str(sharedata['hdd_replacement']) + '</hdd_replacement>\n')
                list.append('   <ip>' + sharedata['ip'] + '</ip>\n')
                list.append('   <sharename>' + sharedata['sharename'] + '</sharename>\n')
                list.append('   <sharedir>' + sharedata['sharedir'] + '</sharedir>\n')
                list.append('   <options>' + sharedata['options'] + '</options>\n')
                if sharedata['mounttype'] == 'cifs':
                    list.append('   <username>' + sharedata['username'] + '</username>\n')
                    list.append('   <password>' + sharedata['password'] + '</password>\n')
                list.append('  </mount>\n')
                list.append(' </' + mtype + '>\n')
                list.append('</fstab>\n')
                out = open('/etc/fstab', 'a')
                if sharedata['mounttype'] == 'nfs':
                    line = sharedata['ip'] + ':/' + sharedata['sharedir'] + ' ' + path + '\tnfs\t_netdev,' + self.sanitizeOptions(sharedata['options'], fstab=True) + '\t0 0\n'
                elif sharedata['mounttype'] == 'cifs':
                    line = '//' + sharedata['ip'] + '/' + sharedata['sharedir'] + ' ' + path + '\tcifs\tusername=' + sharedata['username'] + ',password=' + sharedata['password'] + ',_netdev,' + self.sanitizeOptions(sharedata['options'], cifs=True, fstab=True) + '\t0 0\n'
                out.write(line)
                out.close()
            elif sharedata['mountusing'] == 'enigma2':
                mtype = sharedata['mounttype']
                list.append('<enigma2>\n')
                list.append(' <' + mtype + '>\n')
                list.append('  <mount>\n')
                list.append('   <active>' + str(sharedata['active']) + '</active>\n')
                list.append('   <hdd_replacement>' + str(sharedata['hdd_replacement']) + '</hdd_replacement>\n')
                list.append('   <ip>' + sharedata['ip'] + '</ip>\n')
                list.append('   <sharename>' + sharedata['sharename'] + '</sharename>\n')
                list.append('   <sharedir>' + sharedata['sharedir'] + '</sharedir>\n')
                list.append('   <options>' + sharedata['options'] + '</options>\n')
                if sharedata['mounttype'] == 'cifs':
                    list.append('   <username>' + sharedata['username'] + '</username>\n')
                    list.append('   <password>' + sharedata['password'] + '</password>\n')
                list.append('  </mount>\n')
                list.append(' </' + mtype + '>\n')
                list.append('</enigma2>\n')
            elif sharedata['mountusing'] == 'old_enigma2':
                mtype = sharedata['mounttype']
                list.append(' <' + mtype + '>\n')
                list.append('  <mount>\n')
                list.append('   <active>' + str(sharedata['active']) + '</active>\n')
                list.append('   <hdd_replacement>' + str(sharedata['hdd_replacement']) + '</hdd_replacement>\n')
                list.append('   <ip>' + sharedata['ip'] + '</ip>\n')
                list.append('   <sharename>' + sharedata['sharename'] + '</sharename>\n')
                list.append('   <sharedir>' + sharedata['sharedir'] + '</sharedir>\n')
                list.append('   <options>' + sharedata['options'] + '</options>\n')
                if sharedata['mounttype'] == 'cifs':
                    list.append('   <username>' + sharedata['username'] + '</username>\n')
                    list.append('   <password>' + sharedata['password'] + '</password>\n')
                list.append('  </mount>\n')
                list.append(' </' + mtype + '>\n')

        list.append('</mountmanager>\n')
        try:
            f = open(XML_FSTAB, 'w')
            f.writelines(list)
            f.close()
        except Exception as e:
            print '[NetworkBrowser] Error Saving Mounts List:',
            print e



    def stopMountConsole(self):
        if self.MountConsole is not None:
            self.MountConsole = None



    def removeMount(self, mountpoint, callback = None):
        self.newautomounts = {}
        path = ''
        for (sharename, sharedata,) in self.automounts.items():
            if sharedata['hdd_replacement'] == 'True' or sharedata['hdd_replacement'] is True:
                path = os.path.join('/media/hdd')
                sharepath = os.path.join('/media/net', sharedata['sharename'])
            else:
                path = os.path.join('/media/net', sharedata['sharename'])
                sharepath = ''
            if sharename is not mountpoint.strip():
                self.newautomounts[sharename] = sharedata
            if sharedata['mountusing'] == 'fstab':
                tmpfile = open('/etc/fstab.tmp', 'w')
                file = open('/etc/fstab')
                tmpfile.writelines([ l for l in file.readlines() if sharedata['sharedir'] not in l ])
                tmpfile.close()
                file.close()
                os.rename('/etc/fstab.tmp', '/etc/fstab')

        self.automounts.clear()
        self.automounts = self.newautomounts
        if not self.removeConsole:
            self.removeConsole = Console()
        umountcmd = 'umount -fl ' + path
        self.removeConsole.ePopen(umountcmd, self.removeMountPointFinished, [path, callback])



    def removeMountPointFinished(self, result, retval, extra_args):
        (path, callback,) = extra_args
        if os.path.exists(path):
            if not os.path.ismount(path):
                try:
                    os.rmdir(path)
                    harddiskmanager.removeMountedPartition(path)
                except Exception as ex:
                    print 'Failed to remove',
                    print path,
                    print 'Error:',
                    print ex
        if self.removeConsole:
            if len(self.removeConsole.appContainers) == 0:
                if callback is not None:
                    self.callback = callback
                    self.timer.startLongTimer(1)



iAutoMount = AutoMount()
