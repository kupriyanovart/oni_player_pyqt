import sys
import oni_player
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
window = oni_player.Window()
app.exec()
sys.exit()

