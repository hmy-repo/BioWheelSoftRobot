
#include "CmdSerial.h"

// CmdSerialConstStr 构造函数和析构函数
CmdSerialConstStr::CmdSerialConstStr()
{

}
CmdSerialConstStr::~CmdSerialConstStr()
{

}

// CmdSerial 构造函数和析构函数
CmdSerial::CmdSerial(unsigned long bandrate)
{
    Serial.begin(bandrate);
}

CmdSerial::~CmdSerial()
{
    Serial.end();
}

String CmdSerial::receive_cmd()
{
    String rec_string;
    if(Serial.available() > 0)
    {
        rec_string = Serial.readString(); 
        // Serial.println(rec_string);    
        return  rec_string;
        // return String("Available");
    }
    else
        return String("None");
}

void CmdSerial::send_res_sts(String &str)
{
    // Serial.print(str);
    const char* ret =  str.c_str();
    // char ret[] = "ARSDyyyyttpouiytgfh";
    Serial.write(ret);
    // Serial.println(ret);
}

