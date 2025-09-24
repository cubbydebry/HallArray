#include <FreeRTOS.h>
#include <semphr.h>
#include <task.h>

typedef struct {
    SemaphoreHandle_t lock;
    volatile int *counter;
    TickType_t wait;
} CriticalCtx;

// Outline for deadlock test later

typedef struct {
    SemaphoreHandle_t a;
    SemaphoreHandle_t b;
    TickType_t wait;
    TaskHandle_t thA;
    TaskHandle_t thB;
} DeadlockPair;

 BaseType_t do_iteration(const CriticalCtx *ctx);
 void start_deadlock_pair(DeadlockPair *p, UBaseType_t prio);
 int orphaned_lock(SemaphoreHandle_t semaphore, TickType_t timeout, int *counter);
 int unorphaned_lock(SemaphoreHandle_t semaphore, TickType_t timeout, int *counter);
 