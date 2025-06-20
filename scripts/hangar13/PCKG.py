import os
import struct

class Container:
    def __init__(self, fname):
        self.header=b'PCKG'
        self.fname = fname
        with open(fname, 'rb') as self.f:
            if not self.f.read(4) == self.header:
                raise ValueError('Wrong header! Execution terminated!')
            self.ver, self.total, _ = struct.unpack('III', self.f.read(12))
            print(f'File: {self.fname}\nVersion: {self.ver}\nTotal Files: {self.total}')
            self.filetable = self.f.read(self.total*32)

    def strFromHash(self, hash_) -> str:
        return hash_[::-1].hex().zfill(8).upper()
    
    def bytesFromStrHash(self, s) -> bytes:
        return struct.pack('Q', int(s, 16))
    
    def getTable(self):
            self.table = {}
            self.id = 0
            for self.i in range(0, len(self.filetable), 32):
                self.hash = self.filetable[self.i:self.i+8]
                self.offset, _, self.size, _, self.h, self.w, _ = struct.unpack('IIIIHHI', self.filetable[self.i+8:self.i+32])
                self.hash = self.strFromHash(self.hash)+'.dds'
                self.table[self.id] = (self.hash, self.offset, self.size, self.size, f'{self.w}x{self.h}')
                #print((self.hash, self.offset, self.size, self.size, f'{self.w}x{self.h}'))
                self.id += 1
            return self.table

    def getFile(self, fname, offset, size, csize, args):
        with open(self.fname, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(size)

    def buildContainer(self, iterator, saveDir):
        self.headerdata = self.header + struct.pack('I', self.ver)
        self.indextable = []
        self.files = []
        self.i = 0
        with open(saveDir, 'wb') as self.f2:
            for self.iter in iterator:
                self.hash, self.stream, _, _ = self.iter
                self.hash = self.bytesFromStrHash(self.hash.lstrip('/').rstrip('.dds'))
                self.h, self.w = struct.unpack('II', self.stream[12:20])
                self.indextable.append((self.hash, self.i, len(self.stream), self.h, self.w))
                self.i += len(self.stream)
                self.files.append(self.stream)
            self.fileoffset = len(self.files)*32 + 16
            self.headerdata += struct.pack('I', len(self.files)) + b'\xff\xff\xff\xff'
            self.f2.write(self.headerdata)
            for self.file in self.indextable:
                self.hash, self.offset, self.size, self.h, self.w = self.file
                self.f2.write(self.hash)
                self.f2.write(struct.pack('I', self.offset+self.fileoffset))
                self.f2.write(struct.pack('I', 0))
                self.f2.write(struct.pack('I', self.size))
                self.f2.write(struct.pack('I', self.size))
                self.f2.write(struct.pack('H', self.h))
                self.f2.write(struct.pack('H', self.w))
                self.f2.write(struct.pack('I', 0))
            for self.file in self.files:
                self.f2.write(self.file)
                
                
                
                               
            
                
                
                
            
        
                
            
