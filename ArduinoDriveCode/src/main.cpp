#include <Arduino.h>
#include "CmdSerial.h"
#include "CrawlRobo.h"
// #include "TOFSensor.h"
#include <Wire.h>
#include <VL53L0X.h>

#define CrawlRobo_def 1
#define VL53L0X_DEF 1


//下面几行是 FreeRTOS 的
#include <Arduino_FreeRTOS.h>
#include <semphr.h> // add the FreeRTOS functions for Semaphores (or Flags).

// Declare a mutex Semaphore Handle which we will use to manage the Serial Port.
// It will be used to ensure only one Task is accessing this resource at any time.
SemaphoreHandle_t xSerialSemaphore;

#define LED_SERIAL (12)
#define LED_LOOP (8)



// 全局

// 串口接收的
// String inputString = "";     // a String to hold incoming data
String pc_cmd = "";

bool stringComplete = false; // whether the string is complete

// define two Tasks
void TaskSerial(void *pvParameters);
void TaskLoop(void *pvParameters);

#if CrawlRobo_def
/*******************逻辑层变量定义*********************************************/
CmdSerial cmdserial = CmdSerial(); // 逻辑层的串口协议
PinStruct pinStruct; // 定义用到的引脚
PressureStruct preStruct; // 定义气腔气压值
CrawlRobo crawlrobo = CrawlRobo(pinStruct, preStruct); //实例化Arduino端对象
int dist_avg = 0;
#if VL53L0X_DEF
VL53L0X VL53L0Xsensor = VL53L0X();
#endif
/****************************************************************************/
#endif

// String work_sts = "";
String pc_set_act_cmd = "";
// char* pc_set_act_cmd = "";
// int dist = 0;

/**
 * @brief 现在这个 setup() 里主要初始化 FreeRTOS，
 *        setup() 里的老内容转移到了 TaskLoop() 里
 *
 */
void setup()
{
    
    // 串口初始化，宜早不宜晚，你的串口类里也有初始化，选择一个屏蔽
    // initialize serial communication at 9600 bits per second:
    Serial.begin(9600);
    // Serial.println("Hello Arduino\n");
    #if VL53L0X_DEF
    Wire.begin();
    VL53L0Xsensor.setTimeout(500);
    if (!VL53L0Xsensor.init())
    {
        Serial.println("Failed to detect and initialize sensor!");
        while (1) {}
    }
    // Start continuous back-to-back mode (take readings as
    // fast as possible).  To use continuous timed mode
    // instead, provide a desired inter-measurement period in
    // ms (e.g. sensor.startContinuous(100)).
    VL53L0Xsensor.startContinuous();
    #endif
    


    while (!Serial)
    {
        ; // wait for serial port to connect. Needed for native USB, on LEONARDO, MICRO, YUN, and other 32u4 based boards.
    }

    // Semaphores are useful to stop a Task proceeding, where it should be paused to wait,
    // because it is sharing a resource, such as the Serial port.
    // Semaphores should only be used whilst the scheduler is running, but we can set it up here.
    if (xSerialSemaphore == NULL) // Check to confirm that the Serial Semaphore has not already been created.
    {
        xSerialSemaphore = xSemaphoreCreateMutex(); // Create a mutex semaphore we will use to manage the Serial Port
        if ((xSerialSemaphore) != NULL)
            xSemaphoreGive((xSerialSemaphore)); // Make the Serial Port available for use, by "Giving" the Semaphore.
    }

    // Now set up two Tasks to run independently.
    xTaskCreate(
        TaskSerial // 数字 128 是这个任务的堆栈的总大小
        ,
        "Serial" // A name just for humans
        ,
        1024 // This stack size can be checked & adjusted by reading the Stack Highwater
        ,
        NULL // Parameters for the task
        ,
        2 // Priority, with 3 (configMAX_PRIORITIES - 1) being the highest, and 0 being the lowest.
        ,
        NULL); // Task Handle
               //  TaskSerial 的优先级设大于 TaskLoop
    xTaskCreate(
        TaskLoop, "Loop" // A name just for humans
        ,
        1024 // Stack size
        ,
        NULL // Parameters for the task
        ,
        1 // Priority
        ,
        NULL); // Task Handle
    // Serial.println("xTAST 2  END");
    // Now the Task scheduler, which takes over control of scheduling individual Tasks, is automatically started.
    // 程序永远跑不到这里，只会在 TaskSerial 和 TaskLoop 两个中切换
    // 绝绝大部分时间都在运行 TaskLoop，TaskSerial 只每隔一个 TICK(15ms) 简短运行一次
}

