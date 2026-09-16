import io
import math
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw
import cv2
import matplotlib.pyplot as plt
from knowledge import MANUAL_RULES

st.set_page_config(page_title="SORTEX Bichro Setup Advisor", page_icon="📊", layout="wide")

st.title("SORTEX Z+R Bichro Setup Advisor")
st.caption("Screenshot/photo analysis + manual-derived colour-map guidance + projected corrected histogram")

with st.sidebar:
    st.header("Machine context")
    product = st.text_input("Product / grade", placeholder="e.g. pecans, rice, seed")
    view = st.selectbox("View", ["Unknown", "Front", "Rear"])
    position = st.selectbox("Position", ["Unknown", "Position 1", "Position 2"])
    view_mode = st.selectbox("View combination", ["Unknown", "Combined", "Independent"])
    logic = st.selectbox("Sorting logic", ["Unknown", "OR", "AND"])
    objective = st.text_area("Known good product / known defect", placeholder="Describe what should pass and what should be rejected.")
    st.divider()
    st.markdown("**Interpretation rules**")
    st.caption("Colour 1 = horizontal axis. Colour 2 = vertical axis. Display colours indicate frequency, not physical product colour.")

uploaded = st.file_uploader("Upload a clear photo or screenshot of the current Bühler screen", type=["png", "jpg", "jpeg", "webp"])

if not uploaded:
    st.info("Upload the Colour Map / Histogram screen. A straight-on screenshot is best; a phone photo also works.")
    with st.expander("Manual-derived knowledge built into this version"):
        for section, rules in MANUAL_RULES.items():
            st.markdown(f"**{section.replace('_',' ').title()}**")
            for r in rules:
                st.write("•", r)
    st.stop()

img = Image.open(uploaded).convert("RGB")
arr = np.array(img)
h, w = arr.shape[:2]

st.subheader("1. Locate the histogram / colour map")
st.write("Use the crop controls to place the box tightly around the graph itself. This makes the geometric analysis much more reliable than trying to guess through the whole machine screen.")

c1, c2 = st.columns([1.3, 1])
with c1:
    st.image(img, caption=f"Uploaded image — {w}×{h}", use_container_width=True)
with c2:
    left = st.slider("Crop left %", 0, 90, 5)
    right = st.slider("Crop right %", left + 5, 100, 55)
    top = st.slider("Crop top %", 0, 90, 5)
    bottom = st.slider("Crop bottom %", top + 5, 100, 70)
    x1, x2 = int(w*left/100), int(w*right/100)
    y1, y2 = int(h*top/100), int(h*bottom/100)
    crop = arr[y1:y2, x1:x2]
    st.image(crop, caption="Analysis crop", use_container_width=True)

st.subheader("2. Histogram analysis")

