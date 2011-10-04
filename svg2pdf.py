# -*- coding: utf-8 -*-

import os
import time
import codecs
import tempfile
import threading

import rsvg
import cairo

mm = 2.8347
PDF_WIDTH, PDF_HEIGHT = 210*mm, 297*mm

TEMPLATES_DIR = 'templates'
RESULT_DIR = 'result'


def timeit(method):
    """Dосstring must be here
    """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '%r (%r, %r) %d ms' % (method.__name__, args, kw, 1000 * (te - ts))
        return result
    return timed


def fill_template(template_file, num):
    tmp_dir = tempfile.mkdtemp()
    svg_files = []
    with codecs.open(template_file, encoding='utf-8') as fh:
        file_body = fh.read()
        file_body = file_body.replace(u'$$NAME$$', u'Завод, десу')

    for ind in range(num):
        svg_file = os.path.join(tmp_dir, str(ind))
        with codecs.open(svg_file, encoding='utf-8', mode='w') as fh:
            fh.write(file_body)
            svg_files += [svg_file]
    return svg_files


def svg2pdf(svg_files, pdf_file):
    surf = cairo.PDFSurface(pdf_file, PDF_WIDTH, PDF_HEIGHT)
    for svg_file in svg_files:
        svg = rsvg.Handle(svg_file)
        cr = cairo.Context(surf)
        cr.scale(PDF_WIDTH / svg.props.width, PDF_HEIGHT / svg.props.height)
        svg.render_cairo(cr)
        cr.show_page()
    surf.finish()


@timeit
def main():
    pdf_file = '1.pdf'
##    template_file = os.path.join(TEMPLATES_DIR, 'spec_first_list.svg')
##    svg_files = fill_template(template_file, 10)
    svg2pdf(['result.svg'], pdf_file)


if __name__ == '__main__':
    main()