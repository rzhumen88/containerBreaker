import os
import struct

class Container:
    def __init__(self, fname):
        self.filename = fname

    def getTable(self):
        self.table = sarUnpack(self.filename)
        return self.table

    def getFile(self, fname, offset, size, csize, time):
        with open(self.filename, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(csize)
            
        
def strcpy(data: bytes, i: int):
    s = r""
    while data[i] != 0:
        s += chr(data[i])
        i += 1
    return s, i

def sarUnpack(sar):
    with open(sar, "rb") as f:
        f = f.read()
        table = {}
        q = int.from_bytes(f[:2])
        globalOffset = int.from_bytes(f[4:6])
        i = 6
        for num in range(q):
            name, j = strcpy(f, i)
            i = j + 1
            offset = int.from_bytes(f[i:i+4])
            length = int.from_bytes(f[i+4:i+8])
            i += 8
            table[num] = (name.replace('\\', '/'), globalOffset+offset, length, length, '-')
    return table
