import os
import struct
import zlib
import numpy as np

from g2aes import * #gulman 2 aes encryption

class Container:
    def __init__(self, fname):
        self.g2pack = G2Pack('g2')
        self.g2pack.read(fname)

    def getTable(self):
        self.table = {}
        self.i = 0
        for self.file in self.g2pack.files:
            self.fname, self.foffset, self.fsize, self.fsizeunc = self.g2pack.files[self.file]
            self.table[self.i] = (self.fname, self.foffset+4, self.fsizeunc, self.fsize-4, self.fname)
            self.i += 1
        return self.table
    
    def getFile(self, fname, offset, size, csize, args):
        print(f'Decrypting: {fname}')
        print(f'Key: {args}')
        print(self.g2pack.getRaw(offset, csize))
        self.aes = createEncryptionTable(args)
        self.raw = self.g2pack.getRaw(offset, csize)
        return zlib.decompress(decrypt(self.raw, self.aes)[0])
        
                
    def buildContainer(self, iterator, saveDir):
        self.files = []
        self.indextbl = []
        self.i = 12
        with open(saveDir, 'wb') as self.f:
            self.f.write(b'PACK')            
            for self.file in iterator:
                self.rawSize = len(self.file[1])
                self.compressed = zlib.compress(self.file[1])
                self.aes = createEncryptionTable(self.file[3])
                self.fname = self.file[3]
                _, self.obfusKey = decrypt(self.compressed, self.aes)
                self.obfuscated = []
                for self.b in range(len(self.compressed)):
                    self.obfuscated.append(struct.pack('B', self.compressed[self.b] ^  self.obfusKey[self.b]))
                self.obfuscated = b''.join(self.obfuscated) #more optimized
                self.file = struct.pack('I', self.rawSize) + self.obfuscated
                self.files.append(self.file)
                self.index = struct.pack('248s', self.fname.encode('cp1251')) + struct.pack('I', self.i) + struct.pack('I', self.i + len(self.file))
                self.indextbl.append(self.index)
                self.i += len(self.file)
            self.f.write(struct.pack('I', self.i))
            self.f.write(struct.pack('I', len(self.files)<<8))
            for self.file in self.files:
                self.f.write(self.file)
            for self.index in self.indextbl:
                self.f.write(self.index)
    
