__license__   = 'GPL v3'
__copyright__ = '2009, John Schember <john at nachtimwald.com>'
'''
Write a t2b file to disk.
'''

import StringIO

DEFAULT_T2B_DATA = '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x0f\xff\xff\xff\xf0\xff\x0f\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf8\x00\x00\xff\xff\xff\xf0\xff\x0f\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xe0\xff\xf0\xff\xff\xff\xf0\xff\xff\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc3\xff\xff\xff\xff\xff\xf0\xff\xff\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x07\xff\xff\xfc\x00?\xf0\xff\x0f\xc3\x00?\xf0\xc0\xfe\x00?\xff\xff\xff\xff\xff\xff\xff\x0f\xff\xff\xf0<\x0f\xf0\xff\x0f\xc0,\x0f\xf0\x0e\xf0,\x0f\xff\xff\xff\xff\xff\xff\xff\x0f\xff\xff\xff\xff\xc3\xf0\xff\x0f\xc0\xff\x0f\xf0\xff\xf0\xff\xc7\xff\xff\xff\xff\xff\xff\xff\x0f\xff\xff\xff\xff\xc3\xf0\xff\x0f\xc3\xff\xc3\xf0\xff\xc3\xff\xc3\xff\xff\xff\xff\xff\xff\xff\x0f\xff\xff\xff\x00\x03\xf0\xff\x0f\xc3\xff\xc3\xf0\xff\xc3\xff\xc3\xff\xff\xff\xff\xff\xff\xff\x0f\xff\xff\xf0\x1f\xc3\xf0\xff\x0f\xc3\xff\xc3\xf0\xff\xc0\x00\x03\xff\xff\xff\xff\xff\xff\xff\x0b\xff\xff\xf0\xff\xc3\xf0\xff\x0f\xc3\xff\xc3\xf0\xff\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc3\xff\xff\xf3\xff\xc3\xf0\xff\x0f\xc3\xff\xc3\xf0\xff\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\xff\xfc\xf0\xff\x03\xf0\xff\x0f\xc0\xff\x0f\xf0\xff\xf0\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf0\x0f\x00\xf08\x03\xf0\xff\x0f\xc0,\x0f\xf0\xff\xf0\x1f\x03\xff\xff\xff\xff\xff\xff\xff\xff\x00\x0f\xfc\x00\xc3\xf0\xff\x0f\xc3\x00?\xf0\xff\xff\x00\x0f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf0\x0f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf0\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x03\xfe\x94\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x00\x00\x0f\xff\xff\xff\xff\xff\xff\xfc\x7f\xfe\x94\xff\xff\xff\xff\xff\xff\xff\xff\xfc\x0f\xff\xfe\xa9@\xff\xff\xff\xff\xff\xff\xfc?\xfe\xa4\xff\xff\xff\xff\xff\xff\xff\xff\xfc\xff\xff\xff\xe9P\xff\xff\xff\xff\xff\xff\xfe/\xfe\xa8\xff\xff\xff\xff\xff\xff\xff\xff\xfc\xff\xff\xff\xf9T\xff\xff\xff\xff\xf0@\x00+\xfa\xa8?\xff\xff\xff\xff\xff\xff\xff\xfc\xbf\xff\xff\xf9T\xff\xff\xff\xff\xcb\xe4}*\xaa\xaa?\xff\xff\xff\xff\xff\xff\xff\xfc\xbf\xff\xff\xe9T\xff\xff\xff\xff\xc7\xe4\xfd\x1a\xaa\xaa?\xff\xff\xff\xff\xff\xff\xff\xfc\xaf\xea\xaa\xa6\xa4\xff@\x00\x0f\xc3\xe8\xfe\x1a\xaa\xaa?\xff\xff\xff\xff\xff\xff\xff\xfcj\x95UZ\xa4\x00\x7f\xfe\x90\x03\xe8\xfe\n\xaa\xaa?\xff\xff\xff\xff\xff\xff\xff\xfcj\x95UZ\xa4?\xff\xff\xa5C\xe8\xfe\x06\xaa\xaa?\xff\xff\xff\xff\xff\xff\xff\xfcj\x95UZ\xa4?\xff\xff\xeaC\xe8\xbe\x06\xaa\xaa\x0f\xff\xff\xff\xff\xff\xff\xff\xfcj\x95UZ\xa4/\xff\xff\xea\x82\xe8j\x06\xaa\xaa\x0f\xff\xff\xff\xff\xff\xff\xff\xfcj\x95UZ\xa4/\xff\xff\xaa\x82\xe8*F\xaa\xaa\x8f\xff\xff\xff\xff\xff\xff\xff\xfcj\x95UZ\xa4+\xff\xfe\xaa\x82\xe8*\x86\xaa\xaa\x8f\xff\xff\x80\xff\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xe8*\x86\xaa\xaa\x8f\xf0\x00T?\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xe8*\x81\xaa\xaa\x8c\x03\xff\x95?\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xe8*\x81\xaa\xaa\x80\xbf\xff\x95?\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xe8*\x81\xaa\xaa\x9b\xff\xff\x95\x0f\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xe8\x1a\x81\xaa\xaa\x9a\xff\xfe\x95\x0f\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xe8\n\x81\xaa\xaa\xa6\xbf\xfeUO\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xa8\n\x91j\xaa\xa5\xaa\xa9ZO\xff\xff\xff\xfcj\x95UV\xa4\x1a\xfa\xaa\xaa\x82\xa8\n\xa0j\xaa\xa5Z\x95ZO\xff\xff\xff\xfcj\x95UV\xa4*\xfa\xaa\xaa\x82\xa9\n\xa0j\xaa\xa5UUZC\xff\xff\xff\xfcj\x95UV\xa4*\xfa\xaa\xaa\x82\xaa\n\xa0j\xaa\xa4UUZS\xff\xff\xff\xfcZ\x95UV\xa4*\xfa\xaa\xaa\x82\xaa\n\xa0j\xaa\xa4UUZS\xff\xff\xff\xfcZ\x95UU\xa4*\xfa\xaa\xaa\x82\xaa\n\xa0j\xaa\xa8UUVS\xff\xff\xff\xfcZ\x95UU\xa4*\xea\xaa\xaa\x82\xaa\x06\xa0Z\xaa\xa8UUV\x93\xff\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x81\xaa\x02\xa0\x1a\xaa\xa8UUV\x90\xff\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x80\xaa\x02\xa0\x1a\xaa\xa8\x15UU\x94\xff\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x80\xaa"\xa0\x1a\xaa\xa8\x15UU\x94\xff\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x80\xaa2\xa4\x16\xaa\xa8\x15UU\x94\xff\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x80\xaa2\xa8\x16\xa6\xa9\x15UU\x94\xff\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x80\xaa2\xa8\x16\xa6\xa9\x05UUT?\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x84\xaa2\xa8\x16\xaa\xaa\x05UUU?\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x88\xaa2\xa8\x06\xaa\xaa\x05UUU?\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa1\xa8\xc5\xaa\xaa\x05UUU?\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa0\xa8E\xa9\xaa\x05UUU/\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa<\xa8\x05\xa9\xaaAUUU\x0f\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa<\xa8\x05\xa9\xaaAUUUO\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa<\xa9\x05\xaa\xaaAUUUO\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x1c\xaa\x01\xaa\xaa\x81UUUO\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x0c\xaa\x01\xaa\xaa\x81UUUO\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x0c\xaa1j\xaa\x80UUUC\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x0cj1jj\x90UUUS\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x0c*1jj\x90UUUS\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaaL*1jj\xa0UUUS\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x8f* j\xaa\xa0\x15UUS\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x8f*@j\xaa\xa0\x15UUP\xff\xff\xfcZ\x95UU\xa4*\xaa\xaa\xaa\x8c\xaa\x8f*\x8cZ\xaa\xa1\x15UUT\xff\xff\xfcZ\x95UU\xa4j\xaa\xaa\xaa\x8c\xaa\x8f*\x8cZ\x9a\xa0\x15UUT\xff\xff\xfcZ\x95UU\xa4j\xaa\xaa\xaa\x8c\xaa\x8f*\x8cZ\x9a\xa0\x15UUT\xff\xff\xfcZ\x95UU\xa4j\xaa\xaa\xaa\x8c\xaa\x8f\x1a\x8cZ\x9a\xa4\x15UUT?\xff\xfcZ\x95UU\x94j\xaa\xaa\xaa\x8cj\x8f\n\x8cVj\xa4\x05UU\xa4?\xff\xfcVUUU\xa4j\xaa\xaa\xaa\x8cj\x8fJ\x8c\x16\xaa\xa8\xc5UZ\xa5?\xff\xfcUUUV\xa4j\xaa\xaa\xaa\x8cj\x8f\xca\x8f\x16\xaa\xa8\xc5V\xaa\xa5?\xff\xfcUj\xaa\xaa\xa4j\xaa\xaa\xaa\x8cj\x8f\xca\x8f\x1a\xaa\xa8\x05Z\xaaU?\xff\xfcV\xaa\xaa\xaa\xa5j\xaa\xaa\xaa\x8e*\x8f\xca\x83\x1a\xaa\xa4\x01eUU?\xff\xfcZ\xaa\xaa\xaa\xa5j\xaa\xaa\xaa\x8f*\x8f\xca\x83\x1a\xa5U\x01U\x00\x00\x0f\xff\xfcUUUUUZ\xaa\xaa\xaaO%\x8f\xc6\x93\x15\x00\x001@\x0f\xff\xff\xff\xfcP\x00\x00\x00\x15\x00\x00\x00\x00\x0f\x00\x07\xc0\x03\x00\xff\xff0\x1f\xff\xff\xff\xff\xfc\x00\xff\xff\xf8\x00?\xff\xff\xff\x0f?\xc7\xc3\xf7\x0f\xff\xff\xf1\xff\xff\xff\xff\xff\xfc\xff\xff\xff\xff\xf4\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'  # noqa


