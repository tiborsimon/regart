
def generate(reg_in, forgiveness=False):
    reg = dict(reg_in)
    _normalize_fields(reg)
    _transform_sections(reg, forgiveness)
    _validate_section_position(reg, forgiveness)
    _validate_section_size(reg, forgiveness)

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


def _normalize_fields(reg):
    if 'name' not in reg:
        reg['name'] = 'REG'
    if 'address' in reg:
        reg['address'] = normalize_to_hex(reg['address'], 'address')
        reg['address'] = '0x' + reg['address'][2:].upper()
    if 'width' not in reg:
        reg['width'] = 8
    else:
        reg['width'] = normalize_to_int(reg['width'], 'width')
    if 'sections' not in reg:
        reg['sections'] = {
            reg['name']: {
                'position': 0,
                'size': reg['width']
            }
        }
    else:
        for section_name in reg['sections']:
            section = reg['sections'][section_name]
            section['position'] = normalize_to_int(section['position'], 'position')
            section['size'] = normalize_to_int(section['size'], 'size')


def _remove_redefined_positions(reg):
    current_position = reg['sections'][0]['position']
    position_found = False
    deletable_names = []
    for section in reg['sections']:
        if section['position'] == current_position:
            if not position_found:
                position_found = True
            else:
                deletable_names.append(section['name'])
        else:
            current_position = section['position']
            position_found = False
            if section['position'] == current_position:
                position_found = True
    temp = []
    for section in reg['sections']:
        if section['name'] not in deletable_names:
            temp.append(section)

    reg['sections'] = temp


def _transform_sections(reg, forgiveness=False):
    if 'sections' in reg:
        _convert_dict_to_list(reg)
        reg['sections'].sort(key=lambda s: s['name'])
        reg['sections'].sort(key=lambda s: s['size'])
        reg['sections'].sort(key=lambda s: s['position'], reverse=True)
        if forgiveness:
            _remove_redefined_positions(reg)
            _fill_position_holes(reg)


def _convert_dict_to_list(reg):
    temp = []
    for section_name in reg['sections']:
        section = reg['sections'][section_name]
        try:
            temp.append({
                'name': section_name,
                'position': section['position'],
                'size': section['size']
            })
        except ValueError:
            raise ValueError('Invalid section parameters.')
    reg['sections'] = temp


def _fill_position_holes(reg):
    position_list = list(range(reg['width']))
    for s in reg['sections']:
        position = s['position']
        size = s['size']
        positions = list(range(position, position + size))
        for p in positions:
            position_list = [pos for pos in position_list if pos != p]
    for pos in position_list:
        reg['sections'].append({
            'name': '-',
            'position': pos,
            'size': 1
        })
    reg['sections'].sort(key=lambda s: s['position'], reverse=True)


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


def _validate_section_size(reg, forgiveness):
    if not forgiveness:
        size_sum = 0
        for s in reg['sections']:
            size_sum += s['size']
        if size_sum < reg['width']:
            raise ValueError('Sections do not fill the register width.')
        elif size_sum > reg['width']:
            raise ValueError('Sections size exceed the register width.')


def _validate_section_position(reg, forgiveness):
    if not forgiveness:
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


def normalize_to_hex(value, name):
    try:
        if not value.startswith('0x'):
            try:
                value = hex(int(value))
            except ValueError:
                raise ValueError('Value for key "{}" has to be an integer.'.format(name))
        else:
            try:
                value = hex(int(value, 16))
            except ValueError:
                raise ValueError('Value for key "{}" has to be an integer.'.format(name))
    except:
        value = hex(int(value))
    return value


def normalize_to_int(value, name):
    try:
        if not value.startswith('0x'):
            try:
                value = int(value)
            except ValueError:
                raise ValueError('Value for key "{}" has to be an integer.'.format(name))
        else:
            try:
                value = int(value, 16)
            except ValueError:
                raise ValueError('Value for key "{}" has to be an integer.'.format(name))
    except:
        value = int(value)
    return value


