#include "CrawlRobo.h"
#include <Arduino.h>
//#include <iostream>
//using namespace std;

#define DEBUG 0

CrawlRobo::CrawlRobo(PinStruct &pinStruct, PressureStruct &preStruct)
{
	_preStruct = preStruct;
  _pinStruct = pinStruct;
}

CrawlRobo::~CrawlRobo()
{
//	cout << _preStruct.obstacleStepPre.stepOne.TopRear << std:: endl;
}


/**************public method********************/
// 壁虎模式
int CrawlRobo::GeckoMode()
{
  _work_sts = _WORK_STS.WORKING;
	// Left(_preStruct.geckoModePre.Left);
	// delay(_preStruct.geckoModePre.TimeLeft);
	// Left(0);
	Right(_preStruct.geckoModePre.Right);
	delay(_preStruct.geckoModePre.TimeRight);
	Right(0);

  Left(_preStruct.geckoModePre.Left);
	delay(_preStruct.geckoModePre.TimeLeft);
	Left(0);



  #if DEBUG
  Serial.println(_preStruct.geckoModePre.Left);
  Serial.println(_preStruct.geckoModePre.TimeLeft);
  Serial.println(_preStruct.geckoModePre.Right);
  Serial.println(_preStruct.geckoModePre.TimeRight);
  #endif
  _work_sts = _WORK_STS.FREE;
	return 0;
}

// 尺蠖模式
int CrawlRobo::InchwormMode()
{
  _work_sts = _WORK_STS.WORKING;
  TopFront(_preStruct.inchwormModePre.TopFront);
  TopRear(_preStruct.inchwormModePre.TopRear);
  delay(_preStruct.inchwormModePre.TimeTop);
  TopFront(0);
  TopRear(0);
  delay(1000);
  // BottomFront(_preStruct.inchwormModePre.BottomFront);
  // BottomRear(_preStruct.inchwormModePre.BottomRear);
  // delay(_preStruct.inchwormModePre.TimeBottom);
  // BottomFront(0);
  // BottomRear(0);
  #if DEBUG
  Serial.println("CrawlRobo::InchwormMode()");
  #endif
  _work_sts = _WORK_STS.FREE;
	return 0;
}

// 左转弯：一般
int CrawlRobo::TurnLeftCom()
{
  _work_sts = _WORK_STS.WORKING;
  Right(_preStruct.turnLeftComPre.Right);
  TopFront(_preStruct.turnLeftComPre.TopFront);
  TopRear(_preStruct.turnLeftComPre.TopRear);
  delay(_preStruct.turnLeftComPre.TimeRightTop);
  Right(0);
  TopFront(0);
  TopRear(0);
  delay(_preStruct.turnLeftComPre.TimeZero);
  #if DEBUG
  Serial.println("CrawlRobo::TurnRightCom()");
  #endif
  _work_sts = _WORK_STS.FREE;
	return 0;
}

// 右转弯：一般
int CrawlRobo::TurnRightCom()
{
  _work_sts = _WORK_STS.WORKING;
  Left(_preStruct.turnRightComPre.Left);
  TopFront(_preStruct.turnRightComPre.TopFront);
  TopRear(_preStruct.turnRightComPre.TopRear);
  delay(_preStruct.turnRightComPre.TimeLeftTop);
  Left(0);
  TopFront(0);
  TopRear(0);
  delay(_preStruct.turnRightComPre.TimeZero);
  #if DEBUG
  Serial.println("CrawlRobo::TurnRightCom()");
  #endif
  _work_sts = _WORK_STS.FREE;
	return 0;
}

// 右转弯：急转
int CrawlRobo::TurnRightSwift()
{
  _work_sts = _WORK_STS.WORKING;
  Left(_preStruct.turnRightSwiftPre.Left);
  TopFront(_preStruct.turnRightSwiftPre.TopFront);
  TopRear(_preStruct.turnRightSwiftPre.TopRear);
  delay(_preStruct.turnRightSwiftPre.TimeTop);
  TopFront(0);
  TopRear(0);
  delay(_preStruct.turnRightSwiftPre.TimeZero);
  #if DEBUG
  Serial.println("CrawlRobo::TurnRightSwift()");
  #endif
  _work_sts = _WORK_STS.FREE;
	return 0;
}

// 斜坡（55度）
int CrawlRobo::Slope55Deg()
{
  _work_sts = _WORK_STS.WORKING;
  Left(_preStruct.slope55DegPre.Left);
  delay(_preStruct.slope55DegPre.TimeLeft);
  Left(0);
  Right(_preStruct.slope55DegPre.Right);
  delay(_preStruct.slope55DegPre.TimeRight);
  Right(0);
  #if DEBUG
  Serial.println("CrawlRobo::Slope55Deg()");
  #endif
  _work_sts = _WORK_STS.FREE;
	return 0;
}

