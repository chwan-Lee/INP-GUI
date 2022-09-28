 #-*- coding: utf-8 -*- 

from asyncio.windows_events import NULL
from audioop import reverse
from cmath import nan
from dataclasses import asdict
from email.headerregistry import SingleAddressHeader
from email.policy import default
from http.client import OK
from json import JSONDecoder, decoder
from multiprocessing import Event
import os
from pyexpat import features
from quopri import decodestring
from re import A
from sqlite3 import Cursor, Row
import sys
import subprocess
from xml.dom.minidom import Document
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
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
from jinja2 import Template
import jinja2
import json
from bs4 import BeautifulSoup
import requests
import io
from folium.plugins import Draw
from ast import IsNot, literal_eval
import shutil
import ast



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


#자바 콘솔 출력(폴리곤)을 텍스트로 저장
class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        # coords_dict = json.loads(msg,strict=False)
        # coords = coords_dict['geometry']['coordinates'][0]
        sys.stdout = open('data/polygon.txt', 'w')
        print(msg)
        sys.stdout.close()
        

class App(QWidget):

    def __init__(self):
        super().__init__()
        
        #프레임 설정
        self.TITLE  = "망계획도구"
        self.LEFT   = 150
        self.TOP    = 100
        self.WIDTH  = 1600
        self.HEIGHT = 800
        self.SIZE = 40
        self.setupUI()
                
        #위성 지도 적용
        layer = "Satellite"
        tileType = "jpeg"
        vworld_key="E9283B18-27BB-39EE-A559-F580969D48CD"
        self.map_tile = f"http://api.vworld.kr/req/wmts/1.0.0/{vworld_key}/{layer}/{{z}}/{{y}}/{{x}}.{tileType}"
        self.attr = "Vworld"
        self.name = "위성사진"

        #부대 아이콘 url
        self.node_url1='./img/대형.png'
        self.node_url2='./img/소형.png'
        self.node_url3='./img/부대.png'
        self.node_url4='./img/소형부대.png'
        self.node_url5='./img/중계소.png'
        
        
    def setupUI(self):  #창 제목 및 아이콘
        self.setWindowTitle(self.TITLE)
        self.setWindowIcon(QIcon('./img/favicon.png'))
        self.setGeometry(self.LEFT, self.TOP, self.WIDTH, self.HEIGHT)

        # 로고
        self.lbl_sv_logo = QLabel(self)
        self.lbl_sv_logo.setPixmap(QPixmap('./img/solvit_logo.png'))
        self.lbl_sv_logo.setFixedHeight(50)
        self.lbl_sv_logo.setFixedWidth(140)

        # 위젯 그룹
        groupHL=QGridLayout()
        groupHL.addWidget(self.createHCTRgroup(),0,0)
        groupHL.addWidget(self.createLCTRgroup(),2,0)

        # "종료" 버튼
        self.exitBtn = QPushButton("프로그램 종료")
        self.exitBtn.setFixedHeight(self.SIZE)
        self.exitBtn.clicked.connect(self.exitBtnClicked)
        
        # 시나리오 생성 버튼
        self.newScenBtn=QPushButton("시나리오 파일 생성")
        self.newScenBtn.setFixedHeight(self.SIZE)
        self.newScenBtn.clicked.connect(self.newScenBtnClicked)
        
        # csv 임포팅 버튼
        self.csvOpenBtn=QPushButton("시나리오 파일 열기")
        self.csvOpenBtn.setFixedHeight(self.SIZE)
        self.csvOpenBtn.clicked.connect(self.csvOpenBtnClicked)
        
        # "커버리지 분석" 버튼
        self.covBtn = QPushButton("커버리지 분석")
        self.covBtn.setFixedHeight(self.SIZE)
        self.covBtn.clicked.connect(self.covBtnClicked)

        # "링크 분석" 버튼
        self.linkBtn = QPushButton("링크 연결성 분석")
        self.linkBtn.setFixedHeight(self.SIZE)
        self.linkBtn.clicked.connect(self.linkBtnClicked)

        # "커버리지 출력" 버튼
        self.covResultBtn = QPushButton("커버리지 출력")
        self.covResultBtn.setFixedHeight(self.SIZE)
        self.covResultBtn.setFixedWidth(100)
        self.covResultBtn.clicked.connect(self.covResultBtnClicked)
        
        # "링크 출력(HCTR)" 버튼
        self.HlinkResultBtn = QPushButton("HCTR 링크")
        self.HlinkResultBtn.setFixedHeight(self.SIZE)
        self.HlinkResultBtn.setFixedWidth(100)
        self.HlinkResultBtn.clicked.connect(self.HlinkResultBtnClicked)
        
        # "중계소 배치" 버튼
        self.NodeResultBtn = QPushButton("중계소 배치")
        self.NodeResultBtn.setFixedHeight(self.SIZE)
        self.NodeResultBtn.setFixedWidth(100)
        self.NodeResultBtn.clicked.connect(self.NodeResultBtnClicked)

        # "주파수 할당" 버튼
        self.freqResultBtn = QPushButton("주파수 할당")
        self.freqResultBtn.setFixedHeight(self.SIZE)
        self.freqResultBtn.setFixedWidth(100)
        self.freqResultBtn.clicked.connect(self.freqResultBtnClicked)
        
        # "전체 결과 (HCTR + LCTR)" 버튼
        self.ResultBtn = QPushButton("전체 링크")
        self.ResultBtn.setFixedHeight(self.SIZE)
        self.ResultBtn.setFixedWidth(100)
        self.ResultBtn.clicked.connect(self.ResultBtnClicked)
        
        # "폴리곤 저장" 버튼
        self.addPoly = QPushButton("폴리곤 저장")
        self.addPoly.setFixedHeight(self.SIZE)
        self.addPoly.setFixedWidth(100)
        self.addPoly.clicked.connect(self.polygonSave)
        
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

        lvLay.addWidget(self.newScenBtn)
        lvLay.addWidget(self.csvOpenBtn)
        lvLay.addWidget(self.covBtn)
        lvLay.addWidget(self.linkBtn)
        #lvLay.addStretch(1)
        lvLay.addSpacing(self.SIZE)
        lvLay.addWidget(self.createHCTRgroup())
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
        hbox.addWidget(self.HlinkResultBtn)
        hbox.addWidget(self.ResultBtn)
        hbox.addWidget(self.NodeResultBtn)
        hbox.addWidget(self.freqResultBtn)
        
        hbox.addStretch(1)
        hbox.addWidget(self.addPoly)
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

        # main Layout
        mainLay = QHBoxLayout()
        mainLay.addLayout(lvLay)
        mainLay.addLayout(rvLay)

        # layout 세팅
        self.setLayout(mainLay)
    
    #HCTR 그룹 박스
    def createHCTRgroup(self):
        groupbox=QGroupBox("대용량전송장치(HCTR)")
                
        # "중계소배치 분석(HTZ)" 버튼
        clickbtn4 = QPushButton("중계소 배치 분석")
        clickbtn4.setFixedHeight(self.SIZE)
        clickbtn4.clicked.connect(self.nodeBtnClicked)

        # "주파수 할당 분석(HTZ)" 버튼
        clickbtn5 = QPushButton("주파수 할당 분석")
        clickbtn5.setFixedHeight(self.SIZE)
        clickbtn5.clicked.connect(self.freqBtnClicked)

        # 그룹 박스 구성
        vbox=QVBoxLayout()
        vbox.addWidget(clickbtn4)
        vbox.addWidget(clickbtn5)
        groupbox.setLayout(vbox)

        return groupbox

    #LCTR 그룹 박스
    def createLCTRgroup(self):
        groupbox=QGroupBox("소용량전송장치(LCTR)")

        # "주파수 할당 시작" 버튼
        clickbtn5 = QPushButton("주파수 할당 분석")
        clickbtn5.setFixedHeight(self.SIZE)
        clickbtn5.clicked.connect(self.freqBtnClicked)

        # 그룹 박스 구성
        vbox=QVBoxLayout()
        vbox.addWidget(clickbtn5)
        groupbox.setLayout(vbox)

        return groupbox
    
    #지도맵에 생성된 폴리곤 HTZ 형태로 변환
    def polygonSave(self):
        #파일 읽기
        poly_gui = pd.read_csv("data/polygon.txt",sep=",",header=None)

        ##필요데이터 추출 및 변환(polygon .txt -> 2.VEC -> .VEC)
        #특수 문자 제거
        for i in range(len(poly_gui.columns)):
            poly_gui[i]=poly_gui[i].str.replace('[', repl=r'', regex=True)
            poly_gui[i]=poly_gui[i].str.replace(' ', repl=r'', regex=True)
            poly_gui[i]=poly_gui[i].str.replace(']', repl=r'', regex=True)
            poly_gui[i]=poly_gui[i].str.replace('{', repl=r'', regex=True)
            poly_gui[i]=poly_gui[i].str.replace('}', repl=r'', regex=True)
            if i<3 :
                 poly_gui=poly_gui.drop(i,axis='columns')
        tmp=poly_gui[3].str.split(":") # : 로 구분하여 좌표 추출
        poly_gui[3]=tmp.str.get(1)
        poly_htz = pd.read_csv("outcome/polygon2.VEC",sep=",",header=None) # 
        cal_cnt=len(poly_gui.columns)/2-len(poly_htz)
        
        # 디폴트 포맷을 만들어서 여러개의 폴리곤 좌표 생성시 복사하여 여러 좌표 포맷 생성
        if cal_cnt>0:
            for i in range(int(cal_cnt)):
                poly_htz = poly_htz.append(poly_htz.loc[0], ignore_index = True)
        elif cal_cnt<0:
            for i in range(int(-cal_cnt)):
                poly_htz = poly_htz.drop(poly_htz.index[0])
                
        #변환 후 저장
        for i in range(int(len(poly_gui.columns)/2)):
            poly_htz.iloc[i,3]=float(poly_gui.iloc[:,2*i].values)
            poly_htz.iloc[i,4]=float(poly_gui.iloc[:,2*i+1].values)
            poly_htz.iloc[i,2]=i+1
        poly_htz.to_csv("outcome/polygon.VEC",sep=",",index=False,header=None)
        
    #테이블 더블 클릭후 편집 기능
    def tblCellDblClicked(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print("row: {0}, col: {1}, contents: {2}".format(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text()))
            currentQTableWidgetItem.setForeground(QBrush(QColor(255, 0, 0)))       
    
    #노드 추가 기능
    def addNodeBtnClicked(self):
        self.tableWidget.insertRow(self.tableWidget.currentRow())
        for j in range(2,self.tableWidget.columnCount()) :
            if j ==5 or j == 6 or j==7 or j==8 or j==9 or j== 10 or j==11 or j ==12 or j ==13:
                pass
            else :
                item=QTableWidgetItem(self.tableWidget.item(0,j))
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, j, item)
    
    #노드 삭제 기능
    def delNodeBtnClicked(self):
        #노드 선택해서 삭제
        self.tableWidget.removeRow(self.tableWidget.currentRow())
    
    # 불필요 컬럼 표시 제거 및 '차량수' 컬럼 추가  
    def nodeSet(self): 
        self.tableWidget.hideColumn(7)
        self.tableWidget.hideColumn(10)
        self.tableWidget.hideColumn(11)
        self.tableWidget.hideColumn(12)
        for i in range(14,self.tableWidget.columnCount()):
            self.tableWidget.hideColumn(i)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    #입력받은 테이블에서 HCTR과 LCTR 파일로 분리
    def dbsaveBtnClicked(self):
        #### 테이블 정보로부터 데이터 프레임 생성
        colCnt = self.tableWidget.columnCount()
        rowCnt = self.tableWidget.rowCount()
        headers = [str(self.tableWidget.horizontalHeaderItem(i).text()) for i in range(colCnt) if i>4 or i<2]
        df_list = []
        for row in range(rowCnt):
            df_list2 = []
            for col in range(colCnt):
                    if col == 2 or col == 3 or col == 4:
                        pass
                    else :
                        table_item = self.tableWidget.item(row, col)
                        df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)    
        df = pd.DataFrame(df_list, columns=headers)
        
        #지도 생성
        m = folium.Map(location=[self.tableWidget.item(0,6).text(), self.tableWidget.item(0,5).text()], zoom_start=10)
        folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)
        icon_group= folium.FeatureGroup('부대 배치').add_to(m)
        df_hctr=[]
        df_lctr=[]

        #테이블 정보를 토대로 지도에 아이콘 생성
        for i in range(self.tableWidget.rowCount()):
            callSign = ''
            group =''
            icon_node1 = CustomIcon(self.node_url1,icon_size=(30, 30))
            icon_node2 = CustomIcon(self.node_url2,icon_size=(30, 30))
            icon_node3 = CustomIcon(self.node_url3,icon_size=(30, 30))
            icon_node4 = CustomIcon(self.node_url4,icon_size=(30, 30))
            for j in range(0,10):
                if self.tableHdrLbl[j] == '부대명':
                    callSign = self.tableWidget.item(i,j).text()

                elif self.tableHdrLbl[j] == '경도':
                    lon = self.tableWidget.item(i,j).text()

                elif self.tableHdrLbl[j] == '위도': 
                    lat = self.tableWidget.item(i,j).text()

                elif self.tableHdrLbl[j] == '그룹': 
                    group = self.tableWidget.item(i,j).text()
                    
                elif self.tableHdrLbl[j] == 'HCTR 차량수': 
                    hctr = self.tableWidget.item(i,j).text()
                    
                elif self.tableHdrLbl[j] == 'LCTR MLR': 
                    mlr = self.tableWidget.item(i,j).text()
                    
                elif self.tableHdrLbl[j] == 'LCTR SLR': 
                    slr = self.tableWidget.item(i,j).text()
                else :
                    pass
            if group=='대형노드' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node1).add_to(icon_group)
            elif group=='소형노드' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node2).add_to(icon_group)
            elif group=='대형부대' or group=='중형부대' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node3).add_to(icon_group)
            elif group=='소형부대' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node4).add_to(icon_group)
            else :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=folium.Icon(icon='cloud')).add_to(icon_group)
                
            if int(hctr)>0 :
                df_hctr.append(df.iloc[i])

            elif int(slr)>0:
                df_lctr.append(df.iloc[i])
            if int(mlr)>0 :
                df_lctr.append(df.iloc[i])
        folium.LayerControl(autoZIndex=True).add_to(m)  
              
        # HCTR 파일 만들기
        df_hctr=pd.DataFrame(df_hctr,columns=headers)
        df_hctr.to_csv("./csv/template/INP_hctr.csv")
        # LCTR 파일 만들기
        df_lctr=pd.DataFrame(df_lctr,columns=headers)
        df_lctr.to_csv("./csv/template/INP_lctr.csv")

        #기존 중계소 데이터 초기화
        node_null=pd.read_csv('./outcome/NODE/template/relaynode.csv')
        for i in range(len(node_null)) :#
            node_null=node_null.drop(index=i)
        node_null.to_csv('./outcome/NODE/template/relaynode.csv')

        m.save('C:/gui/result3.html')
        self.web.load(QUrl('C:/gui/result3.html'))
        
    # 시나리오 생성 버톤
    def newScenBtnClicked(self):
        
        # rename col
        data.columns = ['부대명','그룹','HCTR 차량수','LCTR MLR','LCTR SLR','경도','위도','좌표계','안테나 높이 (m)','주파수 (MHz)','송신대역폭 (kHz)','수신대역폭 (kHz)','방위각 (deg)','출력 (W)','송신 안테나 이득 (dB)','수신 안테나 이득 (dB)','송신 손실 (dB)','수신 손실 (dB)','수평 안테나 패턴','수직 안테나 패턴','커버리지 수신감도 (dBm)','수신감도 (dBm)','signal (category)','기울기 (deg)','nfd','freqTx1','freqTx2','freqTx3','freqTx4','freqTx5','freqTx6','freqTx7','freqTx8','freqTx9','freqTx10','freqTx11','freqTx12','freqTx13','freqTx14','freqTx15','freqTx16','Downlink_cx']
        
        #프레임 구성
        self.tableHdrLbl = list(data.columns)
        self.tableWidget.setColumnCount(len(data.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.tableHdrLbl)
        self.tableWidget.setRowCount(1)
        default_format = pd.read_csv('./csv/template/hctr_default.csv')
        m = folium.Map(location=[38, 128], zoom_start=10) # 초기 지도 좌표 임의로 설정
        folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)
        
        # 시나리오 생성시 빈칼럼 설정 
        for i in range(len(default_format.index)):
            for j in range(7,len(default_format.columns)):
                QTableWidgetItem().setTextAlignment(1)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(default_format.iloc[i, j-3])))
            
        self.nodeSet()  #차량수 컬럼
        
        #폴리곤 생성
        draw = Draw(
            draw_options={
                'polyline':False,
                'rectangle':False,
                'polygon':True,
                'circle':False,
                'marker':False,
                'circlemarker':False},
            edit_options={'edit':False})
        m.add_child(draw)
        data1=io.BytesIO()
        page=WebEnginePage(self.web)
        self.web.setPage(page)
        self.web.setHtml(data1.getvalue().decode())
        io.BytesIO.close(data1)
        
        m.save('C:/gui/result2.html')
        self.web.load(QUrl('C:/gui/result2.html'))
    
    #시나리오 열기    
    def csvOpenBtnClicked(self):
        #텍스트 파일 임포팅 -> 지도에 배치
        fname = QFileDialog.getOpenFileName(self, '파일 열기', '', 'csv(*.csv)')
        if fname[0]:
            data = pd.read_csv(fname[0])

            # rename col
            data.columns = ['부대명','그룹','HCTR 차량수','LCTR MLR','LCTR SLR','경도','위도','좌표계','안테나 높이 (m)','주파수 (MHz)','송신대역폭 (kHz)','수신대역폭 (kHz)','방위각 (deg)','출력 (W)','송신 안테나 이득 (dB)','수신 안테나 이득 (dB)','송신 손실 (dB)','수신 손실 (dB)','수평 안테나 패턴','수직 안테나 패턴','커버리지 수신감도 (dBm)','수신감도 (dBm)','signal (category)','기울기 (deg)','nfd','freqTx1','freqTx2','freqTx3','freqTx4','freqTx5','freqTx6','freqTx7','freqTx8','freqTx9','freqTx10','freqTx11','freqTx12','freqTx13','freqTx14','freqTx15','freqTx16','Downlink_cx']

            self.tableHdrLbl = list(data.columns)
        
            self.tableWidget.setColumnCount(len(data.columns))
            self.tableWidget.setHorizontalHeaderLabels(self.tableHdrLbl)
            self.tableWidget.setRowCount(len(data.index))
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            m = folium.Map(location=[data.iloc[0, 6], data.iloc[0, 5]], zoom_start=10)
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
                icon_node4 = CustomIcon(self.node_url4,icon_size=(30, 30))
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
                    folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node1).add_to(icon_group)
                elif group=='소형노드' :
                    folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node2).add_to(icon_group)
                elif group=='대형부대' or group=='중형부대' :
                    folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node3).add_to(icon_group)
                elif group=='소형부대' :
                    folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node4).add_to(icon_group)
                else :
                    folium.Marker([lat, lon], popup=callSign, draggable=True, icon=folium.Icon(icon='cloud')).add_to(icon_group)

            #폴리곤 생성
            draw = Draw(
                draw_options={
                    'polyline':False,
                    'rectangle':False,
                    'polygon':True,
                    'circle':False,
                    'marker':False,
                    'circlemarker':False},
                edit_options={'edit':False})
            m.add_child(draw)
            data1=io.BytesIO()
            page=WebEnginePage(self.web)
            self.web.setPage(page)
            self.web.setHtml(data1.getvalue().decode())
            io.BytesIO.close(data1)

            folium.LayerControl(autoZIndex=True).add_to(m)
            
            m.save('C:/gui/result.html')
            self.web.load(QUrl('C:/gui/result.html'))
            
            #차량수 컬럼추가
            self.nodeSet()  

    #커버리지 분석 기능(HTZ)
    def covBtnClicked(self):
        os.system(".\\batch\\Coverage.bat")
        
    #링크 분석 기능(LCTR, HCTR 개별 DB 접속 및 링크연결분석)
    def linkBtnClicked(self):
        #LCTR DB 연결
        df = pd.read_csv('./csv/template/INP_lctr.csv')
        conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./data/HTZtables.mdb;')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM STATIONX64')

        for row in range(len(df)):            
            query = """INSERT INTO [STATIONX64]([ID], [CALL_SIGN], [ADDRESS], [COORD_X], [COORD_Y],
                                            [TYPE_COORD], [H_ANTENNA], [FREQUENCY], [BANDWIDTH], [BANDWIDTHRX],
                                            [AZIMUTH], [NOMINAL_POWER], [GAIN], [GAINRX], [LOSSES],
                                            [LOSSESRX], [Antenna_nameH], [Antenna_nameV], [THRESHOLD], [THRESHOLDRX],
                                            [Category], [TILT], [nfdname], [D_cx1], [D_cx2], [D_cx3], [D_cx4], 
                                            [D_cx5], [D_cx6], [D_cx7], [D_cx8], [D_cx9], [D_cx10], [D_cx11], [D_cx12], [D_cx13], [D_cx14], [D_cx15], [D_cx16],[Downlink_cx])
                    VALUES({0}, '{1}', '{2}', {3}, {4},
                            '{5}', {6}, {7}, {8}, {9},
                            {10}, {11}, {12}, {13}, {14},
                            {15}, '{16}', '{17}', {18} + 140, {19} + 120, 
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
                        #{18} + 140, {19} + 120 : dBm + 140 = dBu

            cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
        #LCTR 링크 연결
        os.system(".\\batch\\P2P_lctr.bat")
        
        #HCTR DB 접속
        df=[] # 데이터 프레임 초기화
        df = pd.read_csv('./csv/template/INP_hctr.csv')
        conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./data/HTZtables.mdb;')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM STATIONX64')

        for row in range(len(df)):            
            query = """INSERT INTO [STATIONX64]([ID], [CALL_SIGN], [ADDRESS], [COORD_X], [COORD_Y],
                                            [TYPE_COORD], [H_ANTENNA], [FREQUENCY], [BANDWIDTH], [BANDWIDTHRX],
                                            [AZIMUTH], [NOMINAL_POWER], [GAIN], [GAINRX], [LOSSES],
                                            [LOSSESRX], [Antenna_nameH], [Antenna_nameV], [THRESHOLD], [THRESHOLDRX],
                                            [Category], [TILT], [nfdname], [D_cx1], [D_cx2], [D_cx3], [D_cx4], 
                                            [D_cx5], [D_cx6], [D_cx7], [D_cx8], [D_cx9], [D_cx10], [D_cx11], [D_cx12], [D_cx13], [D_cx14], [D_cx15], [D_cx16],[Downlink_cx])
                    VALUES({0}, '{1}', '{2}', {3}, {4},
                            '{5}', {6}, {7}, {8}, {9},
                            {10}, {11}, {12}, {13}, {14},
                            {15}, '{16}', '{17}', {18} + 140, {19} + 120, 
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
                        #{18} + 140, {19} + 120 : dBm + 140 = dBu

            cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
        #HCTR 링크 연결
        os.system(".\\batch\\P2P_hctr.bat")

    #중계소 배치 분석
    def nodeBtnClicked(self):
        
        # GUI -> HTZ (폴리곤)
        self.polyNode() 
        #중계소 배치 분석(HTZ)
        os.system(".\\batch\\Nodes.bat")
        
        #결과 중계소 파일 선택
        node_file=glob.glob('./outcome/NODE/*.CSV')
        nr = pd.read_csv(node_file[0],';',encoding='cp949')

        #결과 파일중 중계소 정보만 추출 
        node_tr=nr.loc[nr['Address']=='New']
        node_tr=node_tr.loc[nr['Address.1']!='New']
        node_tr.reset_index(drop=True,inplace=True)
        
        #중계소 정보 저장
        old_node=pd.read_csv('./outcome/NODE/template/relaynode.csv')
        node_tr2=pd.concat([old_node,node_tr])
        node_tr2.to_csv('./outcome/NODE/template/relaynode.csv')
    
    #주파수 할당 분석
    def freqBtnClicked(self):
        #링크 정보 추출(링크 및 방위각, 기울기)
        link_df=pd.read_csv('./csv/template/hctr_link.csv')
        #중계소 배치 정보 추출
        relay_node=pd.read_csv('./outcome/NODE/template/relaynode.csv')
        #DB 접속을 위한 새로운 포맷
        hctr_trx=pd.read_csv('./csv/template/hctr_freq.csv')
        #(링크 수)개 기지국 임포팅 포맷 만들기
        fre_hctr=pd.concat([link_df,relay_node])
        fre_hctr=fre_hctr.reset_index()
        fre_hctr2=fre_hctr[['Callsign','Address','Long','Lat','Azimuth Tx->Rx (deg)','Tilt Tx->Rx (deg)','Callsign.1','Address.1','Long.1','Lat.1','Azimuth Rx->Tx (deg)','Tilt Rx->Tx (deg)']]
        fre_hctr3=fre_hctr2[['Callsign.1','Address.1','Long.1','Lat.1','Azimuth Rx->Tx (deg)','Tilt Rx->Tx (deg)']]
        fre_hctr3.rename(columns={'Callsign.1':'Callsign','Address.1':'Address','Long.1':'Long','Lat.1':'Lat','Azimuth Rx->Tx (deg)':'Azimuth Tx->Rx (deg)','Tilt Rx->Tx (deg)':'Tilt Tx->Rx (deg)'},inplace=True)
        fre_hctr4=pd.concat([fre_hctr2,fre_hctr3])
        fre_hctr5=fre_hctr4[['Callsign','Address','Long','Lat','Azimuth Tx->Rx (deg)','Tilt Tx->Rx (deg)']]
        fre_hctr5.rename(columns={'Azimuth Tx->Rx (deg)':'Azimuth (deg)','Tilt Tx->Rx (deg)':'Tilt (deg)'},inplace=True)
        fre_hctr5=fre_hctr5.reset_index(drop=True)

        for i in range(len(fre_hctr5)-1):
            hctr_trx=hctr_trx.append(hctr_trx.iloc[0])
        hctr_trx=hctr_trx.reset_index(drop=True)

        input=pd.concat([hctr_trx,fre_hctr5],axis=1)
        input0=input

        hctr_trx=hctr_trx.reset_index(inplace=True, drop=True)
        i_list=input.duplicated('Callsign')

        #기지국 이름 중복에 숫자 붙이기
        for j in range(len(input)):
            if i_list[j]==True:
                input['Callsign'][j]=input0.iloc[j]['Callsign']+str(j%8)
        
        #링크 임포팅 포맷 만들기
        link_num=int(len(input)/2)
        link_get0=input[['Callsign']]
        link_get1=link_get0.iloc[0:link_num,:]
        link_get1.columns=['CS_TX']

        link_get2=link_get0.iloc[link_num:,:]
        link_get2.columns=['CS_RX']
        link_get2=link_get2.reset_index(drop=True)

        link_get=pd.concat([link_get1,link_get2],axis=1)
        
        #각 포맷 파일로 저장
        input.to_csv('./csv/template/freq_input.csv')
        link_get.to_csv('./csv/template/freq_link.csv')
        input=pd.read_csv('./csv/template/freq_input.csv')
        
        #기지국 GUI -> DB 연결 
        conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./data/HTZtables.mdb;')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM STATIONX64')

        for row in range(len(input)):            
            query = """INSERT INTO [STATIONX64]([ID], [CALL_SIGN], [ADDRESS], [COORD_X], [COORD_Y],
                                            [AZIMUTH], [TILT], [TYPE_COORD], [H_ANTENNA], [FREQUENCY], [BANDWIDTH], [BANDWIDTHRX],
                                            [NOMINAL_POWER], [GAIN], [GAINRX], [LOSSES],
                                            [LOSSESRX], [Plan], [Antenna_nameH], [Antenna_nameV], [THRESHOLD], [THRESHOLDRX],
                                            [Category], [nfdname],[WiencodeH],[WiencodeV],[Spacing])
                    VALUES({0}, '{1}', '{2}', {3}, {4}, {5},
                            {6}, '{7}', {8}, {9},
                            {10}, {11}, {12}, {13}, {14},
                            {15}, {16}, '{17}', '{18}', '{19}', 
                            {20}+140, {21}+120, {22}, '{23}','{24}','{25}',{26})""".format(
                            row, input.iloc[row]['Callsign'], input.iloc[row]['Address'], input.iloc[row]['Long'], input.iloc[row]['Lat'],
                        input.iloc[row]['Azimuth (deg)'], input.iloc[row]['Tilt (deg)'],input.iloc[row]['CodeOut'], input.iloc[row]['Antenna (m)'], input.iloc[row]['Frequency MHz'],
                        input.iloc[row]['Tx bandwidth kHz'], input.iloc[row]['Rx bandwidth kHz'], input.iloc[row]['Nominal power (W)'], input.iloc[row]['Tx antenna gain (dB)'], input.iloc[row]['Rx antenna gain (dB)'],
                        input.iloc[row]['Tx losses (dB)'], input.iloc[row]['Rx losses (dB)'], input.iloc[row]['Plan'], input.iloc[row]['Pattern H'], input.iloc[row]['Pattern V'],
                        input.iloc[row]['Coverage threshold (dBm)'], input.iloc[row]['Rx threshold (dBm)'],input.iloc[row]['signal(category)'], input.iloc[row]['nfd'],
                        input.iloc[row]['WiencodeH'], input.iloc[row]['WiencodeV'], input.iloc[row]['Spacing'])
                        #{18} + 140, {19} + 140 : dBm + 140 = dBu

            cursor.execute(query)
        
        cursor.commit()

        cursor.close()
        conn.close()
        #링크 GUI -> HTZ DB 연결
        conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./data/HTZtables.mdb;')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM STATIONX64_LKS')

        for row in range(len(link_get)):            
            query = """INSERT INTO [STATIONX64_LKS]([ID], [CS_TX], [CS_RX], [BITRATE])
                    VALUES({0}, '{1}', '{2}', {3})""".format(
                            row, link_get.iloc[row]['CS_TX'], link_get.iloc[row]['CS_RX'], 0.256)

            cursor.execute(query)
        
        cursor.commit()

        cursor.close()
        conn.close()
        
        #결과 데이터 초기화
        # file='C://Users//INP//AppData//Local//HTZw//TMP//INP//jtemp1000.txt'
        # if os.path.exists(file):
        #     os.remove(file)

        #HTZ 주파수 할당 기능 실행
        os.system(".\\batch\\freq_p2p.bat") 
        
        #결과 파일 저장
        source= r"C:\Users\INP\AppData\Local\HTZw\TMP\INP\jtemp1000.txt"
        if os.path.exists(source) == False:
            source= r"C:\Users\INP\AppData\Local\HTZw\TMP\INP\jtemp2000.txt"
        destination = r"C:\gui\outcome\freq_assign\hctr_freq_assign.txt"
        shutil.copyfile(source,destination)

    #종료 버튼 실행
    def exitBtnClicked(self):
        reply = QMessageBox.question(self, "종료", "프로그램을 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit()
    
    #폴리곤 HTZ 포맷 만들기
    def polyNode(self):
        hctr_list = pd.read_csv('./csv/template/INP_hctr.csv')
        with open("./data/polygon.txt") as f:
             polylist = f.read()

        tmp=polylist.split(":")
        polylist=tmp[5]

        polylist=polylist.replace('}', '', )

        polylist=polylist[:-2]

        polylist=polylist.replace('[','',1 )

        polylist=literal_eval(polylist)

        #폴리곤 영역내의 노드만 추출
        polygon=Polygon(polylist)  
        hctr_list['inside']=hctr_list.apply(lambda x: polygon.contains(Point(x['경도'], x['위도'])), axis=1)

        drop_list=[]
 
        for i in range(len(hctr_list.index)):

            if hctr_list['inside'].iloc[i]==False :
                drop_list.append(i) # 제거 행 리스트

        for i in drop_list:
            hctr_list=hctr_list.drop(i, axis=0) #노드 연결 규칙 적용
        hctr_list.reset_index(drop=True,inplace=True)

        df=hctr_list.drop('inside', axis='columns')
        rowCnt=len(df)
        # 폴리곤 영역 내의 노드만 HTZ DB 연결
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
                            {15}, '{16}', '{17}', {18} + 140, {19} + 120, 
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
        
    #GUI 테이블 내의 노드를 GUI 지도에 업데이트하는 기능(노드 추가 및 삭제 반영)
    def nodeOnMap(self):
        
        m = folium.Map(location=[self.tableWidget.item(0,6).text(), self.tableWidget.item(0,5).text()], zoom_start=10)
        folium.TileLayer(tiles=self.map_tile, attr=self.attr, name=self.name, overlay= true, control=true).add_to(m)
        icon_group= folium.FeatureGroup('분석 결과').add_to(m)
        for i in range(self.tableWidget.rowCount()):
            callSign = ''
            group =''
            icon_node1 = CustomIcon(self.node_url1,icon_size=(30, 30))
            icon_node2 = CustomIcon(self.node_url2,icon_size=(30, 30))
            icon_node3 = CustomIcon(self.node_url3,icon_size=(30, 30))
            icon_node4 = CustomIcon(self.node_url4,icon_size=(30, 30))
            for j in range(0,7):
                if self.tableHdrLbl[j] == '부대명':
                    callSign = self.tableWidget.item(i,j).text()
                elif self.tableHdrLbl[j] == '경도':
                    lon = self.tableWidget.item(i,j).text()
                elif self.tableHdrLbl[j] == '위도':
                    lat = self.tableWidget.item(i,j).text()
                elif self.tableHdrLbl[j] == '그룹':
                    group = self.tableWidget.item(i,j).text()
            if group=='대형노드' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node1).add_to(icon_group)
            elif group=='소형노드' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node2).add_to(icon_group)
            elif group=='대형부대' or group=='중형부대' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node3).add_to(icon_group)
            elif group=='소형부대' :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=icon_node4).add_to(icon_group)       
            else :
                folium.Marker([lat, lon], popup=callSign, draggable=True, icon=folium.Icon(icon='cloud')).add_to(icon_group)       
        
        #폴리곤
        draw = Draw(
            draw_options={
                'polyline':False,
                'rectangle':False,
                'polygon':True,
                'circle':False,
                'marker':False,
                'circlemarker':False},
            edit_options={'edit':False})
        m.add_child(draw)
                
        data1=io.BytesIO()    
        page=WebEnginePage(self.web)
        self.web.setPage(page)
        self.web.setHtml(data1.getvalue().decode())
        io.BytesIO.close(data1)

        folium.LayerControl(autoZIndex=True).add_to(m)
        
        m.save('C:/gui/result_node.html')
        self.web.load(QUrl('C:/gui/result_node.html'))
        
        return (icon_group)

    #커버리지 결과 출력
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
        
        nodemap=self.nodeOnMap()
  
        cov_map=folium.FeatureGroup('커버리지').add_to(nodemap)
        
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
        
    # 링크 결과 출력 HCTR
    def HlinkResultBtnClicked(self):
        self.HlinkDraw()
    
    # 링크 결과 출력 LCTR
    def LlinkResultBtnClicked(self):
        self.LlinkDraw()

    # HCTR 링크 규칙    
    def HlinkCSVopen(self): 
        #링크 파일 선택
        link_file=glob.glob('./outcome/P2P/hctr/*.CSV')
        lr = pd.read_csv(link_file[0],';',encoding='cp949')

        #중복 행 제거 - 멀티 채널
        link_tr=lr.drop_duplicates(['Callsign','Callsign.1'])

        #수신 감도 -77dBm이상 [테스트 -200]
        link_tr2=link_tr.loc[lr['Pr dBm']>-77]

        # 인덱스 초기화
        link_tr2.reset_index(drop=True,inplace=True)

        ###링크 형성 알고리즘###
        
        #####[노드통신소 최대 링크 연결 개수 제한]
        link_tr2.reset_index(drop=True,inplace=True) # 인덱스 초기화
        link_list0=[]
    
        ####노드통신소 최대 링크 연결 개수 제한 - 초기화
        
        ###단방향만 고려하여 중복 제거
        link_list=[]
        for i in range(0,len(link_tr2.index)):
            if link_tr2['Address'].iloc[i]=='소형부대' or link_tr2['Address.1'].iloc[i]=='소형부대':
                link_list.append(i) # 제거 행 리스트
            
            elif link_tr2['Address'].iloc[i]=='소형노드':
                if link_tr2['Address.1'].iloc[i]=='대형부대' or link_tr2['Address.1'].iloc[i]=='대형노드':
                    link_list.append(i) # 제거 행 리스트
                
            elif link_tr2['Address'].iloc[i]=='대형노드':
                if link_tr2['Address.1'].iloc[i]=='대형노드':
                    for j in range(len(link_tr2.index)-i):
                        if(link_tr2['Callsign'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign'].iloc[j]) and j>i:
                            link_list.append(j)
                            pass
            else :
                link_list.append(i) # 제거 행 리스트
        for i in link_list:
            link_tr2=link_tr2.drop(i, axis=0) #노드 연결 규칙 적용   
        
        ###부대 통신소 가장 가까운 노드에 1개만 연결
        link_tr2.reset_index(drop=True,inplace=True)# 인덱스 초기화
        link_list2=[]
        for i in range(0,len(link_tr2.index)):
            if link_tr2['Address'].iloc[i]=='소형노드' and link_tr2['Address.1'].iloc[i]=='중형부대':
                for j in range(0,len(link_tr2.index)):
                    if link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Distance m'].iloc[i]>link_tr2['Distance m'].iloc[j]:
                        link_list2.append(i)
                    elif link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Distance m'].iloc[i]<link_tr2['Distance m'].iloc[j]:
                        link_list2.append(j)
        link_list2 = list(set(link_list2)) #제거 행 리스트 중복 제거
        for i in link_list2:
            link_tr2=link_tr2.drop(i, axis=0) #규칙 적용

        link_tr2.reset_index(drop=True,inplace=True)        #제거 행 리스트 중복 제거
        
        ###소형 노드 통신소 가장 가까운 대형 노드에 1개만 연결
        link_tr2.reset_index(drop=True,inplace=True)# 인덱스 초기화
        link_list2=[]
        for i in range(0,len(link_tr2.index)):
            if link_tr2['Address'].iloc[i]=='대형노드' and link_tr2['Address.1'].iloc[i]=='소형노드':
                for j in range(0,len(link_tr2.index)):
                    if link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Distance m'].iloc[i]>link_tr2['Distance m'].iloc[j]:
                        link_list2.append(i)
                    elif link_tr2['Callsign.1'].iloc[i]==link_tr2['Callsign.1'].iloc[j] and link_tr2['Distance m'].iloc[i]<link_tr2['Distance m'].iloc[j]:
                        link_list2.append(j)
        link_list2 = list(set(link_list2)) #제거 행 리스트 중복 제거
        for i in link_list2:
            link_tr2=link_tr2.drop(i, axis=0) #규칙 적용

        link_tr2.reset_index(drop=True,inplace=True)        #제거 행 리스트 중복 제거
        
        # sort(True 면 대형노드 부터, False면 중형부대 부터 )
        link_tr2.sort_values(['Address.1','Callsign.1'], ascending=False,inplace=True) 
        #print(link_tr2)
        
        #####[노드통신소 최대 링크 연결 개수 제한]
        link_tr2.reset_index(drop=True,inplace=True) # 인덱스 초기화
        link_list0=[]
        link_col=[]
        link_row=['0','1','2'] # 0 : full link, 1: 최대 링크 수, 2 : 연결된 링크 수
        
        for i in range(self.tableWidget.rowCount()):
            link_col.append(self.tableWidget.item(i,0).text())

        link_table = pd.DataFrame(index=link_row,columns=link_col)
        link_table.reset_index()
        link_table=link_table.fillna(0)
        
        for i in range(self.tableWidget.rowCount()):
            link_table.iloc[1,i]=2*int(self.tableWidget.item(i,2).text()) #hctr 차량수
        tx=''
        rx=''   ####노드통신소 최대 링크 연결 개수 제한 - 초기화 
        
        ###최대 링크 연결 제한 - 차량수
        for i in range(len(link_tr2.index)):
            for j in range(self.tableWidget.rowCount()):
                if link_tr2['Callsign.1'].iloc[i]==self.tableWidget.item(j,0).text(): # 0 : 부대명 컬럼
                    tx=link_tr2['Callsign'].iloc[i]
                    rx=link_tr2['Callsign.1'].iloc[i]
                    link_table[tx].iloc[0]=link_table[tx].iloc[0]+1
                    link_table[rx].iloc[0]=link_table[rx].iloc[0]+1
                    
                    if (link_table[tx].iloc[2]>=link_table[tx].iloc[1] or link_table[rx].iloc[2]>=link_table[rx].iloc[1]):
                        link_list0.append(i)
                        
                    elif link_table[tx].iloc[2]<link_table[tx].iloc[1] and link_table[rx].iloc[2]<link_table[rx].iloc[1]:
                        link_table[tx].iloc[2]=link_table[tx].iloc[2]+1
                        link_table[rx].iloc[2]=link_table[rx].iloc[2]+1
                        

        link_list0 = list(set(link_list0)) #제거 리스트
        
        for i in link_list0:
           link_tr2=link_tr2.drop(i, axis=0) #규칙 적용

        link_tr2.reset_index(drop=True,inplace=True)        #제거 행 리스트 중복 제거  
        link_tr2.to_csv('./csv/template/hctr_link.csv') 

        return link_tr2

    #LCTR링크 규칙
    def LlinkCSVopen(self): 
        #링크 파일 선택
        link_file=glob.glob('./outcome/P2P/lctr/*.CSV')
        lr = pd.read_csv(link_file[0],';',encoding='cp949')

        #중복 행 제거 - 멀티 채널
        link_tr=lr.drop_duplicates(['Callsign','Callsign.1'])

        #수신 감도 -77dBm이상 [테스트 -200]
        link_tr2=link_tr.loc[lr['Pr dBm']>-80]

        # 인덱스 초기화
        link_tr2.reset_index(drop=True,inplace=True)

        # ###링크 형성 알고리즘###
        
        # #####[노드통신소 최대 링크 연결 개수 제한]
        link_tr2.reset_index(drop=True,inplace=True) # 인덱스 초기화
        
        ####노드통신소 최대 링크 연결 개수 제한 - 초기화
        
        ###단방향만 고려하여 중복 제거
        link_list=[]
        for i in range(0,len(link_tr2.index)):
            if link_tr2['Address'].iloc[i]!='소형부대':
                link_list.append(i) # 제거 행 리스트
            elif link_tr2['Address'].iloc[i]=='소형부대' and link_tr2['Address.1'].iloc[i]=='소형부대':
                link_list.append(i) # 제거 행 리스트
        for i in link_list:
            link_tr2=link_tr2.drop(i, axis=0) #노드 연결 규칙 적용

        link_tr2.reset_index(drop=True,inplace=True)# 인덱스 초기화
        link_tr2_bk=link_tr2
        # # ### LCTR : 소형부대 통신소 가장 가까운 노드에 1개만 연결
        link_list2=[]
        for i in range(0,len(link_tr2.index)):
            # if link_tr2['Address'].iloc[i]=='소형' and link_tr2['Address.1'].iloc[i]=='중형부대':
            for j in range(0,len(link_tr2.index)):
                if link_tr2['Callsign'].iloc[i]==link_tr2['Callsign'].iloc[j] and link_tr2['Distance m'].iloc[i]>link_tr2['Distance m'].iloc[j]:
                    link_list2.append(i)
                elif link_tr2['Callsign'].iloc[i]==link_tr2['Callsign'].iloc[j] and link_tr2['Distance m'].iloc[i]<link_tr2['Distance m'].iloc[j]:
                    link_list2.append(j)
        link_list2 = list(set(link_list2)) #제거 행 리스트 중복 제거
        for i in link_list2:
            link_tr2=link_tr2.drop(i, axis=0) #규칙 적용
        link_tr2.reset_index(drop=True,inplace=True)        #제거 행 리스트 중복 제거
        
        #####[노드통신소 최대 링크 연결 개수 제한]
        link_tr2.reset_index(drop=True,inplace=True) # 인덱스 초기화
        link_list0=[]
        link_col=[]
        link_row=['0','1','2','3','4'] # 0 : MLR 전체 링크 수, 1: 1섹터(0~89) 링크 수 , 2 : 2섹터(90~179) 링크 수, 3 : 3섹터(180~269) 링크 수, 4 : 4섹터(270~359) 링크 수
        
        for i in range(len(link_tr2.index)):
            if link_tr2['Address.1'].iloc[i] != '소형부대' : 
                link_col.append(link_tr2['Callsign.1'].iloc[i])
        link_col = list(set(link_col))
        link_col.sort()

        link_table = pd.DataFrame(index=link_row,columns=link_col)
        link_table.reset_index()
        link_table=link_table.fillna(0)
    
        tx=''   ####노드통신소 최대 링크 연결 개수 제한 - 초기화 
        
        ###최대 링크 연결 제한 - 섹터별
        for i in range(len(link_tr2.index)):
            tx=link_tr2['Callsign.1'].iloc[i]
            #MLR당 8개 제한
            if link_tr2['Address.1'].iloc[i] != '소형부대' and link_table[tx].iloc[0]<8: #MLR당 8개 제한
                az=link_tr2['Azimuth Rx->Tx (deg)'].iloc[i]
                if az>=0 and az<90 and link_table[tx].iloc[1]<4:    #섹터별 4개 제한
                    link_table[tx].iloc[0]=link_table[tx].iloc[0]+1
                    link_table[tx].iloc[1]=link_table[tx].iloc[1]+1
                    
                elif az>=90 and az<180 and link_table[tx].iloc[2]<4:
                    link_table[tx].iloc[0]=link_table[tx].iloc[0]+1
                    link_table[tx].iloc[2]=link_table[tx].iloc[2]+1
                    
                elif az>=180 and az<270 and link_table[tx].iloc[3]<4:
                    link_table[tx].iloc[0]=link_table[tx].iloc[0]+1
                    link_table[tx].iloc[3]=link_table[tx].iloc[3]+1
                    
                elif az>=270 and az<360 and link_table[tx].iloc[4]<4:
                    link_table[tx].iloc[0]=link_table[tx].iloc[0]+1
                    link_table[tx].iloc[4]=link_table[tx].iloc[4]+1
                else :
                    link_list0.append(i) # LCTR 규칙으로 링크 해제된 목록
            elif link_table[tx].iloc[0]>=8:
                link_list0.append(i) # LCTR 규칙으로 링크 해제된 목록

              
        link_list0 = list(set(link_list0)) #제거 리스트
        
        link_list1=[]
        for i in link_list0: # 링크 연결 해제된 SLR들 목록
            link_list1.append(link_tr2['Callsign'].iloc[i]) 
        
        for i in link_list0:
           link_tr2=link_tr2.drop(i, axis=0) #규칙 적용

        link_tr2.reset_index(drop=True,inplace=True)        #제거 행 리스트 중복 제거  
        
        # 섹터 제한된 소형 부대 다시 MLR에 붙이기
        slr_index=-1 
        for k in link_list1:
            near_mlr_distance=35000 #max_distance
            for i in range(0,len(link_tr2_bk.index)):
                if link_tr2_bk['Callsign'].iloc[i]==k:
                    mlr=link_tr2_bk['Callsign.1'].iloc[i]
                 
                    if near_mlr_distance>link_tr2_bk['Distance m'].iloc[i] and link_table[mlr].iloc[0]<8 and (link_table[mlr].iloc[1]<4 and link_table[mlr].iloc[2]<4 and link_table[mlr].iloc[3]<4 and link_table[mlr].iloc[4]<4):
                        near_mlr_distance=link_tr2_bk['Distance m'].iloc[i]
                        slr_index=i  
                    
            link_tr2=pd.concat([link_tr2,link_tr2_bk.iloc[[slr_index]]],ignore_index=False)
            link_table[mlr].iloc[0]=link_table[mlr].iloc[0]+1

        link_tr2.reset_index(drop=True,inplace=True)   

        return link_tr2

    def HlinkDraw(self):
        
        link_result=self.HlinkCSVopen()
        
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
        
        #폴리곤 
        draw = Draw(
            draw_options={
                'polyline':False,
                'rectangle':False,
                'polygon':True,
                'circle':False,
                'marker':False,
                'circlemarker':False},
            edit_options={'edit':False})
        nodemap.add_child(draw)
        
        data1=io.BytesIO()
        
        page=WebEnginePage(self.web)
        self.web.setPage(page)
        self.web.setHtml(data1.getvalue().decode())
        io.BytesIO.close(data1)

        folium.LayerControl(autoZIndex=True).add_to(nodemap)

        nodemap.save('C:/gui/result_link.html')
        self.web.load(QUrl('C:/gui/result_link.html'))
        link_result.to_csv('C:\\gui\\outcome\\result.csv') #링크 저장

        return link_map
    
    def LlinkDraw(self):
        
        link_result=self.LlinkCSVopen()
        
        nodemap=self.nodeOnMap()
        link_map=folium.FeatureGroup(name='연결 링크',overlay=True).add_to(nodemap)
        
        #링크 GUI에 그리기
        for i in range(0,len(link_result.index)):
            # TX : Long Lat / RX : Long1 Lat1
            lat=link_result['Lat'].iloc[i]
            long=link_result['Long'].iloc[i]
            lat1=link_result['Lat.1'].iloc[i]
            long1=link_result['Long.1'].iloc[i]
            node_A=np.array([lat,long])
            node_B=np.array([lat1,long1])
            folium.vector_layers.PolyLine([node_A,node_B], tooltip="QAM", popup="QAM", color='yellow').add_to(link_map) #QAM : 툴팁 QAM + color blue

        folium.LayerControl(autoZIndex=True).add_to(nodemap)

        nodemap.save('C:/gui/result_link.html')
        self.web.load(QUrl('C:/gui/result_link.html'))
        link_result.to_csv('C:\\gui\\outcome\\result.csv') #링크 저장

        return link_map


    def ResultBtnClicked(self):
        
        nodemap=self.nodeOnMap()
        self.HlinkDraw().add_to(nodemap)
        self.LlinkDraw().add_to(nodemap)

        draw = Draw(
            draw_options={
                'polyline':False,
                'rectangle':False,
                'polygon':True,
                'circle':False,
                'marker':False,
                'circlemarker':False},
            edit_options={'edit':False})
        nodemap.add_child(draw)
        
        data1=io.BytesIO()
        
        page=WebEnginePage(self.web)
        self.web.setPage(page)
        self.web.setHtml(data1.getvalue().decode())
        io.BytesIO.close(data1)
        folium.LayerControl(autoZIndex=True).add_to(nodemap)

        nodemap.save('C:/gui/result_sum.html')
        self.web.load(QUrl('C:/gui/result_sum.html'))
        
        return nodemap

    def NodeResultBtnClicked(self):
        
        nodemap=self.nodeOnMap()
        self.HlinkDraw().add_to(nodemap)
        self.LlinkDraw().add_to(nodemap)
        relaynode_map=folium.FeatureGroup(name='분석 결과',overlay=True).add_to(nodemap)
        #링크 파일 선택
        node_tr=pd.read_csv('./outcome/NODE/template/relaynode.csv')

        #링크 GUI에 그리기
        for i in range(0,len(node_tr.index)):
            icon_node5 = CustomIcon(self.node_url5,icon_size=(30, 30))
            # TX : Long Lat / RX : Long1 Lat1
            callsign=node_tr['Callsign'].iloc[i]
            lat=node_tr['Lat'].iloc[i]
            long=node_tr['Long'].iloc[i]
            lat1=node_tr['Lat.1'].iloc[i]
            long1=node_tr['Long.1'].iloc[i]
            node_A=np.array([lat,long])
            node_B=np.array([lat1,long1])
            folium.vector_layers.PolyLine([node_A,node_B], tooltip="QAM", popup="QAM", color='blue').add_to(relaynode_map) #QAM : 툴팁 QAM + color blue
            folium.Marker([lat, long], popup=callsign, draggable=True,icon=icon_node5).add_to(relaynode_map)
        
        draw = Draw(
            draw_options={
                'polyline':False,
                'rectangle':False,
                'polygon':True,
                'circle':False,
                'marker':False,
                'circlemarker':False},
            edit_options={'edit':False})
        nodemap.add_child(draw)
        
        data1=io.BytesIO()
        
        page=WebEnginePage(self.web)
        self.web.setPage(page)
        self.web.setHtml(data1.getvalue().decode())
        io.BytesIO.close(data1)
                
        folium.LayerControl(autoZIndex=True).add_to(nodemap)
        nodemap.save('C:/gui/result_sum.html')
        self.web.load(QUrl('C:/gui/result_sum.html'))
        
    def freqResultBtnClicked(self):  
        #결과 파일 읽기  
        with open("./outcome/freq_assign/hctr_freq_assign.txt") as f:
             freqlist = f.read()
        f.close()
        
        #출력하기 위한 포맷 변경
        tmp=freqlist.split("\n\n")
        tmp=io.StringIO(tmp[1])
        
        result=pd.read_csv(tmp,sep=";")
        
        result1=result[['Callsign','Address','Assigned Tx frequency (MHz)','Assigned Rx frequency (MHz)']]
        
        result1.columns=['부대명','그룹','송신 주파수','수신 주파수']
        result1=result1.sort_values(['부대명','그룹'],ascending=True)
        
        freq_info=str(result1)
        # 결과 출력
        QMessageBox.information(self, "주파수 할당 결과", freq_info)