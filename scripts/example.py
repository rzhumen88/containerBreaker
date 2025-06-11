'''
class Container:
    def __init__(self, fname):
        #init

    def getTable(self):
        #return dictionary with id:int - (filename, offset, size, compressed size, args):tuple
    
    def getFile(self, fname, offset, size, csize, time):
        #return file:bytes
                
    def buildContainer(self, iterator, saveDir):
        #iterate the table and save it to file
        #iterator = (filename, filebytes, compressed size, args)
            
''' 
        
