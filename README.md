# srec2bin_py
## Motorola S-Record to Binary File Converter (Python 3)

by Oliver Thamm - [ELMICRO Computer](https://elmicro.com)<br>
https://github.com/elmicro/srec2bin_py

### Description
This utility converts binary data from Motorola S-Record file format [1] to raw binary.

### Usage
Start the script with option -h to display help screen and usage description:
```
python srec2bin.py -h
```
### ToDo
* add support for 24/32 bit address range (currently limited to 16 bit / S1 type)
* warn if there are any data bytes below start / beyond end address specified by the user

### Copyright, License
This software is Copyright (C)2017 by ELMICRO Computer - https://elmicro.com<br>
and may be freely used, modified and distributed under the terms<br>
of the MIT License - see accompanying LICENSE.md for details

### References
[1] Wikipedia: [SREC (file format)](https://en.wikipedia.org/wiki/SREC_%28file_format%29)
