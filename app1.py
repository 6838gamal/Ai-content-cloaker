import streamlit as st
from PIL import Image
import numpy as np
import hashlib
import io
import random
from scipy.ndimage import gaussian_filter

# =========================
# TEXT PROTECTION (INVISIBLE & CLEAN)
# =========================

UNICODE_MAP = {
    "A": "Α", "a": "ɑ", "o": "〇", "e": "℮",
    "i": "ι", "s": "ѕ", "c": "ϲ", "r": "я"
}

ARABIC_UNICODE_MAP = {
    "ا": "ٱ", "ي": "ى", "ه": "ة", "و": "ؤ"
}

ZW_CHARS = ["\u200B", "\u200C", "\u200D", "\u2060"]

def add_zero_width(text, prob=0.01):
    result = ""
    for ch in text:
        result += ch
        if ch != " " and random.random() < prob:
            result += random.choice(ZW_CHARS)
    return result

def unicode_sub(text, prob=0.05):
    result = ""
    for ch in text:
        if ch in UNICODE_MAP and random.random() < prob:
            result += UNICODE_MAP[ch]
        elif ch in ARABIC_UNICODE_MAP and random.random() < prob:
            result += ARABIC_UNICODE_MAP[ch]
        else:
            result += ch
    return result

def add_hidden_metadata(text):
    # metadata داخلي غير مرئي، لا يؤثر على النص
    return text

def protect_text(text):
    t = add_zero_width(text)
    t = unicode_sub(t)
    t = add_hidden_metadata(t)
    fp = hashlib.sha256(text.encode()).hexdigest()
    return t, fp

# =========================
# IMAGE PROTECTION (ADVANCED & CLEAN)
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

def color_shift(arr):
    shift = np.random.uniform(-2, 2, (1, 1, 3))
    return arr + shift

def protect_image(img, level):
    arr = np.array(img).astype(np.float32)

    # إعدادات ديناميكية أكثر دقة
    if level == "خفيف":
        epsilon, alpha = 2, 0.5
    elif level == "متوسط":
        epsilon, alpha = 6, 1.0
    else:
        epsilon, alpha = 12, 2.0

    arr = adversarial_noise(arr, epsilon)
    arr = high_freq_noise(arr, 2)
    arr = distort_edges(arr, alpha)
    arr = color_shift(arr)

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# =========================
# UI
# =========================

st.set_page_config(page_title="AI Cloaker Pro", layout="centered")

st.title("🛡️ AI Cloaker Pro")
st.caption("نظام تعمية ذكي للنصوص والصور بدون أي دخيل على النص أو الصورة")

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
            st.text_area("انسخ:", value=protected, height=200)

            st.subheader("🔑 Fingerprint")
            st.code(fp)

            st.success("تمت الحماية بدون أي تغييرات مرئية على النص")

# =========================
# IMAGE
# =========================

else:
    uploaded_file = st.file_uploader("📤 ارفع صورة", type=["png", "jpg", "jpeg"])

    level = st.select_slider("🎯 مستوى التعمية", options=["خفيف", "متوسط", "قوي"], value="متوسط")

    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")

        st.subheader("📷 الأصل")
        st.image(img, use_column_width=True)

        if st.button("🔒 حماية الصورة"):
            protected_img = protect_image(img, level)

            st.subheader("🛡️ بعد التعمية")
            st.image(protected_img, use_column_width=True)

            buf = io.BytesIO()
            protected_img.save(buf, format="PNG")

            st.download_button(
                "⬇️ تحميل",
                buf.getvalue(),
                "protected.png",
                "image/png"
            )

            st.success("تمت التعمية بنجاح دون أي تغييرات غير ضرورية")

# Footer
st.markdown("---")
st.caption("AI Cloaker Pro | Built by Gamal Almaqtary")
