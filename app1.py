import streamlit as st
from PIL import Image
import numpy as np
import hashlib
import io
import random
from scipy.ndimage import gaussian_filter

# =========================
# TEXT PROTECTION (AI-RESISTANT & CLEAN)
# =========================

# حروف بديلة للغة الإنجليزية والعربية
UNICODE_MAP = {
    "A": "Α", "a": "ɑ", "o": "〇", "e": "℮",
    "i": "ι", "s": "ѕ", "c": "ϲ", "r": "я"
}

ARABIC_UNICODE_MAP = {
    "ا": "ٱ", "ي": "ى", "ه": "ة", "و": "ؤ"
}

def unicode_sub_strong(text):
    """
    استبدال حروف ذكي، يجعل النص مقاوم للذكاء الاصطناعي
    دون التأثير على القراءة البشرية.
    """
    result = ""
    for ch in text:
        if ch in UNICODE_MAP and random.random() < 0.2:
            result += UNICODE_MAP[ch]
        elif ch in ARABIC_UNICODE_MAP and random.random() < 0.2:
            result += ARABIC_UNICODE_MAP[ch]
        else:
            result += ch
    return result

def protect_text(text):
    """
    حماية النص بالكامل، مع Fingerprint داخلي
    """
    protected_text = unicode_sub_strong(text)
    fingerprint = hashlib.sha256(text.encode()).hexdigest()
    return protected_text, fingerprint

# =========================
# IMAGE PROTECTION (AI-RESISTANT & CLEAN)
# =========================

def adversarial_noise(arr, epsilon):
    noise = np.random.randn(*arr.shape) * epsilon
    return arr + noise

def high_freq_noise(arr, strength):
    pattern = np.random.randint(-strength, strength, arr.shape)
    return arr + pattern

def distort_edges(arr, alpha):
    blurred = gaussian_filter(arr, sigma=1)
    edges = arr - blurred
    return arr + edges * alpha

def color_shift(arr, max_shift=2.0):
    shift = np.random.uniform(-max_shift, max_shift, (1, 1, 3))
    return arr + shift

def protect_image(img, level):
    arr = np.array(img).astype(np.float32)

    # ضبط مستويات الضوضاء والتشويش
    if level == "خفيف":
        epsilon, alpha = 3, 0.5
    elif level == "متوسط":
        epsilon, alpha = 7, 1.2
    else:  # قوي
        epsilon, alpha = 12, 2.0

    arr = adversarial_noise(arr, epsilon)
    arr = high_freq_noise(arr, 2)
    arr = distort_edges(arr, alpha)
    arr = color_shift(arr)

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(page_title="AI Cloaker Pro", layout="centered")

st.title("🛡️ AI Cloaker Pro")
st.caption("نظام حماية ذكي للنصوص والصور ضد الذكاء الاصطناعي | بدون أي دخيل")

mode = st.radio("اختر النوع:", ["نص", "صورة"])

# =========================
# TEXT
# =========================
if mode == "نص":
    input_text = st.text_area("✍️ أدخل النص:", height=200)

    if st.button("🔒 حماية النص"):
        if not input_text.strip():
            st.warning("أدخل نص أولاً")
        else:
            protected, fp = protect_text(input_text)

            st.subheader("📄 النص المحمي")
            st.text_area("انسخ النص:", value=protected, height=200)

            st.subheader("🔑 Fingerprint")
            st.code(fp)

            st.success("تمت حماية النص بالكامل ضد AI بدون أي تغييرات مرئية على القراءة")

# =========================
# IMAGE
# =========================
else:
    uploaded_file = st.file_uploader("📤 ارفع صورة", type=["png", "jpg", "jpeg"])

    level = st.select_slider("🎯 مستوى الحماية", options=["خفيف", "متوسط", "قوي"], value="متوسط")

    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")

        st.subheader("📷 الصورة الأصلية")
        st.image(img, use_column_width=True)

        if st.button("🔒 حماية الصورة"):
            protected_img = protect_image(img, level)

            st.subheader("🛡️ بعد الحماية")
            st.image(protected_img, use_column_width=True)

            buf = io.BytesIO()
            protected_img.save(buf, format="PNG")

            st.download_button(
                "⬇️ تحميل الصورة المحمية",
                buf.getvalue(),
                "protected.png",
                "image/png"
            )

            st.success("تمت حماية الصورة ضد AI مع الحفاظ على وضوحها للبشر")

# Footer
st.markdown("---")
st.caption("AI Cloaker Pro | Built by Gamal Almaqtary")
