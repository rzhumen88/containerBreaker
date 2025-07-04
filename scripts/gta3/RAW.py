import os
import struct
import wave

class Container:
    def __init__(self, fname):
        self.std = fname[:-3]+'sdt'
        self.sfx = fname[:-3]+'raw'

    def getTable(self):
        self.table = {}
        with open(self.std, 'rb') as self.index:
            self.total = len(self.index.read())//20
            self.index.seek(0)
            for self.i in range(self.total):
                self.offset, self.size, self.samples, self.loopStart, self.loopEnd = struct.unpack('IIIii', self.index.read(20))
                self.sfxname = 'sfx'+str(self.i).zfill(8)+'.wav'
                self.table[self.i] = (self.sfxname, self.offset, self.size, self.size, ':'.join([str(self.samples),str(self.loopStart),str(self.loopEnd)]))
        return self.table

    def getFile(self, fname, offset, size, csize, args):
        with open(self.sfx, 'rb') as self.f:
            self.f.seek(offset)
            self.samples, _, _ = args.split(':')
            self.wav = b"RIFF" + struct.pack('I', size+36) + b"WAVEfmt " + struct.pack('IHHIIHH', 16, 1, 1, int(self.samples), int(self.samples)*2, 2, 16) + b'data' + struct.pack('I', size)
            return self.wav+self.f.read(size)
        
    def buildContainer(self, iterator, saveDir):
        self.iterator = iterator
        self.saveDir = saveDir
        self.offset = 0
        pass
