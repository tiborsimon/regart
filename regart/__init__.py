def generate(reg):
    _transform_sections(reg)
    _error_handling(reg)

    expands = {}

    global_width = _default_width_for_size(reg['width'])

    if 'address' not in reg:
        reg['address'] = ''
    title_min_width = len(reg['name']) + len(reg['address']) + 1

    diff = _default_width_for_size(reg['width']) - title_min_width
    if diff < 0:
        expands[0] = -diff
        title_space = 1
        global_width = title_min_width
    else:
        title_space = global_width - title_min_width + 1

    extra_title_space = 0
    if len(reg['sections']) >= 1 and reg['name'] != reg['sections'][0]['name']:
        sections = []
        for s in reg['sections']:
            section_space = _default_width_for_size(s['size']) - len(s['name'])
            if section_space < 0:
                if s['position'] in expands:
                    old = expands[s['position']]
                    section_space = old
                    global_width += max(-section_space, old)
                    extra_title_space += max(-section_space, old)
                    expands[s['position']] += max(-section_space, old)
                else:
                    global_width += -section_space
                    extra_title_space += -section_space
                    expands[s['position']] = -section_space
            else:
                if s['position'] in expands:
                    old = expands[s['position']]
                    section_space = old
            sections.append(s['name'] + ' ' * section_space)
        sections = ' | '.join(sections)
        sections = '| ' + sections + ' |'

    title = '| {name}{space}{address} |'.format(
        name=reg['name'],
        address=reg['address'],
        space=' ' * (title_space + extra_title_space)
    )

    bits = _generate_bits(reg, expands)

    header = '/*{line}-#'.format(
        line='-' * global_width
    )

    divider = '#-{line}-#'.format(
        line='-' * global_width
    )

    footer = '#-{line}*/'.format(
        line='-' * global_width
    )

    try:
        return '\n'.join([header, title, divider, sections, divider, bits, footer]) + '\n'
    except NameError:
        return '\n'.join([header, title, divider, bits, footer]) + '\n'


def _transform_sections(reg):
    if 'sections' not in reg:
        reg['sections'] = [{
            'name': reg['name'],
            'position': 0,
            'size': reg['width']
        }]
    else:
        temp = []
        for section_name in reg['sections']:
            section = reg['sections'][section_name]
            try:
                temp.append({
                    'name': section_name,
                    'position': int(section['position']),
                    'size': int(section['size'])
                })
            except ValueError:
                raise ValueError('Invalid section parameters.')
        temp.sort(key=lambda s: s['position'], reverse=True)
        reg['sections'] = temp


def _default_width_for_size(size):
    if size == 1:
        return 1
    elif size < 11:
        return (size * 4) - 3
    else:
        return (size * 4) - 3 + (size - 10)


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


def _error_handling(reg):
    _validate_name(reg)
    _validate_width(reg)
    _validate_address(reg)
    _validate_section_size(reg)
    _validate_section_position(reg)


def _validate_name(reg):
    if 'name' not in reg:
        raise KeyError('Missing mandatory key: "name"')


def _validate_width(reg):
    if 'width' not in reg:
        reg['width'] = 8
    try:
        reg['width'] = int(reg['width'])
    except ValueError:
        raise ValueError('Value for key "address" has to be an integer.')


def _validate_address(reg):
    if 'address' in reg:
        try:
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
        except:
            reg['address'] = hex(int(reg['address']))


def _validate_section_size(reg):
    size_sum = 0
    for s in reg['sections']:
        size_sum += s['size']
    if size_sum < reg['width']:
        raise ValueError('Sections do not fill the register width.')
    elif size_sum > reg['width']:
        raise ValueError('Sections size exceed the register width.')


def _validate_section_position(reg):
    position_map = []
    for s in reg['sections']:
        pos = s['position']
        if s['size'] > 1:
            positions = list(range(pos, pos + s['size']))
        else:
            positions = [pos]
        for pos in positions:
            if pos in position_map:
                raise ValueError('Section position redefined.')
        position_map.extend(positions)
