from pyDes import des, PAD_PKCS5, ECB




def encrypt(data, password):
    password = password[:8]
    des_obj = des(password, ECB, password, padmode=PAD_PKCS5)
    return des_obj.encrypt(data)


def decrypt(data, password):
    password = password[:8]
    des_obj = des(password, ECB, password, padmode=PAD_PKCS5)
    return des_obj.decrypt(data)



'''
#  秘钥  （如果和Java对接，两边要有相同的秘钥）
DES_SECRET_KEY = b'1234567o'
s = '12345670'.encode()  # 这里中文要转成字节， 英文好像不用
des_obj = des(DES_SECRET_KEY, ECB, DES_SECRET_KEY, padmode=PAD_PKCS5)  # 初始化一个des对象，参数是秘钥，加密方式，偏移， 填充方式
secret_bytes = des_obj.encrypt(s)   # 用对象的encrypt方法加密
s = des_obj.decrypt(secret_bytes)   # 用对象的decrypt方法解密
print(secret_bytes)
print(s.decode())
print(len(s), len(secret_bytes))
'''
