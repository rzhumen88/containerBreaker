import os
import sys
import warnings
from datetime import datetime
import struct
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTreeWidgetItemIterator, QFileDialog, QApplication, QWidget, QPushButton, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QComboBox
from PyQt6 import uic
from treeIter import iterateTreeWidget

class Window(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('containerBreaker1.ui', self)
        self.initUI()
        self.formatChooser = FormatChooser(self)
        self.table = {}
        self.files = []
        self.newFiles = {}
        self.container = None
        self.module = None
        self.cleantmp()
        
    def initUI(self):
        self.bOpen.clicked.connect(self.openFormatChooser)
        self.bClear.clicked.connect(self.clear)
        self.bBuild.clicked.connect(self.build)
        self.bFAdd.clicked.connect(self.addFile)
        self.bFExt.clicked.connect(self.extFile)
        self.bFReplace.clicked.connect(self.replFile)
        self.bFDel.clicked.connect(self.delFile)
        self.treeWidget.itemDoubleClicked.connect(self.openItem)

    def openFormatChooser(self):
        self.formatChooser.show()

    def tableToTree(self): # this drove me crazy
        self.dirs = []
        self.nodes = {}
        self.nodeNum = 0
        for self.element in range(len(self.table)):
            #print(self.table[self.element])
            if '/' in self.table[self.element][0]:
                self.pathToFile = self.table[self.element][0].split('/')
                self.fileInDir = self.pathToFile[-1]
                self.pathToFile = self.pathToFile[:-1]
                self.parent = None
                self.guiElement = (self.fileInDir,
                                   hex(self.table[self.element][1]).upper().replace('X','x'),
                                   str(self.table[self.element][2]),
                                   str(self.table[self.element][3]),
                                   str(self.table[self.element][4]))
                for self.dir in self.pathToFile:
                    if self.dir not in self.dirs:
                        self.dirs.append(self.dir)
                        self.newNode = QTreeWidgetItem([self.dir, '-','-','-','-'])
                        if self.parent:
                            self.parent.addChild(self.newNode)
                        else:
                            self.treeWidget.addTopLevelItem(self.newNode)
                        self.nodes[self.nodeNum] = self.newNode
                        self.nodeNum += 1
                        self.parent = self.newNode
                    else:
                        self.parentIndex = self.dirs.index(self.dir)
                        self.parent = self.nodes[self.parentIndex]
                self.newNode = QTreeWidgetItem(self.guiElement)
                self.parent.addChild(self.newNode)
            else:
                self.guiElement = (self.table[self.element][0],
                                   hex(self.table[self.element][1]).upper().replace('X','x'),
                                   str(self.table[self.element][2]),
                                   str(self.table[self.element][3]),
                                   str(self.table[self.element][4]))
                
                self.newNode = QTreeWidgetItem(self.guiElement)
                self.treeWidget.addTopLevelItem(self.newNode)
            self.files.append(self.newNode)
        self.cleantmp()
            
    def treeFiles(self):
        for self.item in iterateTreeWidget(self.treeWidget):
            if not self.item.text(1) == '-':
                self.path = []
                self.filename = self.item.text(0)
                self.itemm = self.item
                while self.item.parent():
                    self.path.append(self.item.parent().text(0))
                    self.item = self.item.parent()
                self.item = self.itemm
                del self.itemm
                self.filename = '/'.join(self.path[::-1])+'/'+self.filename
                if self.item.text(1) == 'new':
                    #print(str(self.item))
                    yield (self.filename, self.newFiles[str(self.item)], int(self.item.text(3)), self.item.text(4))
                else:
                    self.bytestream = self.container.getFile(self.filename, int(self.item.text(1), 16), int(self.item.text(2)), int(self.item.text(3)), self.item.text(4))
                    yield (self.filename, self.bytestream, int(self.item.text(3)), self.item.text(4))
                    
    def build(self):
        self.filesIter = self.treeFiles()
        self.saveDir, _ = QFileDialog.getSaveFileName(None, "Build Container (DO NOT OVERWRITE CURRENT CONTAINER)",
                           '',"Any files (*.*)")
        self.container.buildContainer(self.filesIter, self.saveDir)
        self.cleantmp()
        print(f'{self.saveDir} builded!')

    def cleantmp(self):
        self.tmpfiles = os.listdir('tmp/')
        for self.tmpfile in self.tmpfiles:
            if os.path.isfile(self.tmpfile):
                os.remove(self.tmpfile)

    def clear(self):
        """Doing cleaning"""
        self.treeWidget.clear()
        self.newFiles.clear()
        self.cleantmp()
        print('Tree cleared!')

    def addFile(self):
        """Adds sibling to the selected node, writes (str_object:raw bytes) into a dictionary"""
        for self.item in self.treeWidget.selectedItems():
            self.openPath, _ = QFileDialog.getOpenFileName(None, "Append File", './', "Any files (*.*)")
            self.fname = self.openPath.split('/')[-1]
            with open(self.openPath, 'rb') as self.newFile:
                self.newFile = self.newFile.read()
                self.newItem = QTreeWidgetItem((self.fname, 'new', str(len(self.newFile)), str(len(self.newFile)), '-'))
                self.newFiles[str(self.newItem)] = self.newFile
                if self.item.parent():
                    self.item.parent().addChild(self.newItem)
                else:
                    self.treeWidget.addTopLevelItem(self.newItem)
                    
    def delFile(self):
        """Deletes selected node from treeView, if newfile - deletes it also"""
        for self.item in self.treeWidget.selectedItems():
            self.delitem = self.item.text(0)
            if self.item.parent():
                if str(self.item) in self.newFiles:
                    del self.newFiles[str(self.item)]
                self.item.parent().removeChild(self.item)
            else:
                self.treeWidget.takeTopLevelItem(self.treeWidget.indexFromItem(self.item).row())
            print(f'{self.delitem} deleted!')

    def extFile(self):
        """Extracts file(s) into choosen directory"""
        for self.item in self.treeWidget.selectedItems():
            print((self.item.data(0,0), int(self.item.data(1,0), 16), int(self.item.data(2,0)), int(self.item.data(3,0)), self.item.data(4,0)))
            self.rawFile = self.container.getFile(self.item.data(0,0), int(self.item.data(1,0), 16), int(self.item.data(2,0)), int(self.item.data(3,0)), self.item.data(4,0))
            self.savePath, _ = QFileDialog.getSaveFileName(None, "Extract File",
                           self.item.data(0,0),"Any files (*.*)")
            with open(self.savePath, 'wb') as self.f:
                self.f.write(self.rawFile)
            print(f'{self.item.text(0)} extracted!')
            return self.savePath

    def replFile(self):
        """Writes new file bytes into dict, old file will be readed from there"""
        for self.item in self.treeWidget.selectedItems():
            self.openPath, _ = QFileDialog.getOpenFileName(None, "Replace File", './', "Any files (*.*)")
            #self.fname = self.openPath.split('/')[-1]
            self.itemName = self.item.text(0)
            self.itemArgs = self.item.text(4)
            with open(self.openPath, 'rb') as self.f:
                self.f = self.f.read()
                self.flen = str(len(self.f))
                self.newItem = QTreeWidgetItem((self.itemName, 'new', self.flen, self.flen, self.itemArgs))
                self.newFiles[str(self.newItem)] = self.f
            self.delFile()
            if self.item.parent():
                    self.item.parent().addChild(self.newItem)
            else:
                    self.treeWidget.addTopLevelItem(self.newItem)
            print(f'{self.item.text(0)} was replaced with {self.openPath}')
            
    def openItem(self):
        for self.item in self.treeWidget.selectedItems():
            if self.item.data(1,0) == '-':
                return 1
            self.rawFile = self.container.getFile(self.item.data(0,0), int(self.item.data(1,0), 16), int(self.item.data(2,0)), int(self.item.data(3,0)), self.item.data(4,0))
            self.tmpName = 'tmp/tmp.'+self.item.data(0,0).split('.')[-1]
            with open(self.tmpName, 'wb') as self.f:
                self.f.write(self.rawFile)
            os.startfile(os.path.dirname(os.path.abspath(__file__))+'/'+self.tmpName)

class FormatChooser(QWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        uic.loadUi('openContainer.ui', self)
        self.comboBox.clear()
        with open('gamelist.txt', 'r') as self.gamelist:
            self.items = []
            self.modules = []
            for self.i in self.gamelist.readlines():
                self.items.append(self.i.split(';')[0])
                self.modules.append(self.i.split(';')[1])
            self.comboBox.addItems(self.items)
        self.initUI()
        
    def initUI(self):
        self.pushButton.clicked.connect(self.ok)
        
    def ok(self):
        print(self.comboBox.currentIndex())
        gamename = self.items[self.comboBox.currentIndex()]
        moduleName = self.modules[self.comboBox.currentIndex()]
        modulePath = moduleName
        containerFile, _ = QFileDialog.getOpenFileName(None, 'Open Container', './', gamename)
        moduleName = moduleName.split('/')[-1].rstrip('\n').rstrip('.py')
        modulePath = modulePath.rstrip(moduleName+'.py\n')
        sys.path.insert(0, modulePath)
        try:
            self.mainWindow.module = __import__(moduleName)
        except ImportError as e:
            print(f'Error loading module: {e}')
            return 1
        self.mainWindow.container = self.mainWindow.module.Container(containerFile)
        self.mainWindow.table = self.mainWindow.container.getTable()
        self.mainWindow.tableToTree()
        self.hide()
        
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    
def main():
    gamename = ''
    moduleName = ''
    modulePath = ''
    containerFile = ''
    
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    sys.excepthook = except_hook
    app = QApplication([])
    widget = QtWidgets.QStackedWidget()
    window = Window()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
