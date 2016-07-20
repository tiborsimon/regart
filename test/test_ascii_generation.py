from unittest import TestCase

from regart import generate_register_art


class RegisterArt(TestCase):
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

    def test__full_width_section__long_name(self):
        reg = {
            'width': 8,
            'name': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
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
        print(result)
        self.assertEquals(expected, result)
