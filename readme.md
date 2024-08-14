# NeoX NPK Extractor

![Screenshot](https://github.com/user-attachments/assets/0d742699-4269-497c-95bf-ab2c1c3b1460)

# Setup
```
pip install numpy transformations pymeshio tqdm pyqt5 moderngl pyrr zstandard lz4
```
### If you are in China:
```
pip install numpy transformations pymeshio tqdm pyqt5 zstandard lz4 moderngl pyrr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

# Instructions to extract
## Basic examples

To check your current version, use the '-v' or '--version' argument
```txt
> python extractor.py --version
```

No arguments will go through all the files and folders and find all NPK files
```txt
> python extractor.py
```

With the '-h' argument, you can see at the help options
```txt
> python extractor.py -h
```

With the '-p' argument, you can specify a file or a folder which to analyse
```txt
> python extractor.py -p script.npk
```

With the '-d' argument, if there are any ZIP or ZStandard files in the NPK, these will get deleted after extraction
```txt
> python extractor.py -p script.npk -d
```

With the '-i' argument, you can see data on the NPK file being extracted (from 1 to 5 for verbosity)
```txt
> python extractor.py -p res.npk -i (1 to 5)
```

With the '--nxfn-file' argument, there will be a "NXFN_result.txt" file that has the NXFN file structuring from inside the NPK (if applicable)
```txt
> python extractor.py -p res2.npk --nxfn-file
```

With the '--no-nxfn' argument, you can disable the NXFN file structuring (useful if it's failing, you should not be using this unless there is a bug that stops you from extracting, which should be reported)
```txt
> python extractor.py -p res4.npk --no-nxfn
``` 

With the '--do-one' argument, the program will only do one file from inside the NPK (useful for testing purposes)
```txt
> python extractor.py -p script.npk --do-one
```

~~if you'll unpack Onmyoji game.~~
~~you should use onmyoji_extractor.py rather than extractor.py~~

I am trying to add compability to every type of NPK file, always try to use extractor.py and open issue in GitHub if something fails


# Disclaimer:
I am not the creator (please check the original fork), I will only be offering support to the extractor.py and keys.py script, I can fix issues with the mesh viewer / converter if possible but refer those issues to zhouhang95.

# Credits

Thank you to:
* [zhouhang95](https://github.com/zhouhang95/neox_tools) - Original script
* [hax0r313373](https://github.com/hax0r31337/denpk2) - Code for new RSA/NXS3 encryption
* [xforce](https://github.com/xforce/neox-tools) - Research on NPK files and how they work
* [yuanbi](https://github.com/yuanbi/NeteaseUnpackTools) - Rotor encryption and marshalling for PYC

