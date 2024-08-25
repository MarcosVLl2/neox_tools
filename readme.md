# NeoX NPK Extractor - NeoX NPK提取器

![Screenshot](https://github.com/user-attachments/assets/0d742699-4269-497c-95bf-ab2c1c3b1460)

# Setup - 安装程序
```
pip install numpy transformations pymeshio tqdm pyqt5 moderngl pyrr zstandard lz4
```
### If you are in China: - 如果你在中国:
```
pip install numpy transformations pymeshio tqdm pyqt5 zstandard lz4 moderngl pyrr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

# Instructions to extract - 提取说明
## Basic examples - 基本例子

To check your current version, use the '-v' or '--version' argument<br>
要检查当前版本，请使用'-v'或'--version'参数
```txt
> python extractor.py --version
```

No arguments will go through all the files and folders and find all NPK files<br>
没有参数，程序将通过所有文件和文件夹并找到所有NPK文件
```txt
> python extractor.py
```

With the '-h' argument, you can see all the help options<br>
使用'-h'参数，您可以查看帮助选项
```txt
> python extractor.py -h
```

With the '-p' argument, you can specify a file or a folder which to analyse<br>
使用'-p'参数，您可以指定要分析的文件或文件夹
```txt
> python extractor.py -p script.npk
```

With the '-d' argument, if there are any ZIP or ZStandard files in the NPK, these will get deleted after extraction<br>
使用'-d'参数，如果NPK中有任何ZIP或ZStandard文件，这些文件将在提取后被删除
```txt
> python extractor.py -p script.npk -d
```

With the '-i' argument, you can see data on the NPK file being extracted (from 1 to 5 for verbosity)<br>
使用'-i'参数，您可以看到正在提取的NPK文件的数据（从1到5表示详细级别）
```txt
> python extractor.py -p res.npk -i (1 to 5)
```

With the '--nxfn-file' argument, there will be a "NXFN_result.txt" file that has the NXFN file structuring from inside the NPK (if applicable)<br>
使用'--nxfn-file'参数，会有一个"NXFN_result.txt"从NPK内部表示NXFN文件的文件（如果存在）
```txt
> python extractor.py -p res2.npk --nxfn-file
```

With the '--no-nxfn' argument, you can disable the NXFN file structuring (useful if it's failing, you should not be using this unless there is a bug that stops you from extracting, which should be reported)<br>
使用'--no-nxfn'参数，您可以禁用NXFN文件结构（如果失败很有用，您不应该使用它，除非有一个错误阻止您提取，应该报告）
```txt
> python extractor.py -p res4.npk --no-nxfn
``` 

With the '--do-one' argument, the program will only do one file from inside the NPK (useful for testing purposes)<br>
使用'--do-one'参数，程序只会从NPK内部执行一个文件（用于测试目的）
```txt
> python extractor.py -p script.npk --do-one
```

I am trying to add compability to every type of NPK file, it is really appreciated to join the official [Discord](https://discord.gg/3enBA4SY) for more information <br>
我正在尝试为每种类型的NPK文件添加可压缩性，真的很感激加入官方[Discord](https://discord.gg/3enBA4SY)以获取更多信息或打开推送请求进行审核并可能接受

# Disclaimer: - 免责声明:
I am not the creator (please check the original fork), I will be offering support only for the scripts that are found in this GitHub branch, I can fix issues with the "mesh viewer" / "mesh converter" if possible but you are better off referring those issues to zhouhang95.<br>
我不是创建者（请检查原始分叉），我将只提供对此GitHub分支中找到的脚本的支持，如果可能的话，我可以修复"网格查看器"/"网格转换器"的问题，但您最好将这些问题提交给zhouhang95。

# Credits: - 学分:

Thank you to: - 谢谢这些人:
* [zhouhang95](https://github.com/zhouhang95/neox_tools) - Original script - 原剧本
* [hax0r313373](https://github.com/hax0r31337/denpk2) - Code for RSA/NXS3 decryption - RSA/NXS3解密代码
* [xforce](https://github.com/xforce/neox-tools) - Research on NPK files and how they work - NPK文件及其工作原理的研究
* [yuanbi](https://github.com/yuanbi/NeteaseUnpackTools) - Rotor encryption and marshalling for PYC - PYC转子加密和"马歇尔"

