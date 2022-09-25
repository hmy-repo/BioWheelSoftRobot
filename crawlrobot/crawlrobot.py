# import pstats
# from xmlrpc.client import boolean

# import argparse
# import cv2
# import numpy as np
# from picamera2 import Picamera2, Preview
# import time



# print("start crawlrobot.crawlrobot.py")
"""
A package for the crawlrobot project.
"""
import cv2
from picamera2.picamera2 import Picamera2
from detector import yolo_fast_v2


class CrawlRobot:
    def __init__(self, args) -> None:
        self.camera = Camera(args)
        self.tof = ToF()
        self.actuator = Actuator()
        self.cmdserial = CmdSerial()
        self.obj = []
        print("class CrawlRobot __init__")

    def init_obj_list(self):
        pass

    def update_obj_list(self):
        pass
    
    def pop_obj(self):
        pass

    def has_obj(self) -> bool:
        pass

    def search_obj(self):
        pass

    def read_actuator_sts(self) -> bool:
        pass

    def get_obj_pos(self):
        pass

    def cam_in_obj_center(self):
        pass

    def read_obj_dist(self):
        pass

    def is_inrange(self):
        pass

    def cal_actuator_direction_angle(self):
        pass

class Camera:
    def __init__(self, args) -> None:
        print("camera __init__")
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.preview_configuration(main={"format": 'XRGB8888', "size": (800, 600)}))
        self.model = yolo_fast_v2(objThreshold=args.objThreshold, confThreshold=args.confThreshold, nmsThreshold=args.nmsThreshold)

    def cam_start(self):
        self.picam2.start()
    
    def cam_stop(self):
        self.picam2.stop()

    def cam_cap_img(self):
        # picam2_img = self.picam2.capture_array()
        # orig_img = cv2.cvtColor(picam2_img, cv2.COLOR_RGBA2RGB)
        # return orig_img
        return cv2.cvtColor(self.picam2.capture_array(), cv2.COLOR_RGBA2RGB)

    # input:
    def cam_detect(self, org_img):
        outputs = self.model.detect(org_img)
        # print(outputs)
        return outputs

    def postprocess(self, org_img, detect_outputs):
        annotated_img = self.model.postprocess(org_img, detect_outputs)
        return annotated_img
    
    def draw_frame(self):
        pass
    
    def get_specobj_pos(self, objkey):
        all_objs_pos = self.model.get_classID()
        if all_objs_pos.get(objkey) is None:
            return None
        else:
            return {objkey : all_objs_pos.get(objkey)}

    #output:all the objects and positions that camera can see.
    def get_all_objs_pos(self):
        all_objs_pos = self.model.get_classID()
        # print(all_objs_pos)
        return (all_objs_pos)

    

class ToF:
    def __init__(self) -> None:
        self.cmdserial = CmdSerial()

    def get_dist(self) -> int:
        return self.cmdserial.send_cmd(self.cmdserial.GET_TOF_DIST)
        

class Actuator:
    def __init__(self) -> None:
        self.cmdserial = CmdSerial()

    def get_actuator_sts(self):
        return self.cmdserial.send_cmd(self.cmdserial.GET_ACT_STS)

    def set_actuator_direction_angle(self, cmd=None) -> bool:
        return self.cmdserial.send_cmd(cmd)

class CmdSerial:
    def __init__(self) -> None:
        # const properties PC->Arduino
        self.PC_GET_TOF_DIST = "GTD\n" # get the distance of TOF
        self.PC_GET_ACT_STS = "GAS\n" # get the status of actuator
        self.PC_SET_ACT_MODE = {"GeckoMode":"GKM\n", \
                            "InchwormMode":"IWM\n", \
                            "TurnLeftCom":"TLC\n", \
                            "TurnRightCom":"TRC\n", \
                            "TurnRightSwift":"TRS\n", \
                            "Slope55Deg":"S5D\n", \
                            "ClimbStairMode":"CSM\n", \
                            "PaceLeft":"PL\n", \
                            "PaceRight":"PR\n", \
                            "PaceEnd":"PE\n"} # set the mode of actuator
        # const properties Arduino->PC
        self.ARD_RES_STS_GeckoMode = "RSGM\n"
        self.ARD_RES_STS_InchMode = "RSIM\n"
        self.ARD_RES_STS_RightCom = "RSRC\n"
        self.ARD_RES_STS_RightSwift = "RSRS\n"
        self.ARD_RES_STS_FIFFIVDEG = "RSFD\n"
        self.ARD_RES_STS_OBSTSTEP = "RSOS\n"
        
    def send_cmd(self, cmd=None):
        #TODO send the specific commond
        return self._receive_cmd()

    def _receive_cmd(self):
        print("_receive_cmd")

# print("end crawlrobot.crawlrobot.py")

if __name__ == '__main__':
    crawlrobot = CrawlRobot()
    crawlrobot.camera.print()
    crawlrobot.tof.get_dist()
