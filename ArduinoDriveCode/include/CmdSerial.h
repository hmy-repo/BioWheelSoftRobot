#pragma once
// #include <string>
// #include <iostream>
// // #include <HardwareSerial.h>
// using namespace std;

#include <Arduino.h>

class CmdSerialConstStr
{
public:
    CmdSerialConstStr();
    ~CmdSerialConstStr();
    // //public properties
    // // const properties PC->Arduino
    // const String PC_GET_TOF_DIST = "GTD\n";
    // const String PC_GET_ACT_STS = "GAS\n";
    // const struct SetActuatorMode
    // {
    //     const String GeckoMode = "GKM\n";
    //     const String InchwormMode = "IWM\n";
    //     const String TurnRightCom = "TRC\n";
    //     const String TurnRightSwift = "TRS\n";
    //     const String Slope55Deg = "S5D\n";
    // }PC_SET_ACT_MODE;

    // // const properties Arduino->PC
    // const String ARD_RES_STS_GeckoMode = "RSGM\n";
    // const String ARD_RES_STS_InchMode = "RSIM\n";
    // const String ARD_RES_STS_RightCom = "RSRC\n";
    // const String ARD_RES_STS_RightSwift = "RSRS\n";
    // const String ARD_RES_STS_FIFFIVDEG = "RSFD\n";
    // const String ARD_RES_STS_OBSTSTEP = "RSOS\n";

    //public properties
    // const properties PC->Arduino
    const char* PC_GET_TOF_DIST = "GTD\n";
    const char* PC_GET_ACT_STS = "GAS\n";
    const struct SetActuatorMode
    {
        const char* GeckoMode = "GKM\n";
        const char* InchwormMode = "IWM\n";
        const char* TurnLeftCom = "TLC\n";
        const char* TurnRightCom = "TRC\n";
        const char* TurnRightSwift = "TRS\n";
        const char* Slope55Deg = "S5D\n";
        const char* ClimbStairMode = "CSM\n";
        const char* PaceLeft = "PL\n";
        const char* PaceRight = "PR\n";
        const char* PaceEnd = "PE\n";
    }PC_SET_ACT_MODE;

    // const properties Arduino->PC
    const char* ARD_RES_STS_GeckoMode = "RSGM\n";
    const char* ARD_RES_STS_InchMode = "RSIM\n";
    const char* ARD_RES_STS_RightCom = "RSRC\n";
    const char* ARD_RES_STS_RightSwift = "RSRS\n";
    const char* ARD_RES_STS_FIFFIVDEG = "RSFD\n";
    const char* ARD_RES_STS_OBSTSTEP = "RSOS\n";
};


class CmdSerial : public CmdSerialConstStr
{
private:
    
public:
    CmdSerial(unsigned long bandrate = 9600);
    ~CmdSerial();

    // // const properties PC->Arduino
    // String PC_GET_TOF_DIST = String("GTD");
    // String PC_GET_ACT_STS = String("GAS");
    // struct SetActuatorMode
    // {
    //     String GeckoMode = String("GKM");
    //     String InchwormMode = String("IWM");
    //     String TurnRightCom = String("TRC");
    //     String TurnRightSwift = String("TRS");
    //     String Slope55Deg = String("S5D");
    // }PC_SET_ACT_MODE;

    // // const properties Arduino->PC
    // String ARD_RES_STS_GeckoMode = String("RSGM");
    // String ARD_RES_STS_InchMode = String("RSIM");
    // String ARD_RES_STS_RightCom = String("RSRC");
    // String ARD_RES_STS_RightSwift = String("RSRS");
    // String ARD_RES_STS_FIFFIVDEG = String("RSFD");
    // String ARD_RES_STS_OBSTSTEP = String("RSOS");

    // // const properties PC->Arduino
    // const String PC_GET_TOF_DIST = "GTD\n";
    // const String PC_GET_ACT_STS = "GAS\n";
    // const struct SetActuatorMode
    // {
    //     const String GeckoMode = "GKM\n";
    //     const String InchwormMode = "IWM\n";
    //     const String TurnRightCom = "TRC\n";
    //     const String TurnRightSwift = "TRS\n";
    //     const String Slope55Deg = "S5D\n";
    // }PC_SET_ACT_MODE;

    // // const properties Arduino->PC
    // const String ARD_RES_STS_GeckoMode = "RSGM\n";
    // const String ARD_RES_STS_InchMode = "RSIM\n";
    // const String ARD_RES_STS_RightCom = "RSRC\n";
    // const String ARD_RES_STS_RightSwift = "RSRS\n";
    // const String ARD_RES_STS_FIFFIVDEG = "RSFD\n";
    // const String ARD_RES_STS_OBSTSTEP = "RSOS\n";

    // public method
    String receive_cmd();
    void send_res_sts(String &str);
};

