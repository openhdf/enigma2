import os
import re
import string
import subprocess
import sys
import types
import xml.dom.minidom
import shlex
try:
    from multiprocessing import Process
except ImportError:
    from threading import Thread as Process

class PortScanner(object):

    def __init__(self):
        self._scan_result = {}
        self._nmap_version_number = 0
        self._nmap_subversion_number = 0
        self._nmap_last_output = ''
        is_nmap_found = False
        self.__process = None



    def ipscan(self, hosts = '127.0.0.1'):
        self.scan(hosts, arguments='-sP')
        return self.all_hosts()



    def scan(self, hosts = '127.0.0.1', ports = None, arguments = '-sV'):
        f_args = shlex.split(arguments)
        args = ['nmap',
         '-oX',
         '-',
         hosts] + ['-p', ports] * (ports != None) + f_args
        p = subprocess.Popen(args, bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (self._nmap_last_output, nmap_err,) = p.communicate()
        if len(nmap_err) > 0:
            regex_warning = re.compile('^Warning: .*')
            for line in nmap_err.split('\n'):
                if len(line) > 0:
                    rgw = regex_warning.search(line)
                    if rgw is not None:
                        sys.stderr.write(line + '\n')
                    else:
                        raise PortScannerError(nmap_err)

        dom = xml.dom.minidom.parseString(self._nmap_last_output)
        scan_result = []
        for dhost in dom.getElementsByTagName('host'):
            host = ''
            hostname = ''
            host = dhost.getElementsByTagName('address')[0].getAttributeNode('addr').value
            for dhostname in dhost.getElementsByTagName('hostname'):
                hostname = dhostname.getAttributeNode('name').value
                hostname = hostname.split('.')
                hostname = hostname[0]
                host = dhost.getElementsByTagName('address')[0].getAttributeNode('addr').value
                scan_result.append(['host',
                 str(hostname).upper(),
                 str(host),
                 '00:00:00:00:00:00'])


        self._scan_result = scan_result
        return scan_result



    def __getitem__(self, host):
        return self._scan_result['scan'][host]



    def all_hosts(self):
        listh = self._scan_result
        listh.sort()
        return listh

