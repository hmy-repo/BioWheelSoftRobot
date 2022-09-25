import argparse
from calendar import c
from glob import glob
from json.tool import main
from lib2to3.pgen2.token import EQUAL
import re
from xdrlib import Packer
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
import time
from crawlrobot.crawlrobot import CrawlRobot
from pathlib import Path
import os
from datetime import datetime
import serial
import time

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

def increment_path(path, exist_ok=False, sep='', mkdir=False):
    # Increment file or directory path, i.e. runs/exp --> runs/exp{sep}2, runs/exp{sep}3, ... etc.
    path = Path(path)  # os-agnostic
    if path.exists() and not exist_ok:
        path, suffix = (path.with_suffix(''), path.suffix) if path.is_file() else (path, '')

        # Method 1
        for n in range(2, 9999):
            p = f'{path}{sep}{n}{suffix}'  # increment path
            if not os.path.exists(p):  #
                break
        path = Path(p)

    if mkdir:
        path.mkdir(parents=True, exist_ok=True)  # make directory

    return path

def save_img_picture(img):
    now = datetime.now().strftime('%m%d_%H-%M-%S-%f')[:-4]
    now = Path(now)
    filename = Path(now.name + ".jpg")
    save_path = str(save_dir / filename.name)
    cv2.imwrite(save_path, img)

def main_imshow():
    global img
    cv2.imshow("crawlrobot img", img)
    save_img_picture(img)

def main_detect():
    global img, img_name_i, save_dir
    cv2.imshow("crawlrobot img", img)
    img = crawlrobot.camera.cam_cap_img()
    # print("img.cols= ", end= '')
    # print(np.size(img, 1))
    # print("img.rows= ", end= '')
    # print(np.size(img, 0))
    outputs = crawlrobot.camera.cam_detect(img)
    img = crawlrobot.camera.postprocess(img, outputs)
    save_img_picture(img)

def readActSts():
    while True:
        main_imshow() 
        # main_detect()
        arduino.write(crawlrobot.cmdserial.PC_GET_ACT_STS.encode('utf-8'))   
        # time.sleep(0.020)
        printonce = False
        timeout_flag = False
        print("readActSts()")
        timeout_start = time.time()
        while arduino.in_waiting <= 0:
            if not printonce:
                print("inwaiting")
                printonce = True
            # main_imshow() # main_detect()
            time.sleep(0.010)
            timeout_period = time.time() - timeout_start
            # print("timeout_period = {0}".format(timeout_period))
            if timeout_period > 1:
                print("time out")
                arduino.reset_output_buffer()
                # readActSts()
                timeout_flag = True
                print("time out end")
                break
        # time.sleep(.2)
        if timeout_flag == False:
            break

    ActSts = arduino.readline()
    print("ActSta = ", end='')
    print(ActSts)
    return ActSts

def isActSts_FREE():
    if readActSts() == b'FREE\n':
        return True
    return False 

def isActSts_WORKING():
    if readActSts() == b'WORKING\n':
        return True
    return False
    
def isActSts_PACING():
    if readActSts() == b'PACING\n':
        return True
    return False

def isActSts_PACINGFREE():
    if readActSts() == b'PACINGFREE\n':
        return True
    return False

def isTargetFound(target):
    print("isTargetFound body")
    main_detect()
    objs_img = crawlrobot.camera.get_all_objs_pos()
    print(objs_img)
    # 没有检测到目标
    if target.name not in objs_img.keys(): 
        return {'found':False, 'pos':0}
    # 如果检测到目标, 获取目标中心位置
    if target.name in objs_img.keys(): 
        pos = objs_img[target.name][2]
        return {'found':True, 'pos':pos}

def repeatNtimesTargetFound(Ntimes, target):
    global resTargetFound
    for i in range(Ntimes): # 为了保证稳定,避免偶尔检测不到问题
        resTargetFound = isTargetFound(target) #更新状态
        print("resTargetFound = {0}".format(resTargetFound))
        print("repeattimes = {0}".format(i))
        if resTargetFound['found']:
            return
    return

