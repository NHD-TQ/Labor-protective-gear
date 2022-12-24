from flask import Flask, render_template, request, Response, redirect, url_for
from flask_bootstrap import Bootstrap
import pyglet

import sqlite3


# # connect database
# cn = sqlite3.connect('quan_ly.db')
# c = cn.cursor()
#
# sql_create_table = """
#     CREATE TABLE quan_ly_nhanvien (
#     condition text
#     )
# """
# #
# c.execute(sql_create_table)
# cn.commit()
# cn.close()

#
#
from object_detection import *
from camera_settings import *


application = Flask(__name__)
app = Flask(__name__)
Bootstrap(application)

# tương tác với cơ sở dữ liệu
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql + pymysql://root:12345@localhost/nhandien?charset=utf8mb4'








check_settings()
VIDEO = VideoStreaming()


@application.route("/")
def home():
    TITLE = "Detect_protective_gear"
    return render_template("index.html", TITLE=TITLE)

@application.route("/a")
def jdj():
    TITLE = "Detect_protective_gear"
    return render_template("test.html")


@application.route("/video_feed")
def video_feed():
    """
    Video streaming route.
    """
    return Response(
        VIDEO.show(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# * Button requests
@application.route("/request_preview_switch")
def request_preview_switch():
    VIDEO.preview = not VIDEO.preview
    print("*"*10, VIDEO.preview)
    return "nothing"


@application.route("/request_flipH_switch")
def request_flipH_switch():
    VIDEO.flipH = not VIDEO.flipH
    print("*"*10, VIDEO.flipH)
    return "nothing"


@application.route("/request_model_switch")
def request_model_switch():
    music = pyglet.resource.media('hello.m4a')
    music.play()
    VIDEO.detect = not VIDEO.detect
    print("*"*10, VIDEO.detect)
    return "nothing"


@application.route("/request_exposure_down")
def request_exposure_down():
    VIDEO.exposure -= 1
    print("*"*10, VIDEO.exposure)
    return "nothing"


@application.route("/request_exposure_up")
def request_exposure_up():
    VIDEO.exposure += 1
    print("*"*10, VIDEO.exposure)
    return "nothing"


@application.route("/request_contrast_down")
def request_contrast_down():
    VIDEO.contrast -= 4
    print("*"*10, VIDEO.contrast)
    return "nothing"


@application.route("/request_contrast_up")
def request_contrast_up():
    VIDEO.contrast += 4
    print("*"*10, VIDEO.contrast)
    return "nothing"


@application.route("/reset_camera")
def reset_camera():
    STATUS = reset_settings()
    print("*"*10, STATUS)
    return "nothing"


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port="6969")
    application.run(host="0.0.0.0", port="6868")