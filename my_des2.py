from Crypto.Cipher import DES


def encrypt(data, password):
    password = password[:8]
    des_obj = DES.new(password, DES.MODE_ECB)
    return des_obj.encrypt(data)


def decrypt(data, password):
    password = password[:8]
    des_obj = DES.new(password, DES.MODE_ECB)
    return des_obj.decrypt(data)
