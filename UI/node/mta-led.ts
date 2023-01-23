import {
    LedMatrix,
    GpioMapping,
    LedMatrixUtils,
    PixelMapperType,
  } from 'rpi-led-matrix';
  
  const matrix = new LedMatrix(
    {
      ...LedMatrix.defaultMatrixOptions(),
      rows: 32,
      cols: 64,
      chainLength: 2,
      hardwareMapping: GpioMapping.AdafruitHatPwm,
      pixelMapperConfig: LedMatrixUtils.encodeMappers({
        type: PixelMapperType.U,
      }),
    },
    {
      ...LedMatrix.defaultRuntimeOptions(),
      gpioSlowdown: 1,
    }
  );
  