#include <stdio.h>
#include <pico/stdlib.h>
#include <stdint.h>
#include <unity.h>
#include "unity_config.h"
#include "threads.h"

void setUp(void) {}

void tearDown(void) {}

// ---- Activity 2 ----

void test_incr_unlocked(void)
{
    SemaphoreHandle_t s = xSemaphoreCreateCounting(1, 1);
    volatile int counter = 0;
    CriticalCtx ctx = { .lock = s, .counter = &counter, .wait = 0};
    
    TEST_ASSERT_EQUAL(pdTRUE, do_iteration(&ctx));
    TEST_ASSERT_EQUAL(1, counter);

    vSemaphoreDelete(s);
}

void test_incr_locked(void)
{
    SemaphoreHandle_t s = xSemaphoreCreateCounting(1, 1);
    volatile int counter = 0;
    CriticalCtx ctx = { .lock = s, .counter = &counter, .wait = 0};

    TEST_ASSERT_EQUAL(pdTRUE, xSemaphoreTake(ctx.lock, ctx.wait));
    TEST_ASSERT_EQUAL(pdFALSE, do_iteration(&ctx));
    TEST_ASSERT_EQUAL(0, counter);
    xSemaphoreGive(ctx.lock);
    vSemaphoreDelete(s);
}

// ---- Activity 4 ----

void test_deadlock_pair(void) {
    DeadlockPair p = {0};

    p.a = xSemaphoreCreateCounting(1, 1);
    p.b = xSemaphoreCreateCounting(1, 1);
    p.wait = portMAX_DELAY;
    TEST_ASSERT_NOT_NULL(p.a);
    TEST_ASSERT_NOT_NULL(p.b);

    start_deadlock_pair(&p, tskIDLE_PRIORITY + 1);

    // Wait to reach deadlock
    vTaskDelay(pdMS_TO_TICKS(50));

    // Both should be blocked
    eTaskState sa = eTaskGetState(p.thA);
    eTaskState sb = eTaskGetState(p.thB);
    TEST_ASSERT_TRUE(sa == eBlocked || sa == eSuspended);
    TEST_ASSERT_TRUE(sb == eBlocked || sb == eSuspended);

    // Cleanup
    vTaskSuspend(p.thA);
    vTaskSuspend(p.thB);
    vTaskDelete(p.thA);
    vTaskDelete(p.thB);
    vSemaphoreDelete(p.a);
    vSemaphoreDelete(p.b);
}

// ---- Activity 5 ----

void test_orphaned(void)
{
    int counter = 1;
    SemaphoreHandle_t semaphore = xSemaphoreCreateCounting(1, 1);
    TEST_ASSERT_NOT_NULL(semaphore);

    int result = orphaned_lock(semaphore, pdMS_TO_TICKS(500), &counter);
    TEST_ASSERT_EQUAL_INT(2, counter);
    TEST_ASSERT_EQUAL_INT(pdTRUE, result);
    TEST_ASSERT_EQUAL_INT(1, uxSemaphoreGetCount(semaphore));

    result = orphaned_lock(semaphore, pdMS_TO_TICKS(500), &counter);
    TEST_ASSERT_EQUAL_INT(3, counter);
    TEST_ASSERT_EQUAL_INT(0, result);
    TEST_ASSERT_EQUAL_INT(0, uxSemaphoreGetCount(semaphore));

    result = orphaned_lock(semaphore, pdMS_TO_TICKS(500), &counter);
    TEST_ASSERT_EQUAL_INT(3, counter);
    TEST_ASSERT_EQUAL_INT(pdFALSE, result);
    TEST_ASSERT_EQUAL_INT(0, uxSemaphoreGetCount(semaphore));
}

void test_fixed_orphan(void)
{
    int counter = 1;
    SemaphoreHandle_t semaphore = xSemaphoreCreateCounting(1, 1);
    TEST_ASSERT_NOT_NULL(semaphore);

    int result;
    result = unorphaned_lock(semaphore, pdMS_TO_TICKS(500), &counter);
    TEST_ASSERT_EQUAL_INT(2, counter);
    TEST_ASSERT_EQUAL_INT(pdTRUE, result);
    TEST_ASSERT_EQUAL_INT(1, uxSemaphoreGetCount(semaphore));

    result = unorphaned_lock(semaphore, pdMS_TO_TICKS(500), &counter);
    TEST_ASSERT_EQUAL_INT(3, counter);
    TEST_ASSERT_EQUAL_INT(0, result);
    TEST_ASSERT_EQUAL_INT(1, uxSemaphoreGetCount(semaphore));
}

static void rtos_test_task(void *pvParameters) {

    for(;;){
        UNITY_BEGIN();

        printf("\n==== START UNITY TESTS ====");

        RUN_TEST(test_incr_unlocked);
        RUN_TEST(test_incr_locked);
        RUN_TEST(test_orphaned);
        RUN_TEST(test_fixed_orphan);
        RUN_TEST(test_deadlock_pair);

        printf("\n==== END UNITY TESTS ====");

        UNITY_END();
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
    vTaskSuspend(NULL);
}

int main (void)
{
    stdio_init_all();
    sleep_ms(5000); // Give time for TTY to attach.

    xTaskCreate(
        rtos_test_task,
        "tester",               
        configMINIMAL_STACK_SIZE + 1024,
        NULL,                    
        tskIDLE_PRIORITY + 1,    
        NULL                     
    );

    // Start scheduler so vTaskDelay and tasks actually run
    vTaskStartScheduler();
}
