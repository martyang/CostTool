import os
import sys
import sqltools
import pandas
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, INT, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem
from ui_MainWindows import Ui_MainWindow

# 创建对象的基类
Base = declarative_base()


class Material(Base):
    __tablename__ = 'cost_table'
    id = Column(INT, primary_key=True)
    level = Column(INT)
    main_SN = Column(String(15))
    father = Column(String(15))
    have_son = Column(INT)
    SN = Column(String(15))
    name = Column(String(60))
    price = Column(Float)


def addMate(mySession, lv: int, main: str, last_sn: str, have_son: int, mate_sn: str, mate_name: str,
            mate_price: float):
    mate = Material(level=lv, main_SN=main, father=last_sn, have_son=have_son, SN=mate_sn, name=mate_name,
                    price=mate_price)
    mySession.add(mate)


def calculate_price():
    sqltools.updateAllPrice()


def load_data2sql():
    """
    将excel表格数据读取到数据库中
    :return: none
    """
    current_path = os.getcwd()
    excel_file = pandas.read_excel(current_path + '\\A055成本表.xlsx', sheet_name='Sheet1')
    rows_excel = excel_file.shape[0]
    # columns_excel = excel_file.shape[1]

    v0_last, v1_last, v2_last, v3_last = 'None'

    engine = create_engine('mysql+pymysql://root:test1234@localhost:3306/cost_database')
    BDSession = sessionmaker(bind=engine)
    session = BDSession()

    for row in range(rows_excel):
        level = int(excel_file.iloc[row, 0][-1:])
        if row < rows_excel - 1:
            next_level = int(excel_file.iloc[row + 1, 0][-1:])
        else:
            next_level = 0
        if level == 0:
            print(level)
            main_sn = excel_file.iloc[row, 1]
            sn = main_sn
            v0_last = sn
            father = 'None'
            have_son = 1
            name = excel_file.iloc[row, 3]
            price = excel_file.iloc[row, 18]
            addMate(session, level, main_sn, father, have_son, sn, name, price)
        elif level == 1:
            print(level)
            main_sn = excel_file.iloc[row, 1]
            sn = excel_file.iloc[row, 2]
            v1_last = sn
            father = v0_last
            have_son = 0
            if next_level > level:
                have_son = 1
            name = excel_file.iloc[row, 3]
            price = excel_file.iloc[row, 18]
            addMate(session, level, main_sn, father, have_son, sn, name, price)
        elif level == 2:
            print(level)
            main_sn = excel_file.iloc[row, 1]
            sn = excel_file.iloc[row, 2]
            v2_last = sn
            father = v1_last
            have_son = 0
            if next_level > level:
                have_son = 1
            name = excel_file.iloc[row, 3]
            price = excel_file.iloc[row, 18]
            addMate(session, level, main_sn, father, have_son, sn, name, price)
        elif level == 3:
            print(level)
            main_sn = excel_file.iloc[row, 1]
            sn = excel_file.iloc[row, 2]
            v3_last = sn
            father = v2_last
            have_son = 0
            if next_level > level:
                have_son = 1
            name = excel_file.iloc[row, 3]
            price = excel_file.iloc[row, 18]
            addMate(session, level, main_sn, father, have_son, sn, name, price)
        elif level == 4:
            print(level)
            main_sn = excel_file.iloc[row, 1]
            sn = excel_file.iloc[row, 2]
            father = v3_last
            have_son = 0
            if next_level > level:
                have_son = 1
            name = excel_file.iloc[row, 3]
            price = excel_file.iloc[row, 18]
            addMate(session, level, main_sn, father, have_son, sn, name, price)
    session.commit()
    session.close()
    print('数据加载完成')


class MainWindows(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindows, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.addData2Tree)
        self.show()
        sqltools.init_database()
        load_data2sql()
        sqltools.updateAllPrice()

    def addData2Tree(self):
        """
        将数据库中level 0和1的数据添加到TreeWidget显示，同时将数据保存到excel表格。
        :return: None
        """
        tree = self.treeWidget
        tree.clear()
        level_0_mates = sqltools.queryByLevel(0)
        levelList = []
        mainSNList = []
        snList = []
        nameList = []
        priceList = []
        for mate in level_0_mates:
            item0 = QTreeWidgetItem(tree)
            item0.setText(0, str(mate[1]))
            item0.setText(1, str(mate[2]))
            item0.setText(2, str(mate[5]))
            item0.setText(3, str(mate[6]))
            item0.setText(4, str(mate[7]))

            levelList.append(mate[1])
            mainSNList.append(str(mate[2]))
            snList.append(str(mate[5]))
            nameList.append(str(mate[6]))
            priceList.append(mate[7])

            level_1_mates = sqltools.queryData(mate[2], 1)
            for mate1 in level_1_mates:
                item1 = QTreeWidgetItem(item0)
                item1.setText(0, str(mate1[1]))
                item1.setText(1, str(mate1[2]))
                item1.setText(2, str(mate1[5]))
                item1.setText(3, str(mate1[6]))
                item1.setText(4, str(mate1[7]))

                levelList.append(mate1[1])
                mainSNList.append(str(mate1[2]))
                snList.append(str(mate1[5]))
                nameList.append(str(mate1[6]))
                priceList.append(mate1[7])

        dataDict = {'level': levelList, 'main_SN': mainSNList, 'SN': snList, 'Name': nameList,
                    'Price': priceList}
        dataFrame = pandas.DataFrame(dataDict)
        dataFrame.to_excel('result.xlsx')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindows()
    sys.exit(app.exec_())
