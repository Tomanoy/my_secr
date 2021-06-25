#coding:utf-8
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.graphics import Color, Rectangle

from kivy.core.text import Label as CoreLabel

from text_language import text_en as textData

import time
import os
import struct
import threading

import my_secr


font_size = 12
defaultFont = 'msyh'

BACKGROUND_COLOR_NOTHING = [0.0, 0.0, 0.0, 1]
BACKGROUND_COLOR_FOLDER  = [0.6, 0.3, 0.3, 1]
BACKGROUND_COLOR_FILE    = [0.2, 0.2, 0.2, 1]

TYPE_NOTHING = 0
TYPE_FOLDER  = 1
TYPE_FILE    = 2

BUTTON_COLOR_ENABLE  = [0.0, 0.5, 0.5, 1]
BUTTON_COLOR_ENABLE2 = [0.5, 0.5, 1.0, 1]
BUTTON_COLOR_DISABLE = [0.3, 0.3, 0.3, 1]


STATE_MSG  = 1
STATE_PATH = 2

class InfoLabel(Button):
    def on_release(self):
        if self.fileIndex < 0:
            return
        self.appWindow.UnselectAll()
        self.color = [0.4, 0.4, 1, 1]
        self.appWindow.selected = self.fileIndex
        if self.type == TYPE_FOLDER:
            self.appWindow.page = 0
            self.appWindow.OpenFolderByIndex(self.fileIndex)
        
    def SetUnselected(self):
        self.color = [0.8, 0.8, 0.8, 1]

    def Init(self, index, appWindow):
        self.background_color = [0.2, 0.2, 0.2, 1]
        self.index = index
        self.appWindow = appWindow
        self.font_size= '%dsp' % font_size
        self.SetUnselected()
        self.SetNothing()

    def SetBackgroundColor(self, color):
        self.background_color = color

    def SetNothing(self):
        self.SetUnselected()
        self.background_color = BACKGROUND_COLOR_NOTHING
        self.type = TYPE_NOTHING
        self.fileIndex = -1
        self.text = ''

    def SetFile(self, fileIndex, infoString):
        self.background_color = BACKGROUND_COLOR_FILE
        self.type = TYPE_FILE
        self.fileIndex = fileIndex
        self.text = infoString[:60]
        
    def SetFolder(self, fileIndex, infoString):
        self.background_color = BACKGROUND_COLOR_FOLDER
        self.type = TYPE_FOLDER
        self.fileIndex = fileIndex
        self.text = infoString[:60]
        
    
