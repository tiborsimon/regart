from unittest import TestCase

from regart import generate_register_art
from regart import transform_sections
from regart import default_width_for_size

class GetWidthForSize(TestCase):

    def test__basic_11_bit_length(self):
        temp = '10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0'
        size = 11
        expected = len(temp)
        result = default_width_for_size(size)
        self.assertEqual(expected, result)

    def test__basic_8_bit_length(self):
        temp = '7 | 6 | 5 | 4 | 3 | 2 | 1 | 0'
        size = 8
        expected = len(temp)
        result = default_width_for_size(size)
        self.assertEqual(expected, result)

    def test__basic_2_bit_length(self):
        temp = '7 | 6'
        size = 2
        expected = len(temp)
        result = default_width_for_size(size)
        self.assertEqual(expected, result)

    def test__basic_1_bit_length(self):
        temp = '7'
        size = 1
        expected = len(temp)
        result = default_width_for_size(size)
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
        transform_sections(reg)
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
        result = generate_register_art(reg)
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
        result = generate_register_art(reg)
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
        result = generate_register_art(reg)
        self.assertEquals(expected, result)


class NameErrorCases(TestCase):
    def test__no_name__raises_key_error(self):
        reg = {
            'width': 8,
            'address': '0x123',
            'sections': {
                'REGA': {
                    'position': 0,
                    'size': 8
                }
            }
        }
        with self.assertRaises(KeyError):
            generate_register_art(reg)


class WidthErrorCases(TestCase):
    def test__no_width__raises_key_error(self):
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
        with self.assertRaises(KeyError):
            generate_register_art(reg)

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
        result = generate_register_art(reg)
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
            generate_register_art(reg)


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
        result = generate_register_art(reg)
        self.assertEquals(expected, result)

    # def test__address_no_0x_prefix__gets_extended(self):
    #     reg = {
    #         'width': 8,
    #         'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    #         'address': '4',
    #         'sections': {
    #             'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': {
    #                 'position': 0,
    #                 'size': 8
    #             }
    #         }
    #     }
    #     expected = '''\
# /*-----------------------------------#
# | AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0x4 |
# #------------------------------------#
# | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0      |
# #-----------------------------------*/
# '''
    #     result = generate_register_art(reg)
    #     self.assertEquals(expected, result)

    # def test__address_no_0x_prefix_and_not_integer__valueerror_raised(self):
    #     reg = {
    #         'width': 8,
    #         'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    #         'address': 'lkj',
    #         'sections': {
    #             'REGA': {
    #                 'position': 0,
    #                 'size': 8
    #             }
    #         }
    #     }
    #     with self.assertRaises(ValueError):
    #         generate_register_art(reg)

    # def test__address_integer_gets_converted_to_hexa(self):
    #     reg = {
    #         'width': 8,
    #         'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    #         'address': '15',
    #         'sections': {
    #             'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': {
    #                 'position': 0,
    #                 'size': 8
    #             }
    #         }
    #     }
    #     expected = '''\
# /*-----------------------------------#
# | AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0xf |
# #------------------------------------#
# | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0      |
# #-----------------------------------*/
# '''
    #     result = generate_register_art(reg)
    #     self.assertEquals(expected, result)


# # class OnlySectionsTitleIsDifferentFromTheRegisterName(TestCase):
# #     def test__full_width_section_can_be_rendered(self):
# #         reg = {
# #             'width': 8,
# #             'name': 'REGA',
# #             'address': '0x123',
# #             'sections': {
# #                 'SECTIONaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa': {
# #                     'position': 0,
# #                     'size': 8
# #                 }
# #             }
# #         }
# #         expected = '''\
# # /*------------------------------#
# # | REGA                    0x123 |
# # #-------------------------------#
# # | SECTION                       |
# # #-------------------------------#
# # | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
# # #------------------------------*/
# # '''
# #         result = generate_register_art(reg)
# #         print(result)
# #         self.assertEquals(expected, result)
