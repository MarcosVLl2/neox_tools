import ctypes, zlib, zstandard, lz4.block, zipfile, os

def decompression_algorithm(zflag=0):
    match zflag:
        case 0:
            return "NONE"
        case 1:
            return "ZLIB"
        case 2:
            return "LZ4"
        case 3:
            return "ZSTANDARD"
        case 5:
            return "ZSTANDARD - NOT WORKING??"
    raise Exception("ERROR IN DECOMPRESSON ALGORITHM")

def init_rotor():
    asdf_dn = 'j2h56ogodh3se'
    asdf_dt = '=dziaq.'
    asdf_df = '|os=5v7!"-234'
    asdf_tm = asdf_dn * 4 + (asdf_dt + asdf_dn + asdf_df) * 5 + '!' + '#' + asdf_dt * 7 + asdf_df * 2 + '*' + '&' + "'"
    import rotor
    rot = rotor.newrotor(asdf_tm)
    return rot

def _reverse_string(s):
    l = list(s)
    l = list(map(lambda x: x ^ 154, l[0:128])) + l[128:]
    l.reverse()
    return bytes(l)

def nxs_unpack(data):
    wrapped_key = ctypes.create_string_buffer(4)
    data_in = ctypes.create_string_buffer(data[20:])

    if os.name == "posix":
        liblinux = ctypes.CDLL("./dll/libpubdecrypt.so")
        returning = liblinux.public_decrypt(data_in, wrapped_key)
    elif os.name == "nt":
        libwindows = ctypes.CDLL("./dll/libpubdecrypt.dll")
        returning = libwindows.public_decrypt(data_in, wrapped_key)


    ephemeral_key = int.from_bytes(wrapped_key.raw, "little")

    decrypted = []

    for i, x in enumerate(data[20 + 128:]):
        val = x ^ ((ephemeral_key >> (i % 4 * 8)) & 0xff)
        if i % 4 == 3:
            ror = (ephemeral_key >> 19) | ((ephemeral_key << (32 - 19)) & 0xFFFFFFFF)
            ephemeral_key = (ror + ((ror << 2) & 0xFFFFFFFF) + 0xE6546B64) & 0xFFFFFFFF
        decrypted.append(val)

    decrypted = bytes(decrypted)
    return decrypted

def zflag_decompress(flag, data, origlength=0):
    match flag:
        case 1:
            return zlib.decompress(data, bufsize=origlength)
        case 2:
            return lz4.block.decompress(data,uncompressed_size=0x0FFFFFFE)
        case 3:
            return zstandard.ZstdDecompressor().decompress(data)
        case 5:
            return data
    return data

def special_decompress(flag, data):
    match flag:
        case "rot":
            rotor = init_rotor()
            return _reverse_string(zlib.decompress(rotor.decrypt(data)))
            
        case "nxs3":
            buf = nxs_unpack(data)
            return lz4.block.decompress(buf, int.from_bytes(data[16:20], "little"))
    return data
            
    
