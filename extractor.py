import shutil
import os, struct, tempfile, argparse, zipfile
import time
from decompression import zflag_decompress, special_decompress, decompression_algorithm
from decryption import file_decrypt, decryption_algorithm
from detection import get_ext, get_compression
from key import Keys
from timeit import default_timer as timer

#determines the info size by basic math (from the start of the index pointer // EOF or until NXFN data 
def determine_info_size(f, var1, hashmode, encryptmode, index_offset, files):
    if encryptmode == 256:
        return 0x1C
    indexbuf = f.tell()
    f.seek(index_offset)
    buf = f.read()
    f.seek(indexbuf)
    return len(buf) // files

#reads an entry of the NPK index, if its 28 the file sign is 32 bits and if its 32 its 64 bits (NeoX 1.2 / 2 shienanigans)
def read_index(f, info_size, x, nxfn_files, index_offset):
    if info_size == 28:
        file_sign = [readuint32(f), f.tell() + index_offset]
    elif info_size == 32:
        file_sign = [readuint64(f), f.tell() + index_offset]
    file_offset = readuint32(f)
    file_length = readuint32(f)
    file_original_length = readuint32(f)
    zcrc = readuint32(f)                #compressed crc
    crc = readuint32(f)                 #decompressed crc
    zip_flag = readuint16(f)
    file_flag = readuint16(f)
    file_structure = nxfn_files[x] if nxfn_files else None
    return (
        file_sign,
        file_offset, 
        file_length,
        file_original_length,
        zcrc,
        crc,
        file_structure,
        zip_flag,
        file_flag,
        )

#data readers
def readuint64(f):
    return struct.unpack('Q', f.read(8))[0]
def readuint32(f):
    return struct.unpack('I', f.read(4))[0]
def readuint16(f):
    return struct.unpack('H', f.read(2))[0]
def readuint8(f):
    return struct.unpack('B', f.read(1))[0]

#formatted way to print data
def print_data(verblevel, minimumlevel, text, data, typeofdata, pointer=0):
    pointer = hex(pointer)
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

