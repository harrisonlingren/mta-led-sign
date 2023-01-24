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
      chainLength: 1,
      hardwareMapping: GpioMapping.AdafruitHat,
      pixelMapperConfig: LedMatrixUtils.encodeMappers({
        type: PixelMapperType.U,
      }),
    },
    {
      ...LedMatrix.defaultRuntimeOptions(),
      gpioSlowdown: 1,
      dropPrivileges: 1,
    }
  );
  