# Biomimetic Soft Robot Exploiting Wheel-legs and Multimodal Locomotion for High Terrestrial Maneuverability
*Program for the Biomimetic Soft Robot*<br>

## System requiremets
- **Hardwares**: Raspberry Pi 4 Model B Rev 1.4, Arduino Mega 2560, Arducam Pi Camera(5 Mega pixels), ToF sensor(OSTSen-53L0X)<br>
- **Systems**: Debian GNU/Linux 11 (bullseye) *[for Raspberry Pi]*, FreeRTOS *[for Arduino]*<br>
- **Libraries & Languages**: OpenCV, PyTorch; Python, C++<br>

## Installation guide
- **OS Installation**: Raspberry Pi OS(64 bit) and FreeRTOS should be installed on the Raspberry Pi and Arduino<br>
- **Software Enviroments**: vscode and plugs-in, CMake, Vim, Python 3.0, C++<br>
- **Libraries Installation**: libcamera, picamera2, NumPy, OpenCV(4.5.5), PyTorch<br>

## Instructions for use
> **ArduinoDriveCode** 📁
> - **main.cpp**: includes the embedded system *FreeRTOS*, whose job is to manage two main tasks: 1. *the dual-serial-communication between Raspberry Pi and Arduino* 2. *requiring the distance data from the ToF sensor connected to the Arduino.*
> - **CrawlRobo.cpp**: performs the *actuation strategies* by manipulating the Electro-Pneumatic Regulators through PWM waves.
> - **CmdSerial.cpp**: defines the *serial communication protocol* between Raspberry Pi and Arduino.
> - **TOFSensor.cpp**: powered by the Arduino to detect *the distance* when Arduino requires.

> **crawlrobot** 📁
> - **crawlrobot.py**: defines *a class CrawlRobot* to achieve different functionalities of our Biomimetic Soft Robot.
> - **detector.py**: for *object recognition algorithm* which performed on the Raspberry Pi platform.
> - **postprocess.py**: *postprocess* for the object recognition procedure.

> **picamera2** 📁
> - Picamera2 is the libcamera-based replacement for Picamera which was *a Python interface* to the Raspberry Pi's legacy camera stack. Picamera2 also presents an easy to use Python API.

> **main.py**
> - This is *the main program*, when we excute this python file, the program shown above will be called automatically. *An decision-making unit* is contain in this file, which can be regarded as the robot brain. <br>

## Demo
<div align="center">
<img src=/crawlrobot/img/object_recognition_result.jpg width=50%/>
</div>
<p align="center"><i>Fig 1. Object recognition result shown on Raspberry Pi</i></p>
<div align="center">
<img src=/crawlrobot/img/actuated.jpg width=50%/>
</div>
<p align="center"><i>Fig 2. Actuated chambers controled by Arduino</i></p>

## References
- <https://github.com/ultralytics/yolov5><br>
- <https://github.com/eriklindernoren/PyTorch-YOLOv3><br>
- <https://github.com/raspberrypi/picamera2><br>
- <https://www.freertos.org><br>
- <https://www.raspberrypi.com><br>