/**
 * 我在字符串比较这浪费了很长时间，
 * 什么==、strcmp、String、equals、compareTo 试来试去，原因竟然是：
 * 网页仿真里的串口工具发送到单片机的数据后面会多加一个 '\n' 换行符！
 * 看着一模一样，长度却多了 1 ，再也比较不出来了
 * 正常串口工具是不会加这个换行符的
 */
void TaskSerial(void *pvParameters __attribute__((unused))) // This is a Task.
{
    // Serial.begin(9600); // 串口初始化，宜早不宜晚
    // reserve 50 bytes for the inputString:
    // 这个数字自己定，要不比你的一条命令长度小，不比这个任务的堆栈的一半大（创建这个任务时设置的堆栈为 128）
    pc_cmd.reserve(50);
    // CmdSerialConstStr cmdserialconststr = CmdSerialConstStr();
    // Serial.println("TaskSerial....");

    // initialize digital pin LED_BUILTIN as an output.
    pinMode(LED_SERIAL, OUTPUT);
    digitalWrite(LED_SERIAL, LOW);

    for (;;) // A Task shall never return or exit.
    {
        // See if we can obtain or "Take" the Serial Semaphore.
        // If the semaphore is not available, wait 5 ticks of the Scheduler to see if it becomes free.
        if (xSemaphoreTake(xSerialSemaphore, (TickType_t)5) == pdTRUE)
        { // 这个操作做互斥信号量，专门给串口申请的用来把门的门卫，有了它读写的完整过程不会打断与被打断，否则数据会乱套
            // 读和写串口相关的命令 都要放在 xSemaphoreTake 和 xSemaphoreGive 这两句之间，且不要有延时
            // We were able to obtain or "Take" the semaphore and can now access the shared resource.
            // We want to have the Serial Port for us alone, as it takes some time to print,
            // so we don't want it getting stolen during the middle of a conversion.

            // 读串口（其实是读 arduino 底层处理过的缓存）
            while (Serial.available())
            {
                // Serial.println("serial.available Taskserial");
                // get the new byte:
                char inChar = (char)Serial.read();
                // add it to the inputString:
                pc_cmd += inChar;
                // if the incoming character is a newline, set a flag so the main loop can
                // do something about it:
                if (inChar == '\n')
                {
                    stringComplete = true;
                }
            }

            xSemaphoreGive(xSerialSemaphore); // Now free or "Give" the Serial Port for others.
        }

        if (stringComplete == true)
        {
            // Serial.println("string complete == ture");
            stringComplete = false;
            // 下面要做串口命令解析了

            if (xSemaphoreTake(xSerialSemaphore, (TickType_t)5) == pdTRUE)
            {
                // 读和写串口相关的命令 都要放在 xSemaphoreTake 和 xSemaphoreGive 这两句之间，且不要有延时
                // Serial.print("inputCommand: ");
                // Serial.println(pc_cmd);

                if(pc_cmd.equals(cmdserial.PC_GET_ACT_STS))
                {
                    // pc_set_act_cmd = pc_cmd;
                    // Serial.println(crawlrobo.Get_work_sts());
                    Serial.print(crawlrobo.Get_work_sts().c_str());
                }
                else if(pc_cmd.equals(cmdserial.PC_GET_TOF_DIST))
                {
                    #if VL53L0X_DEF // VL53L0X_DEF距离传感器的时间消耗测试程序
                    int readnum = 5;
                    long dist_total = 0;
                    for (int i = 0; i < readnum; i++)
                    {
                      dist_total = dist_total + VL53L0Xsensor.readRangeContinuousMillimeters();
                    }
                    dist_avg = int(dist_total / readnum);
                    #endif //VL53L0X_DEF
                    
                    Serial.print(dist_avg); //直接将int按字面转成byte
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.GeckoMode))
                {
                    // crawlrobo.GeckoMode();
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.InchwormMode))
                {
                    // crawlrobo.InchwormMode();
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.TurnLeftCom))
                {
                  pc_set_act_cmd = pc_cmd;
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.TurnRightCom))
                {
                    // crawlrobo.TurnRightCom();
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.TurnRightSwift))
                {
                    // crawlrobo.TurnRightSwift();
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.Slope55Deg))
                {
                    // crawlrobo.Slope55Deg();
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.ClimbStairMode))
                {
                    pc_set_act_cmd = pc_cmd;
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.PaceLeft))
                {
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.PaceRight))
                {
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else if(pc_cmd.equals(cmdserial.PC_SET_ACT_MODE.PaceEnd))
                {
                    pc_set_act_cmd = pc_cmd;
                    // Serial.println(pc_set_act_cmd);
                }
                else{
                    pc_set_act_cmd = "";
                    // Serial.println(pc_set_act_cmd);
                }

                xSemaphoreGive(xSerialSemaphore); // Now free or "Give" the Serial Port for others.
            }

            // clear the string:
            pc_cmd = "";
        }

        vTaskDelay(1); // one tick delay (15ms) // 这句不能动
    }
}

