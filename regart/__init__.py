
HEADER = '/*{line}-#'
HEADER_FACTOR = 3
TITLE = '| {name}{space}{address} |'
TITLE_FACTOR = 2
DIVIDER = '#-{line}-#'
DIVIDER_FACTOR = 2
FOOTER = '#-{line}*/'
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

    expands = {}

    width = default_width_for_size(reg['width'])

    if 'address' not in reg:
        reg['address'] = ''
    title_min_width = len(reg['name']) + len(reg['address']) + 1

    diff = default_width_for_size(reg['width']) - title_min_width
    if diff < 0:
        expands[0] = -diff
        title_space = 1
        width = title_min_width
    else:
        title_space = width - title_min_width + 1

    title = TITLE.format(
            name=reg['name'],
            address=reg['address'],
            space=' '*title_space
    )

    bits = _generate_bits(reg, expands)

    header = HEADER.format(
        line='-'*width
    )


    divider = DIVIDER.format(
        line='-'*width
    )

    footer = FOOTER.format(
        line='-'*width
    )

    try:
        return '\n'.join([header, title, divider, sections, divider, bits, footer]) + '\n'
    except NameError:
        return '\n'.join([header, title, divider, bits, footer]) + '\n'


def _generate_bits(reg, expands):
    bits = ''
    for i in reversed(range(reg['width'])):
        if i in expands:
            bits += '| {} {}'.format(i, ' ' * expands[i])
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
    if 'address' in reg:
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