// 越障（台阶）
int CrawlRobo::ObstacleStep()
{
  _work_sts = _WORK_STS.WORKING;
  // step1:尺蠖
  for (int i = 0; i < _preStruct.obstacleStepPre.stepOne.LoopNum; i++) //交替运动两个循环
  {
    TopFront(_preStruct.obstacleStepPre.stepOne.TopFront);
    TopRear(_preStruct.obstacleStepPre.stepOne.TopRear);
    delay(_preStruct.obstacleStepPre.stepOne.TimeTop);
    TopFront(0);
    TopRear(0);
    delay(_preStruct.obstacleStepPre.stepOne.TimeZero);
  }
  

  // step2:抬头向上爬
  BottomFront(_preStruct.obstacleStepPre.stepTwo.oneWheel.BottomFront);
  delay(4000);
  Left(_preStruct.obstacleStepPre.stepTwo.oneWheel.Left);
  delay(_preStruct.obstacleStepPre.stepTwo.oneWheel.TimeBFL);
  // Right(_preStruct.obstacleStepPre.stepTwo.otherWheel.Right);
  // delay(_preStruct.obstacleStepPre.stepTwo.otherWheel.TimeBFR);
  BottomFront(0);
  Left(0);
  // Right(0);
  TopFront(_preStruct.obstacleStepPre.stepTwo.oneWheel.TopFront);
  TopRear(_preStruct.obstacleStepPre.stepTwo.oneWheel.TopRear);
  delay(_preStruct.obstacleStepPre.stepTwo.oneWheel.TimeTop);
  TopFront(0);
  TopRear(0);

  //step2:抬另一个轮  TODO 删除,换成S形,气压数值70, 持续时间4s
  // BottomFront(_preStruct.obstacleStepPre.stepTwo.otherWheel.BottomFront);
  // delay(4000);
  // // Right(_preStruct.obstacleStepPre.stepTwo.otherWheel.Right);
  // Left(_preStruct.obstacleStepPre.stepTwo.otherWheel.Left);
  // delay(_preStruct.obstacleStepPre.stepTwo.otherWheel.TimeBFR);
  // // Left(_preStruct.obstacleStepPre.stepTwo.oneWheel.Left);
  // // delay(_preStruct.obstacleStepPre.stepTwo.oneWheel.TimeBFL);
  // BottomFront(0);
  // Right(0);
  // // Left(0);
  // Left(0);
  // TopFront(_preStruct.obstacleStepPre.stepTwo.otherWheel.TopFront);
  // TopRear(_preStruct.obstacleStepPre.stepTwo.otherWheel.TopRear);
  // delay(_preStruct.obstacleStepPre.stepTwo.otherWheel.TimeTop);
  // TopFront(0);
  // TopRear(0);

  //step 2: 换成S形,气压数值70, 持续时间4s
  // BottomFront(90);
  // delay(2000);
  // BottomFront(0);
  // delay(1000);

  TopFront(90); //测试S型弯是否可行
  BottomRear(115);
  // BottomFront(100); //测试C型弯是否可行 不可行
  // TopRear(115);

  delay(3000);
  Right(110);
  delay(1000);
  Right(0);

  TopFront(0); //测试S型弯是否可行
  BottomRear(0);
  // BottomFront(0); //测试C型弯是否可行 不可行
  // TopRear(0);



  // step3:
  for (int i = 0; i < _preStruct.obstacleStepPre.stepThree.LoopNum; i++) //交替运动两个循环
  {
    TopFront(_preStruct.obstacleStepPre.stepThree.TopFront);
    TopRear(_preStruct.obstacleStepPre.stepThree.TopRear);
    delay(_preStruct.obstacleStepPre.stepThree.TimeTop);
    TopFront(0);
    TopRear(0);
    delay(_preStruct.obstacleStepPre.stepThree.TimeZero);
  }
  
  // step4:抬后轮
  for (int i = 0; i < _preStruct.obstacleStepPre.stepFour.LoopNum; i++) //交替运动1个循环
  {
    Left(_preStruct.obstacleStepPre.stepFour.Left);
    BottomRear(90); ////
    delay(1000);
    BottomRear(0);/////
    delay(1000);
    // delay(_preStruct.obstacleStepPre.stepFour.TimeLeft);
    // Left(0);
    TopFront(_preStruct.obstacleStepPre.stepFour.TopFront);
    TopRear(_preStruct.obstacleStepPre.stepFour.TopRear);
    delay(_preStruct.obstacleStepPre.stepFour.TimeTop);
    Left(0);
    TopFront(0);
    TopRear(0);
    delay(1000); //
    Right(_preStruct.obstacleStepPre.stepFour.Right);
    delay(_preStruct.obstacleStepPre.stepFour.TimeRight);
    Right(0);
    // TopFront(_preStruct.obstacleStepPre.stepFour.TopFront);
    // TopRear(_preStruct.obstacleStepPre.stepFour.TopRear);
    // delay(_preStruct.obstacleStepPre.stepFour.TimeTop);
    // // Right(0);
    // TopFront(0);
    // TopRear(0);


    // Right(80);
    // delay(2000);
    // Right(0);
  }
  
  // step5:壁虎 去掉
  for(int i = 0; i < 1; i++)
  {
    // GeckoMode();

	Left(88);
	delay(1400);
	Left(0);
	Right(88);
	delay(1400);
	Right(0);

  // Left(_preStruct.geckoModePre.Left);
	// delay(_preStruct.geckoModePre.TimeLeft);
	// Left(0);
  }
  
  #if DEBUG
  Serial.println("CrawlRobo::ObstacleStep()");
  #endif
  _work_sts = _WORK_STS.FREE;
	return 0;
}

