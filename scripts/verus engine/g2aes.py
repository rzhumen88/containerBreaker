#gulman aes encrypting
import struct
import zlib
import numpy as np

def createEncryptionTable(fname: str):
    encryptionKey = []
    fname = fname.encode('cp1251')
    for c in fname:
        n1 =  c & 0xF
        n1 = n1 << 4
        n2 =  c >> 4
        c = (n1 + n2) ^ 0xFF
        encryptionKey.append(c)
    keyLen = len(encryptionKey)
    encryptedBlock = []
    j = 0
    prevValue = 0
    for i in range(0, 0x100):
        if j == keyLen:
            j = 0
        encryptionValue = encryptionKey[j]
        encryptionValue = encryptionValue & 0xFF
        if encryptionValue >> 7 == 1:
            encryptionValue = encryptionValue - encryptionValue*2
        encryptedBlock.append(encryptionValue)
        prevValue = encryptionValue
        j += 1
    encryptedBlock2 = list(range(0x100))
    prev = 0
    for i in range(0, 0x100):
        index = encryptedBlock2[i]
        value = encryptedBlock[i]
        value = abs(value) + index + prev & 0xff
        prev = value
        encryptedBlock2[i] = encryptedBlock2[value]
        encryptedBlock2[value] = index
    return encryptedBlock2

def decrypt(stream: bytes, table: list):
    size = len(stream)
    decrypted = np.zeros(size, dtype=np.uint8)
    key = np.zeros(size, dtype=np.uint8)
    i = 0
    j = 0
    value2 = 0
    while j < size:
        i += 1
        i = i & 0xff 
        value = table[i] 
        value2 += value
        value2 = value2 & 0xff
        value3 = table[value2]
        table[i] = value3
        table[value2] = value
        value = table[i] + table[value2]
        value = value & 0xff
        value = table[value]
        decrypted[j] = stream[j] ^ value
        key[j] = value
        j += 1
    return decrypted.tobytes(), key.tobytes()
