import cv2 as cv
import numpy as np
from modesEnum import Modes
class Image_processing(object):

    def __init__(self,imgPath: str):
        self.imgPath = imgPath

        self.imgData = cv.imread(self.imgPath,0)
        print(self.imgData)
        self.Size = self.imgData.shape
        self.dft = np.fft.fftshift(np.fft.fft2(self.imgData))
        self.real = np.real(self.dft)
        self.imaginary = np.imag(self.dft)
        self.magnitude = np.abs(self.dft)
        self.phase = np.angle(self.dft)
        # self.unitMag = np.arange(self.Size).astype(type())
        
        self.finalVlue = None
        self.newValue = None


    def mixing(self, imageToBeMixed: 'Image_processing', Ratio: float, mode: 'Modes') -> np.ndarray:
        '''
        func used to change a specific parameter in the image 

        imageToBeMixed : seconed image with type Image_processing
        Ratio : the ratio of change
        mode : there is four modes availabe realMode , imaginaryMode , phaseMode , magnitudeMode
        depend on the mode selected the changing will be ...
        '''
        if mode == Modes.realMode:  
            self.newValue = self.real * Ratio + imageToBeMixed.real * (1 - Ratio)
        elif mode == Modes.imaginaryMode:
            self.newValue = self.imaginary * Ratio + imageToBeMixed.imaginary * (1 - Ratio)
        elif mode == Modes.phaseMode:
            self.newValue = self.phase * Ratio + imageToBeMixed.phase *(1 - Ratio)
        elif mode == Modes.magnitudeMode:
            self.newValue = self.magnitude *Ratio + imageToBeMixed.magnitude * (1-Ratio)
        elif mode == Modes.unitMag:
            self.newValue = 1
        elif mode == Modes.uniPhase:
            self.newValue = 0
        return self.newValue

    def reconstrain ( val1, val2 ,  mode: 'Modes'):
        '''
        func that reconstrain the changed value and return the image

        val1 : real or magnitude depend on mode

        val2 : imagin or phase depen on mode
        
        mode : there is just two modes available realAndImaginary or magnitudeAndPhase
        '''
        if mode == Modes.realAndImaginary:
            finalValue = val1 + val2*1j
        if mode == Modes.magnitudeAndPhase:
            finalValue = val1 * ( np.cos(val2) + np.sin(val2) * 1j )
        
        finalValue = np.abs(np.fft.ifft2(np.fft.ifftshift(finalValue)))

        return(finalValue)



    def mix(self, imageToBeMixed: 'Image_processing', magnitudeOrRealRatio: float, phaesOrImaginaryRatio: float, mode: 'Modes') -> np.ndarray:
        """
        a function that takes ImageModel object mag ratio, phase ration and
        return the magnitude of ifft of the mix
        return type ---> 2D numpy array

        please Add whatever functions realted to the image data in this file
        """

        if mode == Modes.realAndImaginary:  
            self.realComponent =self.mixing(imageToBeMixed,magnitudeOrRealRatio,Modes.realMode)
            self.imaginaryComponent = self.mixing(imageToBeMixed,phaesOrImaginaryRatio , Modes.imaginaryMode)
            self.finalVlue = self.reconstrain(self.realComponent,self.imaginaryComponent , mode)
        else:
            self.magnitudeComponent =self.mixing(imageToBeMixed,magnitudeOrRealRatio,Modes.magnitudeMode)
            self.phaseComponent = self.mixing(imageToBeMixed,phaesOrImaginaryRatio , Modes.phaseMode)
            self.finalVlue = self.reconstrain(self.magnitudeComponent,self.phaseComponent , mode)
        return(self.finalVlue)




