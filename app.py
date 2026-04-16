import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter

st.set_page_config(page_title="MAYA AI - Tracker & Recommender", layout="wide")

st.title("MAYA AI: 70-80% Elimination & Tier Recommender")

# --- 1. Independent Date Controls ---
st.sidebar.header("Shift Date Controls")
st.sidebar.subheader("Base Shift")
base_start = st.sidebar.date_input("Start Date (Base)", datetime(2026, 1, 1))
base_end = st.sidebar.date_input("End Date (Base)", datetime(2026, 4, 16))

st.sidebar.subheader("Other Shifts")
other_start = st.sidebar.date_input("Start Date (Others)", datetime(2026, 1, 1))
other_end = st.sidebar.date_input("End Date (Others)", datetime(2026, 4, 16))

max_repeat_limit = st.sidebar.slider("Max Repeat Limit (Elimination threshold)", 2, 5, 4)

# --- 2. Data Locking Logic ---
@st.cache_data
def load_full_data():
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', end='2026-04-16')
    return pd.DataFrame({
        'Date': dates,
        'Base_Shift': np.random.randint(0, 100, size=len(dates)),
        'Shift_A': np.random.randint(0, 100, size=len(dates)),
        'Shift_B': np.random.randint(0, 100, size=len(dates))
    })

df = load_full_data()
base_data_filtered = df[(df['Date'].dt.date >= base_start) & (df['Date'].dt.date <= base_end)]
other_data_filtered = df[(df['Date'].dt.date >= other_start) & (df['Date'].dt.date <= other_end)]

# --- 3. Massive Elimination & Pattern Scoring ---
def analyze_sheets(shift_list, limit):
    eliminated_total = set()
    pattern_scores = Counter() 
    
    for days in range(1, 31):
        if len(shift_list) < days: continue
        
        sheet = shift_list[-days:]
        counts = Counter(sheet)
        
        # RULE 1: Zero-Repeat (Puri sheet bahar)
        if len(counts) == len(sheet) and len(sheet) > 1:
            eliminated_total.update(sheet)
        
        # RULE 2: Max Hit (Limit cross wale bahar)
        for num, freq in counts.items():
            if freq >= limit:
                eliminated_total.add(num)
            else:
                pattern_scores[num] += 1
                
    return eliminated_total, pattern_scores

base_list = base_data_filtered['Base_Shift'].tolist()
shift_a_list = other_data_filtered['Shift_A'].tolist()

elim1, scores1 = analyze_sheets(base_list, max_repeat_limit)
elim2, scores2 = analyze_sheets(shift_a_list, max_repeat_limit)

final_eliminated = elim1.union(elim2)
final_scores = scores1 + scores2

safe_pool = [n for n in range(100) if n not in final_eliminated]

# --- 4. Tiering System (High, Medium, Low) ---
if safe_pool:
    sorted_safe = sorted(safe_pool, key=lambda x: final_scores[x], reverse=True)
    n = len(sorted_safe)
    
    # Dividing the safe pool into 3 tiers
    high_tier = sorted_safe[:int(n*0.33)]
    med_tier = sorted_safe[int(n*0.33):int(n*0.66)]
    low_tier = sorted_safe[int(n*0.66):]
    
    # --- 5. PERFORMANCE TRACKER & RECOMMENDATION ---
    # Pichle 15 din ka asli result check karna ki wo kis tier mein fit baithta tha
    if len(base_list) >= 15:
        recent_results = base_list[-15:]
    else:
        recent_results = base_list
        
    tier_hits = {"High": 0, "Medium": 0, "Low": 0}
    
    for res in recent_results:
        if res in high_tier: tier_hits["High"] += 1
        elif res in med_tier: tier_hits["Medium"] += 1
        elif res in low_tier: tier_hits["Low"] += 1
        
    best_tier = max(tier_hits, key=tier_hits.get)
    best_tier_hits = tier_hits[best_tier]
    total_tracked = sum(tier_hits.values())
    
    if total_tracked > 0:
        win_rate = (best_tier_hits / total_tracked) * 100
    else:
        win_rate = 0
else:
    high_tier, med_tier, low_tier = [], [], []
    best_tier, win_rate = "None", 0
    tier_hits = {"High": 0, "Medium": 0, "Low": 0}

# --- 6. Final UI Display ---
target_date = base_end + timedelta(days=1)
st.markdown(f"### 🎯 Shift Prediction for: **{target_date.strftime('%d %B %Y')}**")

st.markdown("---")
st.write("### 🏆 AI Recommendation Engine")

if best_tier != "None" and win_rate > 0:
    st.success(f"**Agle din ke liye aapko [{best_tier.upper()} TIER] par lagana sabse behtar rahega.**")
    st.write(f"**Kyon?** Pichle dino mein, jo numbers eliminate nahi huye the, unme se sabse zyada actual results **{best_tier}** category mein gire hain ({tier_hits[best_tier]} baar). Is tier ka recent win rate lagbhag **{win_rate:.0f}%** chal raha hai.")
else:
    st.warning("Data kam hone ki wajah se clear recommendation nahi ban paayi.")

st.markdown("---")
st.subheader("📊 Category Wise Safe Numbers (After 70-80% Elimination)")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"#### 🔥 High Tier (Trend Hits: {tier_hits['High']})")
    st.write(", ".join([f"{x:02d}" for x in high_tier]))
with c2:
    st.markdown(f"#### ⚡ Medium Tier (Trend Hits: {tier_hits['Medium']})")
    st.write(", ".join([f"{x:02d}" for x in med_tier]))
with c3:
    st.markdown(f"#### ❄️ Low Tier (Trend Hits: {tier_hits['Low']})")
    st.write(", ".join([f"{x:02d}" for x in low_tier]))

st.markdown("---")
st.info(f"**Total Eliminated Numbers:** {len(final_eliminated)} | **Total Safe Pool:** {len(safe_pool)}")
  