class G2Pack:
    def __init__(self, game):
        """creating blank file"""
        self.game = game
        self.HEADER = b''
        self.fstruct_ptr = 0
        self.totalFiles = 0
        self.files = {}

    def getRaw(self, offset:int, size:int):
        with open(self.pak, 'rb') as self.f:
            self.f.seek(offset)
            return self.f.read(size)
        
    def read(self, pak: str):
        """reading data from file into structured data"""
        self.pak = pak
        self.i = 0
        with open(self.pak, 'rb') as self.f:
            self.header = self.f.read(12)
            self.HEADER = self.header[:4]
            if self.HEADER == b'2PAK':
                self.game = 'g3'
            if self.HEADER not in (b'PACK', b'2PAK'):
                raise ValueError('Not a Gulman 2 pack file!')
            self.fstruct_ptr = struct.unpack('I', self.header[4:8])[0]
            if self.game == 'sw':
                self.totalFiles = struct.unpack('I', self.header[8:12])[0] // 64 # swiborg
            elif self.game == 'g2':
                self.totalFiles = struct.unpack('I', self.header[9:13]+b'\x00')[0]
            elif self.game == 'g3':
                self.f.seek(0)
                _, self.fstruct_ptr, _, self.totalFiles = struct.unpack('IIII', self.f.read(16))
            self.header = b''
            self.totalFiles = self.totalFiles >> 8
            print(self.totalFiles)
            for self.i in range(self.totalFiles):
                self.f.seek(self.fstruct_ptr)
                self.fstruct = self.f.read()
                if self.game == 'sw':
                    self.fname = self.fstruct[0x40*self.i:0x40*self.i+0x38]    # swiborg
                    self.foffset = struct.unpack('I', self.fstruct[0x40*self.i+0x38:0x40*self.i+0x3c])[0]
                    self.fsize = struct.unpack('I', self.fstruct[0x40*self.i+0x3c:0x40*self.i+0x40])[0]
                elif self.game == 'g2':
                    self.fname = self.fstruct[0x100*self.i:0x100*self.i+0xf8]
                    self.foffset = struct.unpack('I', self.fstruct[0x100*self.i+0xf8:0x100*self.i+0xfc])[0]
                    self.fsize = struct.unpack('I', self.fstruct[0x100*self.i+0xfc:0x100*self.i+0x100])[0]
                elif self.game == 'g3':
                    self.fname = self.fstruct[0x100*self.i:0x100*self.i+0xf0]
                    self.foffset, _, self.fsize, _ = struct.unpack('IIII', self.fstruct[0x100*self.i+0xf0:0x100*self.i+0x100])
                self.fname = self.fname.replace(b'\x00', b'').decode('cp1251')
                self.f.seek(self.foffset)
                self.fsizeunc = struct.unpack('Q', self.f.read(8))[0]
                if self.game == 'g3':
                    self.files[self.i] = (self.fname, self.foffset+4, self.fsize-4, self.fsizeunc)
                else:
                    self.files[self.i] = (self.fname, self.foffset, self.fsize, self.fsizeunc)
                #print((self.fname, self.foffset, self.fsize))

    def unpack(self, d: str):
        """unpacks pack file to the given directory"""
        self.d = d
        if not os.path.isdir(self.d):
            os.mkdir(self.d)
        for self.file in self.files:
            self.fname, self.foffset, self.size = self.files[self.file]
            self.enc = createEncryptionTable(self.fname)
            with open(self.pak, 'rb') as self.f:
                self.f.seek(self.foffset)
                self.decSize = struct.unpack('Q', self.f.read(8))[0]
                self.f.seek(self.foffset+4)
                self.f = self.f.read(self.size)
                self.dec, _ = decrypt(self.f, self.enc)
                self.f = zlib.decompress(self.dec)
                if len(self.f) != self.decSize:
                    print(f'Size mismatch: In pack: {self.decSize} Out data: {len(self.f)}')
                self.unpackPath = self.d+'/'+self.fname
                createFolders(self.unpackPath)
                with open(self.unpackPath, 'wb') as self.f2:
                    self.f2.write(self.f)
                    print(f'Extracted: {self.unpackPath}')

    def pack(self, d: str):
        """packs directory into a pak file"""
        self.d = d
        if not os.path.isdir(d):
            raise ValueError(f'{d} does not exist!')
        self.HEADER = b'PACK'
        with open(self.d+'.pak', 'wb') as pak:
            self.buffer = b''
            self.fnum = 0
            self.i = 12
            self.filesdict = {}
            for self.address, _, self.files in os.walk(d):
                for self.name in self.files:
                    self.path = os.path.join(self.address, self.name)
                    with open(self.path, 'rb') as self.f:
                        self.f = self.f.read()
                        self.uncSize = len(self.f)
                        self.f = zlib.compress(self.f)
                        self.enc = createEncryptionTable(self.path)
                        _, self.key = decrypt(self.f, self.enc)
                        self.encrypted = np.zeros(len(self.f), dtype=np.uint8)
                        for self.j in range(len(self.f)):
                            self.encrypted[self.j] = self.f[self.j] ^ self.key[self.j]
                        self.f = self.encrypted.tobytes()
                        self.filesdict[self.fnum] = (self.path, self.i, len(self.f)+4)
                        self.buffer += struct.pack('Q', self.uncSize)
                        self.buffer += self.f
                        self.i += len(self.f)+8
                        self.fnum += 1
                        print(f'[{self.fnum}] {self.path} imported!')
            self.fstruct_ptr = self.i
            self.totalFiles = self.fnum
            pak.write(self.HEADER)
            pak.write(struct.pack('I', self.fstruct_ptr))
            if self.game == 'sw':
                pak.write(struct.pack('I', self.totalFiles*64))
            elif self.game == 'g2':
                pak.write(struct.pack('I', self.totalFiles<<8))
            pak.write(self.buffer)
            self.buffer = b''
            for self.i in range(self.totalFiles):
                self.pathb = self.filesdict[self.i][0].replace(self.d, '').encode('cp1251').replace(b'\x5c', b'/')[1:]
                if self.game == 'sw':
                    self.pathb = self.pathb+(b'\x00'*(56 - len(self.pathb)))
                elif self.game == 'g2':
                    self.pathb = self.pathb+(b'\x00'*(248 - len(self.pathb)))
                pak.write(self.pathb)
                pak.write(struct.pack('II', self.filesdict[self.i][1], self.filesdict[self.i][2]))

def export(game):
    fname = ''
    while not os.path.isfile(fname):
        print('Welcome to DeGulman2, this script will unpack files from .pak archives.')
        fname = input('Provide path to your .pak file:  ')
    directory = fname.replace('.pak', '')
    createFolders(directory)
    g2pack = G2Pack(game)
    g2pack.read(fname)
    g2pack.unpack(directory)
    input('Done!')

def import_(game):
    g2pack = G2Pack(game)
    d = ''
    while not os.path.isdir(d):
        print('Welcome to DeGulman2, this script will pack files directory.')
        d = input('Provide path to your directory:  ')
    g2pack.pack(d)
    input('Done!')
