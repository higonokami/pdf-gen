# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


app = QtGui.QApplication([])
qt_translator = QtCore.QTranslator()
if qt_translator.load('qt_ru'):
    app.installTranslator(qt_translator)


class _MultiButtonBox(QtGui.QDialog):
    def __init__(self, buttons, msg=''):
        super(_MultiButtonBox, self).__init__(
            None,
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint
        )
        if not buttons:
            err_msg = 'Argument buttons must be nonempty.'
            # FIXME: Custom exception!
            raise ValueError(err_msg)

        main_layout = QtGui.QVBoxLayout()
        main_layout.setMargin(2)
        main_layout.setSpacing(5)
        main_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        main_layout.addWidget(QtGui.QLabel(u'<b>{0}</b>'.format(msg)))

        for i, (button_text, button_event) in enumerate(buttons.iteritems()):
            dyn = vars()
            button = 'button_{0}'.format(i)
            dyn[button] = QtGui.QPushButton(unicode(button_text))
            dyn[button].clicked.connect(lambda: (button_event(), self.close()))
            main_layout.addWidget(dyn[button])

        cancel_button = QtGui.QPushButton(u'Отмена')
        cancel_button.clicked.connect(self.close)
        main_layout.addWidget(cancel_button)

        self.setLayout(main_layout)


class _MultiEnterBox(QtGui.QDialog):
    def __init__(self, field_names, msg='',
                 title='multienterbox', field_values=None):
        super(_MultiEnterBox, self).__init__(
            None,
            QtCore.Qt.WindowSystemMenuHint |
            QtCore.Qt.WindowTitleHint
        )
        if not field_names:
            err_msg = 'argument field_names must be nonempty'
            # FIXME: Custom exception!
            raise ValueError(err_msg)

        self.fields_num = len(field_names)

        if field_values:
            if len(field_values) != len(field_names):
                err_msg = "Dimension of lists {0} and {1} aren't equal"
                # FIXME: Custom exception!
                raise ValueError(err_msg.format(field_names, field_values))
            else:
                self.field_values = field_values
        else:
            self.field_values = len(field_names) * ['']

        dyn_layout = QtGui.QGridLayout()
        dyn_layout.setColumnMinimumWidth(1, 250)
        dyn_layout.setSpacing(2)

        frame_style = QtGui.QFrame.Sunken | QtGui.QFrame.Panel
        for i, (name, value) in enumerate(zip(field_names,
                                              self.field_values)):
            dyn = vars()

            label = 'label_{0}'.format(i)
            dyn[label] = QtGui.QLabel(unicode(name))
            dyn[label].setFrameStyle(frame_style)

            line_edit = 'line_edit_{0}'.format(i)
            setattr(self, line_edit, QtGui.QLineEdit(unicode(value)))

            dyn_layout.addWidget(dyn[label], i, 0)
            dyn_layout.addWidget(getattr(self, line_edit), i, 1)

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                            QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QtGui.QVBoxLayout()
        main_layout.setMargin(2)
        main_layout.setSpacing(10)
        main_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        main_layout.addWidget(QtGui.QLabel(u'<b>{0}</b>'.format(msg)))
        main_layout.addLayout(dyn_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle(title)

    def accept(self):
        for i in range(self.fields_num):
            line_edit = getattr(self, 'line_edit_{0}'.format(i))
            self.field_values[i] = unicode(line_edit.text())
        QtGui.QDialog.accept(self)


def _msgbox(title='msgbox', text=''):
    dialog = QtGui.QMessageBox()
    dialog.setText(text)
    dialog.setWindowTitle(title)
    return dialog


def msgbox(title='msgbox', text=''):
    dialog = _msgbox(title, text)
    dialog.exec_()


def errormsg(title='msgbox', text=''):
    dialog = _msgbox(title, text)
    dialog.setIcon(QtGui.QMessageBox.Critical)
    dialog.exec_()


def multienterbox(field_names, msg='',
                  title='multienterbox', field_values=None):
    dialog = _MultiEnterBox(field_names, msg, title, field_values)
    reply = dialog.exec_()
    if reply:
        return dialog.field_values
    else:
        return None


def multibuttonbox(buttons, msg=''):
    dialog = _MultiButtonBox(buttons, msg)
    dialog.exec_()


if __name__ == '__main__':
    #msgbox('nya', 'desu')
    print multienterbox([u'Привет', u'Привет'], u'Привет')
    #multibuttonbox(msg=u'Выберите тип спецификации', buttons={u'Единичная': lambda: errormsg(u'десу'), u'Групповая': lambda: msgbox()})
    #multienterbox()