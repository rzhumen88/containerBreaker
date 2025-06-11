import os
import struct

class Container:
    def __init__(self, fname):
        self.fname = fname
        self.CHUNK = 0x800

    def getTable(self):
        self.table = {}
        with open(self.fname, 'rb') as self.f:
            self.header, self.total = struct.unpack('4sI', self.f.read(8))
            if not self.header == b'VER2': raise ValueError('Wrong version of IMG file')
            for self.i in range(self.total):
                self.offset, self.size, self.filename = struct.unpack('II24s', self.f.read(0x20))
                if b'\x00' in self.filename:
                    self.filename = self.filename[:self.filename.index(b'\x00')]
                self.filename = self.filename.decode('ANSI')
                self.table[self.i] = (self.filename, self.offset*self.CHUNK, self.size*self.CHUNK, self.size*self.CHUNK, '-')
        return self.table
    
    def getFile(self, fname, offset, size, csize, time):
        with open(self.fname, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(size)
                
    def buildContainer(self, iterator, saveDir):
        self.iterator = iterator
        self.path = saveDir
        self.bytestream = b''
        self.total = 0
        self.tablelen = 8 #for VER2, total int32
        self.names = []
        self.sizes = []
        self.offsets = [0, ]
        self.i = 0 
        for self.file in self.iterator:
            if len(self.file[0]) > 24: raise ValueError(f'Filename {self.file[0]} is too long. Limit is 24 characters per file.')
            self.filename = self.file[0].lstrip('/')
            self.file = self.file[1]
            while len(self.file) % self.CHUNK != 0:
                self.file += b'\x00'
            self.bytestream += self.file
            self.i += len(self.file)
            self.offsets.append(self.i//self.CHUNK)
            self.sizes.append(struct.pack('I', len(self.file)//self.CHUNK))
            self.names.append(struct.pack('24s', self.filename.encode('ANSI')))
            self.total += 1
        self.offsets.pop(-1)
        self.padding = 0
        self.tablelen += self.total * 0x20
        while self.tablelen % self.CHUNK != 0:
                self.tablelen += 1
                self.padding += 1
        self.tablelen = self.tablelen // self.CHUNK
        with open(self.path, 'wb') as self.f:
            self.f.write(b'VER2')
            self.f.write(struct.pack('I', self.total))
            for self.i in range(self.total):
                self.f.write(struct.pack('I', self.offsets[self.i]+self.tablelen))
                self.f.write(self.sizes[self.i])
                self.f.write(self.names[self.i])
            self.f.write(b'\x00'*self.padding)
            self.f.write(self.bytestream)
            
            
        