#main code
def unpack(args, statusBar=None):
    allfiles = []
    crc128key = 0
    if args.info == None:
        args.info = 0
    if args.key:
        #key for CRC128 (type 1) algorithm
        crc128key = args.key
    try:
        #determines the files which the reader will have to operate on
        if args.path == None:
            allfiles = ["./" + x for x in os.listdir(args.path) if x.endswith(".npk")]
        elif os.path.isdir(args.path):
            allfiles = [args.path + "/" + x for x in os.listdir(args.path) if x.endswith(".npk")]
        else:
            allfiles.append(args.path)
    except TypeError as e:
        print("NPK files not found")
    if not allfiles:
        print("No NPK files found in that folder")
        
    #sets the decryption keys for the custom XOR cypher
    keys = Keys()

    #goes through every file
    for path in allfiles:
        
        #starts timer for the time taken
        start = timer()
        
        #sets the final destination path
        print("UNPACKING: {}".format(path))
        folder_path = path[:-4]
        
        #makes the folder where the files will be dumped
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            
        #opens the file
        with open(path, 'rb') as f:
            
            #this is the only thing that the force command does, doesnt read the bytes corresponding the NXPK / EXPK header
            if not args.force:
                data = f.read(4)
                pkg_type = None
                if data == b'NXPK':
                    pkg_type = 0
                elif data == b'EXPK':
                    pkg_type = 1
                else:
                    raise Exception('NOT NXPK/EXPK FILE')
                print_data(args.info, 1,"FILE TYPE:", data, "NXPK", f.tell())
            
            #amount of files
            files = readuint32(f)
            print_data(args.info, 1,"FILES:", files, "NXPK", f.tell())
            print("")
            
            #var1, its always set to 0
            var1 = readuint32(f)
            print_data(args.info, 5,"UNKNOWN:", var1, "NXPK_DATA", f.tell())
            
            #determines what i call "encryption mode", its 256 when theres NXFN file data at the end
            encryption_mode = readuint32(f)
            print_data(args.info, 2,"ENCRYPTMODE:", encryption_mode, "NXPK_DATA", f.tell())
            
            #determines what i call "hash mode", it can be 0, 1, 2, and 3, 0 and 1 are fine, 3 is not supported (i think) and 2 is unknown
            hash_mode = readuint32(f)
            print_data(args.info, 2,"HASHMODE:", hash_mode, "NXPK_DATA", f.tell())
            
            #offset where the index starts
            index_offset = readuint32(f)
            print_data(args.info, 2,"INDEXOFFSET:", index_offset, "NXPK_DATA", f.tell())

            #determines the "info_size" aka the size of each file offset data, it can be 28 or 32 bytes
            info_size = determine_info_size(f, var1, hash_mode, encryption_mode, index_offset, files)
            print_data(args.info, 3, "INDEXSIZE", info_size, "NXPK_DATA", 0)
            print("")

            index_table = []
            nxfn_files = []
            
            #checks for the "hash mode"
            if hash_mode == 2:
                print("HASHING MODE 2 DETECTED, MAY OR MAY NOT WORK!!")
            elif hash_mode == 3:
                raise Exception("HASHING MODE 3 IS CURRENTLY NOT SUPPORTED")
                
            #checks for the encryption mode and does the NXFN shienanigans
            if encryption_mode == 256 and args.nxfn_file:
                with open(folder_path+"/NXFN_result.txt", "w") as nxfn:
                    #data reader goes to where the NXFN file starts, it starts with b"NXFN" + 12 bytes (unknown for now)
                    f.seek(index_offset + (files * info_size) + 16)
                    
                    #nxfn file entries are plaintext bytes, separated by an empty byte
                    nxfn_files = [x for x in (f.read()).split(b'\x00') if x != b'']
                    
                    #dumps this file into a file called NXFN_result.txt
                    for nxfnline in nxfn_files:
                        nxfn.write(nxfnline.decode() + "\n")
            
            #does the same thing above, but doesnt write the file
            elif encryption_mode == 256:
                f.seek(index_offset + (files * info_size) + 16)
                nxfn_files = [x for x in (f.read()).split(b'\x00') if x != b'']

            #goes back to the index offset (or remains in the same place)
            f.seek(index_offset)

            #opens a temporary file
            with tempfile.TemporaryFile() as tmp:
                
                #reads the whole of the index file
                data = f.read(files * info_size)

                #if its an EXPK file, it decodes it with the custom XOR key
                if pkg_type:
                    data = keys.decrypt(data)
                    
                #writes the data
                tmp.write(data)
                
                #goes to the start of the file
                tmp.seek(0)
                
                #checks if its only supposed to read one file, then it reads the data and adds it to a list as touples with the info itself
                if args.do_one:
                    index_table.append(read_index(tmp, info_size, 0, nxfn_files, index_offset))
                else:
                    for x in range(files):
                        index_table.append(read_index(tmp, info_size, x, nxfn_files, index_offset))
                        
            #calculates how many files it should analyse before reporting progress in the console (and adds 1 to not divide by 0)
            step = len(index_table) // 50 + 1

            #goes through every index in the index table
            for i, item in enumerate(index_table):
                data2 = None
                
                #checks if it should print the progression text
                if ((i % step == 0 or i + 1 == files) and args.info <= 2 and args.info != 0) or args.info > 2:
                    print('FILE: {}/{}  ({}%)'.format(i + 1, files, ((i + 1) / files) * 100))
                    
                #unpacks the index
                file_sign, file_offset, file_length, file_original_length, zcrc, crc, file_structure, zflag, file_flag = item
                
                #prints the index data
                print_data(args.info, 4,"FILESIGN:", hex(file_sign[0]), "VERBOSE_FILE", file_sign[1])
                print_data(args.info, 3,"FILEOFFSET:", file_offset, "FILE", file_sign[1] + 4)
                print_data(args.info, 4,"FILELENGTH:", file_length, "VERBOSE_FILE", file_sign[1] + 8)
                print_data(args.info, 4,"FILEORIGLENGTH:", file_original_length, "VERBOSE_FILE", file_sign[1] + 12)
                print_data(args.info, 4,"ZIPCRCFLAG:", zcrc, "VERBOSE_FILE", file_sign[1] + 16)
                print_data(args.info, 4,"CRCFLAG:", crc, "VERBOSE_FILE", file_sign[1] + 20)
                print_data(args.info, 3,"ZFLAG:", zflag, "VERBOSE_FILE", file_sign[1] + 22)
                print_data(args.info, 3,"FILEFLAG:", file_flag, "VERBOSE_FILE", file_sign[1] + 24)
                
                #goes to the offset where the file is indicated by the index
                f.seek(file_offset)
                
                #checks if its empty, and if ignore_empty is true, skips it
                if file_original_length == 0 and args.include_empty:
                    continue
                
                #reads the amount of bytes corresponding to that file
                data = f.read(file_length)
                
                #defines the method for the file structure (if it has NXFN structure, if not its 00000000.extension)
                def check_file_structure(ext):
                    if file_structure and not args.no_nxfn:
                        file_path = folder_path + "/" + file_structure.decode().replace("\\", "/")
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    else:
                        file_path = folder_path + '/{:08}.{}'.format(i, ext)
                    return file_path

                #if its an EXPK file,it decrypts the data
                if pkg_type:
                    data = keys.decrypt(data)
                    
                #prints out the decryption algorithm type    
                print_data(args.info, 5,"DECRYPTION:", decryption_algorithm(file_flag), "FILE", file_offset)

                #does the decryption
                data = file_decrypt(file_flag, data, crc128key, crc, file_length, file_original_length)

                #prints out the compression type
                print_data(args.info, 5,"COMPRESSION0:", decompression_algorithm(zflag), "FILE", file_offset)

                #does the decompression
                data = zflag_decompress(zflag, data, file_original_length)

                #gets the compression type and prints it
                compression = get_compression(data)
                print_data(args.info, 4,"COMPRESSION1:", compression.upper(), "FILE", file_offset)

                #does the special decompresison type (NXS and ROTOR)
                data = special_decompress(compression, data)

                #special code for zip files
                if compression == 'zip':
                    
                    #checks the file structure for zip files
                    file_path = check_file_structure("zip")
                    print_data(args.info, 5,"FILENAME_ZIP:", file_path, "FILE", file_offset)
                    
                    #writes the zip file data
                    with open(file_path, 'wb') as dat:
                        dat.write(data)
                        
                    #extracts the zip file
                    with zipfile.ZipFile(file_path, 'r') as zip:
                        zip.extractall(file_path[0:-4])
                        
                    #deletes the zip file 
                    if args.delete_compressed:
                        os.remove(file_path)
                        
                    #skips the rest of the code and goes on with the next index
                    continue

                #tries to guess the extension of the file
                ext = get_ext(data)
                
                #gets the file structure
                file_path = check_file_structure(ext)
                print_data(args.info, 3,"FILENAME:", file_path, "FILE", file_offset)
                
                #writes the data
                with open(file_path, 'wb') as dat:
                    dat.write(data)
                    
                #converts KTS, PVR and ASTC to PNGs if the flag "convert_images" is set
                if (ext == "ktx" or ext == "pvr" or ext == "astc") and args.convert_images:
                    if os.name == "posix":
                        os.system('./dll/PVRTexToolCLI -i "{}" -d "{}png" -f r8g8b8a8 -noout'.format(file_path, file_path[:-len(ext)]))
                    elif os.name == "nt":
                        os.system('.\dll\PVRTexToolCLI.exe -i "{}" -d "{}png" -f r8g8b8a8 -noout'.format(file_path, file_path[:-len(ext)]))
                        
        #gets the end time
        end = timer()
        
        #prints the end time
        print("FINISHED - DECOMPRESSED {} FILES IN {} seconds".format(files, end - start))


