#pragma once

#include <Arduino.h>
//#define ONESEC 1000
// 定义需要用到的管脚，控制气动开关
struct PinStruct
{
  int LeftPIN = 2; //通道1
  int RightPIN = 3; //通道2
  int TopFrontPIN = 8; //4; //通道3
  int TopRearPIN = 5; //通道4
  int BottomFrontPIN = 6; //通道5
  int BottomRearPIN = 7; //通道5
};

// 定义6种运动模式；分别定义每种模式中需要用到的气压和持续时间，及循环次数。
struct PressureStruct
{
  // 壁虎模式
  struct GeckoModePre
  {
    int Left = 70;
    int TimeLeft = 900;

    int Right = 70;
    int TimeRight = 900;
  }geckoModePre;

  // 尺蠖模式
  struct InchwormModePre
  {
    int TopFront = 105;
    int TopRear = 105;
    int TimeTop = 1000; 

    // int BottomFront = 50;
    // int BottomRear = 60;
    // int TimeBottom = 1000;
  }inchwormModePre;

  // 左转弯：一般
  struct TurnLeftComPre
  {
    int Right = 90;//120;
    int TopFront = 110; //130;
    int TopRear = 120; //140;

    int TimeRightTop = 1000;
    int TimeZero = 1000;
  }turnLeftComPre;

  // 右转弯：一般
  struct TurnRightComPre
  {
    int Left = 90;//120;
    int TopFront = 110; //130;
    int TopRear = 120; //140;

    int TimeLeftTop = 1000;
    int TimeZero = 1000;
  }turnRightComPre;

  // 右转弯：急转
  struct TurnRightSwiftPre
  {
    int TopFront = 130;
    int TopRear = 140;
    int TimeTop = 1000;
    int TimeZero = 1000;
    int Left = 120;
  }turnRightSwiftPre;

  // 斜坡（55度）
  struct Slope55DegPre
  {
    int Left = 80;
    int TimeLeft = 1000;
    int Right = 80;
    int TimeRight = 1000;
  }slope55DegPre;

  // 越障（台阶）
  struct StepBias
  {
    int bias = 30;
  };
  struct ObstacleStepPre
  {
    struct StepOne
    { 
      struct StepBias stepBias;
      int TopFront = 130-stepBias.bias;
      int TopRear = 140-stepBias.bias;
      int TimeTop = 2000;
      int TimeZero = 1000;
      int LoopNum = 2;
    }stepOne;
    struct StepTwo
    {
      struct OneWheel
      {
        struct StepBias stepBias;
        int BottomFront = 135-stepBias.bias;
        int Left = 90-stepBias.bias;
        int TimeBFL = 3000;

        int TopFront = 130-stepBias.bias;
        int TopRear = 140-stepBias.bias;
        int TimeTop = 3000;
      }oneWheel;
      struct OtherWheel
      {
        struct StepBias stepBias;
        int BottomFront = 145-stepBias.bias;
        // int Right = 30-stepBias.bias;
        int Left = 30-stepBias.bias;
        int TimeBFR = 3000;

        int TopFront = 130-stepBias.bias;
        int TopRear = 140-stepBias.bias;
        int TimeTop = 2000;
      }otherWheel;
    }stepTwo;
    struct StepThree
    {
      struct StepBias stepBias;
      int TopFront = 130-stepBias.bias;
      int TopRear = 140-stepBias.bias;
      int TimeTop = 3000;
      int TimeZero = 1000;
      int LoopNum = 2;
    }stepThree;
    struct StepFour
    {
      struct StepBias stepBias;
      int Left = 120-stepBias.bias;
      int TimeLeft = 2000;
      int TopFront = 140-stepBias.bias;
      int TopRear = 140-stepBias.bias;
      int TimeTop = 1000; //2000;
      int Right = 100-stepBias.bias; //125-stepBias.bias;
      int TimeRight = 2000;
      int LoopNum = 1;
    }stepFour;
    // struct StepFive
    // {
    //   int Left = 120;
    //   int TimeLeft = 1;
    //   int Right = 120;
    //   int TimeRight = 2;
    // }stepFive;
  }obstacleStepPre;

};


class CrawlRobo
{
public:
	CrawlRobo(PinStruct &pinStruct, PressureStruct &preStruct);
	~CrawlRobo();
public:
  //public method
	int GeckoMode();
	int InchwormMode();
  int TurnLeftCom();
	int TurnRightCom();
	int TurnRightSwift();
	int Slope55Deg();
	int ObstacleStep();
  int Pace(const char* paceDrc);
  void PaceReset();
  void Start();
  void Stop();
  String Get_work_sts();

	void Left(int preVal);
	void Right(int preVal);
	void TopFront(int preVal);
	void TopRear(int preVal);
	void BottomFront(int preVal);
	void BottomRear(int preVal);

  //public properties
  bool paceIng = false;
  

private:
	PressureStruct _preStruct;
  PinStruct _pinStruct;
  struct work_sts_struct
  {
    String FREE = "FREE\n";
    String WORKING = "WORKING\n";
    String PACING = "PACING\n";
    String PACINGFREE = "PACINGFREE\n";
  }_WORK_STS;
  String _work_sts = _WORK_STS.FREE;
  // char* const _lastPaceDrc = "None"; //_lastPaceDrc 取消
  const char* _PACELEFT = "PL\n";
  const char* _PACERIGHT = "PR\n";
  int _paceVal = 0; //全局变量
  int _smallPaceVal = 10; //根据实际调整
  int _paceValMax = 80; //根据实际调整

  //private method
  void _Pace(const char* paceDrc);
};
