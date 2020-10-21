from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QBasicTimer

import oni_tools


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.frames_color = []
        self.frames_depth = []
        self.tick = 0
        self.timer = QBasicTimer()
        self.pixmap = QtWidgets.QGraphicsPixmapItem()
        self.pixmap2 = QtWidgets.QGraphicsPixmapItem()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.btn_play = QtWidgets.QPushButton(self)
        self.btn_forward = QtWidgets.QPushButton(self)
        self.btn_backward = QtWidgets.QPushButton(self)
        self.btn_open = QtWidgets.QPushButton(self)
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.init_ui()

        self.show()

    def init_ui(self):
        # Общие настройки
        widget = QtWidgets.QWidget(self)
        widget.setGeometry(0, 20, 1400, 650)
        grid = QtWidgets.QGridLayout(widget)
        self.setWindowTitle('PyQt OpenNI player')

        # Инициализация отображения файла
        graphics_view1 = QtWidgets.QGraphicsView()
        graphics_view2 = QtWidgets.QGraphicsView()

        scene1 = QtWidgets.QGraphicsScene()
        scene1.addItem(self.pixmap)
        graphics_view1.setScene(scene1)
        graphics_view1.resize(640, 480)
        grid.addWidget(graphics_view1, 0, 1)

        scene2 = QtWidgets.QGraphicsScene()
        scene2.addItem(self.pixmap2)
        graphics_view2.setScene(scene2)
        graphics_view2.resize(640, 480)
        grid.addWidget(graphics_view2, 0, 0)

        grid.setColumnMinimumWidth(0, 640)
        grid.setColumnMinimumWidth(1, 640)

        widget.setLayout(grid)

        # Инициализация "ползунка"
        self.slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider.setGeometry(20, 700, 1350, 20)
        self.slider.sliderReleased.connect(self.slider_value_changed)
        self.slider.sliderPressed.connect(self.slider_value_changed)
        self.slider.sliderMoved.connect(self.slider_value_changed)

        # Инициализация кнопок управления плеером
        self.btn_play.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.btn_play.setGeometry(140, 750, 70, 40)
        self.btn_play.setToolTip('Воспроизведение')
        self.btn_play.clicked.connect(self.play_file)

        self.btn_forward.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
        self.btn_forward.setToolTip('Следующий кадр')
        self.btn_forward.clicked.connect(self.seek)
        self.btn_forward.setGeometry(215, 750, 70, 40)

        self.btn_backward.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
        self.btn_backward.setToolTip('Предыдущий кадр')
        self.btn_backward.clicked.connect(self.seek)
        self.btn_backward.setGeometry(65, 750, 70, 40)

        self.btn_open.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
        self.btn_open.setToolTip('Открыть файл')
        self.btn_open.clicked.connect(self.file_dialog)
        self.btn_open.setGeometry(10, 750, 50, 40)

        # Инициализация прогресс бара
        self.progress_bar.setGeometry(350, 750, 225, 25)
        self.progress_bar.setVisible(False)
        self.progress_bar.setToolTip('Загрузка')

        # Инициализция меню
        open_file = QtWidgets.QAction('Открыть файл', self)
        open_file.setShortcut('Ctrl+O')
        open_file.triggered.connect(self.file_dialog)

        close_file = QtWidgets.QAction('Выход', self)
        close_file.setShortcut('Alt+Q')
        close_file.triggered.connect(self.close)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&Меню')
        file_menu.addAction(open_file)
        file_menu.addAction(close_file)

        self.setGeometry(250, 100, 1400, 800)
        # graphics_view1.resize(1920, 1080)

    def file_dialog(self):
        """ Диалоговое окно для открытия файла"""
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть файл', '', '*.oni')[0]
        self.frames_color.clear()
        self.frames_depth.clear()
        b_file = str.encode(file)
        self.frames_color, self.frames_depth = oni_tools.get_video(b_file, progress_bar=self.progress_bar)
        self.tick = 0
        self.tick_position()
        self.progress_bar.setVisible(False)
        self.play()

    def play(self):
        """ Функция отображения файла"""
        if self.tick >= len(self.frames_color):
            self.tick = 0

        input_image = self.frames_color[self.tick]
        input_depth = self.frames_depth[self.tick]
        q_depth = QtGui.QImage(input_depth.data, 640, 480, QtGui.QImage.Format_RGB32)
        pixmap02 = QtGui.QPixmap.fromImage(q_depth)

        bytes_per_line_image = input_image.stride

        q_img = QtGui.QImage(input_image.data, 640, 480, bytes_per_line_image, QtGui.QImage.Format_RGB888)
        pixmap01 = QtGui.QPixmap.fromImage(q_img)

        self.pixmap.setPixmap(pixmap01)
        self.pixmap2.setPixmap(pixmap02)
        self.tick += 1

    def seek(self):
        """ Функция, реализующая покадровую перемотку """
        sender = self.sender()

        if sender.toolTip() == 'Следующий кадр':
            # self.tick += 1
            self.play()
            self.tick_position()
        else:
            self.tick -= 2
            self.tick_position()
            self.play()

    def slider_value_changed(self):
        """ Функция, реализующая работу 'ползунка' """
        self.tick = self.slider.value()
        self.play()

    def tick_position(self):
        # Вспомогательная функция для отражения текущего расположения ползунка на слайдере
        self.slider.setValue(self.tick)

    def timerEvent(self, *args, **kwargs):
        self.play()
        self.tick_position()

    def play_file(self):
        """ Функция, реализующая функционалность кнопок play/pause """
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        else:
            self.timer.start(28, self)
            self.slider.setRange(0, len(self.frames_color))
            self.btn_play.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
