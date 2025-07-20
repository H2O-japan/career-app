import streamlit as st
import pandas as pd
import random

# CSVファイルの読み込み（初回のみ）
@st.cache_data
def load_data():
    df = pd.read_csv("過去問題.csv")
    df = df.rename(columns={"実施回": "年度"})  # 列名を統一
    return df

df = load_data()

# セッションステートの初期化
if "history" not in st.session_state:
    st.session_state.history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "mode" not in st.session_state:
    st.session_state.mode = "all"  # or "mistakes"

# 問題のランダム選択（全体 or 間違えた問題から）
def select_random_question():
    if st.session_state.mode == "all":
        st.session_state.current_question = df.sample(1).iloc[0]
    else:
        mistakes = [h["問題ID"] for h in st.session_state.history if not h["正解"]]
        mistaken_df = df[df["問題ID"].isin(mistakes)]
        if not mistaken_df.empty:
            st.session_state.current_question = mistaken_df.sample(1).iloc[0]
        else:
            st.warning("間違えた問題がありません。")
            st.session_state.current_question = None

# ボタンで問題を選ぶ
col1, col2 = st.columns(2)
with col1:
    if st.button("ランダムに1問出す"):
        st.session_state.mode = "all"
        select_random_question()
with col2:
    if st.button("間違えた問題から再出題"):
        st.session_state.mode = "mistakes"
        select_random_question()

# 問題の表示
q = st.session_state.current_question
if q is not None:
    st.markdown(f"### {q['問題文']}")

    options = ["選択肢1", "選択肢2", "選択肢3", "選択肢4"]
    option_texts = [q[o] for o in options]
    selected = st.radio("選択肢を選んでください：", option_texts, key=q["問題ID"])

    if st.button("解答する"):
        correct_key = "選択肢" + str(int(float(q["正解"])))  # 正解を "1.0" → 1 → "選択肢1" に変換
        correct_option = q[correct_key]
        is_correct = (selected == correct_option)

        # 結果表示
        if is_correct:
            st.success("正解です！")
        else:
            st.error(f"不正解です。正解は「{correct_option}」です。")

        # 解説
        st.markdown("#### 解説")
        st.info(q["解説"])

        # 履歴に保存
        st.session_state.history.append({
            "問題ID": q["問題ID"],
            "分野": q["分野"],
            "年度": q["年度"],
            "正解": is_correct
        })

# 正答率の表示
if st.session_state.history:
    st.markdown("## 成績サマリー")

    hist_df = pd.DataFrame(st.session_state.history)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 年度別正答率")
        year_summary = hist_df.groupby("年度")["正解"].agg(["count", "sum"])
        year_summary["正答率"] = (year_summary["sum"] / year_summary["count"] * 100).round(1)
        st.dataframe(year_summary[["正答率"]])

    with col2:
        st.markdown("### 分野別正答率")
        field_summary = hist_df.groupby("分野")["正解"].agg(["count", "sum"])
        field_summary["正答率"] = (field_summary["sum"] / field_summary["count"] * 100).round(1)
        st.dataframe(field_summary[["正答率"]])
