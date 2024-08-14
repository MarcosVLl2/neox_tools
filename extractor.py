import shutil, mmh3
import os, struct, zlib, tempfile, argparse, zstandard, lz4.block, zipfile
import rotor, time
from key import Keys


def readuint64(f):
    return struct.unpack('Q', f.read(8))[0]
def readuint32(f):
    return struct.unpack('I', f.read(4))[0]
def readuint16(f):
    return struct.unpack('H', f.read(2))[0]
def readuint8(f):
    return struct.unpack('B', f.read(1))[0]

def print_data(verblevel, text, data, typeofdata, pointer=0):
    match verblevel:
        case 1:
            if typeofdata == "NXPK":
                print("{} {}".format(text, data))
        case 2:
            if typeofdata != "VERBOSE_FILE" and typeofdata != "FILE":
                print("{} {}".format(text, data))
        case 3:
            if typeofdata != "VERBOSE_FILE":
                print("{:10} {} {}".format(pointer, text, data))
        case 4:
            print("{:10} {} {}".format(pointer, text, data))
        case 5:
            print("{:10} {} {}   DATA TYPE:{}".format(pointer, text, data, typeofdata))

def get_compression(data):
    if len(data) == 0:
        return 'none'
    elif data[:2] == bytes([0x1D, 0x04]) or data[:2] == bytes([0x15, 0x23]):
        return 'rot'
    elif data[0:8] == b"NXS3\x03\x00\x00\x01":
        return 'nxs3'
    elif data[:4] == bytes([0x50, 0x4B, 0x03, 0x04]) or data[:4] == bytes([0x50, 0x4B, 0x05, 0x06]):
        return 'zip'
    return 'none'

def get_ext(data):
    if len(data) == 0:
        return 'none'
    elif data[:12] == b'CocosStudio-UI':
        return 'coc'
    elif data[:8] == b'SKELETON':
        return 'skeleton'
    elif data[:3] == b'hit':
        return 'hit'
    elif data[:3] == b'PKM':
        return 'pkm'
    elif data[:3] == b'PVR':
        return 'pvr'
    elif data[:3] == b'DDS':
        return 'dds'
    elif data[-18:-2] == b'TRUEVISION-XFILE' or data[:3] == bytes([0x00, 0x00, 0x02]) or data[:3] == bytes([0x0D, 0x00, 0x02]):
        return 'tga'
    elif data [:2] == b'BM':
        return 'bmp'
    elif data[:18] == b'from typing import ':
        return 'pyi'
    elif data[1:4] == b'KTX':
        return 'ktx'
    elif data[1:4] == b'PNG':
        return 'png'
    elif data[:4] == bytes([0x34, 0x80, 0xC8, 0xBB]):
        return 'mesh'
    elif data[:4] == bytes([0x14, 0x00, 0x00, 0x00]):
        return 'type1'
    elif data[:4] == bytes([0x04, 0x00, 0x00, 0x00]):
        return 'type2'
    elif data[:4] == bytes([0x00, 0x01, 0x00, 0x00]):
        return 'type3'
    elif data[:4] == b'VANT':
        return 'vant'
    elif data[:4] == b'MDMP':
        return 'mdmp'
    elif data[:4] == b'RGIS':
        return 'gis'
    elif data[:4] == b'NTRK':
        return 'ntrk'
    elif data[:4] == b'RIFF':
        return 'riff'
    elif data[:4] == b'BKHD':
        return 'bnk'
    elif data[:27] == b'-----BEING PUBLIC KEY-----':
        return 'pem'
    elif data[:1] == b'<':
        return 'xml'
    elif data[:1] == b'%':
        return 'tpl'
    elif data[:1] == b'{':
        return 'json'
    elif data[:4] == bytes([0xE3, 0x00, 0x00, 0x00]) or data[:4] == bytes([0x63, 0x00, 0x00, 0x00]) or data[2:4] == bytes([0x0D, 0x0A]):
        return 'pyc'
    elif len(data) < 1000000:
        if b'package google.protobuf' in data:
            return 'proto'
        if b'#ifndef GOOGLE_PROTOBUF' in data:
            return 'h'
        if b'#include <google/protobuf' in data:
            return "cc"
        if b'void' in data or b'main(' in data or b'include' in data or b'float' in data:
            return 'shader'
        if b'technique' in data or b'ifndef' in data:
            return 'shader'
        if b'?xml' in data:
            return 'xml'
        if b'<script' in data:
            return 'html'
        if b'Javascript' in data:
            return 'js'
        if b'biped' in data or b'bip001' in data or b'bone' in data or b'bone001' in data or b'bip01' in data:
            return 'bip'
        if b'div.document' in data:
            return 'css'
    return 'dat'

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