class AppWindow(GridLayout):
    def __init__(self, **kwargs):
        super(AppWindow, self).__init__(**kwargs)
        self.cols = 1
        self.size_width = int(Config.get('graphics', 'width'))
        self.size_height = int(Config.get('graphics', 'height'))
        
        self.listLines = 16
        self.listLabels = []
        self.selected = -1
        self.page = 0

        self.folderOperationEnable = False

        self.msgs = []
    
        self.titelLabel = Label(text='Titel',
                                font_name=defaultFont,
                                font_size="%dsp" % font_size,
                                size_hint_min_y = 1.5 * self.size_height / (self.listLines + 5))
        self.add_widget(self.titelLabel)
            
        for i in range(self.listLines):
            tempLabel = InfoLabel(text='File Name', font_name=defaultFont)
            tempLabel.Init(i, self)
            self.listLabels.append(tempLabel)
            self.add_widget(tempLabel)
        
        self.pageButtonBar = GridLayout()
        self.pageButtonBar.rows = 1
        self.button_PageUp      = Button(text=textData['Page Up'],
                                         font_name=defaultFont,
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_PageUp.bind(on_press=self.PageUp)
        
        self.button_PageBack    = Button(text=textData['Back'],
                                         font_name=defaultFont,
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_PageBack.bind(on_press=self.PageBack)
        
        self.button_PageDown    = Button(text=textData['Page Down'],
                                         font_name=defaultFont,
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_PageDown.bind(on_press=self.PageDown)
        
        self.pageButtonBar.add_widget(self.button_PageUp)
        self.pageButtonBar.add_widget(self.button_PageBack)
        self.pageButtonBar.add_widget(self.button_PageDown)
        self.add_widget(self.pageButtonBar)

        self.passwordBar = GridLayout(rows = 1)
        self.passwordLabel = Label(text=textData['Password'],
                                   font_name=defaultFont)
        self.password = TextInput(multiline=False)
        self.passwordBar.add_widget(self.passwordLabel)
        self.passwordBar.add_widget(self.password)
        self.add_widget(self.passwordBar)
        
        #print(dir(self.password), self.password.width)
        
        self.label_UnlockCheck = Label(text=textData['Unlock'],
                                       font_name=defaultFont)
        self.check_EncryptFolder = CheckBox(color=[1,1,1,1])
        self.check_EncryptFolder.bind(active=self.CheckboxActive)
        self.checkBar = GridLayout(rows = 1)
        self.checkBar.add_widget(self.label_UnlockCheck)
        self.checkBar.add_widget(self.check_EncryptFolder)
        self.add_widget(self.checkBar)
        
        self.buttonBar = GridLayout(rows = 1)      


        self.button_EncryptFolder = Button(text=textData['Encrypt Folder'],
                                         font_size="%dsp" % font_size,
                                         font_name=defaultFont,
                                         background_color=BUTTON_COLOR_DISABLE,
                                         color=BUTTON_COLOR_DISABLE,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_EncryptFolder.bind(on_press=self.EncryptFolder)
        
        self.button_DecryptFolder = Button(text=textData['Decrypt Folder'],
                                         font_size="%dsp" % font_size,
                                         font_name=defaultFont,
                                         background_color=BUTTON_COLOR_DISABLE,
                                         color=BUTTON_COLOR_DISABLE,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_DecryptFolder.bind(on_press=self.DecryptFolder)

        self.button_EncryptFile = Button(text=textData['Encrypt File'],
                                         font_size="%dsp" % font_size,
                                         font_name=defaultFont,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_EncryptFile.bind(on_press=self.EncryptFile)
        
        self.button_DecryptFile = Button(text=textData['Decrypt File'],
                                         font_size="%dsp" % font_size,
                                         font_name=defaultFont,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_DecryptFile.bind(on_press=self.DecryptFile)
        self.buttonBar.add_widget(self.button_EncryptFolder)
        self.buttonBar.add_widget(self.button_DecryptFolder)
        self.buttonBar.add_widget(self.button_EncryptFile)
        self.buttonBar.add_widget(self.button_DecryptFile)
        self.add_widget(self.buttonBar)
        
        self.InitPage()
        
        self.thread = threading.Thread(target = self.ShowMsg, args=())
        self.thread.setDaemon(True)
        self.thread.start()  #打开收数据的线程

    def AddMsg(self, msgText = '', msgTime = 2.0, msgColor = [1, 1, 1, 1]):
        self.msgs.append([msgText, msgTime, msgColor])
    
    def ShowMsg(self):

        msgTime  = 0
        msgTimeStep = 0.1
        msgTimeCount= 0
        
        while True:
            time.sleep(msgTimeStep)
            if msgTimeCount == 0:
                if len(self.msgs) != 0:
                    self.msgState = STATE_MSG
                    if len(self.msgs) > 3:
                        self.msgs = self.msgs[-3:]
                    msgText, msgTime, msgColor = self.msgs[0]
                    del self.msgs[0]
                    print(msgText)
                    if msgTime > 2.0:
                        msgTime = 2.0
                    msgTimeCount = int(msgTime / msgTimeStep)
                    self.titelLabel.text = msgText
                    self.titelLabel.color = msgColor
                elif self.msgState == STATE_MSG:
                    self.msgState = STATE_PATH
                    self.titelLabel.text = self.currentPath
                    self.titelLabel.color = [1,1,1,1]
            else:
                msgTimeCount -= 1

    def ArrangeDir(self, currentPath, listDir):
        if currentPath == '$Home:':
            base = ''
        else:
            base = currentPath
        
        list_folder = []
        list_file   = []
        
        for i in range(len(listDir)):
            fpath = os.path.join(base, listDir[i])
            mark = 'n'
            additionalInfo = ''
            if os.path.isfile(fpath):
                fileData = [TYPE_FILE, listDir[i], '']
                if fpath[-5:] == '.secr':
                    secrInfo = my_secr.SECR_GetInfo(fpath)
                    if not secrInfo is None:
                        fileData[2] = '[%s]' % secrInfo['OFN']
                list_file.append(fileData)
            elif os.path.isdir(fpath):
                list_folder.append([TYPE_FOLDER, listDir[i], ''])
        self.arrangedDirList = list_folder + list_file
        return self.arrangedDirList
        
    def DisplayList(self):
        if self.msgState == STATE_PATH:
            self.titelLabel.text = self.currentPath
            self.titelLabel.color = [1,1,1,1]
        self.selected = -1
        displayStart = self.page * self.listLines
        displayNum = len(self.arrangedDirList) - self.page * self.listLines
        if displayNum > self.listLines:
            displayNum = self.listLines
        
        for i in range(self.listLines):
            self.listLabels[i].SetNothing()
        
        for i in range(displayNum):
            fileData = self.arrangedDirList[displayStart + i]
            if fileData[0] == TYPE_FOLDER:
                self.listLabels[i].SetFolder(displayStart + i, '%3d - %s %s' % (displayStart + i, fileData[1], fileData[2]))
            elif fileData[0] == TYPE_FILE:
                self.listLabels[i].SetFile(displayStart + i, '%3d - %s %s' % (displayStart + i, fileData[1], fileData[2]))
        
    def InitPage(self):
        self.currentPath = '$Home:'
        defult_dirs_path = 'dirs.txt'
        listDir = [os.getcwd().replace('\\', '/')]
        if os.path.isfile(defult_dirs_path):
            f = open(defult_dirs_path, 'r')
            listDir += f.read().splitlines()
            f.close()
        self.ArrangeDir(self.currentPath, listDir)
        self.page = 0
        self.msgState = STATE_PATH
        self.DisplayList()

    def OpenFolderByIndex(self, fileIndex):
        if self.currentPath == '$Home:':
            choosePath = self.arrangedDirList[fileIndex][1]
        else:
            choosePath = os.path.join(self.currentPath, self.arrangedDirList[fileIndex][1])
            choosePath = os.path.abspath(choosePath).replace('\\', '/')
        self.OpenFolderByPath(choosePath)

    def OpenFolderByPath(self, folderPath):
        try:
            listDir = os.listdir(folderPath)
        except:
            msg = 'ERROR: can not open folder!\n(%s)' % folderPath
            self.msgs.append([msg, 2.0, [1, 0, 0, 1]])
            self.InitPage()
            return
        
        self.currentPath = folderPath
        listDir.sort()
        listDir = ['..'] + listDir
        self.ArrangeDir(self.currentPath, listDir)
        self.DisplayList()
        
    def UnselectAll(self):
        for label in self.listLabels:
            label.SetUnselected()
        self.selected = -1


    def PageUp(self, btn):
        if self.page > 0:
            self.page -= 1
            self.DisplayList()
            
    def PageBack(self, btn):
        p1, p2 = os.path.split(self.currentPath)
        if p1 == '' or p2 == '':
            self.InitPage()
        else:
            self.OpenFolderByPath(p1)

        
    def PageDown(self, btn):
        if self.page < int(len(self.arrangedDirList) / self.listLines):
            self.page += 1
            self.DisplayList()
            
    def EncryptFolder(self, btn):
        
        if not self.folderOperationEnable:
            return
        
        password = self.password.text
        counter = 1
        
        if not os.path.isdir(self.currentPath):
            return
        
        if '.serchome' in os.listdir(self.currentPath):
            msg = 'ERROR: DO NOT ENCRYPT THIS SCRIPTS!'
            self.msgs.append([msg, 2.0, [1, 0, 0, 1]])
            return
        
        msg = 'INFO: Encrypting folder.\n(%s)' % self.currentPath
        self.msgs.append([msg, 2.0, [0, 1, 0, 1]])
        num = 0
        for fileName in os.listdir(self.currentPath):
            filePath = os.path.join(self.currentPath, fileName)
            if filePath[-5:] != '.secr' and os.path.isfile(filePath):
                while os.path.isfile(os.path.join(self.currentPath, 'fil_%d.secr' % counter)):
                    counter += 1
                result, msg = my_secr.SECR_Encrypt(filePath, password, newName = 'fil_%d' % counter, version = 0, encryptLen = 102400)
                if result:
                    num += 1
                else:
                    self.msgs.append([msg, 2.0, [1, 0, 0, 1]])
        msg = 'INFO: %d files are encrypted.\n(%s)' % (num, self.currentPath)
        self.msgs.append([msg, 2.0, [0, 1, 0, 1]])
        self.OpenFolderByPath(self.currentPath)
        self.check_EncryptFolder.active = False
        #self.CheckboxActive(None, False)
        
    def DecryptFolder(self, btn):
        if not self.folderOperationEnable:
            return
        password = self.password.text
        counter = 1
        if not os.path.isdir(self.currentPath):
            return
        
        msg = 'INFO: Decrypting folder.\n(%s)' % self.currentPath
        self.msgs.append([msg, 2.0, [0, 1, 0, 1]])
        num = 0
        for fileName in os.listdir(self.currentPath):
            if fileName[-5:] == '.secr':
                result, msg = my_secr.SECR_Decrypt(os.path.join(self.currentPath, fileName), password)        
                if result:
                    num += 1
                else:
                    self.msgs.append([msg, 2.0, [1, 0, 0, 1]])
        msg = 'INFO: %d files are decrypted.\n(%s)' % (num, self.currentPath)
        self.msgs.append([msg, 2.0, [0, 1, 0, 1]])
        self.OpenFolderByPath(self.currentPath)
        self.check_EncryptFolder.active = False

    def EncryptFile(self, btn):
        password = self.password.text
        if self.selected < 0:
            return
        
        if '.serchome' in os.listdir(self.currentPath):
            msg = 'ERROR: DO NOT ENCRYPT THIS SCRIPTS!'
            self.msgs.append([msg, 2.0, [1, 0, 0, 1]])
            return
        
        filePath = os.path.join(self.currentPath, self.arrangedDirList[self.selected][1])
        
        if not os.path.isfile(filePath):
            return
        
        if filePath[-5:] == '.secr':
            return
        
        counter = 1
        while os.path.isfile(os.path.join(self.currentPath, 'fil_%d.secr' % counter)):
            counter += 1
            
        filePath = filePath.replace('\\', '/')
        result, msg = my_secr.SECR_Encrypt(filePath, password, newName = 'fil_%d' % counter, version = 0, encryptLen = 102400)     
        if result:
            msg = 'INFO: file is encrypted.\n(%s)' % filePath
            self.msgs.append([msg, 2.0, [0, 1, 0, 1]])
        else:
            self.msgs.append([msg, 2, [1, 0, 0, 1]])
        self.OpenFolderByPath(self.currentPath)

    def DecryptFile(self, btn):
        password = self.password.text
        if self.selected < 0:
            return
        
        filePath = os.path.join(self.currentPath, self.arrangedDirList[self.selected][1])
        
        if not os.path.isfile(filePath):
            return
        
        if filePath[-5:] != '.secr' and os.path.isfile(filePath):
            return
        filePath = filePath.replace('\\', '/')
        result, msg = my_secr.SECR_Decrypt(filePath, password)
        if result:
            msg = 'INFO: file is decrypted.\n(%s)' % filePath
            self.msgs.append([msg, 2.0, [0, 1, 0, 1]])
        else:
            self.msgs.append([msg, 2, [1, 0, 0, 1]])
        self.OpenFolderByPath(self.currentPath)

    def CheckboxActive(self, checkbox, value):
        
        self.folderOperationEnable = value
        if value:
            self.button_EncryptFolder.background_color = BUTTON_COLOR_ENABLE
            self.button_DecryptFolder.background_color = BUTTON_COLOR_ENABLE
            self.button_EncryptFolder.color = BUTTON_COLOR_ENABLE2
            self.button_DecryptFolder.color = BUTTON_COLOR_ENABLE2
        else:
            self.button_EncryptFolder.background_color = BUTTON_COLOR_DISABLE
            self.button_DecryptFolder.background_color = BUTTON_COLOR_DISABLE
            self.button_EncryptFolder.color = BUTTON_COLOR_DISABLE
            self.button_DecryptFolder.color = BUTTON_COLOR_DISABLE

#checkbox = CheckBox()
#checkbox.bind(active=on_checkbox_active)

class MyApp(App):
    def build(self):
        return AppWindow()

if __name__ == '__main__':
    MyApp().run()