#defines the parser arguments
def get_parser():
    parser = argparse.ArgumentParser(description='NXPK/EXPK Extractor', add_help=False)
    parser.add_argument('-v', '--version', action='version', version='NXPK/EXPK Extractor  ---  Version: 1.7.2 --- Fixed critical detection issue')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    parser.add_argument('-p', '--path', help="Specify the path of the file or directory, if not specified will do all the files in the current directory",type=str)
    parser.add_argument('-d', '--delete-compressed', action="store_true",help="Delete compressed files (such as ZStandard or ZIP files) after decompression")
    parser.add_argument('-i', '--info', help="Print information about the npk file(s) 1 to 5 for least to most verbose",type=int)
    parser.add_argument('-k', '--key', help="Select the key to use in the CRC128 hash algorithm (check the keys.txt for information)",type=int)
    parser.add_argument('--nxfn-file', action="store_true",help="Writes a text file with the NXFN dump output (if applicable)")
    parser.add_argument('--no-nxfn',action="store_true",help="Disables NXFN file structure")
    parser.add_argument('--do-one', action='store_true', help='Only do the first file (TESTING PURPOSES)')
    parser.add_argument('-f','--force', help="Forces the NPK file to be extracted by ignoring the header",action="store_true")
    parser.add_argument('--convert-images', help="Automatically converts KTX, PVR and ASTC to PNG files (WARNING, SUPER SLOW)",action="store_true")
    parser.add_argument('--include-empty', help="Prints empty files", action="store_false")
    opt = parser.parse_args()
    return opt

#main entry point
def main():
    #defines the parser argument
    opt = get_parser()
    
    #runs the unpack script with the given arguments
    unpack(opt)

#entry point if ran as a standalone
if __name__ == '__main__':
    main()
