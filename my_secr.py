#-*- coding:utf-8 -*-
import os
import hashlib
import struct
import random

import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
'''
================tail struct==============
version                   4B        V
original file length     8B        OFL
encrypted data length    4B        EDL
password MD5            16B        PMD5
original filename length 4B        OFNL
original filename        ?B        OFN
additional data length   4B        ADL
additional data          ?B        AD
mark                     4B: SECR  mark
total tail length        4B        TTL
'''
all_version = 2
default_version = 1
support_version = [False for i in range(all_version)]
support_enlib = [None for i in range(all_version)]

try:
    import my_en as en_v0
    support_version[0] = True
    support_enlib[0] = en_v0
except:
    pass
try:
    import my_des2 as en_v1
    support_version[1] = True
    support_enlib[1] = en_v1
except:
    try:
        import my_des as en_v1
        support_version[1] = True
        support_enlib[1] = en_v1
    except:
        pass

for i in range(all_version):
    if support_version[i]:
        print('CHECK: V%d supported.' % i)
    else:
        print('CHECK: V%d unsupported.' % i)

random_pool = 'zyxwvutsrqponmlkjihgfedcbaQWERTYUIOPASDFGHJvhucgdyahwioagasdawuatdygsuiuaWQQWERTYUIJHBHFDXKLZXCVBNM<!@#$%^&*()_++{}?><;][=-0987654321'

def ProcessPassword(password):
    password_utf8 = password.encode('utf-8')
    sechash = hashlib.md5()
    sechash.update(password_utf8)
    password_use = password_utf8 + sechash.digest()
    sechash.update(password_use)
    password_md5 = sechash.digest()
    return password_use, password_md5

def SECR_Encrypt(filePath, password, newName = '', version = default_version, encryptLen = 102400):
    password_use, password_md5 = ProcessPassword(password)

    fileDir, fileName = os.path.split(filePath)
    if newName == '':
        newFilePath = filePath + '.secr'
    else:
        newFilePath = os.path.join(fileDir, newName + '.secr')
    if os.path.isfile(newFilePath) or os.path.isdir(newFilePath):
        print('ERROR: file exists!(%s)' % newFilePath)
        return False

    if support_version[version]:
        en = support_enlib[version]
    else:
        print('ERROR: unsupported version!(V%d)' % version)

    
    secrFile = open(filePath, 'rb+')
    #version
    F_V = struct.pack('I', version)
    
    #original file length
    OFL = os.path.getsize(filePath)
    F_OFL = struct.pack('Q', OFL)
    
    #encrypted data length
    if OFL > encryptLen:
        EDL = encryptLen
    else:
        EDL = OFL
    F_EDL = struct.pack('I', EDL)
    
    #password MD5
    F_PMD5 = password_md5

    #original filename
    F_OFN = fileName.encode('utf-8')

    #original filename length
    OFNL = len(F_OFN)
    F_OFNL = struct.pack('I', OFNL)

    secret_bytes = en.encrypt(secrFile.read(EDL), password_use)
    
    #additional data length
    ADL = len(secret_bytes) - EDL
    F_ADL = struct.pack('I', ADL)
    
    #additional data
    F_AD = secret_bytes[EDL:]

    #mark
    F_mark = b'SECR'

    #total tail length
    TTL = len(F_V) + len(F_OFL) + len(F_EDL) + \
          len(F_PMD5) + len(F_OFNL) + len(F_OFN) + \
          len(F_ADL) + len(F_AD) + len(F_mark) + 4 #len(F_AD) len(F_TTL)
    F_TTL = struct.pack('I', TTL)


    F_Tail = F_V + F_OFL + F_EDL + F_PMD5 + F_OFNL +\
              F_OFN + F_ADL + F_AD + F_mark + F_TTL
    
    secrFile.seek(0)
    secrFile.write(secret_bytes[:EDL])
    secrFile.seek(0, 2)
    secrFile.write(F_Tail)
    secrFile.close()
    os.rename(filePath, newFilePath)
    print('INFO: encrypt sucessfully!(%s)' % filePath)
    return  True

def SECR_GetInfo(filePath):
    secrFile = open(filePath, 'rb')
    secrFile.seek(-8, 2)
    mark, TTL = struct.unpack('=4sI', secrFile.read(8))
    
    if mark != b'SECR':
        print('ERROR: not a SECR file!(%s)' % filePath)
        secrFile.close()
        return None
    
    secrFile.seek(-TTL, 2)
    F_Tail = secrFile.read(TTL)
    secrFile.close()

    info = {}
    
    info['version'] = struct.unpack('I', F_Tail[0:4])[0]
    F_Tail = F_Tail[4:]
    
    info['OFL'] = struct.unpack('Q', F_Tail[0:8])[0]
    F_Tail = F_Tail[8:]
    
    info['EDL'] = struct.unpack('I', F_Tail[0:4])[0]
    F_Tail = F_Tail[4:]
    
    info['PMD5'] = F_Tail[0:16]
    F_Tail = F_Tail[16:]

    info['OFNL'] = struct.unpack('I', F_Tail[0:4])[0]
    F_Tail = F_Tail[4:]

    info['OFN'] = F_Tail[0:info['OFNL']].decode('utf-8')
    F_Tail = F_Tail[info['OFNL']:]
    
    info['ADL'] = struct.unpack('I', F_Tail[0:4])[0]
    F_Tail = F_Tail[4:]

    info['AD'] = F_Tail[0:info['ADL']]
    F_Tail = F_Tail[info['ADL']:]
    
    return info

def SECR_Decrypt(filePath, password):
    secrInfo = SECR_GetInfo(filePath)
    password_use, password_md5 = ProcessPassword(password)
    
    if secrInfo is None:
        return False
    
    if not support_version[secrInfo['version']]:
        print('ERROR: unsupported version!(%s, V%d)' % (filePath, secrInfo['version']))
        return False
    
    if password_md5 != secrInfo['PMD5']:
        print('ERROR: worng password!(%s)' % filePath)
        return False
    
    en = support_enlib[secrInfo['version']]
    secrFile = open(filePath, 'rb+')
    secret_bytes = secrFile.read(secrInfo['EDL']) + secrInfo['AD']
    data_bytes = en.decrypt(secret_bytes, password_use)
    
    secrFile.seek(0)
    secrFile.write(data_bytes)
    secrFile.truncate(secrInfo['OFL'])
    secrFile.close()
    fileDir, fileName = os.path.split(filePath)
    newFilePath = os.path.join(fileDir, secrInfo['OFN'])
    os.rename(filePath, newFilePath)
    
    print('INFO: decrypt sucessfully!(%s)' % filePath)
    return True
    
if __name__ == '__main__':
    #SECR_Encrypt('test - 副本.pdf', 'wasd', 'newserc', version = 0)
    #info = SECR_GetInfo('newserc.secr')
    SECR_Decrypt('newserc.secr', 'wasd')
    
    
