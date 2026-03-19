import streamlit as st
from PIL import Image
import numpy as np
import io
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F

# =========================
# ADVERSARIAL NETWORK (ULTRA STEALTH)
# =========================
class TinyAdversarialCNN(nn.Module):
    """شبكة عصبية صغيرة لتوليد ضوضاء adversarial خفية"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 8, 3, padding=1)
        self.conv2 = nn.Conv2d(8, 16, 3, padding=1)
        self.conv3 = nn.Conv2d(16, 3, 3, padding=1)
        self.tanh = nn.Tanh()
    
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.tanh(self.conv3(x))  # قيمة بين -1 و 1
        return x

device = "cuda" if torch.cuda.is_available() else "cpu"
adv_model = TinyAdversarialCNN().to(device)
adv_model.eval()  # فقط لتوليد الضوضاء

# =========================
# IMAGE PROTECTION PIPELINE
# =========================
def apply_micro_warp_edges(arr, strength=0.2):
    gray = cv2.cvtColor((arr*255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200).astype(bool)
    h, w, c = arr.shape
    dx = (np.random.rand(h, w)-0.5)*2*strength
    dy = (np.random.rand(h, w)-0.5)*2*strength
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (x + dx*edges).astype(np.float32)
    map_y = (y + dy*edges).astype(np.float32)
    return cv2.remap(arr, map_x, map_y, interpolation=cv2.INTER_LINEAR)

def apply_high_freq_pattern(arr, strength=0.003):
    h, w, c = arr.shape
    pattern = np.sin(np.linspace(0, 100, w))
    pattern = np.tile(pattern, (h,1))
    pattern = np.expand_dims(pattern,2)
    return arr + pattern * strength

def apply_freq_scramble(arr, strength=0.01):
    fft = np.fft.fft2(arr, axes=(0,1))
    fft_shift = np.fft.fftshift(fft)
    h, w, c = arr.shape
    mask = np.zeros((h,w))
    mask[h//2-15:h//2+15, w//2-15:w//2+15] = 1
    fft_shift *= (1 - strength*mask[:,:,np.newaxis])
    return np.fft.ifft2(np.fft.ifftshift(fft_shift), axes=(0,1)).real

def protect_image_final(img, level="متوسط"):
    arr = np.array(img).astype(np.float32)/255.0  # ← مهم float32
    h, w, c = arr.shape

    # ضبط القوة حسب المستوى
    if level=="خفيف":
        eps, warp, pattern, freq = 0.001, 0.1, 0.001, 0.003
    elif level=="متوسط":
        eps, warp, pattern, freq = 0.002, 0.2, 0.003, 0.005
    else:  # قوي
        eps, warp, pattern, freq = 0.004, 0.35, 0.005, 0.008

    # 1️⃣ Micro Warp على الحواف
    arr = apply_micro_warp_edges(arr, warp)

    # 2️⃣ High-Frequency Pattern
    arr = apply_high_freq_pattern(arr, pattern)

    # 3️⃣ Adversarial Noise من الشبكة العصبية
    tensor_img = torch.tensor(arr.transpose(2,0,1), dtype=torch.float32).unsqueeze(0).to(device)  # ← float32
    with torch.no_grad():
        perturb = adv_model(tensor_img) * eps
        adv_img = tensor_img + perturb
        adv_img = torch.clamp(adv_img, 0.0, 1.0)
    arr = adv_img.squeeze(0).cpu().numpy().transpose(1,2,0)

    # 4️⃣ Frequency Scramble خفيف
    arr = apply_freq_scramble(arr, freq)

    arr = np.clip(arr, 0, 1)
    return Image.fromarray((arr*255).astype(np.uint8))

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Ultimate AI Image Cloaker", layout="centered")
st.title("🛡️ Ultimate AI Image Cloaker (Final)")
st.caption("حماية الصور ضد أي تحليل AI بدون أي تأثير على البشر")

uploaded_file = st.file_uploader("📤 ارفع صورة", type=["png","jpg","jpeg"])
level = st.selectbox("🎯 مستوى الحماية", ["خفيف","متوسط","قوي"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="📷 الصورة الأصلية", width=600)

    if st.button("🔒 حماية الصورة"):
        protected_img = protect_image_final(img, level)
        st.image(protected_img, caption="🛡️ الصورة بعد الحماية", width=600)

        buf = io.BytesIO()
        protected_img.save(buf, format="PNG")
        st.download_button("⬇️ تحميل الصورة المحمية", buf.getvalue(), "protected.png", "image/png")
        st.success("✅ تمت حماية الصورة بنجاح")

st.markdown("---")
st.caption("Ultimate AI Image Cloaker | Built by Gamal Almaqtary")
