from flask import Flask, render_template, Response
import cv2
import dlib
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Inisialisasi detektor wajah dan predictor landmarks
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Variabel global
not_focused_start_time = None
focused_start_time = None
log = []  # Log ketidakfokusan
total_not_focused_duration = 0  # Total waktu tidak fokus dalam detik
total_focused_duration = 0  # Total waktu fokus dalam detik

def calculate_ear(eye_points):
    """Menghitung Eye Aspect Ratio (EAR) untuk mendeteksi apakah mata terbuka atau tertutup."""
    a = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    b = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    c = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    ear = (a + b) / (2.0 * c)
    return ear

eye_closed_start_time = None
blink_duration_threshold = 0.5  # Waktu maksimal kedipan dalam detik
min_ear_threshold = 0.2  # Batas bawah untuk mata menyipit
max_eye_closed_duration = 3.0  # Batas waktu mata tertutup dianggap tidak fokus (3 detik)

def is_focused(landmarks, sensitivity=15, ear_threshold=0.25):
    """Memeriksa apakah wajah pengguna menghadap kamera dan mata tetap terbuka."""
    global eye_closed_start_time

    left_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
    right_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

    # Hitung EAR untuk kedua mata
    left_ear = calculate_ear(left_eye_points)
    right_ear = calculate_ear(right_eye_points)

    # EAR rata-rata
    avg_ear = (left_ear + right_ear) / 2.0

    # Periksa apakah mata terbuka atau menyipit
    if avg_ear < min_ear_threshold:
        if eye_closed_start_time is None:
            eye_closed_start_time = datetime.now()
        else:
            elapsed = (datetime.now() - eye_closed_start_time).total_seconds()
            if elapsed > max_eye_closed_duration:
                return False  # Mata tertutup lebih dari 3 detik, dianggap tidak fokus
    else:
        eye_closed_start_time = None  # Reset ketika mata terbuka atau menyipit

    # Periksa apakah hidung berada di tengah mata
    left_eye = landmarks.part(36).x
    right_eye = landmarks.part(45).x
    nose_tip = landmarks.part(30).x
    return abs(nose_tip - ((left_eye + right_eye) / 2)) <= sensitivity

def generate_frames():
    global not_focused_start_time, focused_start_time, total_not_focused_duration, total_focused_duration, log
    camera = cv2.VideoCapture(0)  # Akses kamera
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector(gray)

            if len(faces) > 0:
                for face in faces:
                    x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    landmarks = landmark_predictor(gray, face)

                    # Cek apakah fokus atau tidak
                    if is_focused(landmarks, sensitivity=15, ear_threshold=0.25):
                        cv2.putText(frame, "Focus", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        if focused_start_time is None:
                            focused_start_time = datetime.now()
                        # Reset not focused time
                        if not_focused_start_time:
                            elapsed = (datetime.now() - not_focused_start_time).total_seconds()
                            total_not_focused_duration += elapsed
                            # Menambahkan log ketidakfokusan
                            log.append({
                                'time': not_focused_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'duration': round(elapsed, 2)
                            })
                            not_focused_start_time = None
                    else:
                        cv2.putText(frame, "Not Focus", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        if not_focused_start_time is None:
                            not_focused_start_time = datetime.now()
                        # Reset focused time
                        if focused_start_time:
                            elapsed = (datetime.now() - focused_start_time).total_seconds()
                            total_focused_duration += elapsed
                            focused_start_time = None

            # Jika wajah tidak terdeteksi
            else:
                cv2.putText(frame, "Not Focus", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if not_focused_start_time is None:
                    not_focused_start_time = datetime.now()
                if focused_start_time:
                    elapsed = (datetime.now() - focused_start_time).total_seconds()
                    total_focused_duration += elapsed
                    focused_start_time = None

            # Encode frame ke JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/result')
def result():
    global total_focused_duration, total_not_focused_duration, focused_start_time, not_focused_start_time
    
    # Akhiri perhitungan waktu fokus/tidak fokus
    if focused_start_time:
        total_focused_duration += (datetime.now() - focused_start_time).total_seconds()
    if not_focused_start_time:
        total_not_focused_duration += (datetime.now() - not_focused_start_time).total_seconds()

    # Hitung statistik
    total_time = total_focused_duration + total_not_focused_duration
    focus_index = (total_focused_duration / total_time * 100) if total_time > 0 else 0
    
    # Hitung rata-rata durasi tidak fokus
    avg_duration = round(total_not_focused_duration / len(log), 2) if log else 0
    
    # Konversi total_time ke menit
    total_time_minutes = round(total_time / 60, 1)
    
    # Tentukan tingkat konsentrasi
    if focus_index >= 90:
        concentration_level = "Sangat Baik"
        next_target = "Pertahankan performa ini"
    elif focus_index >= 78:
        concentration_level = "Baik"
        next_target = "Tingkatkan ke level sangat baik"
    elif focus_index >= 60:
        concentration_level = "Cukup"
        next_target = "Tingkatkan ke level baik"
    else:
        concentration_level = "Kurang"
        next_target = "Tingkatkan ke level cukup"

    # Menentukan keterangan berdasarkan focus_index
    if focus_index <= 60:
        focus_description = "Kualitas fokus anda sangat buruk"
    elif focus_index <= 78:
        focus_description = "Kualitas fokus anda buruk"
    elif focus_index <= 90:
        focus_description = "Kualitas fokus anda baik"
    else:
        focus_description = "Kualitas fokus anda sangat baik"

    return render_template('result.html', 
                         focus_log=log,
                         total=len(log),
                         focus_index=round(focus_index, 2),
                         focus_description=focus_description,
                         avg_duration=avg_duration,
                         total_time=total_time_minutes,
                         concentration_level=concentration_level,
                         next_target=next_target)

if __name__ == '__main__':
    app.run(debug=True)
