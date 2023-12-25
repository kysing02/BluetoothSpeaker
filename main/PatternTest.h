
#ifndef PatternTest_H
#define PatternTest_H

class PatternTest : public Drawable {
  private:

  public:
    PatternTest() {
      name = (char *)"Test Pattern";
    }

    unsigned int drawFrame() {

      canvas->fillScreen(dma_display->color565(128, 0, 0));  
      return 1000;
    }
};

#endif
