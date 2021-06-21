#coding:utf-8
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.config import Config

import os
import my_secr

import struct

font_size = 12

BACKGROUND_COLOR_NOTHING = [0.0, 0.0, 0.0, 1]
BACKGROUND_COLOR_FOLDER  = [0.4, 0.2, 0.2, 1]
BACKGROUND_COLOR_FILE    = [0.2, 0.2, 0.2, 1]

TYPE_NOTHING = 0
TYPE_FOLDER  = 1
TYPE_FILE    = 2

BUTTON_COLOR_ENABLE  = [0.0, 0.5, 0.5, 1]
BUTTON_COLOR_ENABLE2 = [0.5, 0.5, 1.0, 1]
BUTTON_COLOR_DISABLE = [0.3, 0.3, 0.3, 1]

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
        self.text = (infoString)[:40]
        
    def SetFolder(self, fileIndex, infoString):
        self.background_color = BACKGROUND_COLOR_FOLDER
        self.type = TYPE_FOLDER
        self.fileIndex = fileIndex
        self.text = (infoString)[:40]
        
    
class AppWindow(GridLayout):
    def __init__(self, **kwargs):
        super(AppWindow, self).__init__(**kwargs)
        self.cols = 1
        self.titelLabel = Label(text='Titel')

        self.size_width = Config.get('graphics', 'width')
        self.size_height = Config.get('graphics', 'height')
                
        self.add_widget(self.titelLabel)
        self.listLines = 16
        self.listLabels = []
        self.selected = -1
        self.page = 0

        self.folderOperationEnable = False
    
        bb = b''
        for i in range(102400):
            bb += struct.pack('=B', (99 % 256))
            
        for i in range(self.listLines):
            tempLabel = InfoLabel(text='File Name')
            tempLabel.Init(i, self)
            self.listLabels.append(tempLabel)
            self.add_widget(tempLabel)
        
        self.pageButtonBar = GridLayout()
        self.pageButtonBar.cols = 2
        self.button_PageUp      = Button(text="Page Up",
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_PageUp.bind(on_press=self.PageUp)
        
        self.button_PageDown    = Button(text="Page Down",
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_PageDown.bind(on_press=self.PageDown)
        
        self.pageButtonBar.add_widget(self.button_PageUp)
        self.pageButtonBar.add_widget(self.button_PageDown)
        self.add_widget(self.pageButtonBar)

        self.passwordBar = GridLayout(rows = 1)
        self.passwordLabel = Label(text='Password:', size_hint_max_x = 100)
        self.password = TextInput(multiline=False)
        self.passwordBar.add_widget(self.passwordLabel)
        self.passwordBar.add_widget(self.password)
        self.add_widget(self.passwordBar)
        
        #print(dir(self.password), self.password.width)
         

        self.checkBar = GridLayout(rows = 1) 
        self.label_UnlockCheck = Label(text='Unlock')
        self.check_EncryptFolder = CheckBox(color=[1,1,1,1])
        self.check_EncryptFolder.bind(active=self.CheckboxActive)
        
        self.checkBar.add_widget(self.label_UnlockCheck)
        self.checkBar.add_widget(self.check_EncryptFolder)

        self.add_widget(self.checkBar)
        
        self.buttonBar = GridLayout(rows = 1)     
        self.button_EncryptFolder = Button(text="Encrypt Folder",
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_DISABLE,
                                         color=BUTTON_COLOR_DISABLE,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_EncryptFolder.bind(on_press=self.EncryptFolder)
        
        self.button_DecryptFolder = Button(text="Decrypt Folder",
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_DISABLE,
                                         color=BUTTON_COLOR_DISABLE,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_DecryptFolder.bind(on_press=self.DecryptFolder)

        self.button_EncryptFile = Button(text="Encrypt File",
                                         font_size="%dsp" % font_size,
                                         background_color=BUTTON_COLOR_ENABLE,
                                         color=BUTTON_COLOR_ENABLE2,
                                         size_hint=(.3, .3),
                                         pos=(500, 500)) 
        self.button_EncryptFile.bind(on_press=self.EncryptFile)
        
        self.button_DecryptFile = Button(text="Decrypt File",
                                         font_size="%dsp" % font_size,
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

        self.check_EncryptFolder.size = [10, 10]
        self.InitPage()
        #self.listLabels[1].SetBackgroundColor(BACKGROUND_COLOR_FOLDER)
        #self.listLabels[2].SetBackgroundColor(BACKGROUND_COLOR_FILE)
        #self.listLabels[3].SetBackgroundColor(BACKGROUND_COLOR_NOTHING)
        #self.listLabels[4].SetBackgroundColor(BACKGROUND_COLOR_NOTHING)

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
        self.titelLabel.text = self.currentPath
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
        self.DisplayList()

    def OpenFolderByIndex(self, fileIndex):
        if self.currentPath == '$Home:':
            choosePath = self.arrangedDirList[fileIndex][1]
        else:
            choosePath = os.path.join(self.currentPath, self.arrangedDirList[fileIndex][1])
            choosePath = os.path.abspath(choosePath).replace('\\', '/')
        self.OpenFolderByPath(choosePath)

    def OpenFolderByPath(self, folderPath):
        self.currentPath = folderPath
        listDir = os.listdir(self.currentPath)
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
            print('ERROR: DO NOT ENCRYPT THIS SCRIPTS!')
            return
        
        
        for fileName in os.listdir(self.currentPath):
            filePath = os.path.join(self.currentPath, fileName)
            if filePath[-5:] != '.secr' and os.path.isfile(filePath):
                while os.path.isfile(os.path.join(self.currentPath, 'fil_%d.secr' % counter)):
                    counter += 1
                my_secr.SECR_Encrypt(filePath, password, newName = 'fil_%d' % counter, version = 0, encryptLen = 102400)

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
        for fileName in os.listdir(self.currentPath):
            if fileName[-5:] == '.secr':
                my_secr.SECR_Decrypt(os.path.join(self.currentPath, fileName), password)        

        self.OpenFolderByPath(self.currentPath)
        self.check_EncryptFolder.active = False
        #self.CheckboxActive(None, False)



    def EncryptFile(self, btn):
        password = self.password.text
        if self.selected < 0:
            return
        
        if '.serchome' in os.listdir(self.currentPath):
            print('ERROR: DO NOT ENCRYPT THIS SCRIPTS!')
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
        my_secr.SECR_Encrypt(filePath, password, newName = 'fil_%d' % counter, version = 0, encryptLen = 102400)     

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
        my_secr.SECR_Decrypt(filePath, password) 

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
