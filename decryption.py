#returns the type of decryption algorithm based on the file_flag index parameter
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

#does the decryption algorithm
def file_decrypt(flag, data, key=None,crc=0,file_length=0,file_original_length=0):
    match flag:
        case 1:
            if key == None:
                Exception("KEY FOR FILEFLAG 1 NOT SPECIFIED (check keys.txt)")

            size = file_length

            if size > 0x80:
                size = 0x80

            key = [(key + x) & 0xFF for x in range(0, 0x100)]
            #these keys are for different games, check the "keys.txt" file for more information
            #key1: 150 + x   (Onmyoji, Onmyoji RPG)
            #key2:  -250 + x (HPMA)
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

            key = [(x + b) & 0xFF for x in range(0, 0x81, 1)]
            for j in range(size):
                data[start + j] = data[start + j] ^ key[j % 0x80]
        case 3:
            b = crc ^ file_original_length

            start = 0
            size = file_length
            if size > 0x80:
                start = (crc >> 1) % (file_length - 0x80)
                size = 2 * file_original_length % 0x60 + 0x20
            
            key = [(x + b) & 0xFF for x in range(0, 0x81, 1)]
            data = bytearray(data)
            for j in range(size):
                data[start + j] = data[start + j] ^ key[j % 0x80]
        case 4:
            v3 = int(file_original_length)
            v4 = int(crc)

            crckey = (v3 ^ v4) & 0xff
            offset = 0
            length = 0

            if file_length <= 0x80:
                length = file_length
            elif file_length > 0x80:
                offset = (v3 >> 1) % (file_length - 0x80)
                length = (((v4 << 1) & 0xffffffff) % 0x60 + 0x20)


            data = bytearray(data)

            for xx in range(offset, offset + length, 1):
                data[xx] ^= crckey
                crckey = (crckey + 1) & 0xff

    return data
