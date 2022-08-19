from haversine import haversine
from random import *
import math
import glob
import string
import struct
import os


in_file_name = input("EWX 파일명을 입력하세요. : ")  #("G:\\test2222222.EWX")
max_g = input("생성할 파일 수를 입력하세요. : ")  #("G:\\test2222222.EWX")
max_g = int(max_g)
in_file = open(in_file_name, 'r')
all_lines = in_file.readlines()
in_file.close()
number = 0

# centerpoint 좌표 : 37.275897408 / 127.365225015
while number < max_g :
    number+=1
    outfilename = in_file_name[:-4] + "_" + str(number) +".EWX"
    centerpoint = [37.275897408 , 127.365225015]
    # centerpoint = [(37.05121+37.22106)/2 , (127.43689+127.65472)/2]
    random_value = [uniform(37.19109, 37.36022), uniform(127.25606, 127.47514)] # [lat, lon] (19km 범위)

    while haversine(random_value,centerpoint) > 9.5 :
        random_value = [uniform(37.19109, 37.36022), uniform(127.25606, 127.47514)] # [lat, lon] (19km 범위)

    firstpoint = random_value
    print( "첫번째 포인트는 중심과" + str(haversine(firstpoint,centerpoint)) + "km만큼 떨어져있습니다")
    secondpoint=[]
    #find secondpoint
    while (len(secondpoint) != 4):
        random_value = [firstpoint[0]+uniform(-0.003195, 0.003195), firstpoint[1]+uniform(-0.004115, 0.004115)] # [lat, lon]
        if haversine (random_value, centerpoint) > 9.5 :
            continue
        # print(random_value)
        if len(secondpoint) ==0 :
            secondpoint.append(random_value)
            # print(secondpoint)
        else :
            ispossiblepoint = True
            for i in range(len(secondpoint)) :
                print("거리는 :"+str (haversine(random_value,secondpoint[i])) + "km 만큼 떨어져있습니다.")
                if haversine(random_value,secondpoint[i]) < 0.3 : # 300 이내의 포인트이면 배제
                    ispossiblepoint = False
                    print("300m 이내의 포인트입니다. 다시 포인트를 찾으세요")
            if ispossiblepoint :
                secondpoint.append(random_value)
    print(secondpoint)
    for i in range(len(secondpoint)) :
        print( "두번째 포인트는 중심과" + str(haversine(secondpoint[i],centerpoint)) + "km만큼 떨어져있습니다")
        if haversine(secondpoint[i],centerpoint) > 9.85 :
            print("잇츠 패일")

    finalpoint=[]
    for i in secondpoint :
        thirdpoint = []
        while (len(thirdpoint) != 3):
            random_value = [i[0]+uniform(-0.00142, 0.00142), i[1]+uniform(-0.00183, 0.00183)] # [lat, lon]
            if haversine(random_value, centerpoint) > 10:
                continue
            print("세번째 포인트는 중심과" + str(haversine(random_value, centerpoint)) + "km만큼 떨어져있습니다")
            print("세번째 포인트-두번째포인트사이간 거리는" + str(haversine(random_value, i)) + "km만큼 떨어져있습니다")
            thirdpoint.append(random_value)
        finalpoint = finalpoint+thirdpoint

    print(finalpoint)
    print(len(finalpoint))

    out_file = open(outfilename, 'w')
    print("\n\n"+outfilename + "~!~!!~!~!~!~!~!~!")
    for line in all_lines:
        if "<COORD_X>" in line :
            tmp_point = finalpoint.pop()
            # print(line, end="")
            line = "        <COORD_X>"+str(tmp_point[1])+ "</COORD_X>\n"
            print(line, end="")
        if "<COORD_Y>" in line :
            # print(line, end="")
            line = "        <COORD_Y>" + str(tmp_point[0]) + "</COORD_Y>\n"
            print(line)
        out_file.write (line)
    print(len(finalpoint))
    out_file.close()

os.system("pause")