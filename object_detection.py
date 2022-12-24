import os
import time
import cv2
import numpy as np
import sqlite3
import pyglet

# connect database
cn = sqlite3.connect('quan_ly.db', check_same_thread=False)
c = cn.cursor()


class ObjectDetection:
    def __init__(self):
        PROJECT_PATH = os.path.abspath(os.getcwd())
        MODELS_PATH = os.path.join(PROJECT_PATH, "models")

        self.MODEL = cv2.dnn.readNet(
            os.path.join(MODELS_PATH, "yolov4-custom_best.weights"),
            os.path.join(MODELS_PATH, "yolov4-custom.cfg")
        )

        # self.MODEL = cv2.dnn.readNet(
        #     os.path.join(MODELS_PATH, "yolov3.weights"),
        #     os.path.join(MODELS_PATH, "yolov3.cfg")
        # )

        # self.cn = sqlite3.connect('quan_ly.db')
        # self.c = self.cn.cursor()

        self.CLASSES = []
        with open(os.path.join(MODELS_PATH, "yolo.names"), "r") as f:
            self.CLASSES = [line.strip() for line in f.readlines()]

        # Cac bien check
        self.no_ao = 0
        self.no_mu = 0
        self.no_ao_mu = 0
        self.p = 0
        self.insert = 0

        self.OUTPUT_LAYERS = [
            self.MODEL.getLayerNames()[i - 1] for i in self.MODEL.getUnconnectedOutLayers()
        ]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
        self.COLORS /= (np.sum(self.COLORS**2, axis=1)**0.5/255)[np.newaxis].T


    def detectObj(self, snap):
        no_persion = 0
        # c = cn.cursor()
        # cn = sqlite3.connect('quan_ly.db')
        # c = self.cn.cursor()
        check_mu = False
        check_ao = False
        height, width, channels = snap.shape
        blob = cv2.dnn.blobFromImage(
            snap, 1/255, (416, 416), swapRB=True, crop=False
        )

        self.MODEL.setInput(blob)
        outs = self.MODEL.forward(self.OUTPUT_LAYERS)

        # ! Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # print(confidence)
                # x, y, w, h = boxes[out]
                # label = str(self.CLASSES[class_ids[i]])
                # cv2.putText(snap, "{} [{:.2f}]".format(label, float(confidence)),
                #             (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                #             self.COLORS[out], 2)
                if confidence > 0.5:
                    # * Object detected
                    # cv2.putText(snap, confidence, (x, y - 5), font, 2, color, 2)
                    center_x = int(detection[0]*width)
                    center_y = int(detection[1]*height)
                    w = int(detection[2]*width)
                    h = int(detection[3]*height)

                    # * Rectangle coordinates
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)


        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        font = cv2.FONT_HERSHEY_PLAIN
        a = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.CLASSES[class_ids[i]])
                confidence = str(round(confidences[i],2))
                color = self.COLORS[i]
                cv2.rectangle(snap, (x, y), (x + w, y + h), color, 2)
                cv2.putText(snap, label + " " + confidence, (x, y - 5), font, 2, (255,255,255), 2)

                if class_ids[i] == 2 or class_ids[i] == 3 or class_ids[i] == 4 or class_ids[i] == 5:
                    check_mu = True
                if class_ids[i] == 1:
                    check_ao = True

                a.append(class_ids[i])
        # while len(a) == 0:
        #     no_persion = no_persion + 1
        # if(no_persion > 100000000) :
        #    cv2.putText(snap, "NOT CONECTED", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #    cn.close()
        # else:
        #     cv2.putText(snap, "CONECTED", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #     no_persion = 0

        if len(a) != 0:
            if check_mu == False and len(a) == 2:
                self.no_mu += 1
                self.no_ao = 0
                self.no_ao_mu = 0
                self.p = 0
                if self.no_mu > 20 and self.insert == 0:
                    sql_insert = """
                    INSERT INTO quan_ly_nhanvien VALUES ('NO HELMET')
                    """
                    c.execute(sql_insert)
                    cn.commit()
                    music = pyglet.resource.media('thieu_mu.m4a')
                    music.play()
                    # cn.close()
                    # self.insert = 1
                    cv2.putText(snap, "OK CHECK DONE", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    self.no_mu = 0
                cv2.putText(snap, "NO HELMET", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            elif check_mu == True and check_ao == True and len(a) == 3:
                self.p += 1
                self.no_ao = 0
                self.no_mu = 0
                self.no_ao_mu = 0
                if self.p > 13 and self.insert == 0:
                    sql_insert = """
                        INSERT INTO quan_ly_nhanvien VALUES ('PASS')
                    """
                    c.execute(sql_insert)
                    cn.commit()
                    music = pyglet.resource.media('full.m4a')
                    music.play()
                    # cn.close()
                    # self.insert = 1
                    cv2.putText(snap, "OK CHECK DONE", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    self.p = 0
                cv2.putText(snap, "PASS -->", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            elif check_mu == False and check_ao == False and len(a) == 1:
                self.no_ao_mu += 1
                self.no_ao = 0
                self.no_mu = 0
                self.p = 0
                if self.no_ao_mu > 20 and self.insert == 0:
                    sql_insert = """
                                    INSERT INTO quan_ly_nhanvien VALUES ('NO HELMET AND SHIRT')
                                    """
                    c.execute(sql_insert)
                    cn.commit()
                    self.no_ao_mu = 0
                    # time.sleep(5)
                    music = pyglet.resource.media('thieu_ao_mu.m4a')
                    music.play()
                    # cn.close()
                    # self.insert = 1
                    cv2.putText(snap, "OK CHECK DONE", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(snap, "NO HELMET AND SHIRT", (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            else:
                self.no_ao += 1
                self.no_mu = 0
                self.no_ao_mu = 0
                self.p = 0
                if self.no_ao > 20 and self.insert == 0:
                    sql_insert = """
                                    INSERT INTO quan_ly_nhanvien VALUES ('NO SHIRT')
                                    """
                    c.execute(sql_insert)
                    cn.commit()
                    music = pyglet.resource.media('thieu_ao.m4a')
                    music.play()
                    # cn.close()
                    # self.insert = 1
                    self.no_ao = 0
                    cv2.putText(snap, "OK CHECK DONE", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(snap, "NO SHIRT", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return snap


class VideoStreaming(object):
    def __init__(self):
        super(VideoStreaming, self).__init__()
        self.VIDEO = cv2.VideoCapture(0)

        self.MODEL = ObjectDetection()

        self._preview = True
        self._flipH = False
        self._detect = False
        self._exposure = self.VIDEO.get(cv2.CAP_PROP_EXPOSURE)
        self._contrast = self.VIDEO.get(cv2.CAP_PROP_CONTRAST)

    @property
    def preview(self):
        return self._preview

    @preview.setter
    def preview(self, value):
        self._preview = bool(value)

    @property
    def flipH(self):
        return self._flipH

    @flipH.setter
    def flipH(self, value):
        self._flipH = bool(value)

    @property
    def detect(self):
        return self._detect

    @detect.setter
    def detect(self, value):
        self._detect = bool(value)

    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, value):
        self._exposure = value
        self.VIDEO.set(cv2.CAP_PROP_EXPOSURE, self._exposure)

    @property
    def contrast(self):
        return self._contrast

    @contrast.setter
    def contrast(self, value):
        self._contrast = value
        self.VIDEO.set(cv2.CAP_PROP_CONTRAST, self._contrast)

    def show(self):
        while(self.VIDEO.isOpened()):
            ret, snap = self.VIDEO.read()
            if self.flipH:
                snap = cv2.flip(snap, 1)

            if ret == True:
                if self._preview:
                    # snap = cv2.resize(snap, (0, 0), fx=0.5, fy=0.5)
                    if self.detect:
                        snap = self.MODEL.detectObj(snap)

                else:
                    snap = np.zeros((
                        int(self.VIDEO.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                        int(self.VIDEO.get(cv2.CAP_PROP_FRAME_WIDTH))
                    ), np.uint8)
                    label = "camera disabled"
                    H, W = snap.shape
                    font = cv2.FONT_HERSHEY_PLAIN
                    color = (255, 255, 255)
                    cv2.putText(snap, label, (W//2 - 100, H//2),
                                font, 2, color, 2)

                frame = cv2.imencode(".jpg", snap)[1].tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.01)

            else:
                break
        print("off")
