 #-*- coding: utf-8 -*- 

from audioop import reverse
from cmath import nan
from dataclasses import asdict
from email.policy import default
from http.client import OK
import os
from re import A
from sqlite3 import Row
import sys
import subprocess
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import pandas as pd
import pypyodbc
from sqlalchemy import create_engine, true
import folium
from folium.features import CustomIcon
import data
#from fastkml.kml import *
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, dump, ElementTree
from pykml import parser
import glob
import numpy as np
from config import vworld_key

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.TITLE  = "망계획도구"
        self.LEFT   = 150
        self.TOP    = 100
        self.WIDTH  = 1600
        self.HEIGHT = 800
        self.SIZE = 40
        self.setupUI()
        
        layer = "Satellite"
        tileType = "jpeg"
        self.map_tile = f"http://api.vworld.kr/req/wmts/1.0.0/{vworld_key}/{layer}/{{z}}/{{y}}/{{x}}.{tileType}"
        self.attr = "Vworld"
        self.name = "위성사진"

        self.node_url1='./img/대형.png'
        self.node_url2='./img/소형.png'
        self.node_url3='./img/부대.png'
        
        

    def setupUI(self):
        self.setWindowTitle(self.TITLE)
        self.setWindowIcon(QIcon('./img/favicon.png'))
        self.setGeometry(self.LEFT, self.TOP, self.WIDTH, self.HEIGHT)

        # 로고
        self.lbl_sv_logo = QLabel(self)
        self.lbl_sv_logo.setPixmap(QPixmap('./img/solvit_logo.png'))
        self.lbl_sv_logo.setFixedHeight(50)
        self.lbl_sv_logo.setFixedWidth(140)

        groupHL=QGridLayout()
        groupHL.addWidget(self.createHCTRgroup(),0,0)
        groupHL.addWidget(self.createLCTRgroup(),2,0)

        # "종료" 버튼
        self.exitBtn = QPushButton("프로그램 종료")
        self.exitBtn.setFixedHeight(self.SIZE)
        self.exitBtn.clicked.connect(self.exitBtnClicked)

        # "커버리지 출력" 버튼
        self.covResultBtn = QPushButton("커버리지 출력")
        self.covResultBtn.setFixedHeight(self.SIZE)
        self.covResultBtn.setFixedWidth(100)
        self.covResultBtn.clicked.connect(self.covResultBtnClicked)
        
        # "링크 출력" 버튼
        self.linkResultBtn = QPushButton("테스트(링크)")
        self.linkResultBtn.setFixedHeight(self.SIZE)
        self.linkResultBtn.setFixedWidth(100)
        self.linkResultBtn.clicked.connect(self.linkResultBtnClicked)
        
        # "전체 결과" 버튼
        self.ResultBtn = QPushButton("전체 결과")
        self.ResultBtn.setFixedHeight(self.SIZE)
        self.ResultBtn.setFixedWidth(100)
        self.ResultBtn.clicked.connect(self.ResultBtnClicked)
        
        # "노드 추가" 버튼
        self.addNode = QPushButton("노드 추가")
        self.addNode.setFixedHeight(self.SIZE)
        self.addNode.setFixedWidth(100)
        self.addNode.clicked.connect(self.addNodeBtnClicked)
        
        # "노드 삭제" 버튼
        self.delNode = QPushButton("노드 삭제")
        self.delNode.setFixedHeight(self.SIZE)
        self.delNode.setFixedWidth(100)
        self.delNode.clicked.connect(self.delNodeBtnClicked)
        
        # "노드 저장" 버튼
        self.dbsave = QPushButton("저장")
        self.dbsave.setFixedHeight(self.SIZE)
        self.dbsave.setFixedWidth(100)
        self.dbsave.clicked.connect(self.dbsaveBtnClicked)

        # 좌측 메뉴 레이아웃 설정        
        lvLay = QVBoxLayout()
        lvLay.addWidget(self.lbl_sv_logo)
        lvLay.addSpacing(self.SIZE)
        lvLay.addWidget(self.createHCTRgroup())
        lvLay.addStretch(1)
        lvLay.addWidget(self.createLCTRgroup())
        lvLay.addStretch(1)
        lvLay.addWidget(self.exitBtn)

        # 지도
        self.web = QWebEngineView()

        # 테이블
        self.tableColumn = []
        self.tableWidget = QTableWidget()
        
        # 우측 하단, 노드 추가, 노드 삭제, 저장 버튼 레이아웃 설정
        hbox = QHBoxLayout()
        hbox.addWidget(self.covResultBtn)
        hbox.addWidget(self.linkResultBtn)
        hbox.addWidget(self.ResultBtn)
        hbox.addStretch(1)
        hbox.addWidget(self.addNode)
        hbox.addWidget(self.delNode)
        hbox.addWidget(self.dbsave)

        # 우측 지도, 테이블 레이아웃 설정
        rvLay = QVBoxLayout()
        rvLay.addWidget(self.web)
        rvLay.setStretchFactor(self.web, 8)
        rvLay.addWidget(self.tableWidget)
        rvLay.setStretchFactor(self.tableWidget, 4)
        rvLay.addLayout(hbox)

        # table double clicked
        #self.tableWidget.doubleClicked.connect(self.tblCellDblClicked)

        # main Layout
        mainLay = QHBoxLayout()
        mainLay.addLayout(lvLay)
        mainLay.addLayout(rvLay)

        # layout 세팅
        self.setLayout(mainLay)
    
    def createHCTRgroup(self):
        groupbox=QGroupBox("대용량전송장치(HCTR)")

        # 시나리오 생성 버튼
        clickbtn0=QPushButton("시나리오 파일 생성")
        clickbtn0.setFixedHeight(self.SIZE)
        clickbtn0.clicked.connect(self.newScenBtnClicked)
        
        # csv 임포팅 버튼
        clickbtn1=QPushButton("시나리오 파일 열기")
        clickbtn1.setFixedHeight(self.SIZE)
        clickbtn1.clicked.connect(self.csvOpenBtnClicked)

        # "htz 분석 시작" 버튼
        clickbtn2 = QPushButton("커버리지 분석")
        clickbtn2.setFixedHeight(self.SIZE)
        clickbtn2.clicked.connect(self.covBtnClicked)

        # "링크 분석 시작" 버튼
        clickbtn3 = QPushButton("링크 연결성 분석")
        clickbtn3.setFixedHeight(self.SIZE)
        clickbtn3.clicked.connect(self.linkBtnClicked)
                
        # "중계소배치 시작" 버튼
        clickbtn4 = QPushButton("중계소 배치")
        clickbtn4.setFixedHeight(self.SIZE)
        clickbtn4.clicked.connect(self.nodeBtnClicked)

        # "주파수 할당 시작" 버튼
        clickbtn5 = QPushButton("주파수 할당")
        clickbtn5.setFixedHeight(self.SIZE)
        clickbtn5.clicked.connect(self.freqBtnClicked)

        vbox=QVBoxLayout()
        vbox.addWidget(clickbtn0)
        vbox.addWidget(clickbtn1)
        vbox.addWidget(clickbtn2)
        vbox.addWidget(clickbtn3)
        vbox.addWidget(clickbtn4)
        vbox.addWidget(clickbtn5)

        groupbox.setLayout(vbox)

        return groupbox

    def createLCTRgroup(self):
        groupbox=QGroupBox("소용량전송장치(LCTR)")

        # 시나리오 생성 버튼
        clickbtn0=QPushButton("시나리오 파일 생성")
        clickbtn0.setFixedHeight(self.SIZE)
        clickbtn0.clicked.connect(self.newLCTRScenBtnClicked)
        
        # csv 임포팅 버튼
        clickbtn1=QPushButton("시나리오 파일 열기")
        clickbtn1.setFixedHeight(self.SIZE)
        clickbtn1.clicked.connect(self.csvOpenBtnClicked)

        # "htz 분석 시작" 버튼
        clickbtn2 = QPushButton("커버리지 분석")
        clickbtn2.setFixedHeight(self.SIZE)
        clickbtn2.clicked.connect(self.covBtnClicked)

        # "링크 분석 시작" 버튼
        clickbtn3 = QPushButton("링크 연결성 분석")
        clickbtn3.setFixedHeight(self.SIZE)
        clickbtn3.clicked.connect(self.linkBtnClicked)
                
        # "중계소배치 시작" 버튼
        clickbtn4 = QPushButton("중계소 배치")
        clickbtn4.setFixedHeight(self.SIZE)
        clickbtn4.clicked.connect(self.nodeBtnClicked)

        # "주파수 할당 시작" 버튼
        clickbtn5 = QPushButton("주파수 할당")
        clickbtn5.setFixedHeight(self.SIZE)
        clickbtn5.clicked.connect(self.freqBtnClicked)

        vbox=QVBoxLayout()
        vbox.addWidget(clickbtn0)
        vbox.addWidget(clickbtn1)
        vbox.addWidget(clickbtn2)
        vbox.addWidget(clickbtn3)
        vbox.addWidget(clickbtn4)
        vbox.addWidget(clickbtn5)

        groupbox.setLayout(vbox)

        return groupbox

    def tblCellDblClicked(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print("row: {0}, col: {1}, contents: {2}".format(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text()))
            currentQTableWidgetItem.setForeground(QBrush(QColor(255, 0, 0)))       
            
    def addNodeBtnClicked(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        for i in range(1,self.tableWidget.rowCount()):
            for j in range(5,self.tableWidget.columnCount()):
                item=QTableWidgetItem(self.tableWidget.item(0,j))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, j, item)
                
    def delNodeBtnClicked(self):
        rowNum=self.tableWidget.rowCount()
        self.tableWidget.removeRow(rowNum-1)
        #노드 선택해서 삭제
        
    def nodeSet(self): # 불필요 컬럼 제거 및 '차량수' 컬럼 추가
        #차량수 컬럼 추가
        nodelinkcnt=2   
        self.tableWidget.insertColumn(nodelinkcnt)
        self.tableHdrLbl.insert(nodelinkcnt,'차량수')
        self.tableWidget.setHorizontalHeaderLabels(self.tableHdrLbl)
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.setItem(i,nodelinkcnt,QTableWidgetItem(str('2'))) # hctr 차량 개수 : 2 default 
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        
    def dbsaveBtnClicked(self):
        
        #self.HTZDBconnect
        colCnt = self.tableWidget.columnCount()
        rowCnt = self.tableWidget.rowCount()
        headers = [str(self.tableWidget.horizontalHeaderItem(i).text()) for i in range(colCnt) if i!=2]

        df_list = []
        for row in range(rowCnt):
            df_list2 = []
            for col in range(colCnt):
                    if col == 2:
                        pass
                    else :
                        table_item = self.tableWidget.item(row, col)
                        df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)
        df = pd.DataFrame(df_list, columns=headers)
        
        conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./data/HTZtables.mdb;')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM STATIONX64')

        for row in range(rowCnt):            
            query = """INSERT INTO [STATIONX64]([ID], [CALL_SIGN], [ADDRESS], [COORD_X], [COORD_Y],
                                            [TYPE_COORD], [H_ANTENNA], [FREQUENCY], [BANDWIDTH], [BANDWIDTHRX],
                                            [AZIMUTH], [NOMINAL_POWER], [GAIN], [GAINRX], [LOSSES],
                                            [LOSSESRX], [Antenna_nameH], [Antenna_nameV], [THRESHOLD], [THRESHOLDRX],
                                            [Category], [TILT], [nfdname], [D_cx1], [D_cx2], [D_cx3], [D_cx4], 
                                            [D_cx5], [D_cx6], [D_cx7], [D_cx8], [D_cx9], [D_cx10], [D_cx11], [D_cx12], [D_cx13], [D_cx14], [D_cx15], [D_cx16],[Downlink_cx])
                    VALUES({0}, '{1}', '{2}', {3}, {4},
                            '{5}', {6}, {7}, {8}, {9},
                            {10}, {11}, {12}, {13}, {14},
                            {15}, '{16}', '{17}', {18} + 140, {19} + 140, 
                            {20}, {21}, '{22}', {23}, {24},
                            {25}, {26}, {27}, {28}, {29},
                            {30}, {31}, {32}, {33}, {34},
                            {35}, {36}, {37}, {38}, {39})""".format(
                            row, df.iloc[row]['부대명'], df.iloc[row]['그룹'], df.iloc[row]['경도'], df.iloc[row]['위도'],
                        df.iloc[row]['좌표계'], df.iloc[row]['안테나 높이 (m)'], df.iloc[row]['주파수 (MHz)'], df.iloc[row]['송신대역폭 (kHz)'], df.iloc[row]['수신대역폭 (kHz)'],
                        df.iloc[row]['방위각 (deg)'], df.iloc[row]['출력 (W)'], df.iloc[row]['송신 안테나 이득 (dB)'], df.iloc[row]['수신 안테나 이득 (dB)'], df.iloc[row]['송신 손실 (dB)'],
                        df.iloc[row]['수신 손실 (dB)'], df.iloc[row]['수평 안테나 패턴'], df.iloc[row]['수직 안테나 패턴'], df.iloc[row]['커버리지 수신감도 (dBm)'], df.iloc[row]['수신감도 (dBm)'],
                        df.iloc[row]['signal (category)'], df.iloc[row]['기울기 (deg)'], df.iloc[row]['nfd'],
                        df.iloc[row]['freqTx1'], df.iloc[row]['freqTx2'], df.iloc[row]['freqTx3'], df.iloc[row]['freqTx4'], df.iloc[row]['freqTx5'],
                        df.iloc[row]['freqTx6'], df.iloc[row]['freqTx7'], df.iloc[row]['freqTx8'], df.iloc[row]['freqTx9'], df.iloc[row]['freqTx10'],
                        df.iloc[row]['freqTx11'], df.iloc[row]['freqTx12'], df.iloc[row]['freqTx13'], df.iloc[row]['freqTx14'], df.iloc[row]['freqTx15'],
                        df.iloc[row]['freqTx16'], df.iloc[row]['Downlink_cx'])
                        #{18} + 140, {19} + 140 : dBm + 140 = dBu

            cursor.execute(query)
        
        cursor.commit()

        cursor.close()
        conn.close()
        
        #지도에 노드 생성
        #m = folium.Map(location=[df.iloc[0, 3], df.iloc[0, 2]], zoom_start=11, tiles=self.map_tile, attr=self.attr)
        m = folium.Map(location=[df.iloc[0, 3], df.iloc[0, 2]], zoom_start=11)
        folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)
        
        icon_group= folium.FeatureGroup('부대 배치').add_to(m)

        for i in range(len(df.index)):
            callSign = ''
            group =''
            icon_node1 = CustomIcon(self.node_url1,icon_size=(30, 30))
            icon_node2 = CustomIcon(self.node_url2,icon_size=(30, 30))
            icon_node3 = CustomIcon(self.node_url3,icon_size=(30, 30))
            for j in range(0,5):
                if self.tableHdrLbl[j] == '부대명':
                    callSign = str(df.iloc[i, j])

                elif self.tableHdrLbl[j] == '차량수': #경도 (열이 한개씩 밀림)
                    lon = df.iloc[i, j]

                elif self.tableHdrLbl[j] == '경도': #위도 (열이 한개씩 밀림)
                    lat = df.iloc[i, j]

                elif self.tableHdrLbl[j] == '그룹': 
                    group = df.iloc[i, j]
                else :
                    pass
            if group=='대형노드' :
                folium.Marker([lat, lon], popup=callSign, icon=icon_node1).add_to(icon_group)
            elif group=='소형노드' :
                folium.Marker([lat, lon], popup=callSign, icon=icon_node2).add_to(icon_group)
            elif group=='대형부대' or group=='중형부대' :
                folium.Marker([lat, lon], popup=callSign, icon=icon_node3).add_to(icon_group)
        
        folium.LayerControl(autoZIndex=True).add_to(m)

        m.save('C:/gui/result3.html')
        self.web.load(QUrl('C:/gui/result3.html'))
            
    def newScenBtnClicked(self):
        
        # rename col
        data.columns = ['부대명','그룹','경도','위도','좌표계','안테나 높이 (m)','주파수 (MHz)','송신대역폭 (kHz)','수신대역폭 (kHz)','방위각 (deg)','출력 (W)','송신 안테나 이득 (dB)','수신 안테나 이득 (dB)','송신 손실 (dB)','수신 손실 (dB)','수평 안테나 패턴','수직 안테나 패턴','커버리지 수신감도 (dBm)','수신감도 (dBm)','signal (category)','기울기 (deg)','nfd','freqTx1','freqTx2','freqTx3','freqTx4','freqTx5','freqTx6','freqTx7','freqTx8','freqTx9','freqTx10','freqTx11','freqTx12','freqTx13','freqTx14','freqTx15','freqTx16','Downlink_cx']

        self.tableHdrLbl = list(data.columns)
    
        self.tableWidget.setColumnCount(len(data.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.tableHdrLbl)
        self.tableWidget.setRowCount(1)
        
        default_format = pd.read_csv('./csv/hctr_default.csv')
        #m = folium.Map(location=[38, 128], zoom_start=10, tiles=self.map_tile, attr=self.attr) #노드 좌표 사용자 입력
        m = folium.Map(location=[38, 128], zoom_start=11)
        folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)
        m.save('C:/gui/result2.html')
        self.web.load(QUrl('C:/gui/result2.html'))
        
        for i in range(len(default_format.index)):
            for j in range(4,len(default_format.columns)):
                QTableWidgetItem().setTextAlignment(1)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(default_format.iloc[i, j])))

        # 불필요 파라미터 표시 제거
        self.tableWidget.hideColumn(4)
        self.tableWidget.hideColumn(7)
        self.tableWidget.hideColumn(8)
        self.tableWidget.hideColumn(9)
        for i in range(11,39):
            self.tableWidget.hideColumn(i)
            
        self.nodeSet()  #차량수 컬럼
        
            
            
    def newLCTRScenBtnClicked(self):
        
        # rename col
        data.columns = ['부대명','그룹','경도','위도','좌표계','안테나 높이 (m)','주파수 (MHz)','송신대역폭 (kHz)','수신대역폭 (kHz)','방위각 (deg)','출력 (W)','송신 안테나 이득 (dB)','수신 안테나 이득 (dB)','송신 손실 (dB)','수신 손실 (dB)','수평 안테나 패턴','수직 안테나 패턴','커버리지 수신감도 (dBm)','수신감도 (dBm)','signal (category)','기울기 (deg)','nfd','freqTx1','freqTx2','freqTx3','freqTx4','freqTx5','freqTx6','freqTx7','freqTx8','freqTx9','freqTx10','freqTx11','freqTx12','freqTx13','freqTx14','freqTx15','freqTx16','Downlink_cx']

        self.tableHdrLbl = list(data.columns)
    
        self.tableWidget.setColumnCount(len(data.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.tableHdrLbl)
        self.tableWidget.setRowCount(1)
        
        default_format = pd.read_csv('./csv/lctr_default.csv')
        #m = folium.Map(location=[38, 128], zoom_start=10, tiles=self.map_tile, attr=self.attr) #노드 좌표 사용자 입력
        m = folium.Map(location=[38, 128], zoom_start=11)
        folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)
        m.save('C:/gui/result2.html')
        self.web.load(QUrl('C:/gui/result2.html'))
        
        for i in range(len(default_format.index)):
            for j in range(len(default_format.columns)):
                QTableWidgetItem().setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(default_format.iloc[i, j])))
        
        self.nodeSet()  #차량수 컬럼
        

    def csvOpenBtnClicked(self):
        fname = QFileDialog.getOpenFileName(self, '파일 열기', '', 'csv(*.csv)')
        
        if fname[0]:
            data = pd.read_csv(fname[0])

            # rename col
            data.columns = ['부대명','그룹','경도','위도','좌표계','안테나 높이 (m)','주파수 (MHz)','송신대역폭 (kHz)','수신대역폭 (kHz)','방위각 (deg)','출력 (W)','송신 안테나 이득 (dB)','수신 안테나 이득 (dB)','송신 손실 (dB)','수신 손실 (dB)','수평 안테나 패턴','수직 안테나 패턴','커버리지 수신감도 (dBm)','수신감도 (dBm)','signal (category)','기울기 (deg)','nfd','freqTx1','freqTx2','freqTx3','freqTx4','freqTx5','freqTx6','freqTx7','freqTx8','freqTx9','freqTx10','freqTx11','freqTx12','freqTx13','freqTx14','freqTx15','freqTx16','Downlink_cx']

            self.tableHdrLbl = list(data.columns)
        
            self.tableWidget.setColumnCount(len(data.columns))
            self.tableWidget.setHorizontalHeaderLabels(self.tableHdrLbl)
            self.tableWidget.setRowCount(len(data.index))
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            #m = folium.Map(location=[data.iloc[0, 3], data.iloc[0, 2]], zoom_start=11, tiles=self.map_tile, attr=self.attr)
            m = folium.Map(location=[data.iloc[0, 3], data.iloc[0, 2]], zoom_start=11)
            folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)

            icon_group= folium.FeatureGroup('부대 배치').add_to(m)

            for i in range(len(data.index)):
                callSign = ''
                lon = ''
                lat = ''
                group =''
                icon_node1 = CustomIcon(self.node_url1,icon_size=(30, 30))
                icon_node2 = CustomIcon(self.node_url2,icon_size=(30, 30))
                icon_node3 = CustomIcon(self.node_url3,icon_size=(30, 30))
                QTableWidgetItem().setTextAlignment(Qt.AlignCenter)
                for j in range(len(data.columns)):
                    if self.tableHdrLbl[j] == '부대명':
                        callSign = str(data.iloc[i, j])
                        self.tableWidget.setItem(i, j, QTableWidgetItem(callSign))
                    elif self.tableHdrLbl[j] == '경도':
                        lon = round(data.iloc[i, j], 6)
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(lon)))
                    elif self.tableHdrLbl[j] == '위도':
                        lat = round(data.iloc[i, j], 6)
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(lat)))
                    elif self.tableHdrLbl[j] == '그룹':
                        group = str(data.iloc[i, j])
                        self.tableWidget.setItem(i, j, QTableWidgetItem(group))
                    else:
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(data.iloc[i, j])))
                if group=='대형노드' :
                    folium.Marker([lat, lon], popup=callSign, icon=icon_node1).add_to(icon_group)
                elif group=='소형노드' :
                    folium.Marker([lat, lon], popup=callSign, icon=icon_node2).add_to(icon_group)
                elif group=='대형부대' or group=='중형부대' :
                    folium.Marker([lat, lon], popup=callSign, icon=icon_node3).add_to(icon_group)

            
            folium.LayerControl(autoZIndex=True).add_to(m)
            
            m.save('C:/gui/result.html')
            self.web.load(QUrl('C:/gui/result.html'))
            
            # 불필요 파라미터 표시 제거
            self.tableWidget.hideColumn(4)
            self.tableWidget.hideColumn(7)
            self.tableWidget.hideColumn(8)
            self.tableWidget.hideColumn(9)
            for i in range(11,39):
                self.tableWidget.hideColumn(i)
            
            self.nodeSet()  #차량수 컬럼

            #self.HTZDBconnect
            colCnt = self.tableWidget.columnCount()
            rowCnt = self.tableWidget.rowCount()
            headers = [str(self.tableWidget.horizontalHeaderItem(i).text()) for i in range(colCnt) if i != 2]
            
            df_list = []
            for row in range(rowCnt):
                df_list2 = []
                for col in range(colCnt):
                    if col == 2:
                        pass
                    else :
                        table_item = self.tableWidget.item(row, col)
                        df_list2.append('' if table_item is None else str(table_item.text()))
                df_list.append(df_list2)
            df = pd.DataFrame(df_list, columns=headers)
            
            conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./data/HTZtables.mdb;')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM STATIONX64')

            for row in range(rowCnt):            
                query = """INSERT INTO [STATIONX64]([ID], [CALL_SIGN], [ADDRESS], [COORD_X], [COORD_Y],
                                                [TYPE_COORD], [H_ANTENNA], [FREQUENCY], [BANDWIDTH], [BANDWIDTHRX],
                                                [AZIMUTH], [NOMINAL_POWER], [GAIN], [GAINRX], [LOSSES],
                                                [LOSSESRX], [Antenna_nameH], [Antenna_nameV], [THRESHOLD], [THRESHOLDRX],
                                                [Category], [TILT], [nfdname], [D_cx1], [D_cx2], [D_cx3], [D_cx4], 
                                                [D_cx5], [D_cx6], [D_cx7], [D_cx8], [D_cx9], [D_cx10], [D_cx11], [D_cx12], [D_cx13], [D_cx14], [D_cx15], [D_cx16],[Downlink_cx])
                        VALUES({0}, '{1}', '{2}', {3}, {4},
                                '{5}', {6}, {7}, {8}, {9},
                                {10}, {11}, {12}, {13}, {14},
                                {15}, '{16}', '{17}', {18} + 140, {19} + 140,
                                {20}, {21}, '{22}', {23}, {24},
                                {25}, {26}, {27}, {28}, {29},
                                {30}, {31}, {32}, {33}, {34},
                                {35}, {36}, {37}, {38}, {39})""".format(
                             row, df.iloc[row]['부대명'], df.iloc[row]['그룹'], df.iloc[row]['경도'], df.iloc[row]['위도'],
                           df.iloc[row]['좌표계'], df.iloc[row]['안테나 높이 (m)'], df.iloc[row]['주파수 (MHz)'], df.iloc[row]['송신대역폭 (kHz)'], df.iloc[row]['수신대역폭 (kHz)'],
                           df.iloc[row]['방위각 (deg)'], df.iloc[row]['출력 (W)'], df.iloc[row]['송신 안테나 이득 (dB)'], df.iloc[row]['수신 안테나 이득 (dB)'], df.iloc[row]['송신 손실 (dB)'],
                           df.iloc[row]['수신 손실 (dB)'], df.iloc[row]['수평 안테나 패턴'], df.iloc[row]['수직 안테나 패턴'], df.iloc[row]['커버리지 수신감도 (dBm)'], df.iloc[row]['수신감도 (dBm)'],
                           df.iloc[row]['signal (category)'], df.iloc[row]['기울기 (deg)'], df.iloc[row]['nfd'],
                           df.iloc[row]['freqTx1'], df.iloc[row]['freqTx2'], df.iloc[row]['freqTx3'], df.iloc[row]['freqTx4'], df.iloc[row]['freqTx5'],
                           df.iloc[row]['freqTx6'], df.iloc[row]['freqTx7'], df.iloc[row]['freqTx8'], df.iloc[row]['freqTx9'], df.iloc[row]['freqTx10'],
                           df.iloc[row]['freqTx11'], df.iloc[row]['freqTx12'], df.iloc[row]['freqTx13'], df.iloc[row]['freqTx14'], df.iloc[row]['freqTx15'],
                           df.iloc[row]['freqTx16'], df.iloc[row]['Downlink_cx'])

                cursor.execute(query)
            
            cursor.commit()

            cursor.close()
            conn.close()
        else:
            QMessageBox.about(self, 'Info', '파일을 선택하지 않았습니다.')

    def covBtnClicked(self):
        print('covBtnClicked()')
        os.system(".\\batch\\Coverage.bat")

    def linkBtnClicked(self):
        print('linkBtnClicked')
        os.system(".\\batch\\P2P.bat")

    def nodeBtnClicked(self):
        print('nodeBtnClicked')
        os.system(".\\batch\\Nodes.bat")

    def freqBtnClicked(self):
        print('freqBtnClicked')
        os.system(".\\batch\\freq_p2p.bat")

    def exitBtnClicked(self):
        reply = QMessageBox.question(self, "종료", "프로그램을 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit()
            
    def nodeOnMap(self):
        m = folium.Map(location=[self.tableWidget.item(0,4).text(), self.tableWidget.item(0,3).text()], zoom_start=11)
        folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)
        icon_group= folium.FeatureGroup('분석 결과').add_to(m)
        for i in range(self.tableWidget.rowCount()):
            callSign = ''
            group =''
            icon_node1 = CustomIcon(self.node_url1,icon_size=(30, 30))
            icon_node2 = CustomIcon(self.node_url2,icon_size=(30, 30))
            icon_node3 = CustomIcon(self.node_url3,icon_size=(30, 30))           
            for j in range(0,5):
                if self.tableHdrLbl[j] == '부대명':
                    callSign = self.tableWidget.item(i,j).text()
                elif self.tableHdrLbl[j] == '경도':
                    lon = self.tableWidget.item(i,j).text()
                elif self.tableHdrLbl[j] == '위도':
                    lat = self.tableWidget.item(i,j).text()
                elif self.tableHdrLbl[j] == '그룹':
                    group = self.tableWidget.item(i,j).text()
            if group=='대형노드' :
                folium.Marker([lat, lon], popup=callSign, icon=icon_node1).add_to(icon_group)
            elif group=='소형노드' :
                folium.Marker([lat, lon], popup=callSign, icon=icon_node2).add_to(icon_group)
            elif group=='대형부대' or group=='중형부대' :
                folium.Marker([lat, lon], popup=callSign, icon=icon_node3).add_to(icon_group)            
        
        folium.LayerControl(autoZIndex=True).add_to(m)
        
        m.save('C:/gui/result_node.html')
        self.web.load(QUrl('C:/gui/result_node.html'))
        
        return (icon_group)

    def covResultBtnClicked(self):  
        #커버리지 파일 찾기
        kml_file=glob.glob('./outcome/COV/*.kml')
        cov_file=glob.glob('./outcome/COV/*.png')

        #kml 파일 파싱
        doc=parser.parse(kml_file[0])
        root=doc.getroot()
        lanlonbox_position=root.getchildren()[0].getchildren()[1].getchildren()[3].getchildren()
        corner_top=float(lanlonbox_position[0])
        corner_low=float(lanlonbox_position[1])
        corner_right=float(lanlonbox_position[2])
        corner_left=float(lanlonbox_position[3])

        #center_y=round((corner_top+corner_low)/2,5)
        #center_x=round((corner_left+corner_right)/2,5)
        
        nodemap=self.nodeOnMap()
        # link_result=self.linkDraw()
        # link_map=folium.FeatureGroup(name='연결 링크',overlay=True)

        # link_map.add_child(link_result)
  
        cov_map=folium.FeatureGroup('커버리지').add_to(nodemap)

        # nodemap.add_child(link_map)
        
        folium.raster_layers.ImageOverlay(
            image=cov_file[0],
            name="커버리지",
            bounds=[[corner_low, corner_left], [corner_top, corner_right]],
            opacity=1,
            interactive=False,
            cross_origin=False,
            zindex=1,
        ).add_to(cov_map)

        folium.LayerControl(autoZIndex=True).add_to(cov_map)

        cov_map.save('C:/gui/result_cov.html')
        self.web.load(QUrl('C:/gui/result_cov.html'))
        return (cov_map)
        
    #link analysis
    def linkResultBtnClicked(self):
        self.linkDraw()

        
    def linkCSVopen(self):
        #링크 파일 선택
        link_file=glob.glob('./outcome/P2P/*.CSV')
        lr = pd.read_csv(link_file[0],';',encoding='cp949')

        #중복 행 제거 - 멀티 채널
        link_tr=lr.drop_duplicates(['Callsign','Callsign.1'])

        #수신 감도 -77dBm이상 
        link_tr2=link_tr.loc[lr['Pr dBm']>-200]

        # 인덱스 초기화
        link_tr2.reset_index(drop=True,inplace=True)

        ####링크 형성 알고리즘###
        # ###단방향만 고려하여 중복 제거
        # link_list=[]
        # for i in range(0,len(link_tr2.index)):
        #     if link_tr2['Address'].iloc[i]=='소형노드':
        #         if link_tr2['Address.1'].iloc[i]=='대형부대':
        #             link_list.append(i) # 제거 행 리스트 
        #     elif link_tr2['Address'].iloc[i]=='대형노드':
        #         pass
        #     else :
        #         link_list.append(i) # 제거 행 리스트
        # for i in link_list:
        #     link_tr2=link_tr2.drop(i, axis=0) #노드 연결 규칙 적용
        
        
        # ###부대 통신소 가장 가까운 노드에 1개만 연결 기능
        # link_tr2.reset_index(drop=True,inplace=True)# 인덱스 초기화
        # link_list2=[]
        # for i in range(0,len(link_tr2.index)):
        #     if link_tr2['Address'].iloc[i]=='소형노드' and link_tr2['Address.1'].iloc[i]=='중형부대':
        #         for j in range(0,len(link_tr2.index)):
        #             if link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Distance m'].iloc[i]>link_tr2['Distance m'].iloc[j]:
        #                 link_list2.append(i)
        #             elif link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Distance m'].iloc[i]<link_tr2['Distance m'].iloc[j]:
        #                 link_list2.append(j)
        # link_list2 = list(set(link_list2)) #제거 행 리스트 중복 제거
        # for i in link_list2:
        #     link_tr2=link_tr2.drop(i, axis=0) #규칙 적용

        link_tr2.reset_index(drop=True,inplace=True)        #제거 행 리스트 중복 제거
        
        #중형 부대부터 sort(차량수 적은 그룹 순으로 )

        link_tr2.sort_values(['Address.1','Callsign.1'], ascending=False,inplace=True)
        print(link_tr2)
        
        #####노드통신소 링크 연결 개수 제한 - 단방향에 대한 노드 연결 개수 제한(차량수)
        link_tr2.reset_index(drop=True,inplace=True) # 인덱스 초기화
        link_list0=[]
        link_col=[]
        link_row=['0']
        for i in range(self.tableWidget.rowCount()):
            link_col.append(self.tableWidget.item(i,0).text())
        print(link_col)
        link_table = pd.DataFrame(index=link_row,columns=link_col)
        link_table.reset_index()
        link_table=link_table.fillna(0)
        print(link_table)
        node_cnt=0
        callsign=''
        tx=''
        rx=''
        print('~~~~~~~~~~~~~~',link_table['hctr1'].iloc[0])
        for i in range(len(link_tr2.index)):
            for j in range(self.tableWidget.rowCount()):
                if link_tr2['Callsign.1'].iloc[i]==self.tableWidget.item(j,0).text(): # 0 : 부대명 컬럼
                    callsign=link_tr2['Callsign.1'].iloc[i]
                    tx=link_tr2['Callsign'].iloc[i]
                    rx=link_tr2['Callsign.1'].iloc[i]
                    print(link_tr2['Callsign.1'].iloc[i],link_tr2['Address.1'].iloc[i])
                    print(link_tr2['Callsign'].iloc[i],link_tr2['Address'].iloc[i])
                    node_cnt=node_cnt+1
                    car_cnt=2*int(self.tableWidget.item(j,2).text())
                    link_table[tx].iloc[0]=link_table[tx].iloc[0]+1
                    link_table[rx].iloc[0]=link_table[rx].iloc[0]+1
                    print(node_cnt,car_cnt)
                    
                    if node_cnt>car_cnt:
                        link_list0.append(i)
                        print('remove : ',i)
                        
                    if i<len(link_tr2.index)-1 and callsign!=link_tr2['Callsign.1'].iloc[i+1]:
                        node_cnt=0
                        print('~~~~~~~~~~~~~~~~~~~cnt 0')
                        
                    if link_table[tx].iloc[0]>car_cnt:
                        link_list0.append(i)
                        print(link_table, 'i : ', i)
                    # elif link_table[rx].iloc[0]>car_cnt:
                    #     link_list0.append(j)
                    #     print(link_table, 'j : ', j)
                    print(link_list0)

        link_list0 = list(set(link_list0)) #제거 리스트
        print(link_list0)
        
        for i in link_list0:
            link_tr2=link_tr2.drop(i, axis=0) #규칙 적용

        link_tr2.reset_index(drop=True,inplace=True)        #제거 행 리스트 중복 제거
        
        # ###########양방향 링크 리스트
        # link_tr2.reset_index(drop=True,inplace=True) # 인덱스 초기화
        # link_list1=[]
        # for i in range(len(link_tr2.index)):
        #     for j in range(len(link_tr2.index)):
        #         if link_tr2['Callsign'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign'].iloc[j]: # 송신 수신이 서로 각각 같은지
        #             print(link_tr2['Callsign.1'].iloc[i],link_tr2['Callsign'].iloc[i])
        #             link_list1.append(i)
        #             print(link_list1)

        # link_list1 = list(set(link_list1)) #제거 리스트
        # print(link_list1)
        
        # for i in link_list1:
        #     link_tr2=link_tr2.drop(i, axis=0) #규칙 적용

        # link_tr2.reset_index(drop=True,inplace=True)             

        return link_tr2

    def linkDraw(self):
        
        link_result=self.linkCSVopen()
        print(link_result)
        
        nodemap=self.nodeOnMap()
        link_map=folium.FeatureGroup(name='연결 링크',overlay=True).add_to(nodemap)
        
        #변조방식 추천 기능 - 1
        # user_mod, ok = QInputDialog.getText(self, "변조방식", "QAM 신호레벨(dBm)")
        # if ok :
        #     mod=int(user_mod) # 입력 변조방식 값
        # else :
        #     mod=-55 # 변조방식 default 값

        #링크 GUI에 그리기
        for i in range(0,len(link_result.index)):
            # TX : Long Lat / RX : Long1 Lat1
            lat=link_result['Lat'].iloc[i]
            long=link_result['Long'].iloc[i]
            lat1=link_result['Lat.1'].iloc[i]
            long1=link_result['Long.1'].iloc[i]
            node_A=np.array([lat,long])
            node_B=np.array([lat1,long1])
            folium.vector_layers.PolyLine([node_A,node_B], tooltip="QAM", popup="QAM", color='blue').add_to(link_map) #QAM : 툴팁 QAM + color blue
            #변조방식 추천 기능 - 2
            # if link_result['Pr dBm'].iloc[i]>mod:
            #     folium.vector_layers.PolyLine([node_A,node_B], tooltip="QAM", popup="QAM", color='blue').add_to(link_map) #QAM : 툴팁 QAM + color blue
            # elif link_result['Pr dBm'].iloc[i]<mod:
            #     folium.vector_layers.PolyLine([node_A,node_B], tooltip="PSK", popup="PSK", color='red').add_to(link_map) #PSK : 툴팁 PSK + color red

        folium.LayerControl(autoZIndex=True).add_to(nodemap)

        nodemap.save('C:/gui/result_link.html')
        self.web.load(QUrl('C:/gui/result_link.html'))
        
        return link_map

    def ResultBtnClicked(self):
        
        nodemap=self.nodeOnMap()
        self.linkDraw().add_to(nodemap)
        self.covResultBtnClicked().add_to(nodemap)
        folium.LayerControl(autoZIndex=True).add_to(nodemap)

        nodemap.save('C:/gui/result_sum.html')
        self.web.load(QUrl('C:/gui/result_sum.html'))