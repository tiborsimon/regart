from unittest import TestCase

from regart import generate
from regart import _transform_sections
from regart import _default_width_for_size


class GetWidthForSize(TestCase):

    def test__basic_11_bit_length(self):
        temp = '10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0'
        size = 11
        expected = len(temp)
        result = _default_width_for_size(size)
        self.assertEqual(expected, result)

    def test__basic_8_bit_length(self):
        temp = '7 | 6 | 5 | 4 | 3 | 2 | 1 | 0'
        size = 8
        expected = len(temp)
        result = _default_width_for_size(size)
        self.assertEqual(expected, result)

    def test__basic_2_bit_length(self):
        temp = '7 | 6'
        size = 2
        expected = len(temp)
        result = _default_width_for_size(size)
        self.assertEqual(expected, result)

    def test__basic_1_bit_length(self):
        temp = '7'
        size = 1
        expected = len(temp)
        result = _default_width_for_size(size)
        self.assertEqual(expected, result)


class SectionTransformation(TestCase):
    def test__sections_can_be_transformaed(self):
        reg = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'S1': {
                    'position': 0,
                    'size': 1
                },
                'S3': {
                    'position': 2,
                    'size': 1
                },
                'S2': {
                    'position': 1,
                    'size': 1
                }
            }
        }
        expected = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': [
                {
                    'name': 'S3',
                    'position': 2,
                    'size': 1
                },
                {
                    'name': 'S2',
                    'position': 1,
                    'size': 1
                },
                {
                    'name': 'S1',
                    'position': 0,
                    'size': 1
                }
            ]
        }
        _transform_sections(reg)
        self.assertEqual(expected, reg)


class OnlySectionsTitleIsTheRegisterName(TestCase):
    def test__full_width_section_can_be_rendered(self):
        reg = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'REGA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*------------------------------#
