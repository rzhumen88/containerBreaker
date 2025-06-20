import os
import struct

class Container:
    def __init__(self, fname):
        self.header=b'AKPK'
        self.headerlen = 0x30
        self.statics = (1, 0x14, 4)
        self.statics1 = (4, 1, 0xc, 0)
        self.statics2 = (b'\x73\x00\x66\x00\x78\x00\x00\x00\x00\x00\x00\x00')
        self.total = 0
        self.tableoffset = 8
        self.container = fname

    def strFromHash(self, hash_) -> str:
        return hash_[::-1].hex().zfill(8).upper()
    
    def bytesFromStrHash(self, s) -> bytes:
        return struct.pack('I', int(s, 16))
    
    def getTable(self):
            self.table = {}
            with open(self.container, 'rb') as self.f:
                if self.f.read(4) != self.header:
                    raise ValueError('Wrong header, parsing terminated!')
                self.tableoffset += struct.unpack('I', self.f.read(4))[0]
                self.f.read(44)
                self.total = struct.unpack('I', self.f.read(4))[0]
                for self.i in range(self.total):
                    self.hash = self.f.read(4)
                    self.bitDepth, self.size, self.offset, _= struct.unpack('IIII', self.f.read(16))
                    self.name = self.strFromHash(self.hash) + '.wem' #use foobar to open if
                    self.table[self.i] = (self.name, self.offset*0x10, self.size, self.size, f'bit depth={self.bitDepth}')
            return self.table

    def getFile(self, fname, offset, size, csize, args):
        with open(self.container, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(size)

    def buildContainer(self, iterator, saveDir):
        self.headerdata = [self.header, ]
        self.indextable = []
        self.files = []
        self.headerlen = 56
        self.i = 0
        with open(saveDir, 'wb') as self.f2:
            for self.iter in iterator:
                self.fname, self.stream, _, self.args = self.iter
                self.fname = self.bytesFromStrHash(self.fname.lstrip('/').rstrip('.wem'))
                try:
                    _, self.bitDepth = self.args.split('=')
                except: raise ValueError(f'Args error at {self.fname}: {self.args}')
                self.bitDepth = struct.pack('I', int(self.bitDepth))
                while len(self.stream) % 16 != 0:
                    self.stream += b'\x00'
                self.indextable.append((self.fname, self.bitDepth, len(self.stream), self.i, 0))
                self.i += len(self.stream)
                self.files.append(self.stream)
            self.filesoffset = self.headerlen+(len(self.files)*20)  #unsure about that
            self.headerdata.append(struct.pack('I', self.filesoffset-4))
            self.headerdata.append(b'\x01\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00')
            self.headerdata.append(struct.pack('I', self.filesoffset-52))
            self.headerdata.append(b'\x04\x00\x00\x00\x01\x00\x00\x00\x0C\x00\x00\x00\x00\x00\x00\x00s\x00f\x00x\x00\x00\x00\x00\x00\x00\x00')
            self.headerdata.append(struct.pack('I', len(self.files)))
            self.paddingindex = b''
            while self.filesoffset % 16 != 0:
                    self.paddingindex += b'\x00'
                    self.filesoffset += 1
            for self.i in self.headerdata:
                self.f2.write(self.i)
            for self.i in self.indextable:
                self.fname, self.bitDepth, self.size, self.offset, self.padding = self.i
                self.offset = (self.offset + self.headerlen + (len(self.files)*20) + len(self.paddingindex))//16#(self.offset // 16) + self.headerlen  + (len(self.files)*20) + len(self.paddingindex)
                self.f2.write(self.fname)
                self.f2.write(self.bitDepth)
                self.f2.write(struct.pack('I', self.size))
                self.f2.write(struct.pack('I', self.offset))
                self.f2.write(struct.pack('I', self.padding))
            self.f2.write(self.paddingindex)
            for self.i in self.files:
                self.f2.write(self.i)
            self.files = None
                               
            
                
                
                
            
        
                
            
