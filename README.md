# Biomimetic Soft Robot Exploiting Wheel-legs and Multimodal Locomotion for High Terrestrial Maneuverability
*Program for the Biomimetic Soft Robot*<br>

## System requiremets
- **Hardware**: Raspberry Pi 4 Model B Rev 1.4, Arduino Mega 2560, Arducam Pi Camera(5 Mega pixels), ToF sensor(OSTSen-53L0X)<br>
- **System**: Debian GNU/Linux 11 (bullseye) *[for Raspberry Pi]*, FreeRTOS *[for Arduino]*<br>
- **Library & Language**: OpenCV, PyTorch; Python, C++<br>

## Instructions for use
> ArduinoDriveCode 📁
>> - main.cpp --including the embedded system *FreeRTOS*, whose job is to manage two main tasks: 1.the dual-serial-communication between Raspberry Pi and Arduino, 2.requiring the distance data from the ToF sensor connected to the Arduino.
>> - CrawlRobo.cpp
>> - CmdSerial.cpp
>> - TOFSensor.cpp

## Installation guide

## Demo


## Reference
- <https://github.com/ultralytics/yolov5><br>
- <https://github.com/eriklindernoren/PyTorch-YOLOv3><br>
