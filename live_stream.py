from flask import Flask, Response, request
import cv2
import numpy as np
import pyautogui

app = Flask(__name__)

# 🔹 استریم تصویر صفحه (همان کد قبلی)
def screen_stream():
    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/stream')
def stream():
    return Response(screen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 🔹 قابلیت حرکت موس
@app.route('/move_mouse', methods=['POST'])
def move_mouse():
    data = request.json
    x, y = data.get('x'), data.get('y')
    if x is not None and y is not None:
        pyautogui.moveTo(x, y)
        return "Mouse moved", 200
    return "Invalid data", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)


























# from flask import Flask, Response
# import cv2
# import numpy as np
# import pyautogui

# app = Flask(__name__)


# def screen_stream():
#     while True:
#         screenshot = pyautogui.screenshot()
#         frame = np.array(screenshot)
#         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

#         _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
#         frame_bytes = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# @app.route('/stream')
# def stream():
#     return Response(screen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
