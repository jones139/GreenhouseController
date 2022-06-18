/**
 * This file is part of waterController.
 *
 * WaterController is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * WaterController  is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with WaterController. If not, see <https://www.gnu.org/licenses/>.
 *
 * Copyright Graham Jones 2022 (graham@openseizuredetector.org.uk)
 *
 */


#include "waterController.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "driver/uart.h"
#include "driver/gpio.h"


int onSecs = 1;
int cycleSecs = 5;
int debug = 1;

TaskHandle_t TaskHandle_xtask1;
TaskHandle_t TaskHandle_xtask2;

#define WATER_PIN 2
#define GPIO_OUTPUT_PIN_SEL  ((1ULL<<WATER_PIN))
#define STACK_SIZE_xtask1		4096
#define STACK_SIZE_xtask2		4096


void TaskWaterController(void *pvParameters)  // This is a task.
{
  (void) pvParameters;

  gpio_config_t io_conf;
  //disable interrupt
  io_conf.intr_type = GPIO_INTR_DISABLE;
  //set as output mode
  io_conf.mode = GPIO_MODE_OUTPUT;
  //bit mask of the pins that you want to set,e.g.GPIO15/16
  io_conf.pin_bit_mask = GPIO_OUTPUT_PIN_SEL;
  //disable pull-down mode
  io_conf.pull_down_en = 0;
  //disable pull-up mode
  io_conf.pull_up_en = 0;
  //configure GPIO with the given settings
  gpio_config(&io_conf);

  for (;;) {
    // Switch on the water at teh start of the cycle
    if (debug) printf("WATER ON\n");
    gpio_set_level(WATER_PIN, 0);
    // We only delay for 1 sec to avoid integer overflow on number of
    // ticks to delay.
    for (int i=0; i<onSecs; i++) {
      vTaskDelay( 1000 / portTICK_PERIOD_MS );
    }
    if (debug) printf("WATER OFF\n");
    gpio_set_level(WATER_PIN, 1);
    // Now wait for the rest of the cycle with the water off.
    // Again we only delay for 1 sec to avoid integer overruns.
    for (int i=0; i<(cycleSecs-onSecs); i++) {
      vTaskDelay( 1000 / portTICK_PERIOD_MS );
    }
  }
}



/**
 * This is an example which echos any data it receives on UART0 back to the sender,
 * with hardware flow control turned off. It does not use UART driver event queue.
 *
 * - Port: UART0
 * - Receive (Rx) buffer: on
 * - Transmit (Tx) buffer: off
 * - Flow control: off
 * - Event queue: off
 */

#define BUF_SIZE (1024)

static void echo_task()
{
  char *lineStr;
  char *token;
  char *key;
  //char *valStr;
  // Configure parameters of an UART driver,
  // communication pins and install the driver
  uart_config_t uart_config = {
    .baud_rate = 74880,
    .data_bits = UART_DATA_8_BITS,
    .parity    = UART_PARITY_DISABLE,
    .stop_bits = UART_STOP_BITS_1,
    .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
  };
  uart_param_config(UART_NUM_0, &uart_config);
  uart_driver_install(UART_NUM_0, BUF_SIZE * 2, 0, 0, NULL, 0);
  
  // Configure a temporary buffer for the incoming data
  uint8_t *data = (uint8_t *) malloc(BUF_SIZE);
  
  while (1) {
    // Read data from the UART
    int len = uart_read_bytes(UART_NUM_0, data, BUF_SIZE, 20 / portTICK_RATE_MS);
    // Write data back to the UART
    //uart_write_bytes(UART_NUM_0, (const char *) data, len);

    if (len > 0) {
      lineStr = (char *)data;
      token = strtok_r(lineStr,"\n", &lineStr);
      printf("Found newline - token=%s, lineStr=%s\n", token, lineStr);
      while (token != NULL) {
	printf("Found newline - token=%s, lineStr=%s\n", token, lineStr);
	//key = strtok_r(lineStr,"=",&lineStr);
	//printf("key=%s\n",key);
	//printf("valStr%s\n",lineStr);
	  
      }
	
    }
  }
}



/* -----------------------------------------------------------------------------
   GetTaskHighWaterMarkPercent( TaskHandle_t task_handle, uint32_t stack_allotment )
   
   Input Params:
   - task_handle: The task handle name
   - stack_allotment:  How much stack space did you allocate to it when you created it
   
  Returns: float with the % of stacke used
  Example:   printf("Stack Used %04.1f%%\r\n", GetTaskHighWaterMarkPercent(xTask1, 2048) );
  Notes:
  -----------------------------------------------------------------------------*/
float GetTaskHighWaterMarkPercent( TaskHandle_t task_handle,
				   uint32_t stack_allotment ) {
  UBaseType_t uxHighWaterMark;
  uint32_t diff;
  float result;
  uxHighWaterMark = uxTaskGetStackHighWaterMark( task_handle );
  diff = stack_allotment - uxHighWaterMark;
  result = ( (float)diff / (float)stack_allotment ) * 100.0;  
  return result;
}


void app_main()
{
  xTaskCreate(echo_task,
	      "uart_echo_task", STACK_SIZE_xtask1,
	      NULL, 10, &TaskHandle_xtask1);

  xTaskCreate(
	      TaskWaterController
	      ,  "Water Controller"   // A name just for humans
	      ,  STACK_SIZE_xtask2  // stack size
	      ,  NULL
	      ,  2  
	      ,  &TaskHandle_xtask2 );
  
  while(1)
    {
      TickType_t xTime1 = xTaskGetTickCount();
      
      
      uint8_t temp1 =  (uint8_t)GetTaskHighWaterMarkPercent(TaskHandle_xtask1, STACK_SIZE_xtask1);
      uint8_t temp2 =  (uint8_t)GetTaskHighWaterMarkPercent(TaskHandle_xtask2, STACK_SIZE_xtask2);
      
      printf("\r\n************************************************\r\n");
      printf("Tick:         %06.1f\r\n", (float)xTime1 / 100.00);
      printf("xTask1:       %03u%%\r\n", temp1);
      printf("xTask2:       %03u%%\r\n", temp2);
      
      if(temp1 > 90)
	{
	  printf("!!! WARNING xTask1 Stack Useage to HIGH !!!\r\n");
	}
      
      
      vTaskDelay(10000 / portTICK_PERIOD_MS);	
    }  
}
