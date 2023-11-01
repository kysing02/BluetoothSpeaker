#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include "display.h"

// Display pointer
MatrixPanel_I2S_DMA *dma_display = nullptr;

void initialize_display() {
    HUB75_I2S_CFG::i2s_pins _pins={R1_PIN, G1_PIN, B1_PIN, R2_PIN, G2_PIN, B2_PIN, A_PIN, B_PIN, C_PIN, D_PIN, E_PIN, LAT_PIN, OE_PIN, CLK_PIN};
    HUB75_I2S_CFG mxconfig(
        PANEL_RES_X, // Module width
        PANEL_RES_Y, // Module height
        PANEL_CHAIN, // chain length
        _pins // pin mapping
    );
    dma_display = new MatrixPanel_I2S_DMA(mxconfig);
}