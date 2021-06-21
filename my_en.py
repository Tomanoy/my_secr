import hashlib
import struct

def GetMask(baseString, maskLen):
    n = int(maskLen / 16) + 1
    mask = b''
    sechash = hashlib.md5()
    stringLen = len(baseString)
    for i in range(n):
        offset = i % stringLen
        sechash.update(baseString[i:] + baseString[:i])
        mask += sechash.digest()
    return mask[:maskLen]

def encrypt(data, password):
    dataLen  = len(data)
    formatStr = 'B' * dataLen
    mask = struct.unpack(formatStr, GetMask(password, dataLen))
    listData = struct.unpack(formatStr, data)
    
    resultData = b''
    for i in range(dataLen):
        resultData += struct.pack('=B', (int(listData[i] + int(mask[i])) % 256))

    return resultData

def decrypt(data, password):
    dataLen  = len(data)
    formatStr = 'B' * dataLen
    mask = struct.unpack(formatStr, GetMask(password, dataLen))
    listData = struct.unpack(formatStr, data)

    resultData = b''
    for i in range(dataLen):
        resultData += struct.pack('=B', (int(listData[i] - int(mask[i])) % 256))

    return resultData
