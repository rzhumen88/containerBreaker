import os
import struct

class Container:
    def __init__(self, fname):
        self.ext = fname[-3:].lower()
        self.filename = fname

    def getTable(self):
        self.table = nsaUnpack(self.filename)
        return self.table

    def getFile(self, fname, offset, size, csize, time):
        with open(self.filename, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(csize)

    def buildContainer(self, iterator, path):
        self.iter = iterator
        self.path = path
        self.files = []
        self.total = 0
        self.header = b''
        self.table = b''
        self.offset = 0
        for self.file in self.iter:
            self.files.append(self.file)
            self.total += 1
            self.table += self.file[0].replace('/', '\\').lstrip('\\').encode('ANSI') + b'\x00'
            match self.file[3]:
                case 'Unknown':
                    self.table += b'\x01'
                    self.table += struct.pack('>III', self.offset, len(self.file[1]), self.file[2])
                case 'Compressed':
                    self.table += b'\x02'
                    self.table += struct.pack('>III', self.offset, len(self.file[1]), self.file[2])
                case _:
                    self.table += b'\x00'
                    self.table += struct.pack('>III', self.offset, len(self.file[1]), len(self.file[1]))
            self.offset += len(self.file[1])
        self.header += struct.pack('>HI', self.total, 6+len(self.table))
        with open(self.path, 'wb') as self.f:
            self.f.write(self.header)
            self.f.write(self.table)
            for self.file_ in self.files:
                self.f.write(self.self.file_[1])
            
def strcpy(data: bytes, i: int):
    s = r""
    while data[i] != 0:
        s += chr(data[i])
        i += 1
    return s, i
    
def nsaUnpack(nsa):
    with open(nsa, "rb") as f:
        f = f.read()
        i = 6
        q, globalOffset = struct.unpack('>HI', f[:i])
        table = {}
        for num in range(q):
            name, j = strcpy(f, i)
            i = j
            _, sType, offset, size, decSize = struct.unpack('>BBIII', f[i:i+14])
            i += 14
            offset += globalOffset
            match sType:
                case 0:
                    """No compression"""
                    if size == decSize:
                        pass
                        #saveFile(path+name, f[offset:offset+size])
                        #print(f"[{num}/{q}] Extracted: {path+name} | Size: {round(size//1024,2)}kb")
                    else: pass #print(f'Sizes mismatch | {name}')
                    sType = 'Uncompressed'
                case 1:
                    """Unknown"""
                    print(f'Unknown storing type {sType} | {name}')
                    sType = 'Unknown'
                case 2:
                    """Compressed unpacks as is, looks like xored BZ2 compression"""
                    sType = 'Compressed'
                    #print(f"File {name} is compressed! Can't unpack!")
                    #saveFile(path+name, f[offset:offset+size])
            table[num] = (name.replace('\\', '/'), offset, size, decSize, sType)
    return table

