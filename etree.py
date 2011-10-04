# -*- coding: utf-8 -*-

from copy import deepcopy
from lxml import etree


class Field(object):

    def __init__(self):
        self.parent_attrs = ''

    def add_attrs(self, parent, *attrs):
        attrs_str = ''
        if not attrs:
            for key, value in parent.attrib.iteritems():
                attrs_str += u' {0}="{1}"'.format(unicode(key), unicode(value))
        else:
            for attr in attrs:
                attrs_str += u' {0}="{1}"'.format(unicode(attr),
                                                  unicode(parent.attrib[attr]))
        self.parent_attrs = attrs_str

    def get_etree(self):
        pass


class UnderlinedText(Field):

    def __init__(self, text, indent=0):
        super(UnderlinedText, self).__init__()

        self.text = text
        self.indent = indent

    def get_etree(self):
        UNDERLINE = '&#8213;' * (len(self.text) + 1)
        INDENT = ' ' * self.indent

        TEXT_TMPL = (u'<tspan dy="-3px"{parent_attrs}>'
                     u'{indent}{text}</tspan>')
        ULINE_TMPL = (u'<tspan dy="10px"{parent_attrs}>'
                      u'{indent}{underline}</tspan>')
        XML_TMPL = u'<tspan>{0}{1}</tspan>'

        xml_text = TEXT_TMPL.format(text=self.text, indent=INDENT,
                                    parent_attrs=self.parent_attrs)
        xml_uline = ULINE_TMPL.format(underline=UNDERLINE, indent=INDENT,
                                      parent_attrs=self.parent_attrs)
        xml = XML_TMPL.format(xml_text, xml_uline)

        return etree.fromstring(xml)


class ComboMaterial(Field):

    def __init__(self, mat_type, fst_std, snd_std):
        super(ComboMaterial, self).__init__()

        self.mat_type = mat_type
        self.fst_std = fst_std
        self.snd_std = snd_std

    def get_etree(self):
        DELIMITER_LEN = max(len(self.fst_std), len(self.snd_std)) + 1
        DELIMITER = '&#8213;' * DELIMITER_LEN
        SPACE = ' ' * (len(self.mat_type) + 4)

        UP_STR_TMPL = (u'<tspan dy="2.5px"{parent_attrs}>'
                       u'{space}{fst_std}</tspan>')
        CENTER_STR_TMPL = (u'<tspan dy="-5.5px"{parent_attrs}>'
                           u'{mat_type}  {delimiter}</tspan>')
        BOTTOM_STR_TMPL = (u'<tspan dy="-5.5px"{parent_attrs}>'
                           u'{space}{snd_std}</tspan>')
        XML_TMPL = u'<tspan font-size="10pt">{0}{1}{2}</tspan>'

        centered = lambda st: u'{{0:^{0}}}'.format(DELIMITER_LEN).format(st)

        up_str = UP_STR_TMPL.format(parent_attrs=self.parent_attrs, space=SPACE,
                                    fst_std=centered(self.fst_std))
        center_str = CENTER_STR_TMPL.format(parent_attrs=self.parent_attrs,
                                            mat_type=self.mat_type,
                                            delimiter=DELIMITER)
        bottom_str = BOTTOM_STR_TMPL.format(parent_attrs=self.parent_attrs,
                                            space=SPACE,
                                            snd_std=centered(self.snd_std))
        xml = XML_TMPL.format(up_str, center_str,bottom_str)

        return etree.fromstring(xml)


NAMESPACES = {
    'svg':'http://www.w3.org/2000/svg',
}


def drange(start, stop, step):
    """Docstring must be here

    """
    r = start
    while r <= stop:
        yield r
        r += step


def normalize_tmpl(in_tmpl, out_tmpl):
    """Docstring must be here

    """
    tree = etree.parse(in_tmpl)
    root = tree.getroot()

    # clear all single tspan tags and transfer values to text tags
    text_tags = root.xpath('//svg:text[svg:tspan]',
                           namespaces=NAMESPACES)
    for tag in text_tags:
        if len(tag) == 1:
            tag.text = tag[0].text
            try:
                tag.attrib['x'] = tag[0].attrib['x']
                tag.attrib['y'] = tag[0].attrib['y']
                tag.attrib['style'] = tag[0].attrib['style']
            except KeyError:
                pass # FIXME: logging here
            tag.remove(tag[0])

    # round tags' coords
    tags_with_coords = root.xpath('//*[@x and @y]')
    rc = lambda tag, cd: str(round(float(tag.attrib[cd]), 1))
    for tag in tags_with_coords:
        tag.attrib['x'] = rc(tag, 'x')
        tag.attrib['y'] = rc(tag, 'y')

    # find table params and construct table cells
    tbl_cells = root.xpath('//svg:text[. = "#"]',
                            namespaces=NAMESPACES)

    if tbl_cells:
        g_coord = lambda cell, coord: float(cell.attrib[coord])

        # finding x coords lists
        x_coords = sorted(list(set([g_coord(cell, 'x') for cell in tbl_cells])))

        # finding y coords params (min, max, step)
        y_params = sorted(list(set([g_coord(cell, 'y') for cell in tbl_cells])))

        if len(y_params) != 3:
            pass # FIXME: raise custom exception here!!!

        y_min = y_params[0]
        y_max = y_params[-1]
        y_step = y_params[1] - y_params[0]

        y_coords = drange(y_min, y_max + 1, y_step)

        # checks whether all text_cells elements have the same parent
        if len(set([tc.getparent() for tc in tbl_cells])) != 1:
            pass # FIXME: raise custom exception here!!!

        # retrive parent of all text cells
        tbl_container = tbl_cells[0].getparent()

        # copy of text_cell
        cell_pattern = deepcopy(tbl_cells[0])

        # remove all text cells
        for i, _ in enumerate(tbl_cells):
            tbl_container.remove(tbl_cells[i])

        # create full table
        for i, y in enumerate(y_coords):
            for j, x in enumerate(x_coords):
                tc = deepcopy(cell_pattern)

                tc.text = ''
                tc.attrib['id'] = 'text#{0}:{1}'.format(i, j)
                tc.attrib['x'] = str(x)
                tc.attrib['y'] = str(y)

                tbl_container.append(tc)
    else:
        pass # FIXME: raise custom exception here!!!

    # find all the simple fields starting with $ and convert them
    smp_fields = root.xpath('//svg:text[starts-with(text(), "$")]',
                            namespaces=NAMESPACES)
    if smp_fields:
        for field in smp_fields:
            field.attrib['id'] = field.text
            field.text = ''
    else:
        pass # FIXME: raise custom exception here!!!

    tree.write(out_tmpl)


