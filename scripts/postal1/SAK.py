import os
import struct

class PostalSAK():
    '''Working with Postal 1 SAK files'''
    
    def __init__(self):
        self.is_closed = True
        self.i = 0
        self.version = 1
        self.total_files = 0
        self.offsets = []
        self.names = []
        self.files = []

    def __len__(self):
        return self.total_files

    def open(self, sak: str):
        '''Opens and reads file'''
        self.is_closed = False
        self.sak = sak
        self.fname = sak
        with open(self.sak, 'rb') as self.sak:
            self.sak = self.sak.read()
            if self.sak[:4] != b'SAK ':
                raise Exception('Wrong header given')
            self.version = struct.unpack('<I', self.sak[4:8])[0]
            if self.version != 1:
                print(f'Warning: Weird SAK version ({self.version})')
            self.total_files = struct.unpack('<H', self.sak[8:10])[0]
            self.i = 10
            for file in range(self.total_files):
                self.file_name = ''
                while self.sak[self.i] != 0:
                    self.file_name += chr(self.sak[self.i])
                    self.i += 1
                self.i += 1
                self.offsets.append(struct.unpack('<I', self.sak[self.i:self.i+4])[0])
                self.names.append(self.file_name)
                self.i += 4
            self.offsets.append(len(self.sak))
            self.i = 0
            for self.file in range(self.total_files):
                self.files.append(self.sak[self.offsets[self.i] : self.offsets[self.i+1]])
                self.i += 1
            self.sak = None

    def save(self, path: str):
        '''Builds SAK file'''
        if self.is_closed: raise Exception('File is closed')
        self.path = path
        if '/' in self.path:
            self.dir = self.path.split('/')
            self.dir = ''.join(self.dir[:-1])
            if not os.path.isdir(self.dir):
                os.mkdir(self.dir)
        self.tblsize = 10
        for self.file in self.names:
            self.tblsize = self.tblsize + len(self.file) + 5
        self.i = self.tblsize
        self.offsets = [self.i, ]
        for self.file in self.files:
            self.i += len(self.file)
            self.offsets.append(self.i)
        with open(self.path, 'wb') as self.f:
            '''Packing header'''
            self.f.write(struct.pack('@4sIH', b'SAK ', self.version, self.total_files))
            '''Packing table'''
            for self.i in range(0, self.total_files):
                self.f.write(self.names[self.i].encode(encoding='ascii'))
                self.f.write(b'\x00')
                self.f.write(struct.pack('<I', self.offsets[self.i]))
            '''Packing files'''
            for self.file in self.files:
                self.f.write(self.file)

    def extract(self, path: str):
        '''Extracts all files from archive'''
        if self.is_closed: raise Exception('File is closed')
        self.path = path
        self.i = 0
        if not os.path.isdir(self.path): os.mkdir(self.path)
        for self.file in self.names:
            self.dir = ''
            if '/' in self.file:
                self.dir = self.file.split('/')
                self.file = self.dir[-1]
                self.dir = '/'.join(self.dir[:-1])
                if not os.path.isdir(self.path+self.dir):
                    os.mkdir(self.path+self.dir)
            with open(self.path+self.dir+'/'+self.file, 'wb') as self.file:
                self.file.write(self.files[self.i])
                self.i += 1

    def close(self):
        '''Closes file'''
        self.is_closed = True
        self.i = 0
        self.version = 1
        self.total_files = 0
        self.offsets = []
        self.names = []
        self.files = []

    def get_name(self, id_: int):
        if not self.is_closed:
            self.id = id_
            return self.names[self.id]

    def get_names(self):
        if not self.is_closed:
            return self.names

    def set_name(self, id_: int, name: str):
        if not self.is_closed:
            self.id = id_
            self.name = name
            self.names[self.id] = self.name
            
    def set_names(self, names: list):
        if not self.is_closed: self.names = names

    def get_offset(self, id_: int):
        if not self.is_closed:
            self.id = id_
            return self.offsets[self.id]

    def get_offsets(self):
        if not self.is_closed:
            return self.offsets

    def get_file(self, id_: int):
        if not self.is_closed:
            self.id = id_
            return self.files[self.id]

    def get_files(self):
        if not self.is_closed: return self.files

    def set_file(self, id_, bytearr: bytes):
        if not self.is_closed:
            self.id = id_
            self.bytearr = bytearr
            self.files[self.id] = self.bytearr

    def set_files(self, files: list):
        if not self.is_closed: self.files = files
        
    def get_version(self):
         if not self.is_closed: return self.version

    def set_version(self, ver: int):
        if not self.is_closed: self.version = ver

    def get_raw(self, offset: int, size: int):
        if not self.is_closed:
            with open(self.fname, 'rb') as self.sak:
                self.sak.seek(offset)
                return self.sak.read(size)

    def saveFromGenerator(self, generator, saveDir):
        '''Builds SAK file'''
        self.tblsize = 10
        self.names = []
        for self.file in generator:
            self.tblsize = self.tblsize + len(self.file[0]) + 5
            self.names.append(self.file[0])
            self.files.append(self.file[1])
        self.i = self.tblsize
        self.offsets = [self.i, ]
        for self.file in self.files:
            self.i += len(self.file)
            self.offsets.append(self.i)
        with open(saveDir, 'wb') as self.f:
            '''Packing header'''
            self.f.write(struct.pack('@4sIH', b'SAK ', self.version, self.total_files))
            '''Packing table'''
            for self.i in range(len(self.names)):
                self.f.write(self.names[self.i].encode(encoding='ascii'))
                self.f.write(b'\x00')
                self.f.write(struct.pack('I', self.offsets[self.i]))
            '''Packing files'''
            for self.file in self.files:
                self.f.write(self.file)


class Container():
    def __init__(self, fname):
        #you get filename, do initial operations
        self.sak = PostalSAK()
        self.sak.open(fname)
        
    def getTable(self):
        #you return (filename, offset, size, compressed size, time)
        self.table = {}
        self.offsets = self.sak.get_offsets()
        self.sizes = []
        for self.i in range(len(self.sak)):
            self.table[self.i] = (self.sak.get_name(self.i), self.sak.get_offset(self.i), len(self.sak.get_file(self.i)), len(self.sak.get_file(self.i)), '-')
        return self.table
    
    def getFile(self, fname, offset, size, csize, time):
        #you get filename, offset, size, compressed size, time
        #you return file raw bytes
        return self.sak.get_raw(offset, size)

    def buildContainer(self, iterator, saveDir):
        self.version = 1
        self.iterator = iterator
        self.saveDir = saveDir
        self.tblsize = 10
        self.total = 0
        self.names = []
        self.filestream = b''
        self.i = 0
        self.offsets = [self.i, ]
        for self.file in self.iterator:
            self.total += 1
            self.tblsize += len(self.file[0]) + 5
            self.names.append(self.file[0])
            self.filestream += self.file[1]
            self.i += len(self.file[1])
            self.offsets.append(self.i)
        with open(self.saveDir, 'wb') as self.f:
            self.f.write(struct.pack('@4sIH', b'SAK ', self.version, self.total))
            for self.i in range(self.total):
                self.f.write(self.names[self.i].encode(encoding='ascii'))
                self.f.write(b'\x00')
                self.f.write(struct.pack('I', self.offsets[self.i]+self.tblsize))
            self.f.write(self.filestream)
            
            

#if __name__ == '__main__':
    #sak = PostalSAK()
    #sak.open('22050_16.sak')
    #sak.set_name(0, 'example.wav')
    #sak.save('22050_161.sak')
    #sak.extract('22050_161/')
    #extract_sak('22050_16.sak', '22050_16/')
