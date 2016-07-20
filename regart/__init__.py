
HEADER = '/*{line}#'
HEADER_FACTOR = 3
TITLE = '| {name}{space}{address} |'
TITLE_FACTOR = 4
DIVIDER = '#{line}#'
DIVIDER_FACTOR = 2
FOOTER = '#{line}*/'
FOOTER_FACTOR = 3


def generate_register_art(reg):
    bits = ''
    for i in reversed(range(reg['width'])):
        bits += '| {0} '.format(i)
    else:
        bits += '|'

    width = len(bits)

    header = HEADER.format(
        line='-'*(width-HEADER_FACTOR)
    )

    title = TITLE.format(
        name=reg['name'],
        address=reg['address'],
        space=' '*(width-TITLE_FACTOR-len(reg['name'])-len(reg['address']))
    )

    divider = DIVIDER.format(
        line='-'*(width-DIVIDER_FACTOR)
    )

    footer = FOOTER.format(
        line='-'*(width-FOOTER_FACTOR)
    )
    return '\n'.join([header, title, divider, bits, footer]) + '\n'