| REGA                    0x123 |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__full_width_section__long_name_edge_case(self):
        reg = {
            'width': 8,
            'name': 'AAAAAAAAAAAAAAAAAAAAAAA',
            'address': '0x123',
            'sections': {
                'AAAAAAAAAAAAAAAAAAAAAAA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*------------------------------#
| AAAAAAAAAAAAAAAAAAAAAAA 0x123 |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__full_width_section__long_name(self):
        reg = {
            'width': 8,
            'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'address': '0x123',
            'sections': {
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*-------------------------------------#
| AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0x123 |
#--------------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0        |
#-------------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

class MinimalConfig(TestCase):
    def test__no_name__set_default_to_REG(self):
        reg = {}
        expected = '''\
/*------------------------------#
| REG                           |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)


class NameErrorCases(TestCase):
    def test__no_name__set_default_to_REG(self):
        reg = {
            'width': 8,
            'address': '0x123'
        }
        expected = '''\
/*------------------------------#
| REG                     0x123 |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)


class WidthErrorCases(TestCase):
    def test__no_width__set_to_default_8(self):
        reg = {
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'REGA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*------------------------------#
| REGA                    0x123 |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__string_width_gets_converted(self):
        reg = {
            'name': 'REGA',
            'address': '0x123',
            'width': '8',
            'sections': {
                'REGA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*------------------------------#
| REGA                    0x123 |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__width_not_integer__raises_valueerror(self):
        reg = {
            'name': 'rega',
            'address': '0x123',
            'width': 'asdf',
            'sections': {
                'rega': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        with self.assertRaises(ValueError):
            generate(reg)


class AddressErrorCases(TestCase):
    def test__no_address__its_okay__address_is_optional(self):
        reg = {
            'name': 'REGA',
            'width': 8,
            'sections': {
                'REGA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*------------------------------#
| REGA                          |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__address_no_0x_prefix__gets_extended(self):
        reg = {
            'width': 8,
            'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'address': '4',
            'sections': {
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*-----------------------------------#
| AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0x4 |
#------------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0      |
#-----------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__address_no_0x_prefix_and_not_integer__valueerror_raised(self):
        reg = {
            'width': 8,
            'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'address': 'lkj',
            'sections': {
                'REGA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        with self.assertRaises(ValueError):
            generate(reg)

    def test__address_integer_gets_converted_to_hexa(self):
        reg = {
            'width': 8,
            'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'address': '15',
            'sections': {
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*-----------------------------------#
| AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0xf |
#------------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0      |
#-----------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__address_not_string_integer_gets_converted_to_hexa(self):
        reg = {
            'width': 8,
            'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'address': 15,
            'sections': {
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*-----------------------------------#
| AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0xf |
#------------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0      |
#-----------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)


class SectionsTitleIsDifferentFromTheRegisterName(TestCase):
    def test__full_width_section_can_be_rendered(self):
        reg = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'SECTION': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        expected = '''\
/*------------------------------#
| REGA                    0x123 |
#-------------------------------#
| SECTION                       |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__two_sections(self):
        reg = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'A': {
                    'position': 7,
                    'size': 1
                },
                'B': {
                    'position': 0,
                    'size': 7
                }
            }
        }
        expected = '''\
/*------------------------------#
| REGA                    0x123 |
#-------------------------------#
| A | B                         |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__two_sections__first_one_longer_than_the_position_place(self):
        reg = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AA': {
                    'position': 7,
                    'size': 1
                },
                'B': {
                    'position': 0,
                    'size': 7
                }
            }
        }
        expected = '''\
/*-------------------------------#
| REGA                     0x123 |
#--------------------------------#
| AA | B                         |
#--------------------------------#
| 7  | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#-------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__full_section_with_one_lenghts(self):
        reg = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'A': {
                    'position': 7,
                    'size': 1
                },
                'B': {
                    'position': 6,
                    'size': 1
                },
                'C': {
                    'position': 5,
                    'size': 1
                },
                'D': {
                    'position': 4,
                    'size': 1
                },
                'E': {
                    'position': 3,
                    'size': 1
                },
                'F': {
                    'position': 2,
                    'size': 1
                },
                'G': {
                    'position': 1,
                    'size': 1
                },
                'H': {
                    'position': 0,
                    'size': 1
                }
            }
        }
        expected = '''\
/*------------------------------#
| REGA                    0x123 |
#-------------------------------#
| A | B | C | D | E | F | G | H |
#-------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__full_section_with_one_lenghts_with_longer_names(self):
        reg = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AAA': {
                    'position': 7,
                    'size': 1
                },
                'BBB': {
                    'position': 6,
                    'size': 1
                },
                'CCC': {
                    'position': 5,
                    'size': 1
                },
                'DDD': {
                    'position': 4,
                    'size': 1
                },
                'EEE': {
                    'position': 3,
                    'size': 1
                },
                'FFF': {
                    'position': 2,
                    'size': 1
                },
                'GGG': {
                    'position': 1,
                    'size': 1
                },
                'HHH': {
                    'position': 0,
                    'size': 1
                }
            }
        }
        expected = '''\
/*----------------------------------------------#
| REGA                                    0x123 |
#-----------------------------------------------#
| AAA | BBB | CCC | DDD | EEE | FFF | GGG | HHH |
#-----------------------------------------------#
| 7   | 6   | 5   | 4   | 3   | 2   | 1   | 0   |
#----------------------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__full_sections_with_long_reg_name(self):
        reg = {
            'width': 8,
            'name': 'REGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'address': '0x123',
            'sections': {
                'A': {
                    'position': 7,
                    'size': 1
                },
                'B': {
                    'position': 6,
                    'size': 1
                },
                'C': {
                    'position': 5,
                    'size': 1
                },
                'D': {
                    'position': 4,
                    'size': 1
                },
                'E': {
                    'position': 3,
                    'size': 1
                },
                'F': {
                    'position': 2,
                    'size': 1
                },
                'G': {
                    'position': 1,
                    'size': 1
                },
                'H': {
                    'position': 0,
                    'size': 1
                }
            }
        }
        expected = '''\
/*-----------------------------------------------#
| REGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0x123 |
#------------------------------------------------#
| A | B | C | D | E | F | G | H                  |
#------------------------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0                  |
#-----------------------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__full_sections_with_long_reg_name_and_even_longer_last_section(self):
        reg = {
            'width': 8,
            'name': 'REGAAAAAAAAAAAAAAAAAAAAA',
            'address': '0x123',
            'sections': {
                'A': {
                    'position': 7,
                    'size': 1
                },
                'B': {
                    'position': 6,
                    'size': 1
                },
                'C': {
                    'position': 5,
                    'size': 1
                },
                'D': {
                    'position': 4,
                    'size': 1
                },
                'E': {
                    'position': 3,
                    'size': 1
                },
                'F': {
                    'position': 2,
                    'size': 1
                },
                'G': {
                    'position': 1,
                    'size': 1
                },
                'HH': {
                    'position': 0,
                    'size': 1
                }
            }
        }
        expected = '''\
/*--------------------------------#
| REGAAAAAAAAAAAAAAAAAAAAA  0x123 |
#---------------------------------#
| A | B | C | D | E | F | G | HH  |
#---------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0   |
#--------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__full_sections_with_long_reg_name_and_even_longer_an_other_section(self):
        reg = {
            'width': 8,
            'name': 'REGAAAAAAAAAAAAAAAAAAAAA',
            'address': '0x123',
            'sections': {
                'A': {
                    'position': 7,
                    'size': 1
                },
                'B': {
                    'position': 6,
                    'size': 1
                },
                'C': {
                    'position': 5,
                    'size': 1
                },
                'D': {
                    'position': 4,
                    'size': 1
                },
                'E': {
                    'position': 3,
                    'size': 1
                },
                'F': {
                    'position': 2,
                    'size': 1
                },
                'GGGGG': {
                    'position': 1,
                    'size': 1
                },
                'H': {
                    'position': 0,
                    'size': 1
                }
            }
        }
        expected = '''\
/*-----------------------------------#
| REGAAAAAAAAAAAAAAAAAAAAA     0x123 |
#------------------------------------#
| A | B | C | D | E | F | GGGGG | H  |
#------------------------------------#
| 7 | 6 | 5 | 4 | 3 | 2 | 1     | 0  |
#-----------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)


class MoreThan8BitTests(TestCase):
    def test__32_bit_width(self):
        reg = {
            'width': 32,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AA': {
                    'position': 0,
                    'size': 32
                }
            }
        }
        expected = '''\
/*----------------------------------------------------------------------------------------------------------------------------------------------------#
| REGA                                                                                                                                          0x123 |
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
| AA                                                                                                                                                  |
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
| 31 | 30 | 29 | 28 | 27 | 26 | 25 | 24 | 23 | 22 | 21 | 20 | 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
#----------------------------------------------------------------------------------------------------------------------------------------------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__4_bit_width(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AA': {
                    'position': 0,
                    'size': 4
                }
            }
        }
        expected = '''\
/*--------------#
| REGA    0x123 |
#---------------#
| AA            |
#---------------#
| 3 | 2 | 1 | 0 |
#--------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)


class SectionErrorHandling(TestCase):
    def test__no_sections__sections_inserted(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123'
        }
        expected = '''\
/*--------------#
| REGA    0x123 |
#---------------#
| 3 | 2 | 1 | 0 |
#--------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__sections_not_filling_the_width(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AA': {
                    'position': 0,
                    'size': 3
                }
            }
        }
        with self.assertRaises(ValueError):
            generate(reg)

    def test__sections_exceeding_the_width(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AA': {
                    'position': 0,
                    'size': 5
                }
            }
        }
        with self.assertRaises(ValueError):
            generate(reg)

    def test__position_defined_twice(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'B': {
                    'position': 0,
                    'size': 2
                },
                'A': {
                    'position': 0,
                    'size': 2
                }
            }
        }
        with self.assertRaises(ValueError):
            generate(reg)

    def test__position_defined_twice_with_forgiveness(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'B': {
                    'position': 0,
                    'size': 2
                },
                'A': {
                    'position': 0,
                    'size': 2
                },
                'C': {
                    'position': 2,
                    'size': 2
                }
            }
        }
        generate(reg, forgiveness=True)

    def test__section_intersection(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'B': {
                    'position': 0,
                    'size': 3
                },
                'A': {
                    'position': 2,
                    'size': 1
                }
            }
        }
        with self.assertRaises(ValueError):
            generate(reg)

    def test__string_section_values_gets_converted(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AA': {
                    'position': '0',
                    'size': '4'
                }
            }
        }
        expected = '''\
/*--------------#
| REGA    0x123 |
#---------------#
| AA            |
#---------------#
| 3 | 2 | 1 | 0 |
#--------------*/
'''
        result = generate(reg)
        self.assertEquals(expected, result)

    def test__string_non_integer_section_values_gets_converted__error(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'AA': {
                    'position': 'lkj',
                    'size': '4'
                }
            }
        }
        with self.assertRaises(ValueError):
            generate(reg)

class ForgivenessCases(TestCase):
    def test__not_fully_defined_register__empty_sections_can_be_printed(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'A': {
                    'position': '0',
                    'size': '1'
                },
                'B': {
                    'position': '1',
                    'size': '1'
                },
                'D': {
                    'position': '3',
                    'size': '1'
                }
            }
        }
        expected = '''\
/*--------------#
| REGA    0x123 |
#---------------#
| D | - | B | A |
#---------------#
| 3 | 2 | 1 | 0 |
#--------------*/
'''
        result = generate(reg, forgiveness=True)
        print(result)
        self.assertEquals(expected, result)

    def test__not_fully_defined_register__empty_sections_can_be_printed_2(self):
        reg = {
            'width': 4,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'A': {
                    'position': '0',
                    'size': '1'
                },
                'B': {
                    'position': '1',
                    'size': '1'
                },
                'D': {
                    'position': '2',
                    'size': '1'
                }
            }
        }
        expected = '''\
/*--------------#
| REGA    0x123 |
#---------------#
| - | D | B | A |
#---------------#
| 3 | 2 | 1 | 0 |
#--------------*/
'''
        result = generate(reg, forgiveness=True)
        print(result)
        self.assertEquals(expected, result)