def reduce_color(c):
    if c <= 64:
        return 0
    elif c > 64 and c <= 128:
        return 1
    elif c > 128 and c <= 192:
        return 2
    else:
        return 3


def i2b(n):
    return "".join([str((n >> y) & 1) for y in range(1, -1, -1)])


def write_t2b(t2bfile, coverdata=None):
    '''
    t2bfile is a file handle ready to write binary data to disk.
    coverdata is a string representation of a JPEG file.
    '''
    from PIL import Image
    if coverdata is not None:
        coverdata = StringIO.StringIO(coverdata)
        cover = Image.open(coverdata).convert("L")
        cover.thumbnail((96, 144), Image.ANTIALIAS)
        t2bcover = Image.new('L', (96, 144), 'white')

        x, y = cover.size
        t2bcover.paste(cover, ((96-x)/2, (144-y)/2))

        px = []
        pxs = t2bcover.getdata()
        for i in range(len(pxs)):
            px.append(pxs[i])
            if len(px) >= 4:
                binstr = i2b(reduce_color(px[0])) + i2b(reduce_color(px[1])) + i2b(reduce_color(px[2])) + i2b(reduce_color(px[3]))
                t2bfile.write(chr(int(binstr, 2)))
                px = []
    else:
        t2bfile.write(DEFAULT_T2B_DATA)

