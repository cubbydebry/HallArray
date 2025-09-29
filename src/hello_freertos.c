/**
 * Copyright (c) 2022 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include <stdio.h>

#include "FreeRTOS.h"
#include "task.h"
#include "hall.h"

#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "pico/cyw43_arch.h"

#include "hardware/adc.h"
#include "hardware/gpio.h"

int count = 0;
bool on = false;
sma_t filter = {.N = 4};

#define MAIN_TASK_PRIORITY      ( tskIDLE_PRIORITY + 1UL )
#define BLINK_TASK_PRIORITY     ( tskIDLE_PRIORITY + 2UL )
#define MAIN_TASK_STACK_SIZE configMINIMAL_STACK_SIZE
#define BLINK_TASK_STACK_SIZE configMINIMAL_STACK_SIZE

void ADC_setup() {
    adc_init();
    adc_gpio_init(28);
    adc_select_input(2);
}

void blink_task(__unused void *params) {
    hard_assert(cyw43_arch_init() == PICO_OK);
    while (true) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, on);
        if (count++ % 11) on = !on;
        vTaskDelay(500);
    }
}

void main_task(__unused void *params) {
    xTaskCreate(blink_task, "BlinkThread",
                BLINK_TASK_STACK_SIZE, NULL, BLINK_TASK_PRIORITY, NULL);
    while(1) {
        uint16_t raw = adc_read();
        uint16_t result = sma_push(&filter, raw) * 3300 / (1 << 12);
        printf("Voltage: %d\n", result);
        vTaskDelay(100);
    }
}

int main( void )
{
    stdio_init_all();
    ADC_setup();
    const char *rtos_name;
    rtos_name = "FreeRTOS";
    TaskHandle_t task;
    sma_init(&filter);
    xTaskCreate(main_task, "MainThread",
                MAIN_TASK_STACK_SIZE, NULL, MAIN_TASK_PRIORITY, &task);
    vTaskStartScheduler();
    return 0;
}