//按出入参数定义的方向踱步，气压从0开始增加到最大值max，之后归0,重复。
int CrawlRobo::Pace(const char* paceDrc)
{
  _work_sts = _WORK_STS.PACING;
  if(!paceIng)
    _paceVal = 0;
  // if(!(strcmp(paceDrc, _lastPaceDrc) == 0)) // _lastPaceDrc 取消
  //   _paceVal = 0;
  #if DEBUG
  Serial.print("_paceVal_before = ");
  Serial.println(_paceVal);
  Serial.print("paceDrc = ");
  Serial.println(paceDrc);
  #endif
  _Pace(paceDrc);
  paceIng = true;
  #if DEBUG
  // Serial.print("_lastPaceDrc = ");
  // Serial.println(_lastPaceDrc);
  // strcpy(_lastPaceDrc, paceDrc); //非常重要 //_lastPaceDrc 取消
  // Serial.print("currentPaceDrc = ");
  // Serial.println(paceDrc);
  Serial.print("_paceVal_after = ");
  Serial.println(_paceVal);
  #endif
  _work_sts = _WORK_STS.PACINGFREE;
  return 0;
}

//重置Pace相关变量，paceImg = false; _lastPaceDrc = "None";
void CrawlRobo::PaceReset()
{
  paceIng = false;
  // // _lastPaceDrc = "None";
  // strcpy(_lastPaceDrc, "None"); //_lastPaceDrc 取消
  _paceVal = 0;
  Left(0);
  Right(0);
  _work_sts = _WORK_STS.FREE;
}

//开始，所有气腔气压值清零
void CrawlRobo::Start()
{
  Left(0);
  Right(0);
  TopFront(0);
  TopRear(0);
  BottomFront(0);
  BottomRear(0);
}

//结束，所有气腔气压值清零
void CrawlRobo::Stop()
{
  Start();
}

//获取气腔工作状态
String CrawlRobo::Get_work_sts()
{
  return _work_sts;
}

/**************private method********************/
// 传入参数为气压变换后的Arduino控制信号值
//左气腔充气
void CrawlRobo::Left(int preVal)
{
  analogWrite(_pinStruct.LeftPIN,preVal);
}

//右气腔充气
void CrawlRobo::Right(int preVal)
{
  analogWrite(_pinStruct.RightPIN,preVal);
}

//上前气腔充气
void CrawlRobo::TopFront(int preVal)
{
  analogWrite(_pinStruct.TopFrontPIN,preVal);
}

//上后气腔充气
void CrawlRobo::TopRear(int preVal)
{
	analogWrite(_pinStruct.TopRearPIN,preVal);
}

//后前气腔充气
void CrawlRobo::BottomFront(int preVal)
{
  analogWrite(_pinStruct.BottomFrontPIN,preVal);
}

//下后气腔充气
void CrawlRobo::BottomRear(int preVal)
{
  analogWrite(_pinStruct.BottomRearPIN,preVal);
}


//Private method
void CrawlRobo::_Pace(const char* paceDrc)
{
  (_paceVal + _smallPaceVal) > _paceValMax ? _paceVal = 0 : _paceVal = _paceVal + _smallPaceVal;
  #if DEBUG
  Serial.println("_Pace Func");
  // Serial.print("StrcmpLeft = ");
  // Serial.println(strcmp(paceDrc, _PACELEFT) == 0);
  // Serial.print("StrcmpRight = ");
  // Serial.println(strcmp(paceDrc, _PACERIGHT) == 0);
  #endif 

  if(strcmp(paceDrc, _PACELEFT) == 0)
  {
    #if DEBUG
    Serial.println("_PACELEFT");
    #else
    Right(_paceVal);
    // delay(500);
    #endif
  }
  if(strcmp(paceDrc, _PACERIGHT) == 0)
  {
    #if DEBUG
    Serial.println("_PACERIGHT");
    #else
    Left(_paceVal);
    // delay(500);
    #endif
  }
}