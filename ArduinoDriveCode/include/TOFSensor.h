#pragma once
#include <Wire.h>

class TOFSensor
{
private:
    unsigned short lenth_val = 0;
    unsigned char i2c_rx_buf[16];
    void _SensorRead(unsigned char addr,unsigned char* datbuf,int cnt); //unsigned char cnt
public:
    TOFSensor();
    ~TOFSensor();

    // public methods
    int ReadDistance();
};