def paceRight(target):
    global resTargetFound
    print("paceRight body")
    while not isActSts_FREE() and not isActSts_PACINGFREE(): # Actuator非Free或者非PaceFree状态时,等待
        print("paceRight body begin loop...")
        main_detect()
    # resTargetFound = isTargetFound(target)
    repeatNtimesTargetFound(3, target)
    if not resTargetFound['found']:
        print("paceRight body target not found")
        return 
    if resTargetFound['found']: #TODO 注意pace过程中连续情况下气压数值递增
        while resTargetFound['found'] and resTargetFound['pos'] > target.centerMostRight: #0.5: 目标偏右时,循环pace
            print("paceRight body found repeat")
            # print("resTargetFound'found':{0}, 'pos':{1} --- {2}.centerMostRight = {3}".format(resTargetFound['found'], resTargetFound['pos'], target.name, target.centerMostRight))
            arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["PaceRight"].encode('utf-8'))
            time.sleep(0.020) #main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
            # print("paceRight debug --------------")
            while not isActSts_PACINGFREE(): # Actuator在非PaceFree状态时,等待
                main_imshow() # main_detect() 
            # print("paceRight debug ---------end end -----")
            # while True:
            #     time.sleep(23333)
            # resTargetFound = isTargetFound(target) #更新状态
            repeatNtimesTargetFound(3, target)
        print("resTargetFound in loop = {0}".format(resTargetFound))
        arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["PaceEnd"].encode('utf-8')) # Pace结束时需要清除Pace各标志
        # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
        time.sleep(0.020)
        while not isActSts_FREE(): # 等待Pace结束
            time.sleep(0.005)
        # repeatNtimesTargetFound(3, target) #消除0.4的影响,实际驱动器会回弹
        print("resTargetFound finish loop = {0}".format(resTargetFound))

def paceLeft(target):
    global resTargetFound
    print("paceLeft body")
    while not isActSts_FREE() and not isActSts_PACINGFREE(): # Actuator非Free或者非PaceFree状态时,等待
        print("paceLeft body begin loop...")
        main_detect()
    resTargetFound = isTargetFound(target)
    if not resTargetFound['found']:
        print("paceLeft body target not found")
        return 
    if resTargetFound['found']: #TODO 注意pace过程中连续情况下气压数值递增
        while resTargetFound['found'] and resTargetFound['pos'] < target.centerMostLeft: # 0.5: 目标偏左时,循环pace
            print("paceLeft body found repeat")
            # print("resTargetFound 'found':{0}, 'pos':{1} --- {2}.centerMostLeft = {3}".format(resTargetFound['found'], resTargetFound['pos'], target.name, target.centerMostLeft))
            arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["PaceLeft"].encode('utf-8'))
            time.sleep(0.020) #main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
            while not isActSts_PACINGFREE(): # Actuator在非PaceFree状态时,等待
                main_imshow()# main_detect() #  
            # resTargetFound = isTargetFound(target) #更新状态
            repeatNtimesTargetFound(3, target)
        print("resTargetFound in loop = {0}".format(resTargetFound))
        arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["PaceEnd"].encode('utf-8')) # Pace结束时需要清除Pace各标志
        # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
        time.sleep(0.020)
        while not isActSts_FREE(): # 等待Pace结束
            time.sleep(0.005)
        # repeatNtimesTargetFound(3, target) #消除0.6的影响,实际驱动器会回弹
        print("resTargetFound finish loop = {0}".format(resTargetFound))

def isTargetInRange(target):
    # global blindArea
    main_detect()
    arduino.write(crawlrobot.cmdserial.PC_GET_TOF_DIST.encode('utf-8'))     
    while arduino.in_waiting <= 0: 
        # main_detect()   # 100ms 用 pass 是67ms
        time.sleep(0.010)
    dist_str = arduino.readline() # 100ms
    # print("dist_str = ", end='')
    # print(dist_str)
    dist_avg = int(dist_str)
    print("dist_avg = ", end = '')
    print(dist_avg)
    if target.name == "Right Obstacle":
        if dist_avg < 200: # mm
            print("target dist_avg < 180")
            return {'inRange':True, 'dist':dist_avg}
        else:
            if dist_avg < (200+200):
                target.blindArea = True
            else:
                target.blindArea = False
            return {'inRange':False, 'dist':dist_avg}
    elif target.name == "Stair Climbing":
        if dist_avg < 300: # mm
            return {'inRange':True, 'dist':dist_avg}
        else:
            if dist_avg < (300+50):
                target.blindArea = True
            else:
                target.blindArea = False
            return {'inRange':False, 'dist':dist_avg}
    elif target.name == "Left Turn":
        if dist_avg < 300: # mm
            return {'inRange':True, 'dist':dist_avg}
        else:
            if dist_avg < (300+50):
                target.blindArea = True
            else:
                target.blindArea = False
            return {'inRange':False, 'dist':dist_avg}
    elif target.name == "Narrow Lane":
        if dist_avg < 300: # mm
            return {'inRange':True, 'dist':dist_avg}
        else:
            if dist_avg < (300+300):
                target.blindArea = True
            else:
                target.blindArea = False
            return {'inRange':False, 'dist':dist_avg}
    else:
        return {'inRange':False, 'dist':dist_avg}

