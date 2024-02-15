import cv2 as cv
import numpy as np 
from keras.models import load_model
from enum import Enum
from pfand_types import BankWorkState
import threading as thrd

class NeuralState(Enum):
    NOT_INITED = 61
    INITED = 62
    FAILED = 63
    FAILED_DOUBLE = 64
    INITING = 65

class Neural:
    def __init__(self, app):
        self.app = app
        self.camId = app.config['cam_id']
        self.logger = app.logger
        self.state = NeuralState.NOT_INITED
        self._fails = 0

    def init(self):
        try:
            self.state = NeuralState.INITING
            self.logger("started initing camera")
            self.cvCam = cv.VideoCapture(self.camId)
            self.cvCam.read()
            self.logger("camera inited")
            self.logger("loading model")
            self.model = load_model("model.h5", compile=False)
            self.logger("model loaded")
            self.logger("neural inited")
            self.state = NeuralState.INITED
        except Exception as e:
            self._fails += 1
            if self._fails > 1: self.state = NeuralState.FAILED_DOUBLE
            else:               self.state = NeuralState.FAILED
            self.logger(f"ERROR --- init neural failed: {e}")

    def __call__(self):
        if self.app.bankWorkState == BankWorkState.NEED_START_NEURAL:
            thrd.Thread(target=self.neuralCheck).start()
            self.app.bankWorkState = BankWorkState.NEURAL_CHECK
            self.logger("neural check started")

    def neuralCheck(self):
        isSuccess, frame = self.cvCam.read()
        if isSuccess:   
            self.logger("cam read success")
            cv.imwrite("lastNeuralFrame.png", frame)
            frame = cv.resize(frame, (224, 224))
            frame = (frame.astype('float32')/127.5)-1
            frameArray = np.asarray([frame.tolist()])
            if self.app.bankWorkState == BankWorkState.NEURAL_CHECK:
                self.logger("predicts started")
                preds = self.model.predict(frameArray)
            else:
                self.logger("iterupted")
                return
            predIndex = np.argmax(preds)
            if self.app.bankWorkState == BankWorkState.NEURAL_CHECK:
                match predIndex:
                    case 0:
                        self.app.bankWorkState = BankWorkState.CARD
                        self.logger("neural success with result: CARD")
                    case 1:
                        self.app.bankWorkState = BankWorkState.NEURAL_FAIL
                        self.logger("neural success with result: NEURAL_FAIL")
        else:
            self.app.bankWorkState = BankWorkState.NEURAL_FAIL
            self.logger("ERROR --- camera returned not success code")