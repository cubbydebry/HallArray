#include "threads.h"
#include <stdio.h>

BaseType_t do_iteration(const CriticalCtx *ctx) {
    if (xSemaphoreTake(ctx->lock, ctx->wait) != pdTRUE) {
        return pdFALSE;
    }
    (*ctx->counter)++;
    xSemaphoreGive(ctx->lock);
    return pdTRUE;
}

// Orphaned Lock (broken)
int orphaned_lock(SemaphoreHandle_t semaphore, TickType_t timeout, int *counter)
{
    if (xSemaphoreTake(semaphore, timeout) == pdFALSE)
        return pdFALSE;
    {
        (*counter)++;
        if (*counter % 2) {
            return 0;
        }
        printf("Count %d\n", *counter);
    }
    xSemaphoreGive(semaphore);
    return pdTRUE;
}

// Orphaned Lock (fixed)
int unorphaned_lock(SemaphoreHandle_t semaphore, TickType_t timeout, int *counter)
{
    if (xSemaphoreTake(semaphore, timeout) == pdFALSE)
        return pdFALSE;
    {
        (*counter)++;
        if (!(*counter % 2)) {
            printf("Count %d\n", *counter);
        }
    }
    xSemaphoreGive(semaphore);
    return pdTRUE;
}


// Take A, wait, then try B
static void taskA(void *pv) {
    DeadlockPair *p = (DeadlockPair*)pv;

    xSemaphoreTake(p->a, portMAX_DELAY);
    vTaskDelay(pdMS_TO_TICKS(10));
    xSemaphoreTake(p->b, p->wait); // Should stall here

    xSemaphoreGive(p->b);   // Clean up
    xSemaphoreGive(p->a);
    vTaskDelete(NULL);
}

static void taskB(void *pv) {
    DeadlockPair *p = (DeadlockPair*)pv;

    xSemaphoreTake(p->b, portMAX_DELAY);
    vTaskDelay(pdMS_TO_TICKS(10));
    xSemaphoreTake(p->a, p->wait); // Stalls here

    xSemaphoreGive(p->a);   // Clean up, shouldn't make it here
    xSemaphoreGive(p->b);
    vTaskDelete(NULL);
}

// Task to test the broken orphned_lock function with small delay
static void lockedOrphanTask(void *pv)
{
    struct{SemaphoreHandle_t s; TickType_t timeout; int *counter;} *p = pv;
    while(1)
    {
        orphaned_lock(p->s, p->timeout, p->counter);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}


// Task to test the fixed orphned_lock function with small delay
static void unlockedOrphanTask(void *pv)
{
    struct{SemaphoreHandle_t s; TickType_t timeout; int *counter;} *p = pv;
    while(1)
    {
        unorphaned_lock(p->s, p->timeout, p->counter);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void start_deadlock_pair(DeadlockPair *p, UBaseType_t prio) {
    // p->a = xSemaphoreCreateCounting(1, 1);   // Create these in test instead
    // p->b = xSemaphoreCreateCounting(1, 1);

    configASSERT(p->a && p->b);
    xTaskCreate(taskA, "A", configMINIMAL_STACK_SIZE, p, prio, &p->thA);
    xTaskCreate(taskB, "B", configMINIMAL_STACK_SIZE, p, prio, &p->thB);
}

// Start the broken/deadlocked orphan thread
static void startLockedOrphanTask(SemaphoreHandle_t s, TickType_t timeout, int *counter, UBaseType_t prio, TaskHandle_t *out)
{
    static struct {
         SemaphoreHandle_t s;
         TickType_t t; int *c;
         } args;

    args.s = s;
    args.t = timeout;
    args.c = counter;

    xTaskCreate(lockedOrphanTask, "deadlocked_orphan", configMINIMAL_STACK_SIZE, &args, prio, out);
}

// Star the fixed/unlocked orphan thread
static void startUnlockedOrphanTask(SemaphoreHandle_t s, TickType_t timeout, int *counter, UBaseType_t prio, TaskHandle_t *out)
{
    static struct {
         SemaphoreHandle_t s;
         TickType_t t; int *c;
         } args;

    args.s = s;
    args.t = timeout;
    args.c = counter;

    xTaskCreate(unlockedOrphanTask, "unlocked_orphan", configMINIMAL_STACK_SIZE, &args, prio, out);
}