def GeckModeCrawl():
    starttime1 = time.time()
    print("GeckModeCrawl()")
    while not isActSts_FREE(): # Actuator非Free状态时,等待
        main_detect()
    print("starttime_1 = {0}".format(time.time()-starttime1))
    arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["GeckoMode"].encode('utf-8'))
    # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
    time.sleep(0.020)
    while not isActSts_FREE(): # Actuator非Free状态时,等待
        main_detect()

def InchwormModeCrawl():
    print("InchwormModeCrawl()")
    while not isActSts_FREE(): ## Actuator非Free状态时,等待
        main_detect()
    arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["InchwormMode"].encode('utf-8'))
    # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
    time.sleep(0.020)
    while not isActSts_FREE(): # Actuator非Free状态时,等待
        main_detect()


def ObstacleCrawl():
    starttime1 = time.time()
    print("ObstacleCrawl()")
    while not isActSts_FREE(): # Actuator非Free状态时,等待
        main_detect()
    print("starttime_1 = {0}".format(time.time()-starttime1))
    arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["GeckoMode"].encode('utf-8'))
    # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
    time.sleep(0.020)
    while not isActSts_FREE(): # Actuator非Free状态时,等待
        main_detect()

def StairCrawl():
    print("StairCrawl()")
    while not isActSts_FREE(): # Actuator非Free状态时,等待
        main_detect()
    # print("starttime_1 = {0}".format(time.time()-starttime1))
    arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["ClimbStairMode"].encode('utf-8'))
    main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
    # time.sleep(0.020)
    while not isActSts_FREE(): ## Actuator非Free状态时,等待
        main_detect()
    print("StairCrawl()---End")

def TurnCrawl():
    print("TurnCrawl()")
    pass

def SlitCrawl():
    print("SlitCrawl()")
    while not isActSts_FREE(): ## Actuator非Free状态时,等待
        main_detect()
    arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["InchwormMode"].encode('utf-8'))
    # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
    time.sleep(0.020)
    while not isActSts_FREE(): ## Actuator非Free状态时,等待
        main_detect()
    print("SlitCrawl()---End")