/**
 * @brief 这个任务是原来 setup() 与 loop() 的结合
 *
 * @param __attribute__
 */
void TaskLoop(void *pvParameters __attribute__((unused))) // This is a Task.
{
    // 原来放在 setup() 里的现在放在这
    
    // Serial.println("Taskloop in ....");

    
    // pinMode(LED_LOOP, OUTPUT);

    // 原来放在 loop() 里的放在下面这个死循环里
    for (;;)
    {
        // Serial.println("uioo loop");
        #define test_pin 0
        #if test_pin
        // // // crawlrobo.Left(50);
        // // // delay(2000);
        // // crawlrobo.Right(50);
        // // delay(2000);
        // // // crawlrobo.TopFront(50);
        // // // delay(2000);
        // // crawlrobo.TopRear(50);
        // // delay(2000);
        // // crawlrobo.Stop();
        // // delay(2000);
        // crawlrobo.ObstacleStep();
        // delay(2000);
        // crawlrobo.Stop();
        // delay(3000);

        // crawlrobo.Left(50);
        // crawlrobo.Right(50);
        // crawlrobo.TopFront(50);
        // crawlrobo.TopRear(50);
        // crawlrobo.BottomFront(50);
        // delay(10000);
        crawlrobo.GeckoMode();
        delay(1000);
        crawlrobo.Stop();
        delay(2000);
        



        #endif

        // crawlrobo.Right(255);

        // digitalWrite(LED_LOOP, !digitalRead(LED_LOOP));
        #define main_loop 1
        #if main_loop
        // Serial.println("in main_loop__000");
        // Serial.print(pc_set_act_cmd);
        // if(pc_set_act_cmd == cmdserial.PC_GET_ACT_STS)
        //     Serial.println("in main_loop");
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.GeckoMode))
        {
            crawlrobo.GeckoMode();
            pc_set_act_cmd = "";
        }
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.InchwormMode))
        {
            crawlrobo.InchwormMode();
            pc_set_act_cmd = "";
        }
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.TurnLeftCom))
        {
            crawlrobo.TurnLeftCom();
		        pc_set_act_cmd = "";
        }
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.TurnRightCom))
        {
            crawlrobo.TurnRightCom();
            pc_set_act_cmd = "";
        }
        // if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.TurnRightSwift))
        // {
        //     crawlrobo.TurnRightSwift();
        //     pc_set_act_cmd = "";
        // }
        // if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.Slope55Deg))
        // {
        //     crawlrobo.Slope55Deg();
        //     pc_set_act_cmd = "";
        // }
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.ClimbStairMode))
        {
            crawlrobo.ObstacleStep();
		        pc_set_act_cmd = "";
        }
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.PaceLeft))
        {
            // Serial.println("PaceLeft meaga");
            crawlrobo.Pace(pc_set_act_cmd.c_str()); 
            pc_set_act_cmd = "";
        }
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.PaceRight))
        {
            // Serial.println("PaceRight meaga");
            crawlrobo.Pace(pc_set_act_cmd.c_str());
            pc_set_act_cmd = "";
        }
        if(pc_set_act_cmd.equals(cmdserial.PC_SET_ACT_MODE.PaceEnd))
        {
            // Serial.println("PaceEnd meaga");
            crawlrobo.PaceReset();
            pc_set_act_cmd = "";
        }
        // pc_set_act_cmd = "";

        
        #endif

        // #if VL53L0X_DEF // VL53L0X_DEF距离传感器的时间消耗测试程序
        // int readnum = 5;
        // long dist_total = 0;
        // for (int i = 0; i < readnum; i++)
        // {
        //   dist_total = dist_total + VL53L0Xsensor.readRangeContinuousMillimeters();
        // }
        // dist_avg = int(dist_total / readnum);
        // #endif //VL53L0X_DEF



        if (xSemaphoreTake(xSerialSemaphore, (TickType_t)5) == pdTRUE)
        {
            // 读和写串口相关的命令 都要放在 xSemaphoreTake 和 xSemaphoreGive 这两句之间，且不要有延时
            // Serial.println("*******************looop***********************");

            
            // #define test_dist 0
            // #if test_dist
            // Serial.println("test io");
            // unsigned long starttime_one, endtime_one, starttime_hundred, endtime_hundred, starttime_hundone, endtime_hundone;
            // starttime_one = millis();
            // Serial.println(VL53L0Xsensor.readRangeContinuousMillimeters());
            // endtime_one = millis();
            // Serial.print("one_period = ");
            // Serial.println(endtime_one - starttime_one);
            // // if (VL53L0Xsensor.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
            // // Serial.println();

            // int readnum = 100;
            // long dist_total = 0;
            // int dist_avg = 0;
            // starttime_hundred = millis();
            // for (int i = 0; i < readnum; i++)
            // {
            //     starttime_hundone = millis();
            //     dist_total = dist_total + VL53L0Xsensor.readRangeContinuousMillimeters();
            //     endtime_hundone = millis();
            // }
            // Serial.print("hundone_period = ");
            // Serial.println(endtime_hundone - starttime_hundone);
            // endtime_hundred = millis();
            // Serial.print("hundred_period = ");
            // Serial.print(endtime_hundred);
            // dist_avg = int(dist_total / readnum);
            // // Serial.println(dist_avg); //只能一个字节0-255,转换成16进制
            // Serial.println(dist_avg); //直接将int按字面转成byte
            // #endif


            xSemaphoreGive(xSerialSemaphore); // Now free or "Give" the Serial Port for others.
        }

        // delay(3000); // 可以用 delay()，因为它被 FreeFTOS 重定义为兼容的 vTaskDelay() 了，不过用到 delay() 的文件文件一定要加 #include <Arduino_FreeRTOS.h>
                     // 用到 delay() 的文件文件一定要加 #include <Arduino_FreeRTOS.h>

        // (如果只有这两个 task 的话)这个任务优先级低，所以它不需要主动进入阻塞态，下面这句可以不写
        // vTaskDelay(1);  // one tick delay (15ms)
    }
}

/**
 * @brief 现在这个 loop() 永远不会被执行到
 *
 */
void loop()
{
    // Empty. Things are done in Tasks.
}