def complete_tmpl(tmpl, out_file, values=None, table=None):
    """Docstring must be here

    """
    tree = etree.parse(tmpl)
    root = tree.getroot()

    if values:
        value_address = '//svg:text[@id = "${0}"]'

        for i, value in enumerate(values):
            value_path = root.xpath(value_address.format(i),
                                    namespaces=NAMESPACES)[0]
            if value:
                if isinstance(value, Field):
                    value.add_attrs(value_path, 'x')
                    value_path.append(value.get_etree())
                else:
                    value_path.text = value
            else:
                value_path.getparent().remove(value_path)

    if table:
        cell_address = '//svg:text[@id = "text#{0}:{1}"]'

        for i, row in enumerate(table):
            for j, cell in enumerate(row):
                cell_path = root.xpath(cell_address.format(i, j),
                                        namespaces=NAMESPACES)[0]
                if cell:
                    if isinstance(cell, Field):
                        cell.add_attrs(cell_path, 'x')
                        cell_path.append(cell.get_etree())
                    else:
                        cell_path.text = cell
                else:
                    cell_path.getparent().remove(cell_path)

    tree.write(out_file)


if __name__ == '__main__':
    get_table = lambda x, y: [[None for row in range(x)] for col in range(y)]
    get_values = lambda x: [None for val in range(x)]

    mtable = get_table(7, 29)
    mvalues = get_values(42)

    mvalues[4] = '1'
    mvalues[5] = '2'
    mvalues[6] = u'ОАО «Тяжмаш»'
    mvalues[7] = u'Корпус'
    mvalues[8] = '32.32.662.05.02-0'
    mvalues[19] = u'Маврина'
    mvalues[21] = '04.03.03'
    mvalues[22] = u'Хаустов'
    mvalues[24] = '05.03.03'
    mvalues[25] = u'Нач. бюро'
    mvalues[26] = u'Горлов'
    mvalues[28] = '10.03.03'
    mvalues[29] = u'Жукова'
    mvalues[31] = '29.04.03'

    mtable[1][4] = UnderlinedText(u'Документация', 10)

    mtable[3][0] = u'А1'
    mtable[3][3] = u'32.32.662.05.02-0 СБ'
    mtable[3][4] = u'Сборочный чертеж'

    mtable[6][4] = UnderlinedText(u'Детали', 14)

    mtable[8][0] = u'А4'
    mtable[8][2] = '1'
    mtable[8][3] = u'32.32.662.05.02-1'
    mtable[8][4] = u'Втулка'
    mtable[8][5] = '1'

    mtable[9][0] = u'А4'
    mtable[9][2] = '2'
    mtable[9][3] = u'32.32.662.05.02-2'
    mtable[9][4] = u'Втулка'
    mtable[9][5] = '1'

    mtable[10][0] = u'БЧ'
    mtable[10][2] = '3'
    mtable[10][3] = u'32.32.662.05.02-0/3'
    mtable[10][4] = u'Патрубок'
    mtable[11][4] = ComboMaterial(u'Труба', u'В20 ГОСТ 8731-74',
                                  u'57х3,5 ГОСТ 8732-78')
    mtable[12][4] = u'L=95+1 мм'
    mtable[12][5] = '3'
    mtable[12][6] = u'0,46 кг'

    mtable[15][4] = UnderlinedText(u'Стандартные изделия', 5)

    mtable[17][2] = '5'
    mtable[17][4] = u'Фланец 1-50-25'
    mtable[18][4] = u'Ст3сп5 ГОСТ 12820-80'
    mtable[17][5] = '3'

    normalize_tmpl('spec.svg', 'nya.svg')
    complete_tmpl('nya.svg', 'result.svg', values=mvalues, table=mtable)