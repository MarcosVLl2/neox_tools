import shutil
import os, struct, tempfile, argparse, zipfile
import time
from decompression import zflag_decompress, special_decompress, decompression_algorithm
from decryption import file_decrypt, decryption_algorithm
from detection import get_ext, get_compression
from key import Keys
from timeit import default_timer as timer

def readuint64(f):
    return struct.unpack('Q', f.read(8))[0]
def readuint32(f):
    return struct.unpack('I', f.read(4))[0]
def readuint16(f):
    return struct.unpack('H', f.read(2))[0]
def readuint8(f):
    return struct.unpack('B', f.read(1))[0]

def print_data(verblevel, minimumlevel, text, data, typeofdata, pointer=0):
    match verblevel:
        case 1:
            if verblevel >= minimumlevel:
                print("{} {}".format(text, data))
        case 2:
            if verblevel >= minimumlevel:
                print("{} {}".format(text, data))
        case 3:
            if verblevel >= minimumlevel:
                print("{:10} {} {}".format(pointer, text, data))
        case 4:
            if verblevel >= minimumlevel:
                print("{:10} {} {}".format(pointer, text, data))
        case 5:
            if verblevel >= minimumlevel:
                print("{:10} {} {}   DATA TYPE:{}".format(pointer, text, data, typeofdata))

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
        start = timer()
        print("UNPACKING: {}".format(path))
        folder_path = path[:-4]
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        with open(path, 'rb') as f:
            if not args.force:
                data = f.read(4)
                pkg_type = None
                if data == b'NXPK':
                    pkg_type = 0
                elif data == b'EXPK':
                    pkg_type = 1
                else:
                    raise Exception('NOT NXPK/EXPK FILE')
                print_data(args.info, 0,"FILE TYPE:", data, "NXPK", f.tell())
            files = readuint32(f)
            print_data(args.info, 0,"FILES:", files, "NXPK", f.tell())
            print("")
            var1 = readuint32(f)
            print_data(args.info, 5,"UNKNOWN:", var1, "NXPK_DATA", f.tell())
            encryption_mode = readuint32(f)
            print_data(args.info, 1,"ENCRYPTMODE:", encryption_mode, "NXPK_DATA", f.tell())
            hash_mode = readuint32(f)
            print_data(args.info, 1,"HASHMODE:", hash_mode, "NXPK_DATA", f.tell())
            #mode = 1 if var1 and hash_mode else 0
            #info_size = 0x28 if mode else 0x1c
            index_offset = readuint32(f)
            print_data(args.info, 1,"INDEXOFFSET:", index_offset, "NXPK_DATA", f.tell())
            print("")

            index_table = []
            nxfn_files = []
            test = False

            if encryption_mode == 256 and args.nxfn_file:
                with open(folder_path+"/NXFN_result.txt", "w") as nxfn:
                    f.seek(index_offset + (files * 28) + 16)
                    nxfn_files = [x for x in (f.read()).split(b'\x00') if x != b'']
                    for nxfnline in nxfn_files:
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
                if (i % step == 0 or i + 1 == files and args.info < 2 and args.info != 0) or args.info > 2:
                    print('FILE: {}/{}'.format(i + 1, files))
                file_sign, file_offset, file_length, file_original_length, zcrc, crc, file_structure, zflag, file_flag = item
                print_data(args.info, 3,"FILESIGN:", file_sign[0], "VERBOSE_FILE", file_sign[1])
                print_data(args.info, 1,"FILEOFFSET:", file_offset, "FILE", file_sign[1] + 4)
                print_data(args.info, 3,"FILELENGTH:", file_length, "VERBOSE_FILE", file_sign[1] + 8)
                print_data(args.info, 3,"FILEORIGLENGTH:", file_original_length, "VERBOSE_FILE", file_sign[1] + 12)
                print_data(args.info, 3,"ZIPCRCFLAG:", zcrc, "VERBOSE_FILE", file_sign[1] + 16)
                print_data(args.info, 3,"CRCFLAG:", crc, "VERBOSE_FILE", file_sign[1] + 20)
                print_data(args.info, 2,"ZFLAG:", zflag, "VERBOSE_FILE", file_sign[1] + 22)
                print_data(args.info, 2,"FILEFLAG:", file_flag, "VERBOSE_FILE", file_sign[1] + 24)
                f.seek(file_offset)
                data = f.read(file_length)

                def check_file_structure(ext):
                    if file_structure and not args.no_nxfn:
                        file_path = folder_path + "/" + file_structure.decode().replace("\\", "/")
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    else:
                        file_path = folder_path + '/{:08}.{}'.format(i, ext)
                    return file_path

                if pkg_type:
                    data = keys.decrypt(data)
                                
                print_data(args.info, 5,"DECRYPTION:", decryption_algorithm(file_flag), "FILE", file_offset)

                data = file_decrypt(file_flag, data, crc, file_length, file_original_length)

                print_data(args.info, 5,"COMPRESSION0:", decompression_algorithm(zflag), "FILE", file_offset)

                data = zflag_decompress(zflag, data, file_original_length)

                compression = get_compression(data)
                print_data(args.info, 4,"COMPRESSION1:", compression.upper(), "FILE", file_offset)

                data = special_decompress(compression, data)

                if compression == 'zip':
                    file_path = check_file_structure("zip")
                    print_data(args.info, 1,"FILENAME:", file_path, "FILE", file_offset)
                    with open(file_path, 'wb') as dat:
                        dat.write(data)
                    with zipfile.ZipFile(file_path, 'r') as zip:
                        zip.extractall(file_path[0:-4])
                    if args.delete_compressed:
                        os.remove(file_path)
                    continue

                
                ext = get_ext(data)
                file_path = check_file_structure(ext)
                print_data(args.info, 1,"FILENAME:", file_path, "FILE", file_offset)
                with open(file_path, 'wb') as dat:
                    dat.write(data)
                if args.nxs3 and data2 != None:
                    with open(file_path[:-3] + "nxs3", "wb") as dat2:
                        dat2.write(data2)
        end = timer()
        print("FINISHED - DECOMPRESSED {} FILES IN {} seconds".format(files, end - start))


def get_parser():
    parser = argparse.ArgumentParser(description='NXPK/EXPK Extractor', add_help=False)
    parser.add_argument('-v','--version', action='version', version='NXPK/EXPK Extractor  ---  Version: 1.3 (fix NXFN, raw force extraction, optimized code, added detections)')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    parser.add_argument('-p','--path', help="Specify the path of the file or directory, if not specified will do all the files in the current directory",type=str)
    parser.add_argument('-d', "--delete-compressed", action="store_true",help="Delete compressed files (such as ZStandard or ZIP files) after decompression")
    parser.add_argument('-i', '--info', help="Print information about the npk file(s) 1 to 5 for least to most verbose",type=int)
    parser.add_argument('-f','--force', help="Forces the NPK file to be extracted by ignoring the header",action="store_true")
    parser.add_argument('--nxfn-file', action="store_true",help="Writes a text file with the NXFN dump output (if applicable)")
    parser.add_argument('--no-nxfn',action="store_true",help="Disables NXFN file structure")
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
