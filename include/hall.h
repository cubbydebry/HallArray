#include <stdint.h>
#include <stddef.h>

#define FS_HZ 750
#define PERIOD pdMS_TO_TICKS(1000 / FS_HZ)

typedef struct {
    int32_t sum;
    uint16_t buf[64];
    size_t N;
    size_t i;
    size_t filled;
} sma_t;

void sma_init(sma_t *f);
uint16_t sma_push(sma_t *f, uint16_t in);