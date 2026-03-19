import streamlit as st
from PIL import Image
import numpy as np
import io
import cv2

# =========================
# IMAGE PROCESSING
# =========================

def micro_warp(arr, strength=1.0):
    h, w, c = arr.shape
    dx = (np.random.rand(h, w) - 0.5) * strength
    dy = (np.random.rand(h, w) - 0.5) * strength
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (x + dx).astype(np.float32)
    map_y = (y + dy).astype(np.float32)
    return cv2.remap(arr, map_x, map_y, interpolation=cv2.INTER_LINEAR)

def high_freq_noise(arr, intensity):
    noise = np.random.randn(*arr.shape) * (0.02 * intensity)
    return arr + noise

def frequency_scramble(arr, intensity):
    fft = np.fft.fft2(arr, axes=(0,1))
    fft_shift = np.fft.fftshift(fft)

    h, w, c = arr.shape
    mask = np.random.rand(h, w) < (0.05 * intensity)
    fft_shift[mask] *= (0.8 + np.random.rand())

    return np.fft.ifft2(np.fft.ifftshift(fft_shift), axes=(0,1)).real

def jpeg_artifacts(arr, quality):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, encimg = cv2.imencode('.jpg', (arr*255).astype(np.uint8), encode_param)
    decimg = cv2.imdecode(encimg, 1).astype(np.float32) / 255.0
    return decimg

def protect_image(img, intensity=0.5, quality=85):
    arr = np.array(img).astype(np.float32) / 255.0

    # تطبيق المعالجات
    arr = micro_warp(arr, 1.5 * intensity)
    arr = high_freq_noise(arr, intensity)
    arr = frequency_scramble(arr, intensity)
    arr = jpeg_artifacts(arr, quality)

    arr = np.clip(arr, 0, 1)
    return Image.fromarray((arr * 255).astype(np.uint8))

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(page_title="AI Cloaker Pro", layout="centered")

st.title("🛡️ AI Image Cloaker Pro")
st.caption("حماية الصور ضد تحليل الذكاء الاصطناعي مع الحفاظ على الجودة")

# رفع الصورة
uploaded_file = st.file_uploader("📤 ارفع صورة", type=["png","jpg","jpeg"])

# إعدادات
intensity = st.slider("🎛️ قوة الحماية (Intensity)", 0.0, 1.0, 0.5)
quality = st.slider("🧩 جودة الصورة (JPEG Quality)", 50, 100, 85)

# عرض
if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="📷 الأصل", width=300)

    if st.button("🔒 تطبيق الحماية"):
        protected = protect_image(img, intensity, quality)

        with col2:
            st.image(protected, caption="🛡️ بعد الحماية", width=300)

        # تحميل
        buf = io.BytesIO()
        protected.save(buf, format="PNG")

        st.download_button(
            "⬇️ تحميل الصورة",
            buf.getvalue(),
            "protected.png",
            "image/png"
        )

        st.success("✅ تمت الحماية بنجاح")

st.markdown("---")
st.caption("AI Cloaker Pro | Built by Gamal Almaqtary")