# Build a conservative point mask: exclude near-white/gray UI background and very dark text/axes.
hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
H, S, V = cv2.split(hsv)
# Histogram dots on the legacy SORTEX UI are generally coloured/teal; saturation is useful.
mask = ((S > 45) & (V > 45)).astype(np.uint8) * 255
# Remove tiny isolated UI noise.
kernel = np.ones((3,3), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
ys, xs = np.where(mask > 0)

# Coordinate convention for chart: y increases upward.
points = np.column_stack([xs, crop.shape[0]-1-ys]) if len(xs) else np.empty((0,2))

# Exclude a likely background blob at extreme lower-right when it is spatially isolated.
filtered = points.copy()
if len(points) > 100:
    xn = points[:,0] / max(crop.shape[1]-1, 1)
    yn = points[:,1] / max(crop.shape[0]-1, 1)
    likely_bg = (xn > 0.68) & (yn < 0.25)
    if likely_bg.sum() > 25 and (~likely_bg).sum() > 50:
        filtered = points[~likely_bg]

# Robustly keep central 90% in each dimension before ellipse fit.
fit_pts = filtered
if len(filtered) > 100:
    qx = np.quantile(filtered[:,0], [0.05, 0.95])
    qy = np.quantile(filtered[:,1], [0.05, 0.95])
    keep = (filtered[:,0]>=qx[0])&(filtered[:,0]<=qx[1])&(filtered[:,1]>=qy[0])&(filtered[:,1]<=qy[1])
    fit_pts = filtered[keep]

ellipse = None
if len(fit_pts) >= 5:
    cvpts = fit_pts.copy().astype(np.float32)
    cvpts[:,1] = crop.shape[0]-1-cvpts[:,1]
    try:
        ellipse = cv2.fitEllipse(cvpts.reshape(-1,1,2))
    except cv2.error:
        ellipse = None

m1, m2, m3 = st.columns(3)
m1.metric("Detected histogram pixels", f"{len(points):,}")
m2.metric("Product-fit pixels", f"{len(fit_pts):,}")
m3.metric("Geometry confidence", "Moderate" if ellipse and len(fit_pts)>250 else "Low")

if ellipse is None:
    st.warning("I could not reliably fit an Accept distribution from this crop. Tighten the crop around the histogram and try again.")
    st.stop()

(center, axes, angle_img) = ellipse
cx, cy_img = center
major, minor = max(axes), min(axes)
# OpenCV angle is image-coordinate ellipse orientation; convert to chart-like descriptive rotation.
rotation = (90 - angle_img) % 180

# Give user control over recommendation conservatism.
coverage = st.slider("Recommended Accept coverage", 80, 99, 94, help="Higher values make the proposed Accept ovoid more inclusive. Validate against known defects before use.")
scale = 0.82 + (coverage-80) * (0.30/19)
rec_axes = (axes[0]*scale, axes[1]*scale)

# Projected visualization.
fig, ax = plt.subplots(figsize=(8,6))
ax.imshow(crop, origin="upper")
from matplotlib.patches import Ellipse
cur = Ellipse((cx, cy_img), axes[0], axes[1], angle=angle_img, fill=False, linewidth=2, linestyle="--", label="Detected dominant distribution")
rec = Ellipse((cx, cy_img), rec_axes[0], rec_axes[1], angle=angle_img, fill=False, linewidth=3, label="Projected Accept ovoid")
ax.add_patch(cur); ax.add_patch(rec)
ax.set_title("Projected colour-map geometry")
ax.set_xlabel("Colour 1 →")
ax.set_ylabel("Colour 2")
ax.legend(loc="best")
ax.set_xlim(0, crop.shape[1]); ax.set_ylim(crop.shape[0], 0)
st.pyplot(fig, clear_figure=True)

# Normalized recommendations.
ncx = cx/max(crop.shape[1],1)*100
ncy = (crop.shape[0]-cy_img)/max(crop.shape[0],1)*100
aw = rec_axes[0]/max(crop.shape[1],1)*100
ah = rec_axes[1]/max(crop.shape[0],1)*100

st.subheader("3. Proposed correction plan")
status = "Advisory — verify with representative product before production"
st.warning(status)

# Diagnostic notes based on context.
notes = []
if view_mode == "Independent" and view in ("Front", "Rear"):
    notes.append(f"Apply this recommendation only to the {view} view unless the other view is separately verified.")
elif view_mode == "Combined":
    notes.append("Combined view means front/rear mode parameters are intended to match; verify both camera distributions before copying a geometric change.")
if logic == "AND":
    notes.append("AND logic changes rejection behavior for selected classes: a colour-map change must be checked against simultaneous Front/Rear detection behavior.")
elif logic == "OR":
    notes.append("OR logic can reject from either camera; avoid making one view overly aggressive without checking false rejects.")
if not objective.strip():
    notes.append("Known-good and known-defect descriptions were not supplied, so this version can fit the dominant distribution but cannot prove that nearby secondary pixels are good product or defect.")

instructions = [
    "Open **Colour Map Setup** and select the same Module / Camera / Position represented by this photo.",
    "Confirm the dominant cluster is genuinely **Accept product** using representative good product and expected defects.",
    "Select the **Accept** colour space / ovoid, then open its geometry or **Dimensions** controls.",
    f"Use the projected target as the geometric guide: centroid ≈ **Colour 1 {ncx:.1f}% / Colour 2 {ncy:.1f}%** of this cropped map; projected width ≈ **{aw:.1f}%**, height ≈ **{ah:.1f}%**, rotation ≈ **{rotation:.0f}°**.",
    "Adjust **Top / Right / Bottom / Left** incrementally toward the projected boundary rather than making a large one-step change.",
    "Do not absorb a clearly separate defect blotch merely to make the Accept ovoid smooth. Use a General/Spot defect colour space or perimeter where appropriate.",
    "Do not treat the histogram's artificial display colours as the actual colour of the product; they indicate frequency.",
    "Capture another representative frame after the change and compare the new histogram, false rejects and defect escape before production use.",
]

for i, item in enumerate(instructions, 1):
    st.markdown(f"**{i}.** {item}")

if notes:
    st.markdown("#### Configuration-specific cautions")
    for n in notes:
        st.write("•", n)

st.subheader("4. What the app thinks it sees")
summary = pd.DataFrame([
    ["Screen type", "Histogram / Colour Map (user-cropped)"],
    ["X axis", "Colour 1"],
    ["Y axis", "Colour 2"],
    ["Dominant distribution", "Detected from saturated histogram pixels"],
    ["Likely lower-right background", "Excluded from fit when sufficiently isolated"],
    ["Proposed base shape", "Ovoid"],
    ["Product", product or "Unknown"],
    ["View", view], ["Position", position], ["View mode", view_mode], ["Sorting logic", logic],
], columns=["Field", "Interpretation"])
st.dataframe(summary, use_container_width=True, hide_index=True)

with st.expander("Manual-derived reasoning used by the advisor"):
    for section in ["axes", "histogram", "classes", "geometry", "views", "workflow"]:
        st.markdown(f"**{section.title()}**")
        for r in MANUAL_RULES[section]:
            st.write("•", r)

st.caption("Version 1 intentionally separates image-derived geometry from operator-verified product knowledge. It will not claim a setting is correct when the photo cannot establish what is good product versus defect.")
