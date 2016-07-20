
HEADER = '/*{line}#'
HEADER_FACTOR = 3
TITLE = '| {name}{space}{address} |'
TITLE_FACTOR = 4
DIVIDER = '#{line}#'
DIVIDER_FACTOR = 2
FOOTER = '#{line}*/'
FOOTER_FACTOR = 3


def default_width_for_size(size):
    if size == 1:
        return 1
    elif size < 11:
        return (size * 4) - 3
    else:
        return (size * 4) - 3 + (size - 10)

def get_bit_factor(size):
    if size == 1:
        return 1
    else:
        return (size * 4) - 1


def transform_sections(reg):
    temp = []
    for section_name in reg['sections']:
        section = reg['sections'][section_name]
        temp.append({
            'name': section_name,
            'position': section['position'],
            'size': section['size']
        })
    temp.sort(key=lambda s: s['position'], reverse=True)
    reg['sections'] = temp


def generate_register_art(reg):
    error_handling(reg)

    transform_sections(reg)

    ready = False
    expandeable_section = None

    while not ready:
        ready = True
        bits = ''
        bits = _generate_bits(bits, expandeable_section, reg)

        expandeable_section = None

        width = len(bits)

        header = HEADER.format(
            line='-'*(width-HEADER_FACTOR)
        )

        title_space = width-TITLE_FACTOR-len(reg['name'])-len(reg['address'])
        if title_space < 1:
            ready = False
            expandeable_section = {
                'position': 0,
                'needed': -title_space+1
            }
            continue
        title = TITLE.format(
            name=reg['name'],
            address=reg['address'],
            space=' '*title_space
        )

        divider = DIVIDER.format(
            line='-'*(width-DIVIDER_FACTOR)
        )

        if len(reg['sections']) > 1 or (reg['name'] not in [s['name'] for s in reg['sections']] and len(reg['sections']) == 1) :
            sections = '| '
            for section in reg['sections']:
                section_space = get_bit_factor(section['size']) - len(section['name'])
                if section_space < 0:
                    ready = False
                    expandeable_section = {
                        'position': section['position'],
                        'needed': -section_space + 1
                    }
                    break
                sections += section['name'] + ' | '
            if not ready:
                continue


        footer = FOOTER.format(
            line='-'*(width-FOOTER_FACTOR)
        )

    try:
        return '\n'.join([header, title, divider, sections, divider, bits, footer]) + '\n'
    except NameError:
        return '\n'.join([header, title, divider, bits, footer]) + '\n'


def _generate_bits(bits, expandeable_section, reg):
    for i in reversed(range(reg['width'])):
        if expandeable_section and i == expandeable_section['position']:
            bits += '| {} {}'.format(i, ' ' * expandeable_section['needed'])
        else:
            bits += '| {} '.format(i)
    else:
        bits += '|'
    return bits


def error_handling(reg):
    if 'name' not in reg:
        raise KeyError('Missing mandatory key: "name"')
    if 'width' not in reg:
        raise KeyError('Missing mandatory key: "width"')
    try:
        reg['width'] = int(reg['width'])
    except ValueError:
        raise ValueError('Value for key "address" has to be an integer.')
    if 'address' not in reg:
        raise KeyError('Missing mandatory key: "address"')
    if not reg['address'].startswith('0x'):
        try:
            reg['address'] = hex(int(reg['address']))
        except ValueError:
            raise ValueError('Value for key "address" has to be an integer.')
    else:
        try:
            reg['address'] = hex(int(reg['address'], 16))
        except ValueError:
            raise ValueError('Value for key "address" has to be an integer.')
