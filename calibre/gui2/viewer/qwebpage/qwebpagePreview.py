from calibre.gui2.viewer.qwebpage.qwebpage import Qwebpage


class QwebpagePreview(Qwebpage):
    def __init__(self, *args, **kwargs):
        super(QwebpagePreview, self).__init__(*args, **kwargs)