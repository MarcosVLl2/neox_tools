def decryption_algorithm(flag):
    match flag:
        case 0:
            return "NONE"
        case 3:
            return "CRCTYPE1"
        case 4:
            return "CRCTYPE2"
    raise Exception("ERROR IN DECRYPTION ALGORITHM")

def file_decrypt(flag, data, crc=0,file_length=0,file_original_length=0):
    match flag:
        case 3:
            b = crc ^ file_original_length

            start = 0
            size = file_length
            if size > 0x80:
                start = (crc >> 1) % (file_length - 0x80)
                size = 2 * file_original_length % 0x60 + 0x20
            
            key = [(x + b) & 0xFF for x in range(0, 0x100)]
            data = bytearray(data)
            for j in range(size):
                data[start + j] = data[start + j] ^ key[j % len(key)]
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
