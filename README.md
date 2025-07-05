# 🎬 Interactive Video Analyzer with Audio Separation

An interactive Streamlit-based web application that allows users to upload a video, extract its audio, separate vocals and background music using AI (Spleeter), and navigate through individual video frames. This tool is ideal for media analysis, educational purposes, and audio-visual content inspection.

---

## 🧩 Features

### 🎞️ Original Video Playback
- Upload and play videos directly in the browser.
- Supported formats: `.mp4`, `.mov`, `.avi`.

### 🔊 Audio Extraction
- Extract audio from the uploaded video file.
- Play the extracted audio directly in the interface.

### 🎤 Audio Separation (Vocals & Background)
- Use **Spleeter (2 stems)** to separate:
  - **Vocals (speech, singing)**
  - **Accompaniment (background music)**
- Preview separated audio tracks interactively.

### 📸 Frame-by-Frame Viewer
- Navigate through specific frames of the video using:
  - Slider
  - Next/Previous buttons
- Useful for video inspection and media analysis.

---

## 🛠️ Technologies Used

| Technology | Purpose                         |
|------------|---------------------------------|
| Streamlit  | Web interface & interaction     |
| MoviePy    | Audio extraction from video     |
| Spleeter   | AI-based audio source separation|
| OpenCV     | Frame extraction & manipulation |
| PIL        | Image rendering in Streamlit    |

---

## Demo User Interface Images:
(https://github.com/user-attachments/assets/85aa9184-bba0-4642-86f9-bb2cf332546b)
(https://github.com/user-attachments/assets/08840285-7131-4623-917b-e1199d7c1158)
(https://github.com/user-attachments/assets/e8f8ba4d-b3ff-4bfd-83dc-83b5cb3b36d0)
(https://github.com/user-attachments/assets/82db23a2-ff0f-488c-b03a-a7b7f1600ec1)
(https://github.com/user-attachments/assets/c900ca3e-9ff8-4117-9a09-ded5434ea0ac)

## 🚀 Getting Started

### 🔧 Prerequisites

Ensure you have Python 3.7+ and the following dependencies:

```bash
pip install streamlit moviepy spleeter opencv-python-headless pillow
