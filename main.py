import json
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QDir
from functools import partial
import isa


def show_popup(fileLoadFail, notMachine):
    msg = QMessageBox()
    msg.setWindowTitle("Oops! error")

    if fileLoadFail and not notMachine:
        msg.setText("Wrong file extension.")
    elif notMachine:
        msg.setText("The file does not contain machine code.")
    else:
        msg.setText("Load the code file first.")
    msg.setIcon(QMessageBox.Warning)

    msg.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("main.ui", self)
        self.instructions = []
        self.tableWidget.setFixedHeight(940)
        self.tableWidget.setFixedWidth(1090)
        self.loadAsmButton.clicked.connect(partial(self.load_file, False))
        self.loadMachineButton.clicked.connect(partial(self.load_file, True))
        self.loadJSONButton.clicked.connect(partial(self.load_file, False))
        self.visualizeButton.clicked.connect(self.visualize_pipeline)
        self.clearButton.clicked.connect(self.clear)

    def clear(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        rowHeaders = []
        colHeaders = []
        self.tableWidget.setVerticalHeaderLabels(rowHeaders)
        self.tableWidget.setHorizontalHeaderLabels(colHeaders)

    def handle_json(self, data):
        rowHeaders = []
        colHeaders = []

        colCounter = 0

        self.tableWidget.setRowCount(data[0][-1]['id'] + 1)
        # self.tableWidget.setColumnCount(data[0][-1]['cycle'])

        # for i in range(self.tableWidget.columnCount()):
        #     colHeaders.append("CC" + str(i + 1))

        stages = []

        for line in data[0]:
            type = line['type']
            id = line['id']

            if type == "Event":
                cycle = line['cycle']
                stage = line['stage']

                if "CC" + str(cycle) not in colHeaders:
                    colHeaders.append("CC" + str(cycle))
                    self.tableWidget.insertColumn(colCounter)
                    colCounter = colCounter + 1

                row = id
                # self.tableWidget.setItem(row, cycle - 1, QtWidgets.QTableWidgetItem(stages[stage]))
                self.fill_cell(row, colCounter - 1, stages[stage])

            elif type == "Stage":
                description = line['description']

                if description == 'Fetch':
                    path = "img/fetch.png"
                elif description == 'Decode':
                    path = "img/decode.png"
                elif description == 'Execute':
                    path = "img/execute.png"
                elif description == 'Memory':
                    path = "img/memory.png"
                elif description == 'Writeback':
                    path = "img/writeback.png"

                stages.insert(id, path)

            elif type == "Record":
                disassembly = line['disassembly']
                rowHeaders.append(disassembly)

        self.tableWidget.setVerticalHeaderLabels(rowHeaders)
        self.tableWidget.setHorizontalHeaderLabels(colHeaders)

    def fetch_and_decode(self, asm, machineCode):
        self.instructions = []

        for line in asm:
            self.instructions.append(isa.Instruction(line, machineCode))

        rowCount = len(self.instructions) + 1
        colCount = len(self.instructions) * 4

        if len(self.instructions) == 1:
            colCount = 7

        self.tableWidget.setRowCount(rowCount)
        self.tableWidget.setColumnCount(colCount)

        rowHeaders = ["Instructions:"]
        colHeaders = ["mem address:", "instr №"]

        i = 1

        while i <= colCount:
            colHeaders.append("CC" + str(i))
            i = i + 1

        self.tableWidget.setHorizontalHeaderLabels(colHeaders)

        row = 1

        for instr in self.instructions:
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(instr.NPC)))

            if machineCode:
                rowHeaders.append(instr.decodedInstr)
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem("I" + str(row - 1)))

            else:
                rowHeaders.append(instr.fullInstr)
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem("I" + str(row - 1)))

            row = row + 1

        self.tableWidget.setVerticalHeaderLabels(rowHeaders)
        self.tableWidget.setHorizontalHeaderLabels(colHeaders)

    def load_file(self, machineCode):
        self.clear()

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setFilter(QDir.Files)

        if dialog.exec_():
            fileName = dialog.selectedFiles()

            if fileName[0].endswith('.json'):
                with open(fileName[0], 'r') as f:
                    data = json.load(f)

                    self.handle_json(data)

            elif fileName[0].endswith('.txt') or fileName[0].endswith('.asm'):
                with open(fileName[0], 'r') as f:
                    if not machineCode:
                        asm = [line.rstrip('\n') for line in f]
                    else:
                        asm = [line for line in f]

                    if (asm[0][0] != "0" and asm[0][0] != "1") and machineCode:
                        show_popup(True, True)
                        f.close()
                    else:
                        self.tableWidget.setRowCount(0)
                        self.fetch_and_decode(asm, machineCode)
                        isa.PC = - 4
                        f.close()
            else:
                show_popup(True, False)

    def get_img_label(self, path):
        imgLabel = QtWidgets.QLabel(self.centralWidget())
        imgLabel.setText("")
        imgLabel.setScaledContents(True)
        pixmap = QtGui.QPixmap()
        pixmap.load(path, 'png')
        imgLabel.setPixmap(pixmap)

        return imgLabel

    def fill_cell(self, row, col, path):
        img = self.get_img_label(path)
        self.tableWidget.setCellWidget(row, col, img)

    def fill_line(self, row, col, pipeline):

        i = 0

        for stage in pipeline:
            img = self.get_img_label(stage)
            self.tableWidget.setCellWidget(row, col + i, img)
            i = i + 1

    def visualize_pipeline(self):
        row = 0
        col = 1

        stages = ["img/fetch.png", "img/decode.png", "img/execute.png", "img/memory.png", "img/writeback.png",
                  "img/bubble.png"]

        stallCounter = 0
        cycleCounter = -1

        if len(self.instructions) > 0:
            for i in range(len(self.instructions)):

                row = row + 1
                col = col + 1

                if i < len(self.instructions) - 1 and \
                    (self.instructions[i].name == "lw" or self.instructions[i].name == "lui") and \
                        self.instructions[i + 1].type != "J":

                    if self.instructions[i].rt == self.instructions[i + 1].rs or \
                            self.instructions[i].rt == self.instructions[i + 1].rt:

                        stallCounter = stallCounter + 1

                        if stallCounter > 1 and cycleCounter == 3:
                            cycleCounter = 3
                        elif stallCounter > 2 and stallCounter % 2 != 0:
                            if self.tableWidget.item(row - 1, col).text() == "D":
                                cycleCounter = 2
                            else:
                                cycleCounter = 3
                        elif stallCounter > 2 and stallCounter % 2 == 0:
                            cycleCounter = 2
                        elif stallCounter > 1:
                            cycleCounter = 2
                        else:
                            cycleCounter = cycleCounter + 1

                if cycleCounter == -1:
                    pipeline = stages[0:5]
                    self.fill_line(row, col, pipeline)

                elif cycleCounter == 0:

                    pipeline = stages[0:5]
                    self.fill_line(row, col, pipeline)

                    cycleCounter = cycleCounter + 1

                elif cycleCounter == 1:

                    pipeline = [stages[0], stages[1], stages[1], stages[2], stages[3], stages[4]]
                    self.fill_line(row, col, pipeline)

                    cycleCounter = cycleCounter + 1

                elif cycleCounter == 2:

                    pipeline = [stages[0], stages[0], stages[1], stages[2], stages[3], stages[4]]
                    self.fill_line(row, col, pipeline)

                    if stallCounter > 3:
                        cycleCounter = -3
                    elif stallCounter > 1:
                        cycleCounter = -2
                    else:
                        cycleCounter = cycleCounter + 1

                elif cycleCounter == 3:

                    pipeline = [stages[5], stages[0], stages[1], stages[2], stages[3], stages[4]]
                    self.fill_line(row, col, pipeline)

                    col = col + 1

                    stallCounter = stallCounter - 1

                    if stallCounter > 0:
                        cycleCounter = 1
                    else:
                        cycleCounter = -1

                elif cycleCounter == 4:

                    pipeline = [stages[5], stages[0], stages[1], stages[2], stages[3], stages[4]]
                    self.fill_line(row, col, pipeline)

                    col = col + 1
                    stallCounter = stallCounter - 1
                    cycleCounter = 1

                elif cycleCounter == -2:

                    if (self.instructions[i - 1].name == "lw" or self.instructions[i - 1].name == "lui") and \
                            self.instructions[i].type != "J":

                        if self.instructions[i - 1].rt == self.instructions[i].rs or \
                                self.instructions[i - 1].rt == self.instructions[i].rt:
                            pipeline = [stages[5], stages[0], stages[1], stages[1], stages[2], stages[3], stages[4]]
                            cycleCounter = 2
                    else:
                        pipeline = [stages[5], stages[0], stages[1], stages[2], stages[3], stages[4]]
                        cycleCounter = -1

                    self.fill_line(row, col, pipeline)

                    col = col + 1

                    stallCounter = stallCounter - 1
                elif cycleCounter == -3:

                    pipeline = [stages[5], stages[0], stages[0], stages[1], stages[2], stages[3], stages[4]]
                    self.fill_line(row, col, pipeline)

                    col = col + 1

                    stallCounter = stallCounter - 1
                    cycleCounter = 3
                else:
                    pipeline = stages[0:5]
                    self.fill_line(row, col, pipeline)
        else:
            show_popup(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
    widget.setFixedHeight(1000)
    widget.setFixedWidth(1248)
    widget.setWindowTitle("MIPS Pipeline Visualizer")
    widget.show()

    sys.exit(app.exec_())