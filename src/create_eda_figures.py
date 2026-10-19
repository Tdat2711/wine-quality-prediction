"""
EDA Figures Generator – Wine Quality Project
=============================================
Tạo hai biểu đồ EDA phục vụ báo cáo / slide:
  1. Phân bố giá (Price Distribution) – Histogram + KDE + Median/Mean
  2. Quan hệ Giá–Điểm (Price vs Points) – Scatter + Hồi quy log

Mỗi hình được hiển thị rõ ràng:
  - Số lượng mẫu (Sample size N)
  - Trục tọa độ và đơn vị rõ ràng (Price in USD, Points 80–100)
  - Khung kết luận (Insights) trực quan ngay trên biểu đồ
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Thiết lập encoding cho stdout
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "wine_cleaned_final.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "eda_figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FIG1_PATH = os.path.join(OUTPUT_DIR, "fig1_price_distribution.png")
FIG2_PATH = os.path.join(OUTPUT_DIR, "fig2_price_vs_points.png")

# ── Load data ──────────────────────────────────────────────────────────
print("Loading data …")
df_all = pd.read_csv(DATA_PATH)

# Theo quy trình làm sạch dữ liệu: giữ dòng có giá quan sát được để phân tích
if "price_was_missing" in df_all.columns:
    df = df_all[df_all["price_was_missing"] == False].copy()
else:
    df = df_all.dropna(subset=["price"]).copy()

n_total = len(df_all)
n_with_price = len(df)
n_missing_price = n_total - n_with_price

print(f"  Tổng số mẫu sau cleaning: {n_total:,}")
print(f"  Số mẫu có giá quan sát  : {n_with_price:,}")
print(f"  Số mẫu thiếu giá        : {n_missing_price:,}")

# ── Thiết lập phong cách đồ họa ─────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.1)
WINE_RED = "#722F37"
WINE_GOLD = "#C5A02E"

# ══════════════════════════════════════════════════════════════════════
# HÌNH 1 – Phân bố giá (Price Distribution)
# ══════════════════════════════════════════════════════════════════════
print("Đang tạo Hình 1: Phân bố giá ...")
fig1, ax1 = plt.subplots(figsize=(10, 6))

price_data = df["price"].dropna()

# 1. Histogram
ax1.hist(
    price_data,
    bins=100,
    range=(0, 300),
    color=WINE_RED,
    alpha=0.75,
    edgecolor="white",
    linewidth=0.5,
    label="Tần suất (Histogram)"
)

# 2. KDE overlay trên trục thứ hai
ax1_kde = ax1.twinx()
sns.kdeplot(
    price_data,
    ax=ax1_kde,
    color=WINE_GOLD,
    linewidth=2.5,
    clip=(0, 300),
    label="Mật độ xác suất (KDE)"
)
ax1_kde.set_ylabel("")
ax1_kde.set_yticks([])

# 3. Median & Mean lines
median_price = price_data.median()
mean_price = price_data.mean()
ax1.axvline(median_price, color="#1E88E5", linestyle="--", linewidth=2,
            label=f"Trung vị (Median) = ${median_price:.0f}")
ax1.axvline(mean_price, color="#FB8C00", linestyle="--", linewidth=2,
            label=f"Trung bình (Mean) = ${mean_price:.1f}")

# Trục & Nhãn
ax1.set_xlabel("Giá (Đơn vị: USD)", fontsize=13, fontweight="bold")
ax1.set_ylabel("Số lượng mẫu rượu (Chai)", fontsize=13, fontweight="bold")
ax1.set_title("Phân Bố Giá Rượu Vang (Wine Price Distribution)", fontsize=15, fontweight="bold", pad=15)
ax1.set_xlim(0, 300)

# Khung thông tin: Số mẫu + Trục/Đơn vị + Kết luận
conclusion_1 = (
    f"• Số mẫu: N = {n_with_price:,} (loại trừ {n_missing_price:,} mẫu thiếu giá)\n"
    f"• Trục X: Giá (USD) | Trục Y: Số lượng chai\n"
    f"• Thống kê: Trung vị = ${median_price:.0f}, Trung bình = ${mean_price:.1f}\n"
    f"• Kết luận: Phân bố bị lệch phải mạnh (right-skewed), tập trung chính ở phân khúc dưới $50.\n"
    f"  → Khuyến nghị biến đổi log(price) hoặc phân khúc nhóm giá trước khi huấn luyện mô hình."
)
ax1.text(
    0.98, 0.95, conclusion_1,
    transform=ax1.transAxes,
    fontsize=9.5,
    verticalalignment="top",
    horizontalalignment="right",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#FFFFF0", edgecolor="#BDBDBD", alpha=0.92)
)

ax1.legend(loc="center right", fontsize=10.5)
fig1.tight_layout()
fig1.savefig(FIG1_PATH, dpi=300, bbox_inches="tight")
plt.close(fig1)
print(f"✓ Đã lưu Hình 1 tại: {FIG1_PATH}")

# ══════════════════════════════════════════════════════════════════════
# HÌNH 2 – Quan hệ Giá – Điểm (Price vs Points)
# ══════════════════════════════════════════════════════════════════════
print("Đang tạo Hình 2: Quan hệ Giá - Điểm ...")
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Lấy mẫu ngẫu nhiên có seed để biểu đồ scatter thoáng và rõ ràng
np.random.seed(42)
if len(df) > 15000:
    df_plot = df.sample(15000, random_state=42)
else:
    df_plot = df

scatter = ax2.scatter(
    df_plot["price"], df_plot["points"],
    c=df_plot["points"], cmap="viridis",
    alpha=0.35, s=14, edgecolors="none"
)

# Đường xu hướng hồi quy phi tuyến dạng log(price)
log_price = np.log1p(df["price"].values)
points_vals = df["points"].values
coeffs = np.polyfit(log_price, points_vals, 1)
poly_fn = np.poly1d(coeffs)
x_line = np.linspace(df["price"].min(), 300, 200)
y_line = poly_fn(np.log1p(x_line))

ax2.plot(
    x_line, y_line, color="#D32F2F", linewidth=2.5,
    label=f"Xu hướng: Points ≈ {coeffs[0]:.2f} × ln(Price + 1) + {coeffs[1]:.1f}"
)

# Hệ số tương quan
corr_raw = df[["price", "points"]].corr().iloc[0, 1]
corr_log = pd.Series(log_price).corr(pd.Series(points_vals))

# Trục & Nhãn
ax2.set_xlabel("Giá (Đơn vị: USD)", fontsize=13, fontweight="bold")
ax2.set_ylabel("Điểm đánh giá (Đơn vị: Points, thang điểm 80–100)", fontsize=13, fontweight="bold")
ax2.set_title("Mối Quan Hệ Giữa Giá Và Điểm Đánh Giá (Price vs. Points)", fontsize=15, fontweight="bold", pad=15)
ax2.set_xlim(0, 300)
ax2.set_ylim(79, 101)

# Thanh màu điểm số (Colorbar)
cbar = fig2.colorbar(scatter, ax=ax2, pad=0.02, shrink=0.85)
cbar.set_label("Thang điểm (Points)", fontsize=10.5)

# Khung thông tin: Số mẫu + Trục/Đơn vị + Kết luận
conclusion_2 = (
    f"• Số mẫu: N = {n_with_price:,} (hiển thị sample 15,000 điểm tránh chồng lấn)\n"
    f"• Trục: Trục X = Giá (USD) | Trục Y = Điểm (80-100)\n"
    f"• Hệ số tương quan: r(Price, Points) = {corr_raw:.3f} | r(ln_Price, Points) = {corr_log:.3f}\n"
    f"• Kết luận: Rượu giá cao thường có xu hướng điểm cao hơn, nhưng độ phân tán rất lớn.\n"
    f"  Giá đơn thuần chưa giải thích được trọn vẹn điểm số (r ≈ 0.43).\n"
    f"  → Khẳng định tính cần thiết phải bổ sung metadata (quốc gia, giống nho, vùng...) cho mô hình."
)
ax2.text(
    0.98, 0.05, conclusion_2,
    transform=ax2.transAxes,
    fontsize=9.5,
    verticalalignment="bottom",
    horizontalalignment="right",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#FFFFF0", edgecolor="#BDBDBD", alpha=0.92)
)

ax2.legend(loc="upper left", fontsize=10.5)
fig2.tight_layout()
fig2.savefig(FIG2_PATH, dpi=300, bbox_inches="tight")
plt.close(fig2)
print(f"✓ Đã lưu Hình 2 tại: {FIG2_PATH}")

print("\n🎉 Hoàn thành! 2 hình ảnh đã được lưu tại:", OUTPUT_DIR)
