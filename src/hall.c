#include "hall.h"

/**
 * Initialize the SMA filter
 * @param f Pointer to the sma_t structure
 * @return void
 */
void sma_init(sma_t *f) {
    f->sum = 0;
    f->i = 0;
    f->filled = 0;
    for (size_t k = 0; k < f->N; k++)
        f->buf[k] = 0;
}

/**
 * Push a new value into the SMA filter and get the current average
 * @param f Pointer to the sma_t structure
 * @param in New input value
 * @param out Pointer to store the output average
 * @return The current average
 */
uint16_t sma_push(sma_t *f, uint16_t in) {
    if (f->filled == f->N) {
        f->sum -= f->buf[f->i];
    } else {
        f->filled++;
    }
    
    f->buf[f->i] = in;
    f->sum += in;

    f->i = (f->i + 1) % f->N;

    uint16_t out = (uint16_t)f->sum / (int32_t)f->filled;
    return out;
}