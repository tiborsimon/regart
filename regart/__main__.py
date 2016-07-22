import sys
import re
import pydoc
from termcolor import colored
from regart import generate

HELP = '''\
===============================================================================
                                 R E G A R T
-------------------------------------------------------------------------------
                       by Tibor Simon - tiborsimon.io
===============================================================================

 The responsive register drawing command line tool.

 Press q to exit this manual.

 Usage:
    regart
    regart (-n|--name) <name>
    regart (-a|--address) <address>
    regart (-w|--width) <width>
    regart (-s|-section) <section_string> ...
    regart (-h|--help)

 Options:
    -n --name      Name of the register. Default: REG.
    -a --address   Register address. By default there is no address defined.
    -w --width     Register width. Default is 8.
    -s --section   Section definition string. Syntax: "name@from:to"
    -h --help      Prints out this help.



 All previously described options are optional. If you did not specify any 
 parameter, an empty register will be printed out:
 
 $ regart
 /*------------------------------#
 | REG                           |
 #-------------------------------#
 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
 #------------------------------*/

 As you can see, the default name is REG and the default width is 8 bits. You
 can also notice that if there is no section defined, the register section row
 did not get printed.

 You can add name, address and different width to your register:

 $ regart --name REGA --address 0x120 --width 16
 /*--------------------------------------------------------------------#
 | REGA                                                          0x120 |
 #---------------------------------------------------------------------#
 | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
 #--------------------------------------------------------------------*/

 These were the long named options. You can also use the short versions to
 save typing: $ regart -n REGA -a 0x120 -w 16
 The result will be the same.

 The address was given as a hexadecimal number, but you are free to use decimal
 numbers as well.

 For the register width the only limitation is your screen width :D



 Let's define some register sections!

 $ regart --section SECTION@0:7
 /*------------------------------#
 | REG                           |
 #-------------------------------#
 | SECTION                       |
 #-------------------------------#
 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
 #------------------------------*/

 There is a new row below the register name. This row is the register section
 definition row. We have defined a section named SECTION from bit 0 to bit 7
 with the following syntax: "name@from:to". You can also change direction of 
 the definition: "name@to:from". 
 
 I you left out one of the position limit, the defined section will be added 
 as a one bit wide section.

 You can use the short section definition as well: $ regart -s SECTION@0:7

 Be careful, when you define sections. The defined sections have to fill the
 entire register width.

 The following definition is syntactically wrong:

 $ regart -s SECTION@0:5
 Sections do not fill the register width.

 The default register width is 8 bit. The defined section takes 6 bits, so the 
 last 2 bits are undefined. This is an error. You always have to define all
 bits in your registers.


 Let's see a fully defined 8 bit wide register:

 $ regart -n REGA -a 0x123 -s STATUS@7:5 -s CARRY@4 -s ENABLE@3 -s SUM@2:0
 /*---------------------------------------#
 | REGA                             0x123 |
 #----------------------------------------#
 | STATUS    | CARRY | ENABLE | SUM       |
 #----------------------------------------#
 | 7 | 6 | 5 | 4     | 3      | 2 | 1 | 0 |
 #---------------------------------------*/

 Sections are responsive, as they take up as much space as the needs to keep
 themselves aligned with their bits.



 You can use regart as a python module as well. The following example code will
 demonstrate the usage. It will prodice the same output as the previous 
 command:

 import regart

 reg = {
     'name': 'REGA',
     'address': '0x123',
     'width': 8,
     'sections': {
         'STATUS': {
             'position': 5,
             'size': 3
          },
          'CARRY': {
              'position': 4,
              'size': 1
          },
          'ENABLE': {
              'position': 3,
              'size': 1
          },
          'SUM': {
              'position': 0,
              'size': 3
          }
     }
 }

 result = regart.generate(reg)
 print(result)

 As you can see, this is basically the same register description. The only
 difference is the way you define the sections. Instead of the from-to approach
 you define the lowest bit number and the section size.

 Every key in the reg dictionay is optional too. You can pass an empty 
 dictionary as well, and the default register art will be produced.



 The MIT License (MIT)
 
 Copyright (c) 2016 Tibor Simon
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
'''

reg = {}
current_key = None
try:
    for p in sys.argv[1:]:
        if not current_key:
            if p in ['-n', '--name']:
                current_key = 'name'
            if p in ['-a', '--address']:
                current_key = 'address'
            if p in ['-w', '--width']:
                current_key = 'width'
            if p in ['-s', '--section']:
                current_key = 'section'
            if p in ['-h', '--help']:
               pydoc.pager(HELP)
               sys.exit(0)

        else:
            if current_key == 'section':
                if 'sections' not in reg:
                    reg['sections'] = {}
                m = re.match('^(\w+)@(\d+)(?::(\d+))?$', p)
                if m:
                    name = m.group(1)
                    a = int(m.group(2))
                    if m.group(3):
                        b = int(m.group(3))
                        pos = min(a, b)
                        size = abs(a-b) + 1
                    else:
                        pos = a
                        size = 1

                    reg['sections'][name] = {
                        'position': pos,
                        'size': size
                    }
                else:
                    raise SyntaxError('Invalid section syntax!')
            else:
                reg[current_key] = p
            current_key = None
    print(generate(reg))
except Exception as e:
    print(colored(e.args[0], 'red'))
    sys.exit(1)

