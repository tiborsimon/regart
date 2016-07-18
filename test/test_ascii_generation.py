from unittest import TestCase


class RegisterArt(TestCase):
    def test__full_width_section_can_be_rendered(self):
        input = {
            'width': 8,
            'name': 'REGA',
            'address': '0x123',
            'sections': {
                'REGA': {
                    'position': '0',
                    'size': '8'
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
        result = generate_register_art(input)
        self.assertEquals(expected, result)
