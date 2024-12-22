let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let logList = document.getElementById("log-list");

let faceCascade;
let isRecording = false;  // Variable untuk menandakan apakah sedang merekam atau tidak

// Fungsi untuk memuat OpenCV.js
function openCvReady() {
    console.log("OpenCV.js is ready!");

    // Load Haar cascade untuk deteksi wajah
    faceCascade = new cv.CascadeClassifier();
    faceCascade.load('haarcascade_frontalface_default.xml');

    // Mulai streaming video
    startVideo();
}

// Deteksi wajah
function detectFace() {
    if (!faceCascade || !isRecording) return;  // Hanya deteksi wajah jika sedang merekam

    const src = new cv.Mat(video.videoHeight, video.videoWidth, cv.CV_8UC4);
    const gray = new cv.Mat();
    const faces = new cv.RectVector();

    // Tangkap frame video dan konversi ke grayscale
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    src.data.set(ctx.getImageData(0, 0, canvas.width, canvas.height).data);
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY, 0);

    // Deteksi wajah
    faceCascade.detectMultiScale(gray, faces, 1.1, 3, 0);

    // Periksa apakah wajah terdeteksi
    if (faces.size() > 0) {
        for (let i = 0; i < faces.size(); ++i) {
            let face = faces.get(i);
            ctx.beginPath();
            ctx.rect(face.x, face.y, face.width, face.height);
            ctx.lineWidth = 2;
            ctx.strokeStyle = "green";
            ctx.stroke();
        }
    } else {
        // Log waktu ketidakfokusan jika tidak ada wajah
        const now = new Date();
        const time = `${now.getHours()}:${now.getMinutes()}`;
        const listItem = document.createElement("li");
        listItem.textContent = `Not Focused at ${time}`;
        logList.appendChild(listItem);
    }

    src.delete();
    gray.delete();
    faces.delete();
}

// Jalankan deteksi wajah setiap 100ms
setInterval(detectFace, 100);

// Menambahkan event listener untuk tombol "Start Focus Record"
document.getElementById("startFocusButton").addEventListener("click", () => {
    isRecording = true;  // Set isRecording menjadi true ketika tombol ditekan
    document.getElementById("startFocusButton").disabled = true;  // Menonaktifkan tombol setelah ditekan
    console.log("Focus recording started");
});

