import os
import struct

class Container:
    def __init__(self, fname):
        self.containerPath = fname
        with open(self.containerPath, 'rb') as self.f:
            self.HEADER, self.total = struct.unpack('12sI', self.f.read(0x10))
        if not self.HEADER == b'PackFile    ':
            raise ValueError(f'Not a Green Green pack file! Headers mismatch {self.HEADER:} != PackFile    ')
            
    def getTable(self):
        self.table = {}
        self.hdrlen = 0x20 * (self.total+1)
        with open(self.containerPath, 'rb') as self.f:
            self.f.seek(0x10)
            for self.id in range(self.total):
                self.fname = self.f.read(0x10).replace(b'\x00', b'').decode('ansi')
                self.offset, self.size, _, _ = struct.unpack('IIII', self.f.read(0x10))
                self.table[self.id] = (self.fname, self.offset+self.hdrlen, self.size, self.size, '-')
        return self.table

    def getFile(self, fname, offset, size, csize, args):
        with open(self.containerPath, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(size)

    def buildContainer(self, iterator, savePath):
        self.index = []
        self.files = []
        self.i = 0
        with open(savePath, 'wb') as self.f:
            self.f.write(b'PackFile    ')
            for self.iter in iterator:
                self.fname, self.bytes, _, _ = self.iter
                if len(self.fname) >  0x10:
                    raise ValueError(f'Filename {self.fname} is too long, max length is 16 characters!')
                self.fname = self.fname.encode('ansi') + b'\x00'*(0x10 - len(self.fname))
                self.index.append((self.fname, self.i, len(self.bytes)))
                self.i += len(self.bytes)
                self.files.append(self.bytes)
            self.f.write(struct.pack('I', len(self.files)))
            for self.file in self.index:
                self.f.write(self.file[0])
                self.f.write(struct.pack('I', self.file[1]))
                self.f.write(struct.pack('I', self.file[2]))
                self.f.write(b'\x00'*8)
            for self.file in self.files:
                self.f.write(self.file)
            