class Target:
    def __init__(self, name, centerMostLeft = 0.5, centerMostRight = 0.5, blindArea = False) -> None:
        self.name = name
        self.centerMostLeft = centerMostLeft
        self.centerMostRight = centerMostRight
        self.blindArea = blindArea


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--imgpath', type=str, default='img/000139.jpg', help="image path")
    parser.add_argument('--objThreshold', default=0.4, type=float, help='object confidence')
    parser.add_argument('--confThreshold', default=0.4, type=float, help='class confidence')
    parser.add_argument('--nmsThreshold', default=0.4, type=float, help='nms iou thresh')
    args = parser.parse_args()

    targets = (Target("Narrow Lane", centerMostLeft = 0.47, centerMostRight = 0.68), \
                Target("Left Turn", centerMostLeft = 0.35, centerMostRight = 0.65), \
                Target("Stair Climbing", centerMostLeft = 0.35, centerMostRight = 0.65), \
                Target("Right Obstacle", centerMostLeft = 0.40, centerMostRight = 0.60), \
                Target("None"))

    cv2.startWindowThread()
    
    crawlrobot = CrawlRobot(args)
    crawlrobot.camera.cam_start()
    global img, resTargetFound
    global img_name_i 
    img_name_i = 0 #输出图片名称
    global save_dir
    save_dir = increment_path(Path("/home/mao/Desktop/results/picture"), exist_ok=False)  # increment run
    (save_dir).mkdir(parents=True, exist_ok=True)  # make dir
    img = crawlrobot.camera.cam_cap_img()
    target_index = 0
    target = targets[target_index]
    
    # -------------窄缝开始----------------
    flag_crawl = False
    target_lost_count = 0

    while True:
        # # test SlitCrawl()
        # while True:
        #     # SlitCrawl()
        #     for i in range(1):
        #         main_detect()
        #         print("SlitCrawl()")
        #         while not isActSts_FREE(): ## Actuator非Free状态时,等待
        #             main_detect()
        #         arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["ClimbStairMode"].encode('utf-8'))
        #         # arduino.write(crawlrobot.cmdserial.PC_GET_TOF_DIST.encode('utf-8'))
                
        #         # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
        #         time.sleep(0.020)
        #         # while not isActSts_FREE(): ## Actuator非Free状态时,等待
        #         #     main_detect()
        #         print("SlitCrawl()---End")
        #     while True:
        #         print("ending.......")
        #         time.sleep(23444)
        
        # #test dist
        # while True:
        #     main_detect()
        #     arduino.write(crawlrobot.cmdserial.PC_GET_TOF_DIST.encode('utf-8'))     
        #     while arduino.in_waiting <= 0: 
        #         # main_detect()   # 100ms 用 pass 是67ms
        #         # print("sleep")
        #         time.sleep(0.010)
        #     dist_str = arduino.readline() # 100ms
        #     print("dist_str = ", end='')
        #     print(dist_str)
        #     dist_avg = int(dist_str)
        #     print("dist_avg = ", end = '')
        #     print(dist_avg)
        #     print("end")

        # # test serial
        # while True:
        #     arduino.write("123\n".encode('utf-8'))
        #     # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
        #     time.sleep(0.020)
        #     print("on")
        #     time.sleep(2)
        #     arduino.write("456\n".encode('utf-8'))
        #     # main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数
        #     time.sleep(0.020)
        #     time.sleep(2)
        #     print("off")

        # #test main_detect() endure period
        # timePeriodAve = 0
        # timeSum = 0
        # timeIndex = 0
        # while True:
        #     startTime = time.time()
        #     main_detect()
        #     timePeriod = time.time()-startTime
        #     timeSum = timeSum + timePeriod
        #     timeIndex = timeIndex + 1
        #     if timeIndex == 20:
        #         timePeriodAve = timeSum/timeIndex
        #         print(timePeriodAve)
        #         timePeriodAve = 0
        #         timeSum = 0
        #         timeIndex = 0

        #     # print("main_detect time = {0}".format(time.time()-startTime))

        # new for final project --begin-- without distance detect first
        main_detect()
        if flag_crawl == True and target_lost_count > 6:
            print("target_lost_count = {0}".format(target_lost_count))
            break
        else:
            print("1.---while isActSts_WORKING().{0}:---".format(target.name))
            # Actuator 是否在工作?
            while isActSts_WORKING() or isActSts_PACING(): # 如果Actuator在工作, 等待
                print("hell")
                
            print("2.---resTargetFound = isTargetFound({0})---".format(target.name))
            # 是否检测到目标?
            resTargetFound = isTargetFound(target) #没有找到返回false和pos=0,找到返回true和pos;返回字典,{'found':true, 'pos':0}
            if not resTargetFound['found']:
                while not resTargetFound['found']: # 此处为查找目标
                    print("target not found")
                    target_lost_count = target_lost_count + 1
                    break # TODO 如果没有目前不执行动作,返回到主循环
                continue
            print("3.---while resTargetFound['pos'] < centerMostLeft or resTargetFound['pos'] > centerMostRight:---")
            # 目标是否在正中? 
            # print("{0}.centerMostLeft = {1}".format(target.name, target.centerMostLeft))
            # print("{0}.centerMostRight = {1}".format(target.name, target.centerMostRight))
            while resTargetFound['found'] and (resTargetFound['pos'] < target.centerMostLeft or resTargetFound['pos'] > target.centerMostRight):
                print("resTargetFound main_0 = {0}".format(resTargetFound))
                if resTargetFound['pos'] < target.centerMostLeft: # 偏左
                    # print("resTargetFound['pos'] = {0} -----{1}.centerMostLeft = {2}".format(resTargetFound['pos'], target.name, target.centerMostLeft))
                    paceLeft(target)
                    print("resTargetFound main_1 = {0}".format(resTargetFound))
                elif resTargetFound['pos'] > target.centerMostRight: # 偏右
                    # print("resTargetFound['pos'] = {0} -----{1}.centerMostRight = {2}".format(resTargetFound['pos'], target.name, target.centerMostRight))
                    paceRight(target)
                    print("resTargetFound main_2 = {0}".format(resTargetFound))
                else:
                    if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                        break    #如果没有找到目标,跳出
                    # continue
            if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                continue    #如果没有找到目标,返回到主循环
            SlitCrawl()
            # while not isActSts_FREE(): ## Actuator非Free状态时,等待
            #     main_detect()
            # for i in range(30):
            #     main_detect()
            # time.sleep(3)
            flag_crawl = True
            target_lost_count = 0
            continue # 爬行后,返回到主循环
    
    while isActSts_WORKING() or isActSts_PACING(): #单片机中执行完走路程序后才能测距.
        time.sleep(0.020)
    retTargetInRange = isTargetInRange(target) 
    while not retTargetInRange['inRange']:
        SlitCrawl()
        print("error here ---------")
        # while not isActSts_FREE(): ## Actuator非Free状态时,等待
        #     main_detect()
        # for i in range(30):
        #     main_detect()
        # time.sleep(3)
        retTargetInRange = isTargetInRange(target)
   
        # new for final project --end-- without distance detect first 
    
        # main_detect()
        # print("1.---while isActSts_WORKING().{0}:---".format(target.name))
        # # Actuator 是否在工作?
        # while isActSts_WORKING() or isActSts_PACING(): # 如果Actuator在工作, 等待
        #     print("hell")
            
        # print("2.---resTargetFound = isTargetFound({0})---".format(target.name))
        # # 是否检测到目标?
        # starttime = time.time()
        # # global resTargetFound
        # resTargetFound = isTargetFound(target) #没有找到返回false和pos=0,找到返回true和pos;返回字典,{'found':true, 'pos':0}
        # if not target.blindArea:
        #     if not resTargetFound['found']:
        #         while not resTargetFound['found']: # 此处为查找目标
        #             print("target not found")
        #             break # TODO 如果没有目前不执行动作,返回到主循环
        #         continue
        #     print("3.---while resTargetFound['pos'] < centerMostLeft or resTargetFound['pos'] > centerMostRight:---")
        #     # 目标是否在正中? 
        #     # print("{0}.centerMostLeft = {1}".format(target.name, target.centerMostLeft))
        #     # print("{0}.centerMostRight = {1}".format(target.name, target.centerMostRight))
        #     while resTargetFound['pos'] < target.centerMostLeft or resTargetFound['pos'] > target.centerMostRight:
        #         print("resTargetFound main_0 = {0}".format(resTargetFound))
        #         if resTargetFound['pos'] < target.centerMostLeft: # 偏左
        #             # print("resTargetFound['pos'] = {0} -----{1}.centerMostLeft = {2}".format(resTargetFound['pos'], target.name, target.centerMostLeft))
        #             paceLeft(target)
        #             print("resTargetFound main_1 = {0}".format(resTargetFound))
        #         elif resTargetFound['pos'] > target.centerMostRight: # 偏右
        #             # print("resTargetFound['pos'] = {0} -----{1}.centerMostRight = {2}".format(resTargetFound['pos'], target.name, target.centerMostRight))
        #             paceRight(target)
        #             print("resTargetFound main_2 = {0}".format(resTargetFound))
        #         else:
        #             if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
        #                 break    #如果没有找到目标,跳出
        #             # continue
        #         # if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
        #         #     break    #如果没有找到目标,跳出
        #     if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
        #         continue    #如果没有找到目标,返回到主循环
        # print("4.---retTargetInRange = isTargetInRange({0})---".format(target.name))
        # # 是否到达目标?
        # # while isActSts_WORKING() or isActSts_PACING(): #单片机中执行完走路程序后才能测距.
        # #     time.sleep(0.020)
        # # time.sleep(1)
        # retTargetInRange = isTargetInRange(target) # 不在变形范围内=false和dist,在变形范围=true和dist; {'inRange':true, 'dist':10}
        # if not retTargetInRange['inRange']:
        #     # 距离目标较远,根据目标确定爬行方式
        #     if target.name == "Narrow Lane":
        #         print("during time = {0}".format(time.time()-starttime))
        #         SlitCrawl()
        #     continue # 爬行后,返回到主循环
        # #TODO 在变形范围内需要不同的变形机制
        # # if target.name == "Narrow Lane":
        # #     print("target Left Turn right common")
        # #     for i in range(3):
        # #         arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["TurnRightCom"].encode('utf-8'))
        # #         main_detect() # 等会
        # #         while not isActSts_FREE():
        # #             main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
            
        # # if target.name == "Stair Climbing":
        # #     pass

        # # if target.name == "Left Turn":
        # #     pass
        # # if target.name == "Narrow Lane":
        # #     for i in range(3):
        # #         arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["InchwormMode"].encode('utf-8'))
        # #         main_detect() # 等会
        # #         while not isActSts_FREE():
        # #             main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
        # #         time.sleep(1)

    # TODO 更新target
    target_index = target_index + 1
    target = targets[target_index]
    # break

        # if target.name == "None":
        #     while True:
        #         time.sleep(1)
        #         print("program stop...")
    print("Slit End ------")
    # -------------窄缝结束----------------

    # -------------拐弯开始----------------
    while True:
        main_detect()
        print("1.---while isActSts_WORKING().{0}:---".format(target.name))
        # Actuator 是否在工作?
        while isActSts_WORKING() or isActSts_PACING(): # 如果Actuator在工作, 等待
            print("hell")
            
        print("2.---resTargetFound = isTargetFound({0})---".format(target.name))
        # 是否检测到目标?
        starttime = time.time()
        # global resTargetFound
        resTargetFound = isTargetFound(target) #没有找到返回false和pos=0,找到返回true和pos;返回字典,{'found':true, 'pos':0}
        if not target.blindArea:
            if not resTargetFound['found']:
                while not resTargetFound['found']: # 此处为查找目标
                    print("target not found")
                    break # TODO 如果没有目前不执行动作,返回到主循环
                continue
            print("3.---while resTargetFound['pos'] < centerMostLeft or resTargetFound['pos'] > centerMostRight:---")
            # 目标是否在正中? 
            # print("{0}.centerMostLeft = {1}".format(target.name, target.centerMostLeft))
            # print("{0}.centerMostRight = {1}".format(target.name, target.centerMostRight))
            while resTargetFound['found'] and (resTargetFound['pos'] < target.centerMostLeft or resTargetFound['pos'] > target.centerMostRight):
                print("resTargetFound main_0 = {0}".format(resTargetFound))
                if resTargetFound['pos'] < target.centerMostLeft: # 偏左
                    # print("resTargetFound['pos'] = {0} -----{1}.centerMostLeft = {2}".format(resTargetFound['pos'], target.name, target.centerMostLeft))
                    paceLeft(target)
                    print("resTargetFound main_1 = {0}".format(resTargetFound))
                elif resTargetFound['pos'] > target.centerMostRight: # 偏右
                    # print("resTargetFound['pos'] = {0} -----{1}.centerMostRight = {2}".format(resTargetFound['pos'], target.name, target.centerMostRight))
                    paceRight(target)
                    print("resTargetFound main_2 = {0}".format(resTargetFound))
                else:
                    if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                        break    #如果没有找到目标,跳出
                    # continue
                # if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                #     break    #如果没有找到目标,跳出
            if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                continue    #如果没有找到目标,返回到主循环
        print("4.---retTargetInRange = isTargetInRange({0})---".format(target.name))
        # 是否到达目标?
        retTargetInRange = isTargetInRange(target) # 不在变形范围内=false和dist,在变形范围=true和dist; {'inRange':true, 'dist':10}
        if not retTargetInRange['inRange']:
            # 距离目标较远,根据目标确定爬行方式
            if target.name == "Left Turn":
                print("during time = {0}".format(time.time()-starttime))
                InchwormModeCrawl()
            continue # 爬行后,返回到主循环
        #TODO 在变形范围内需要不同的变形机制
        if target.name == "Left Turn":
            print("target Left Turn left common")
            for i in range(3):
                print("the {0} left Left Turn".format(i))
                # while not isActSts_FREE():
                #     main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
                arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["TurnLeftCom"].encode('utf-8'))
                main_detect() # 等会
                time.sleep(0.020)
                while not isActSts_FREE():
                    main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
            
        # if target.name == "Stair Climbing":
        #     pass

        # if target.name == "Left Turn":
        #     pass
        # if target.name == "Narrow Lane":
        #     for i in range(3):
        #         arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["InchwormMode"].encode('utf-8'))
        #         main_detect() # 等会
        #         while not isActSts_FREE():
        #             main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
        #         time.sleep(1)

        # TODO 更新target
        target_index = target_index + 1
        target = targets[target_index]
        break

        # if target.name == "None":
        #     while True:
        #         time.sleep(1)
        #         print("program stop...")
    print("Turn End ------")
    # while True: #拐弯结束后停止,只测试前两步
    #     pass
    # -------------拐弯结束----------------

    # -------------台阶开始----------------
    while True:

        main_detect()
        print("1.---while isActSts_WORKING().{0}:---".format(target.name))
        # Actuator 是否在工作?
        while isActSts_WORKING() or isActSts_PACING(): # 如果Actuator在工作, 等待
            print("hell")
            
        print("2.---resTargetFound = isTargetFound({0})---".format(target.name))
        # 是否检测到目标?
        starttime = time.time()
        # global resTargetFound
        resTargetFound = isTargetFound(target) #没有找到返回false和pos=0,找到返回true和pos;返回字典,{'found':true, 'pos':0}
        if not target.blindArea:
            if not resTargetFound['found']:
                while not resTargetFound['found']: # 此处为查找目标
                    print("target not found")
                    break # TODO 如果没有目前不执行动作,返回到主循环
                continue
            # print("3.---while resTargetFound['pos'] < centerMostLeft or resTargetFound['pos'] > centerMostRight:---")
            # # 目标是否在正中? 
            # # print("{0}.centerMostLeft = {1}".format(target.name, target.centerMostLeft))
            # # print("{0}.centerMostRight = {1}".format(target.name, target.centerMostRight))
            # while resTargetFound['found'] and (resTargetFound['pos'] < target.centerMostLeft or resTargetFound['pos'] > target.centerMostRight):
            #     print("resTargetFound main_0 = {0}".format(resTargetFound))
            #     if resTargetFound['pos'] < target.centerMostLeft: # 偏左
            #         # print("resTargetFound['pos'] = {0} -----{1}.centerMostLeft = {2}".format(resTargetFound['pos'], target.name, target.centerMostLeft))
            #         paceLeft(target)
            #         print("resTargetFound main_1 = {0}".format(resTargetFound))
            #     elif resTargetFound['pos'] > target.centerMostRight: # 偏右
            #         # print("resTargetFound['pos'] = {0} -----{1}.centerMostRight = {2}".format(resTargetFound['pos'], target.name, target.centerMostRight))
            #         paceRight(target)
            #         print("resTargetFound main_2 = {0}".format(resTargetFound))
            #     else:
            #         if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
            #             break    #如果没有找到目标,跳出
            #         # continue
            #     # if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
            #     #     break    #如果没有找到目标,跳出
            if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                continue    #如果没有找到目标,返回到主循环
        print("4.---retTargetInRange = isTargetInRange({0})---".format(target.name))
        # # 是否到达目标?
        # retTargetInRange = isTargetInRange(target) # 不在变形范围内=false和dist,在变形范围=true和dist; {'inRange':true, 'dist':10}
        # if not retTargetInRange['inRange']:
        #     # 距离目标较远,根据目标确定爬行方式
        #     if target.name == "Stair Climbing":
        #         print("during time = {0}".format(time.time()-starttime))
        #         InchwormModeCrawl()
        #         # GeckModeCrawl()

        #     # continue # 爬行后,返回到主循环
        #TODO 在变形范围内需要不同的变形机制
        if target.name == "Stair Climbing":
            print("InchwormMode to Stair Climbing")
            for i in range(2):
                arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["InchwormMode"].encode('utf-8'))
                # for i in range(27):
                #     main_detect()
                # main_detect() # 等会
                # time.sleep(0.020)
                while not isActSts_FREE():
                    main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
            StairCrawl()
            # while not isActSts_FREE():
            #     main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要

        # if target.name == "Stair Climbing":
        #     pass

        # if target.name == "Left Turn":
        #     pass
        # if target.name == "Narrow Lane":
        #     for i in range(3):
        #         arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["InchwormMode"].encode('utf-8'))
        #         main_detect() # 等会
        #         while not isActSts_FREE():
        #             main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
        #         time.sleep(1)

        # TODO 更新target
        target_index = target_index + 1
        target = targets[target_index]
        break

        # if target.name == "None":
        #     while True:
        #         time.sleep(1)
        #         print("program stop...")
    print("Stair End ------")
    # -------------台阶结束----------------

    # -------------避障开始----------------
    while True:
        # while True:
        #     main_detect()
        main_detect()
        print("1.---while isActSts_WORKING().{0}:---".format(target.name))
        # Actuator 是否在工作?
        while isActSts_WORKING() or isActSts_PACING(): # 如果Actuator在工作, 等待
            print("hell")
            main_detect()
            
        print("2.---resTargetFound = isTargetFound({0})---".format(target.name))
        # 是否检测到目标?
        starttime = time.time()
        # global resTargetFound
        resTargetFound = isTargetFound(target) #没有找到返回false和pos=0,找到返回true和pos;返回字典,{'found':true, 'pos':0}
        if not target.blindArea:
            if not resTargetFound['found']:
                while not resTargetFound['found']: # 此处为查找目标
                    print("target not found")
                    break # TODO 如果没有目前不执行动作,返回到主循环
                continue
            print("3.---while resTargetFound['pos'] < centerMostLeft or resTargetFound['pos'] > centerMostRight:---")
            # 目标是否在正中? 
            # print("{0}.centerMostLeft = {1}".format(target.name, target.centerMostLeft))
            # print("{0}.centerMostRight = {1}".format(target.name, target.centerMostRight))
            while resTargetFound['found'] and (resTargetFound['pos'] < target.centerMostLeft or resTargetFound['pos'] > target.centerMostRight):
                print("resTargetFound main_0 = {0}".format(resTargetFound))
                if resTargetFound['pos'] < target.centerMostLeft: # 偏左
                    # print("resTargetFound['pos'] = {0} -----{1}.centerMostLeft = {2}".format(resTargetFound['pos'], target.name, target.centerMostLeft))
                    paceLeft(target)
                    print("resTargetFound main_1 = {0}".format(resTargetFound))
                elif resTargetFound['pos'] > target.centerMostRight: # 偏右
                    # print("resTargetFound['pos'] = {0} -----{1}.centerMostRight = {2}".format(resTargetFound['pos'], target.name, target.centerMostRight))
                    paceRight(target)
                    print("resTargetFound main_2 = {0}".format(resTargetFound))
                else:
                    if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                        break    #如果没有找到目标,跳出
                    # continue
                # if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                #     break    #如果没有找到目标,跳出
            if not resTargetFound['found']: # resTargetFound会在 偏左 偏右步骤中不断更新
                continue    #如果没有找到目标,返回到主循环
        print("4.---retTargetInRange = isTargetInRange({0})---".format(target.name))
        # 是否到达目标?
        retTargetInRange = isTargetInRange(target) # 不在变形范围内=false和dist,在变形范围=true和dist; {'inRange':true, 'dist':10}
        if not retTargetInRange['inRange']:
            # 距离目标较远,根据目标确定爬行方式
            if target.name == "Right Obstacle":
                print("during time = {0}".format(time.time()-starttime))
                ObstacleCrawl()
            # if target.name == "Stair Climbing":
            #     # StairCrawl()
            #     pass
            # if target.name == "Left Turn":
            #     # TurnCrawl()
            #     pass
            # if target.name == "Narrow Lane":
            #     SlitCrawl()
            #     pass
            continue # 爬行后,返回到主循环
        #TODO 在变形范围内需要不同的变形机制
        if target.name == "Right Obstacle":
            print("target Left Turn left common")
            for i in range(3):
                arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["TurnLeftCom"].encode('utf-8'))
                main_detect() # 等会
                # time.sleep(0.020)
                while not isActSts_FREE():
                    main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要

        GeckModeCrawl()
        while not isActSts_FREE():
            main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要
        GeckModeCrawl()
        while not isActSts_FREE():
            main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要

        for i in range(20):
            main_detect()

        print("target Left Turn Right common")
        for i in range(2):
            arduino.write(crawlrobot.cmdserial.PC_SET_ACT_MODE["TurnRightCom"].encode('utf-8'))
            main_detect() # 等会
            # time.sleep(0.020)
            while not isActSts_FREE():
                main_detect() # time.sleep(.020) 等待Arduino读取串口并开始执行loop中对应的函数 #!!!!!!!判断是否需要

        # TODO 更新target
        i = i + 1
        target = targets[i]
        break

        # if target.name == "None":
        #     while True:
        #         time.sleep(1)
        #         print("program stop...")
    print("Obstacle End ------")
    # -------------避障结束----------------
