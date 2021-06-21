#-*- coding:utf-8 -*-
import os
import my_secr

def DisplayDir(currentPath, listDir):
    print('\ncurrect path: ' + currentPath)
    if currentPath == '$Home:':
        base = ''
    else:
        base = currentPath
        
    for i in range(len(listDir)):
        fpath = os.path.join(base, listDir[i])
        mark = 'n'
        additionalInfo = ''
        if os.path.isfile(fpath):
            mark = 'f'
            if fpath[-5:] == '.secr':
                secrInfo = my_secr.SECR_GetInfo(fpath)
                if not secrInfo is None:
                    additionalInfo = '[%s]' % secrInfo['OFN']
        elif os.path.isdir(fpath):
            mark = 'd'
        print('%4d %s - %s %s' % (i, mark, listDir[i], additionalInfo))

def SelectFileOrDir(startPath = '', selectFile = True):
    currentPath = startPath
    finished = False
    defult_dirs_path = 'dirs.txt'

    while not finished:
        if os.path.isdir(currentPath):
            listDir = ['..']
            listDir += os.listdir(currentPath)
        else:
            currentPath = '$Home:'
            listDir = [os.getcwd().replace('\\', '/')]
            if os.path.isfile(defult_dirs_path):
                f = open(defult_dirs_path, 'r')
                listDir += f.read().splitlines()
                f.close()
        DisplayDir(currentPath, listDir)
        try:
            if selectFile:
                chooseInput = input('choose file:')
            else:
                chooseInput = input('choose dir:')
            choose = int(chooseInput)
            if currentPath == '$Home:':
                choosePath = listDir[choose]
            else:
                choosePath = os.path.join(currentPath, listDir[choose])
                choosePath = os.path.abspath(choosePath).replace('\\', '/')
        except:
            if chooseInput == '' and not selectFile and os.path.isdir(currentPath):
                selectPath = currentPath
                break
            else:
                continue
        if os.path.isdir(choosePath):
            currentPath = choosePath
            continue
        elif os.path.isfile(choosePath) and selectFile:
            currentPath = choosePath
            break
        else:
            continue
    print('selected: %s' % currentPath)
    return currentPath
     
if __name__ == '__main__':
    import getpass
    while True:
        try:
            operation = int(input('0 - Decrypt\n1 - Encrypt\nchoose:'))
            if operation in [0, 1]:
                break
        except:
            pass
        
    selectedDir = SelectFileOrDir('', selectFile = False)
    fileList_all = os.listdir(selectedDir)
    fileList = []
    for i in range(len(fileList_all)):
        filePath = os.path.join(selectedDir, fileList_all[i])
        if os.path.isfile(filePath):
            fileList.append(filePath)

    if operation == 0:
        password = getpass.getpass("password:")
        for filePath in fileList:
            if filePath[-5:] == '.secr':
                my_secr.SECR_Decrypt(filePath, password)
    elif operation == 1:
        while True:
            password_1 = getpass.getpass("password:")
            password_2 = getpass.getpass("   again:")
            if password_1 == password_2:
                password = password_1
                break
            else:
                print('ERROR: The two inputs do not match')
        counter = 1
        for filePath in fileList:
            if filePath[-5:] != '.secr' and os.path.isfile(filePath):
                while os.path.isfile(os.path.join(selectedDir, 'fil_%d.secr' % counter)):
                    counter += 1
                my_secr.SECR_Encrypt(filePath, password, newName = 'fil_%d' % counter, version = 0, encryptLen = 102400)        
    
