import os
import struct

class Container:
    def __init__(self, fname):
        self.CHUNK = 0x800
        self.fname = fname
        self.f = None

    def getTable(self):
        self.table = {}
        self.i = 0
        with open(self.fname, 'rb') as self.f:
            while True:
                self.offset, self.size = struct.unpack('II', self.f.read(8))
                self.size -= self.offset
                self.bin = str(self.i).zfill(8)+'.bin'
                if self.offset < 1:
                    break
                else:
                    self.table[self.i] = (self.bin, self.offset, self.size, self.size, '-')
                    self.i += 1
            return self.table
    
    def getFile(self, fname, offset, size, csize, time):
        with open(self.fname, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(size)
                
    def buildContainer(self, iterator, saveDir):
        self.i = self.CHUNK
        self.j = 0
        self.files = []
        with open(saveDir, 'wb') as self.new:
            for self.file in iterator:
                self.stream  = self.file[1]
                while len(self.stream) % self.CHUNK != 0:
                    self.stream += b'\x00'
                self.files.append(self.stream)
                self.new.write(struct.pack('I', self.i))
                self.i += len(self.stream)
                self.new.write(struct.pack('I', self.i))
                self.j += 8
            if self.j > self.CHUNK: raise ValueError('Max size: 512 files')
            self.new.write(b'\x00'*(self.CHUNK-self.j))
            for self.file in self.files:
                self.new.write(self.file)

        
