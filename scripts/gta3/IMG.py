import os
import struct

class Container:
    def __init__(self, fname):
        self.dir = fname[:-3]+'dir'
        self.img = fname[:-3]+'img'
        self.CHUNK = 0x800

    def getTable(self):
        self.table = {}
        self.i = 0
        with open(self.dir, 'rb') as self.dirfile:
            self.dirfile = self.dirfile.read()
            for self.data in range(0, len(self.dirfile), 32):
                self.offset, self.size, self.fname = struct.unpack('II24s', self.dirfile[self.data:self.data+32])
                if b'\x00' in self.fname:
                    self.fname = self.fname[:self.fname.index(b'\x00')]
                self.table[self.i] = (self.fname.decode('ANSI'), self.offset*self.CHUNK, self.size*self.CHUNK, self.size*self.CHUNK, '-')
                self.i += 1
        return self.table

    def getFile(self, fname, offset, size, csize, args):
        with open(self.img, 'rb') as self.imgfile:
            self.imgfile.seek(offset)
            return self.imgfile.read(size)
        
    def buildContainer(self, iterator, saveDir):
        self.iterator = iterator
        self.saveDir = saveDir
        self.offset = 0
        with open(self.saveDir[:-3]+'dir', 'wb') as self.newdir:
            with open(self.saveDir[:-3]+'img', 'wb') as self.newimg:
                for self.file in self.iterator:
                    self.fname, self.bytes, self.csize, self.args = self.file
                    while len(self.bytes) % self.CHUNK != 0:
                        self.bytes+=b'\x00'
                    self.newimg.write(self.bytes)
                    self.index = struct.pack('II24s', self.offset//self.CHUNK, len(self.bytes)//self.CHUNK, self.fname.lstrip('/').encode())
                    self.offset += len(self.bytes)
                    self.newdir.write(self.index)
            