def unpack(args, statusBar=None):
    allfiles = []
    try:
        if args.info == None:
            args.info = 0
        if args.path == None or os.path.isdir(args.path):
            allfiles = [args.path + "/" +x for x in os.listdir(args.path) if x.endswith(".npk")]
        else:
            allfiles.append(args.path)
    except TypeError as e:
        print("NPK files not found")
    keys = Keys()

    for path in allfiles:
        print("UNPACKING: {}".format(path))
        folder_path = path[:-4]
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        with open(path, 'rb') as f:
            data = f.read(4)
            pkg_type = None
            if data == b'NXPK':
                pkg_type = 0
            elif data == b'EXPK':
                pkg_type = 1
            else:
                raise Exception('NOT NXPK/EXPK FILE')
            print_data(args.info, "FILE TYPE:", data, "NXPK", f.tell())
            files = readuint32(f)
            print_data(args.info, "FILES:", files, "NXPK", f.tell())
            print("")
            var1 = readuint32(f)
            print_data(args.info, "UNKNOWN:", var1, "NXPK_DATA", f.tell())
            encryption_mode = readuint32(f)
            print_data(args.info, "ENCRYPTMODE:", encryption_mode, "NXPK_DATA", f.tell())
            hash_mode = readuint32(f)
            print_data(args.info, "HASHMODE:", hash_mode, "NXPK_DATA", f.tell())
            #mode = 1 if var1 and hash_mode else 0
            #info_size = 0x28 if mode else 0x1c
            index_offset = readuint32(f)
            print_data(args.info, "INDEXOFFSET:", index_offset, "NXPK_DATA", f.tell())
            print("")

            index_table = []
            nxfn_files = []
            hash_table = {}
            test = False

            if encryption_mode == 256 and args.nxfn_file:
                with open(folder_path+"/NXFN_result.txt", "w") as nxfn:
                    f.seek(index_offset + (files * 28) + 16)
                    nxfn_files = [x for x in (f.read()).split(b'\x00') if x != b'']
                    for nxfnline in nxfn_files:
                        complete_hash = int(mmh3.hash(nxfnline, signed=False)) # 0x66666666
                        if not test:
                            test = True
                            print(args)
                            print(complete_hash)
                        hash_table.update({nxfnline:complete_hash})
                        nxfn.write(nxfnline.decode() + "\n")
            elif encryption_mode == 256:
                f.seek(index_offset + (files * 28) + 16)
                nxfn_files = [x for x in (f.read()).split(b'\x00') if x != b'']

            f.seek(index_offset)

            with tempfile.TemporaryFile() as tmp:
                data = f.read(files * 28)

                if pkg_type:
                    data = keys.decrypt(data)
                tmp.write(data)
                tmp.seek(0)
                if args.do_one:
                    file_sign = [readuint32(tmp), tmp.tell()]
                    file_offset = readuint32(tmp)
                    file_length = readuint32(tmp)
                    file_original_length = readuint32(tmp)
                    zcrc = readuint32(tmp)                #compressed crc
                    crc = readuint32(tmp)                 #decompressed crc
                    zip_flag = readuint16(tmp)
                    file_flag = readuint16(tmp)
                    file_structure = nxfn_files[0] if nxfn_files else None
                    index_table.append((
                        file_sign,
                        file_offset, 
                        file_length,
                        file_original_length,
                        zcrc,
                        crc,
                        file_structure,
                        zip_flag,
                        file_flag,
                        ))
                else:
                    for x in range(files):
                        file_sign = [readuint32(tmp), tmp.tell()]
                        file_offset = readuint32(tmp)
                        file_length = readuint32(tmp)
                        file_original_length = readuint32(tmp)
                        zcrc = readuint32(tmp)                #compressed crc
                        crc = readuint32(tmp)                 #decompressed crc
                        zip_flag = readuint16(tmp)
                        file_flag = readuint16(tmp)
                        file_structure = nxfn_files[x] if nxfn_files else None
                        index_table.append((
                            file_sign,
                            file_offset, 
                            file_length,
                            file_original_length,
                            zcrc,
                            crc,
                            file_structure,
                            zip_flag,
                            file_flag,
                            ))
            step = files // 50 + 1
            
            for i, item in enumerate(index_table):
                data2 = None
                if (i % step == 0 or i + 1 == files and args.info < 2) or args.info > 2:
                    print('FILE: {}/{}'.format(i + 1, files))
                file_sign, file_offset, file_length, file_original_length, zcrc, crc, file_structure, zflag, file_flag = item
                print_data(args.info, "FILESIGN:", file_sign[0], "VERBOSE_FILE", file_sign[1])
                print_data(args.info, "FILEOFFSET:", file_offset, "FILE", file_sign[1] + 4)
                print_data(args.info, "FILELENGTH:", file_length, "VERBOSE_FILE", file_sign[1] + 8)
                print_data(args.info, "FILEORIGLENGTH:", file_original_length, "VERBOSE_FILE", file_sign[1] + 12)
                print_data(args.info, "ZIPCRCFLAG:", zcrc, "VERBOSE_FILE", file_sign[1] + 16)
                print_data(args.info, "CRCFLAG:", crc, "VERBOSE_FILE", file_sign[1] + 20)
                print_data(args.info, "ZFLAG:", zflag, "VERBOSE_FILE", file_sign[1] + 22)
                print_data(args.info, "FILEFLAG:", file_flag, "VERBOSE_FILE", file_sign[1] + 24)
                f.seek(file_offset)
                data = f.read(file_length)

                def check_file_structure(ext):
                    if file_structure and not args.no_nxfn:
                        file_path = folder_path + "/" + file_structure.decode().replace("\\", "/")
                    else:
                        file_path = folder_path + '/{:08}.{}'.format(i, ext)
                    return file_path

                if pkg_type:
                    data = keys.decrypt(data)
                
                if file_flag == 3:
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

                if file_flag == 4:
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

                compression = get_compression(data)

                if compression == "rot":
                    rotor = init_rotor()
                    data = rotor.decrypt(data)
                    data = zlib.decompress(data)
                    data = _reverse_string(data)


                if zflag == 1 and compression != 'rot':
                    data = zlib.decompress(data, bufsize=file_original_length)
                elif zflag == 2 and compression != 'rot':
                    data = lz4.block.decompress(data, uncompressed_size=file_original_length)
                elif zflag == 3 and compression != 'rot':
                    data = zstandard.ZstdDecompressor().decompress(data)

                file_path = check_file_structure(compression)

                compression = get_compression(data)
                print_data(args.info, "COMPRESSION:", compression.upper(), "FILE", file_offset)

                if compression == "nxs3":
                    with open("file.tmp", "wb") as wr:
                        wr.write(data)
                    os.system('./denxs3')
                    #time.sleep(0.0001) #if youre getting the error "done.tmp does not exist", try incrementing the sleep time
                    data2 = data
                    with open("done.tmp", "rb") as rd:
                        data = rd.read()
                    os.remove("file.tmp")
                    os.remove("done.tmp")

                if compression == 'zip':
                    print_data(args.info, "FILENAME:", file_path, "FILE", file_offset)
                    with open(file_path + ".zip", 'wb') as dat:
                        dat.write(data) 
                    try:
                        get_ext(data)
                        with zipfile.ZipFile(file_path + ".zip", 'r') as zip:
                            zip.extractall(file_path.replace(".zip", ""))
                    except Exception as e:
                        print("ZIP ERROR")
                    if args.delete_compressed:
                        os.remove(file_path)

                
                ext = get_ext(data)
                file_path = check_file_structure(ext)
                print_data(args.info, "FILENAME:", file_path, "FILE", file_offset)
                with open(file_path, 'wb') as dat:
                    dat.write(data)
                if args.nxs3 and data2 != None:
                    with open(file_path[:-3] + "nxs3", "wb") as dat2:
                        dat2.write(data2)
            print("FINISHED!")


def get_parser():
    parser = argparse.ArgumentParser(description='NXPK/EXPK Extractor', add_help=False)
    parser.add_argument('-v','--version', action='version', version='NXPK/EXPK Extractor  ---  Version: 1.1 (added .bip and fixed .nxs3 extraction)')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    parser.add_argument('-p','--path', help="Specify the path of the file or directory, if not specified will do all the files in the current directory",type=str)
    parser.add_argument('-d', "--delete-compressed", action="store_true",help="Delete compressed files (such as ZStandard or ZIP files) after decompression")
    parser.add_argument('-i', '--info', help="Print information about the npk file(s) 1 to 5 for least to most verbose",type=int)
    parser.add_argument('--nxfn-file', action="store_true",help="Writes a text file with the NXFN dump output (if applicable)")
    parser.add_argument('--no-nxfn',action="store_false",help="Disables NXFN file structure")
    parser.add_argument('--do-one', action='store_true', help='Only do the first file (TESTING PURPOSES)')
    parser.add_argument('--nxs3', action='store_true', help="Keep NXS3 files if there's any")
    #nxs_unpack()
    opt = parser.parse_args()
    return opt

def main():
    opt = get_parser()
    unpack(opt)


if __name__ == '__main__':
    main()
