def decryption_algorithm(flag):
    match flag:
        case 0:
            return "NONE"
        case 1:
            return "XOR_128"
        case 2:
            return "XOR_32_127_TYPE1"
        case 3:
            return "XOR_32_127_TYPE2"
        case 4:
            return "XOR_32_127_TYPE3"
    raise Exception("ERROR IN DECRYPTION ALGORITHM: VALUE {}".format(flag))

def file_decrypt(flag, data, key=0,crc=0,file_length=0,file_original_length=0):
    match flag:
        case 1:
            size = file_length

            if size > 0x80:
                size = 0x80

            key = [(key + x) & 0xFF for x in range(0, 0x100)]
            #key1: 150 + x   (Onmyoji, Onmyoji RPG)
            #key2:  -250 + x 
            data = bytearray(data)
            for j in range(size):
                data[j] = data[j] ^ key[j % 0xff]
            
        case 2:
            b = crc ^ file_original_length

            start = 0
            size = file_length

            if size > 0x80:
                start = (crc >> 1) % (file_length - 0x80)
                size = 2 * file_original_length % 0x60 + 0x20

            key = [(x + b) & 0xFF for x in range(0, 0x81)]
            for j in range(size):
                data[start + j] = data[start + j] ^ key[j % 0x80]
        case 3:
            b = crc ^ file_original_length

            start = 0
            size = file_length
            if size > 0x80:
                start = (crc >> 1) % (file_length - 0x80)
                size = 2 * file_original_length % 0x60 + 0x20
            
            key = [(x + b) & 0xFF for x in range(0, 0x81)]
            data = bytearray(data)
            for j in range(size):
                data[start + j] = data[start + j] ^ key[j % 0x80]
        case 4:
            v3 = int(file_original_length)
            v4 = int(crc)

            offset = 0
            length = 0                    

            if file_length < 0x80:
                length = file_length
            else:
                offset = (v3 >> 1) % (file_length - 0x80)
                length = (((v4 << 1) & 0xffffffff) % 0x60 + 0x20)

            key = (v3 ^ v4) & 0xff
            data = bytearray(data)

            for xx in range(offset, min(offset + length, file_original_length)):
                data[xx] ^= key
                key = (key + 1) & 0xff

    return data
