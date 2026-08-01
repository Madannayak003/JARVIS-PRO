import cv2
import threading
import datetime
from config.paths import RECORDINGS

class CameraManager:

    def __init__(self):

        self.camera = None
        self.index = 0

        self.preview = False
        self.thread = None

        self.current_frame = None
        
        self.recording = False
        self.writer = None
        
        self.is_open = False
        

    def start(self):

        if self.camera is None:

            self.camera = cv2.VideoCapture(self.index)

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def frame(self):

        self.start()

        ok, frame = self.camera.read()

        if ok:

            self.current_frame = frame

            return frame

        return None
    
    def capture_with_countdown(self, seconds=3):

        self.start()

        window = "JARVIS Camera"

        frame = None

        for sec in range(seconds, 0, -1):

            start = cv2.getTickCount()

            while True:

                ok, frame = self.camera.read()

                if not ok:
                    continue

                self.current_frame = frame

                display = frame.copy()

                cv2.putText(
                    display,
                    str(sec),
                    (display.shape[1] // 2 - 40, display.shape[0] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    5,
                    (0, 255, 0),
                    8
                )

                cv2.imshow(window, display)

                key = cv2.waitKey(1)

                if key == 27:
                    self.stop()
                    return None

                elapsed = (
                    cv2.getTickCount() - start
                ) / cv2.getTickFrequency()

                if elapsed >= 1:
                    break

        # Flash effect

        flash = frame.copy()

        flash[:] = 255

        cv2.imshow(window, flash)

        cv2.waitKey(120)

        ok, frame = self.camera.read()

        if ok:
            self.current_frame = frame

        return self.current_frame

    def _preview_loop(self):

        self.preview = True

        self.start()

        while self.preview:

            ok, frame = self.camera.read()

            if not ok:
                continue

            self.current_frame = frame
            
            if self.recording and self.writer:

                self.writer.write(frame)

            cv2.imshow("JARVIS Camera", frame)

            if cv2.waitKey(1) == 27:

                self.preview = False

        self._cleanup()

    def show(self):

        if self.thread and self.thread.is_alive():
            return

        self.thread = threading.Thread(
            target=self._preview_loop,
            daemon=True
        )

        self.thread.start()
        
    def start_recording(self):

        self.start()

        if self.recording:
            return

        filename = datetime.datetime.now().strftime(
            "Video_%Y%m%d_%H%M%S.mp4"
        )

        path = RECORDINGS / filename

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.writer = cv2.VideoWriter(
            str(path),
            fourcc,
            30,
            (width, height)
        )

        self.recording = True

        print("Recording:", path)
        
    def stop_recording(self):

        self.recording = False

        if self.writer:

            self.writer.release()

            self.writer = None

        print("Recording stopped.")        

    def stop(self):

        self.preview = False

        if (
            self.thread
            and self.thread.is_alive()
            and threading.current_thread() != self.thread
        ):
            self.thread.join(timeout=1)

        self._cleanup()

    def _cleanup(self):

        self.recording = False

        if self.writer:

            self.writer.release()

            self.writer = None

        if self.camera:

            self.camera.release()

            self.camera = None

        cv2.destroyAllWindows()
        
    def opened(self):

        return self.camera is not None

    def switch(self, index):

        self.stop()

        self.index = index

        self.start()

camera = CameraManager()