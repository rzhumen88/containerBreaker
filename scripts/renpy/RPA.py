#research by https://gist.github.com/dekarrin/36f1908aa794f92e50b46c58a604dee0
import os
import struct
import zlib
from pickle import loads, dumps

class Container:
    def __init__(self, fname):
        self.fname = fname
        self.version = ''
        self.tableOffset = ''
        self.key = ''
        self.description = ''
        with open(fname, 'rb') as self.header:
            self.header, self.description = self.header.read(50).decode('ANSI').split('\n')
            self.version, self.tableOffset, self.key = self.header.split(' ')
            self.tableOffsetText = self.tableOffset
            self.tableOffset = int(self.tableOffset, 16)
            self.keytext = self.key
            self.key = int(self.key, 16)
        print(f'Version: {self.version}\nTable Offset: {self.tableOffsetText}\nKey: {self.keytext}\nDescription: {self.description}')
        self.table = b''
        with open(fname, 'rb') as self.f:
            self.f.seek(self.tableOffset)
            self.index = loads(zlib.decompress(self.f.read()))
        
    def getTable(self):
        self.table = []
        print(type(self.index))
        for self.k in self.index.keys():
            if len(self.index[self.k][0]) == 2:
                self.index[self.k] = [ (self.offset ^ self.key, self.dlen ^ self.key) for self.offset, self.dlen in self.index[self.k] ]
                self.start = ''
            else:
                self.index[self.k] = [ (self.offset ^ self.key, self.dlen ^ self.key, self.start) for self.offset, self.dlen, self.start in self.index[self.k] ]
            #print(f'{self.k}:   {self.index[self.k]}')
            self.table.append((self.k, self.index[self.k][0][0], self.index[self.k][0][1], self.index[self.k][0][1], self.start))
        return self.table

    def getFile(self, fn, o, s, cs, a):
        with open(self.fname, 'rb') as self.f:
            self.f.seek(o)
            return self.f.read(s)

    def buildContainer(self, iterator, path):
        self.iter = iterator
        self.path = path
        self.header = b"RPA-3.0 "
        self.files = []
        self.i = 51
        self.index = {}
        for self.file in self.iter:
            self.fn, self.stream, self.csize, self.args = self.file
            self.index[self.fn] = [(self.i, len(self.stream), self.args)]
            self.i += len(self.stream)
            self.files.append(self.stream)
        self.index = zlib.compress(dumps(self.index, protocol=2))
        self.header += struct.pack('>Q', self.i).hex().encode('ANSI') + b' ' +  b'0'*8 + b"\x0aMade with Ren'Py."
        with open(self.path, 'wb') as self.f:
            self.f.write(self.header)
            for self.file in self.files:
                self.f.write(self.file)
            self.f.write(self.index)
            
