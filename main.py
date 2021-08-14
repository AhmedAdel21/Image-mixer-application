
#libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QFileDialog,QMessageBox )
import numpy as np
from final_GUI import *
import cv2 as cv
from imageModel import Image_processing
from modesEnum import Modes
import logging


class ApplicationWindow(Ui_MainWindow):
    def __init__ (self, MainWindow):
        super(ApplicationWindow, self).setupUi(MainWindow)
        #create and configure logger
        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename="D:\\Sys & Bio\\Sys & Bio 3rd year\\2nd Semester\\DSP\\assignments\\task_3\\Submission\\sbe309-2020-task3-AAA2021\\tracking.log",
                            level=logging.DEBUG,
                            format=LOG_FORMAT)
        self.logger = logging.getLogger()
        ## hidding the unwanted things in thee plot 
        self.img_list =[self.Image1_change,self.Image1_view,self.Image2_change,self.Image2_view,
        self.output1,self.output2]
        for i in self.img_list:
            i.ui.roiBtn.hide()
            i.ui.menuBtn.hide()
            i.ui.histogram.hide()
            i.ui.roiPlot.hide()
        #######
        self.file1_flag=False               # flag to know if there is a file or not
        self.img1_flag=False                # ,,  ,, ,,   ,, there is an image 1 or not
        self.img2_flag =False               # ,,  ,  ,  , , , ,,  , ,  ,   , ,  2 ,, ,,
        self.slider_2_value = 0             # init the slider 2 value to 0
        self.slider_1_value = 0             # ,,   ,,   ,,    1  ,,   ,, ,,
        self.Open_image.triggered.connect(self.open_file)           # when click to open image connect it to func open file to open it
        self.Block1_combo.currentIndexChanged.connect(lambda:self.inputTronsformPlot(0))        # when change the combo box of image 1 connect it with value 0 (to know that is the combobox 1) to func inputTronsformPlot that contain the transformation of the image
        self.Block2_combo.currentIndexChanged.connect(lambda:self.inputTronsformPlot(1))        # ... image 2 ...
        self.combo_choose_output.currentIndexChanged[int].connect(self.output_view)             # when the combobox of the output changed connect it to output_view
        self.component_1_slider.valueChanged[int].connect(self.dataMixer)          # when slider of component 1 changed conncet it to pp
        self.component_2_slider.valueChanged[int].connect(self.dataMixer)          # ..            ....       2  .....
        self.combobox1List = [self.component_1_check_real,self.component_1_check_imag,self.component_1_check_mag,self.component_1_check_phase,self.component_1_check_umag,self.component_1_check_uphase]    # list of the checkboxes of component 1
        self.combobox2List = [self.component_2_check_real,self.component_2_check_imag,self.component_2_check_mag,self.component_2_check_phase,self.component_2_check_umag,self.component_2_check_uphase]    # list of the checkboxes of component 2
        self.component_1_combobox.currentIndexChanged[int].connect(lambda:self.change_image(0)) # chosse which image to be in the component 1
        self.component_2_combobox.currentIndexChanged[int].connect(lambda:self.change_image(1)) #  ..               . . . .  ..  . . . .   2
        #######     manage the check boxes      #######
        self.buttongroup1 = QtWidgets.QButtonGroup()        # make a buttongroup to contain all the check boxes of component 1
        self.buttongroup1.setExclusive(True)                # when we ckeck one of the checkbox all the others will be unchecked
        for i in range(len(self.combobox1List)):            # put all check boxes of component 1 in buttongroup 1 with id from 0 to 5
            self.buttongroup1.addButton(self.combobox1List[i],i)

        self.buttongroup2 = QtWidgets.QButtonGroup()        # make a buttongroup to contain all the check boxes of component 2
        self.buttongroup2.setExclusive(True)                # ...
        for i in range(len(self.combobox2List)):            # put all check boxes of component 2 in buttongroup 2 with id from 6 to 11
            self.buttongroup2.addButton(self.combobox2List[i],6+i)

        self.change ={'0':1,'1':0,'2':3,'3':2,'4':5,'5':4} # make a dic contain the check box and its counterpart 
        # connect the buttongroups to its clicked func
        self.buttongroup1.buttonClicked[int].connect(self.on_button_clicked)
        self.buttongroup2.buttonClicked[int].connect(self.on_button_clicked)
        ######
        # make a list contain all modes that we will use
        self.modeList = [ Modes.realMode , Modes.imaginaryMode , Modes.magnitudeMode , Modes.phaseMode , Modes.unitMag , Modes.uniPhase]    # modes to mixing the images
        self.modeReconstrainList = [Modes.realAndImaginary,Modes.magnitudeAndPhase] # modes to reconstrian the image
        ####
        self.output_viewList = [self.output1,self.output2] # list contain the output imageviews
        self.outIndex =0        # index of the output imageview in the output_viewList
        self.choose_img = []        # a list to but in all image that we will insert 
        self.component_1_value =0   # the data that will return from mixing the component 1 
        self.component_2_value =0   # the data that will return from mixing the component 2
        self.errorMasg = ["There is no image 2","It must have same size of image 1","you should restart the program to be able to relaod new images","Please open an image first","Please check one of the checkboxes"]       # Error messages
        self.component_1_image , self.component_2_image = None, None
        self.componentImageList = [self.component_1_image,self.component_2_image]
        self.componentComboboxList = [self.component_1_combobox,self.component_2_combobox] 
    def output_view(self,index):
        '''
        take the index of the combobox and plot the image if this imageview
        '''
        if self.img1_flag == True:
            self.outIndex = index
            self.output_viewList[self.outIndex].setImage(self.finalOutput.T)
        else:
            self.logger.warning("the user choose one of the output imageview without load any image")
            self.Error(3)

    def change_image(self, index):
        '''
        depend on the index we decide which combobox we dea with
        if 0 that indicate to component 1.
        if 1 that indicate to component 2.
        '''
        try:
            self.componentImageList[index] = self.choose_img[self.componentComboboxList[index].currentIndex()]  # we take the image that the user choose from component's combobox
            self.resetSliderValues()            # set the two sliders to 0 value 
        except:
            # if there is one image and the user choose image 2 we will popup an error message
            self.logger.warning("the user doesn't load image two but choose image 2 from component's combobox ")
            self.componentComboboxList[index].setCurrentIndex(0)
            self.Error(0)
        
        
    def resetSliderValues(self):
        self.component_1_slider.setValue(50)
        self.component_2_slider.setValue(151)
        

    def on_button_clicked(self, id):
        '''
        this func control the two groups of checkboxes depend on the id we will know which one of the 12 checkboxes in checked
        id from 0 to 5 this mean that the check box in buttongroup one (checkbox of the component 1)
        id from 6 to 11 this mean that the check box in buttongroup two (checkbox of the component 2)
        '''
        if self.img1_flag == True:
            if id < 6:
                if id == 4:
                    self.buttongroup2.button(self.change[str(id)]+4).toggle()
                elif id == 5 :
                    self.buttongroup2.button(self.change[str(id)]+4).toggle()
                else:
                    self.buttongroup2.button(self.change[str(id)]+6).toggle()
                
            else:
                if id == 10:
                    self.buttongroup1.button(self.change[str(id-6)]-2).toggle()
                elif id == 11:
                    self.buttongroup1.button(self.change[str(id-6)]-2).toggle()
                else:
                    self.buttongroup1.button(self.change[str(id-6)]).toggle()
            self.resetSliderValues() # set the two sliders to 0 value 
        else:
            self.logger.warning("the user check one of the checkboxes but s\he doesn't load any image ")
            self.Error(3)
            

    def dataMixer(self,value):
        '''
        in this func we control the values of the 2 sliders 
        if the value sent is from 0 to 100 so, it's slider 1
        if the value sent is from 101 to 201 so, it's slider 2
        '''
        # get sliders' values
        if self.img1_flag == True:
            if self.buttongroup1.checkedButton():
                if value < 101:
                    self.component_1_slider_lable.setText(str(value)+'%')

                    try:            # we use try to avoid the Zerodivision error
                        self.slider_1_value = value/100             # make the value of the slider 1 as a Ratio 
                    except:
                        self.logger.info("the user make slider 1 being zero value")
                        self.slider_1_value =0

                    self.modeSelect_1 = self.modeList[self.buttongroup1.checkedId()]    # we choose the mode depend on the checkbox of the component 1

                    self.component_1_value = self.componentImageList[0].mixing(self.componentImageList[1],self.slider_1_value,self.modeSelect_1) # take the result of the mixing happened in component 1  
                else:
                    # as above
                    self.component_2_slider_lable.setText(str(value-101)+'%')
                    try:
                        self.slider_2_value =(value-101)/100
                    except:
                        self.logger.info("the user make slider 2 being zero value")
                        self.slider_2_value = 0

                    self.modeSelect_2 = self.modeList[np.abs(self.buttongroup2.checkedId()-6)]      
                    self.component_2_value = self.componentImageList[1].mixing(self.componentImageList[0],self.slider_2_value,self.modeSelect_2)

                self.reconstrainImage()
            else:
                self.logger.warning("the user move the slider but s/he doesn't check any checkbox")
                self.Error(4)
        else:
            self.logger.warning("the user move the slider but s/he doesn't load any image")
            self.Error(3)




    def reconstrainImage(self):
        '''
        in this func we use the changed data and reconstrain the image in specific output imageview
        '''
        if self.buttongroup1.checkedId() < 2:
            self.select = 0     # to select RealAndImaginary mode
        else:
            self.select = 1     # to select PhaseAndMagnetude mode

        if self.modeSelect_1 == Modes.realMode or self.modeSelect_1 == Modes.magnitudeMode or self.modeSelect_1 == Modes.unitMag:
            self.finalOutput = Image_processing.reconstrain(self.component_1_value , self.component_2_value , self.modeReconstrainList[self.select])
        elif self.modeSelect_1 == Modes.imaginaryMode or self.modeSelect_1 == Modes.phaseMode or self.modeSelect_1 == Modes.uniPhase:
            self.finalOutput = Image_processing.reconstrain( self.component_2_value , self.component_1_value , self.modeReconstrainList[self.select] )

        # plot the image in specific output imageview
        self.output_viewList[self.outIndex].setImage(self.finalOutput.T)
        

    def inputTronsformPlot(self,index):
        """
        plot the input in its transform form
        """
        if index == 0 :
            if self.img1_flag ==True:
                self.img1List = [20*np.log(self.img1.magnitude.T),self.img1.phase.T,20*np.log(self.img1.real.T),self.img1.imaginary.T]
                self.Image1_change.setImage(self.img1List[self.Block1_combo.currentIndex()])       
        else :
            if self.img2_flag ==True:
                self.img2List =[20*np.log(self.img2.magnitude.T),self.img2.phase.T,20*np.log(self.img2.real.T),self.img2.imaginary.T]
                self.Image2_change.setImage(self.img2List[self.Block2_combo.currentIndex()])     

    def open_file(self):
        fname = QFileDialog.getOpenFileName(None, 'Open file', "D:\Sys & Bio\Sys & Bio 3rd year\2nd Semester\DSP\assignments\task_3\First Version")
        if fname[0]:
            if self.img1_flag == False: 
                self.img1_flag = True
                self.img1 = Image_processing(fname[0])       # make an object of class image processing
                self.Image1_view.setImage(self.img1.imgData.T)       # plot the image
                self.Image1_change.setImage(20*np.log(self.img1.magnitude.T))   
                self.finalOutput = self.img1.imgData        # init the final output
                self.output1.setImage(self.finalOutput.T)   
                self.choose_img.append(self.img1)       #put this image in the image list
                self.componentImageList[0] = self.img1  
                self.componentImageList[1] = self.img1
                

            elif self.img2_flag == False:
                self.img2 = Image_processing(fname[0])
                if self.img1.Size == self.img2.Size:
                    self.img2_flag =True
                    self.Image2_view.setImage(self.img2.imgData.T)
                    self.Image2_change.setImage(20*np.log(self.img2.magnitude.T))
                    self.choose_img.append(self.img2)
                else:
                    self.logger.warning("the user load two images not in the same size")
                    self.Error(1)
            else:
                self.logger.warning("the user load more than two images")
                self.Error(2)


    def Error(self,type):
        '''
        popup a specific error message depend on type sent
        '''
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(self.errorMasg[type])
        msg.setIcon(QMessageBox.Critical)
        x = msg.exec_()





            


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = ApplicationWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())