import streamlit as st
import json
import os
import zipfile
import io

# 1. 網頁配置與基礎初始化
st.set_page_config(page_title="114年專師認定自檢-終極旗艦版", layout="wide")

UPLOAD_DIR = "uploaded_evidence"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. 核心資料庫：完整 23 項條文與細項 (完全對照自評表 Word 檔文字) 
def get_full_criteria():
    return [
        # --- 第 1 章：教學資源與組織管理 ---
        {"id": "1.1.1", "is_mandatory": True, "chapter": "第1章", "title": "專責培育及管理單位與勞動權益 (必)", 
         "grading": {"C": "由醫師、專師及護理主管組成，副院長任召集人。每3個月開會1次，每年至少4次，訂有勞動權益維護措施。", "B": "符合C項。專責單位有護理部督導長以上代表，且有專屬窗口負責管理運作。會議內容包含權益維護議題。", "A": "符合B項。專科護理師代表佔委員人數50%（含）以上，具有適當科別代表性。"},
         "check": ["檢視組織架構及成員名單", "檢視會議運作規範及會議紀錄", "檢視執業及勞動權益維護相關資料"]},
        {"id": "1.1.2", "is_mandatory": True, "chapter": "第1章", "title": "明確之執業內容訂定與公告 (必)", 
         "grading": {"C": "依辦法訂定各分科可執行醫療業務範圍、項目及特定訓練，並公告周知且確實執行。", "B": "符合C項，且依執業內容訂有工作契約書且確實執行。", "A": "符合B項，且每年檢討修訂專科護理師執業內容。"},
         "check": ["檢視分科可執行業務規範與工作契約文件"]},
        {"id": "1.1.3", "is_mandatory": True, "chapter": "第1章", "title": "預立醫療流程 (PMP) SOP (必)", 
         "grading": {"C": "成立委員會由副院長以上任召集人。監督醫師於24小時內完成核對及簽署。", "B": "符合C項。依能力訂定執行項目及範圍，檢視訓練計畫與預立醫療流程之適當性。", "A": "符合B項。PMP有要求特定訓練、評值、定期修正與審查機制。"},
         "check": ["檢視 PMP SOP 及其運作情形"]},
        {"id": "1.1.4", "is_mandatory": False, "chapter": "第1章", "title": "建立專科護理師病歷書寫之審查機制", 
         "grading": {"C": "主治醫師對專科護理師之病歷記載給予指導。", "B": "符合C項，具體審查項目、抽樣人數、頻率與明確審查機制。", "A": "符合B項，能依指導或審查意見製作教案或案例討論教學。"},
         "check": ["檢視審查機制及執行情形"]},
        {"id": "1.1.5", "is_mandatory": False, "chapter": "第1章", "title": "訂定明確之臨床執業品質監測機制", 
         "grading": {"C": "依執業範疇與契約訂有品質監測規範、辦法及機制，且提出佐證。", "B": "符合C項，提出指標、方法、具體定義、範圍，且確實執行。", "A": "符合B項，且每年檢討改善。"},
         "check": ["檢視品質監測辦法及運作情形"]},
        {"id": "1.1.6", "is_mandatory": False, "chapter": "第1章", "title": "建立專科護理師考核機制", 
         "grading": {"C": "訂有專師考核機制且由醫護部門共同負責。", "B": "符合C項，且有專科護理師參與考核機制。", "A": "符合B項，每年檢討考核機制並有檢討紀錄與改善。"},
         "check": ["檢視考核規範與運作紀錄"]},
        {"id": "1.2.1", "is_mandatory": True, "chapter": "第1章", "title": "妥適的訓練場所 (必)", 
         "grading": {"C": "提供妥適場所(地點/環境)，兼顧學習、品質、病人安全與隱私。", "B": "符合C項，提供優質場所並兼顧品質與隱私。", "A": "符合B項，具人員工作安全與健康照護策略。"},
         "check": ["檢視臨床訓練場所設施與空間"]},
        {"id": "1.2.2", "is_mandatory": True, "chapter": "第1章", "title": "提供訓練必須之設備 (必)", 
         "grading": {"C": "提供訓練所需之相關設備。", "B": "符合C項，具網路學習平台、文獻檢索功能。", "A": "符合B項，設置或特約臨床技能中心提供模擬。"},
         "check": ["檢視訓練相關設備與環境"]},
        {"id": "1.2.3", "is_mandatory": False, "chapter": "第1章", "title": "提供適當之圖書期刊並管理", 
         "grading": {"C": "提供近5年內圖書及期刊(含紙本/電子)，含倫理、法律、品質等。", "B": "符合C項，新購資源有清單並定期公告且有管理機制。", "A": "符合B項，定期評估需求購置必要資源。"},
         "check": ["檢視資源清單與公告形式"]},

        # --- 第 2 章：教學師資、培育與繼續教育 ---
        {"id": "2.1.1", "is_mandatory": True, "chapter": "第2章", "title": "醫師師資應具適當資格 (必)", 
         "grading": {"C": "具專科醫師資格，實際從事專科工作至少2年。", "B": "符合C項，具有專科教師資格且符合院內培育制度。", "A": "符合B項，由負責教育之主治醫師參與規劃督導。"},
         "check": ["檢視指導醫師資格證明"]},
        {"id": "2.1.2", "is_mandatory": True, "chapter": "第2章", "title": "專師師資應具適當資格 (必)", 
         "grading": {"C": "具專師資格且實際從事專科護理師工作至少2年。", "B": "符合C項，從事專師工作滿3年以上佔80%以上。", "A": "符合B項，具碩士2年或學士4年資歷佔80%以上。"},
         "check": ["檢視指導專師資格證明"]},
        {"id": "2.1.3", "is_mandatory": True, "chapter": "第2章", "title": "配置比與品質評值 (必)", 
         "grading": {"C": "比例 醫師:專師:學員(含補充) = 1:4:4。", "B": "符合C項，並有專責醫護人員負責照護及教學。", "A": "符合B項，每年針對師資評值檢討改善。"},
         "check": ["檢視配置比例統計表", "檢視評值紀錄"]},
        {"id": "2.2.1", "is_mandatory": True, "chapter": "第2章", "title": "師資培育制度落實執行 (必)", 
         "grading": {"C": "明訂培訓制度、有計畫地培育師資並訂有發展計畫。", "B": "符合C項。與學校合作，提供進修訓練及獎勵措施。", "A": "符合B項。分析執行成效改善，安排臨床技能培育規劃課程。"},
         "check": ["檢視師資發展計畫與紀錄"]},
        {"id": "2.2.2", "is_mandatory": False, "chapter": "第2章", "title": "專師師資教學能力提升", 
         "grading": {"C": "教師參訓率100%，時數至少4小時。", "B": "符合C項。2年以上年資專師參與課程率達60%以上。", "A": "符合B項。2年以上年資專師參與率達80%以上。"},
         "check": ["檢視參訓情形與課後評估"]},
        {"id": "2.2.3", "is_mandatory": True, "chapter": "第2章", "title": "專師繼續教育制度 (必)", 
         "grading": {"C": "訂有繼續教育機制，規劃每年辦理至少20小時課程。", "B": "符合C項，鼓勵參與活動且執行能力進階制度。", "A": "符合B項，每年檢討修正計畫內容。"},
         "check": ["檢視教育計畫及進階紀錄"]},

        # --- 第 3 章：教學訓練計畫與執行成果 ---
        {"id": "3.1.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫內容具體適當 (必)", 
         "grading": {"C": "計畫含目的、目標、課程、品質維護與評值回饋，應用於臨床。", "B": "符合C項，且訓練計畫有教師參與共同訂定。", "A": "符合B項，定期針對計畫進行評估並適時修訂。"},
         "check": ["檢視訓練計畫書內容"]},
        {"id": "3.1.2", "is_mandatory": True, "chapter": "第3章", "title": "課程與活動安排 (必)", 
         "grading": {"C": "依能力安排合適課程，時間兼顧學習與工作需求。", "B": "符合C項。因故無法完成時訂有檢討補救機制。", "A": "符合B項。教師在執行過程中有建議管道可反映。"},
         "check": ["檢視時程與補訓措施"]},
        {"id": "3.2.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練課程符合法規並落實 (必)", 
         "grading": {"C": "課程內容符合甄審辦法訓練內容規定。", "B": "符合C項，且定期檢討執行成效。", "A": "符合B項，執行成效良好足為同儕表率。"},
         "check": ["檢視課程符合甄審辦法"]},
        {"id": "3.2.2", "is_mandatory": True, "chapter": "第3章", "title": "臨床實務訓練落實執行 (必)", 
         "grading": {"C": "內容符合法規並落實執行檢討改善機制。", "B": "符合C項，以產出成果呈現確實落實臨床業務。", "A": "符合B項，具證據顯示持續改善成效。"},
         "check": ["檢視實務訓練案例與紀錄"]},
        {"id": "3.3.1", "is_mandatory": True, "chapter": "第3章", "title": "回饋機制與反映管道 (必)", 
         "grading": {"C": "教師即時回饋指導，學員有反映問題管道並保障權益。", "B": "符合C項，針對反映問題有具體改善措施。", "A": "符合B項，改善成果良好。"},
         "check": ["檢視輔導回饋與反映管道紀錄"]},
        {"id": "3.3.2", "is_mandatory": False, "chapter": "第3章", "title": "對於教師多元化評估機制", 
         "grading": {"C": "訂有評估成效機制，利用多元管道進行評估。", "B": "符合C項，結果訂有回饋與輔導改善措施。", "A": "符合B項，能落實執行回饋與改善。"},
         "check": ["檢視教師評估機制與紀錄"]},
        {"id": "3.3.3", "is_mandatory": False, "chapter": "第3章", "title": "學員訓練成果分析改善", 
         "grading": {"C": "訂有評估訓練成效機制，多元管道分析結果。", "B": "符合C項，針對結果訂定回饋與輔導改善措施。", "A": "符合B項，能落實執行改善輔導。"},
         "check": ["檢視分析報告與輔導紀錄"]},
        {"id": "3.3.4", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫成效評估 (必)", 
         "grading": {"C": "對計畫成果訂有評值計畫(含考照率)，每年定期檢討。", "B": "符合C項，依評值結果提出檢討改善方法。", "A": "符合B項，改善措施具追蹤機制且成效良好。"},
         "check": ["檢視評值分析與檢討文件"]}
    ]

# 3. 資料持久化與輔助功能
def load_progress():
    if os.path.exists('progress.json'):
        try:
            with open('progress.json', 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_progress(progress):
    with open('progress.json', 'w', encoding='utf-8') as f: 
        json.dump(progress, f, ensure_ascii=False)

def create_zip(dir_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for root, _, files in os.walk(dir_path):
            for file in files: z.write(os.path.join(root, file), file)
    return buf.getvalue()

# --- 主程式執行 ---
all_criteria = get_full_criteria()
total_items = len(all_criteria)  # <--- 重要修復：確保此變數在最頂層被定義
saved_progress = load_progress()
user_data = {}

st.title("🛡️ 114年度專師認定自檢 - 終極整合旗艦版")
st.markdown(f"系統已對應 **23 項全條項**。C級以上達 90% 且必要項 100% 達標為合格。 [cite: 17, 134-135]")

tab_chk, tab_files, tab_time = st.tabs(["📋 專業報告撰寫", "🎯 檔案分類戰情室", "🕒 訪視當日時程"])

with tab_chk:
    for chap_name in ["第1章", "第2章", "第3章"]:
        st.subheader(f"📍 {chap_name}")
        chap_items = [d for d in all_criteria if d['chapter'] == chap_name]
        for item in chap_items:
            badge = " (必)" if item['is_mandatory'] else ""
            with st.expander(f"{item['id']} {item['title']}{badge}"):
                
                # 安全載入舊數據
                old = saved_progress.get(item['id'], {})
                old_score = old.get("score", "D")
                old_res = old.get("res", "未指派")
                old_status = old.get("status", "")
                old_note = old.get("note", "")
                old_checks = old.get("checks", [])
                old_urls = old.get("urls", "")
                
                # 區塊 1：等級指引
                st.write("**⭐ 評分標準描述：**")
                g1, g2, g3 = st.columns(3)
                g1.info(f"**【C級基準】**\n{item['grading']['C']}")
                g2.success(f"**【B級優化】**\n{item['grading']['B']}")
                g3.warning(f"**【A級卓越】**\n{item['grading']['A']}")
                
                # 區塊 2：撰寫區
                st.write("**✍️ 自評報告撰寫區：**")
                t1, t2 = st.columns(2)
                with t1:
                    status = st.text_area(f"執行現況說明 ({item['id']})", value=old_status, height=150, key=f"st_{item['id']}")
                with t2:
                    note = st.text_area(f"訪查記錄 / 備註 ({item['id']})", value=old_note, height=150, key=f"nt_{item['id']}")

                # 區塊 3：佐證資料管理 (含檔案與網址)
                st.divider()
                st.write("**📤 佐證資料管理 (上傳檔案與連結)：**")
                
                # 檔案管理
                col_up, col_url = st.columns(2)
                with col_up:
                    current_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(f"{item['id']}_")]
                    if current_files:
                        st.caption("目前存檔：")
                        for cf in current_files: st.markdown(f"- 📄 `{cf}`")
                    
                    files = st.file_uploader(f"上傳佐證檔案", accept_multiple_files=True, key=f"up_{item['id']}", label_visibility="collapsed")
                    if files:
                        for f in files:
                            ext = os.path.splitext(f.name)[1]
                            std_name = f"{item['id']}_{item['title'][:15]}_2026備評用{ext}"
                            if os.path.exists(os.path.join(UPLOAD_DIR, std_name)):
                                st.warning(f"⚠️ 提示：偵測到重複檔名，將覆蓋舊版。")
                            with open(os.path.join(UPLOAD_DIR, std_name), "wb") as sf: sf.write(f.getbuffer())
                        st.success(f"檔案儲存成功。")
                
                with col_url:
                    url_input = st.text_input("🔗 雲端網址 (英文逗號隔開)", value=old_urls, key=f"url_{item['id']}", placeholder="貼上雲端硬碟連結")
                    if url_input:
                        url_list = [u.strip() for u in url_input.split(",") if u.strip()]
                        btn_cols = st.columns(len(url_list))
                        for idx, link in enumerate(url_list):
                            with btn_cols[idx]: st.link_button(f"🌐 連結佐證 {idx+1}", link, use_container_width=True)

                # 區塊 4：檢核與判定
                st.write("**📑 檢核細項與等級：**")
                curr_chks = []
                for idx, text in enumerate(item['check']):
                    val = old_checks[idx] if idx < len(old_checks) else False
                    curr_chks.append(st.checkbox(text, value=val, key=f"chk_{item['id']}_{idx}"))

                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    score = st.radio("自評等級", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(old_score), key=f"r_{item['id']}", horizontal=True)
                with c2:
                    roles = ["未指派", "行政組", "教學組", "臨床組", "學術組長"]
                    sel_res = st.selectbox("👤 負責組別", roles, index=roles.index(old_res) if old_res in roles else 0, key=f"sl_{item['id']}")
                
                user_data[item['id']] = {
                    "score": score, "res": sel_res, "checks": curr_chks, 
                    "status": status, "note": note, "urls": url_input
                }

    if st.button("💾 儲存自評報告進度"):
        save_progress(user_data)
        st.toast("所有自評報告內容與網址連結已存檔！")

# 戰情室分頁
with tab_files:
    st.subheader("🎯 備評佐證分類戰情室")
    all_stored = sorted(os.listdir(UPLOAD_DIR))
    for cn in ["第1章", "第2章", "第3章"]:
        with st.expander(f"📁 {cn} 佐證彙整"):
            c_items = [i for i in all_criteria if i['chapter'] == cn]
            for it in c_items:
                fl = [f for f in all_stored if f.startswith(f"{it['id']}_")]
                if fl:
                    st.write(f"📌 **{it['id']} {it['title']}**")
                    for fn in fl:
                        col1, col2 = st.columns([8, 2])
                        col1.write(f"📄 {fn}")
                        if col2.button("🗑️ 刪除", key=f"del_{fn}"):
                            os.remove(os.path.join(UPLOAD_DIR, fn)); st.rerun()
                else: st.caption(f"⚪ {it['id']} 尚未上傳佐證")
    st.divider()
    st.download_button("📦 打包下載所有檔案 (.zip)", data=create_zip(UPLOAD_DIR), file_name="114專師認定佐證.zip")

# 時程分頁
with tab_time:
    st.info("🕒 訪視當天時程參考 (總計 3.5 小時) [cite: 50-51]：")
    st.table([
        {"階段": "會前會", "時間": "20 min", "重點": "委員先行溝通共識與流程"},
        {"階段": "醫院簡報", "時間": "20 min", "重點": "限定於專師訓練認定基準細項"},
        {"階段": "實地/書審", "時間": "130 min", "重點": "佐證核對、場所參觀與訪談"},
        {"階段": "整理回饋", "時間": "40 min", "重點": "共識達成與回饋建議說明"}
    ])

# 側邊欄計算判定
passed_count = sum(1 for d in user_data.values() if d['score'] in ['A', 'B', 'C'])
pass_rate = (passed_count / total_items) * 100 if total_items > 0 else 0
mandatory_failed = [id for id, d in user_data.items() if any(i['id'] == id and i['is_mandatory'] for i in all_criteria) and d['score'] == 'D']

st.sidebar.metric("目前總達成率", f"{pass_rate:.1f}%")
if mandatory_failed:
    st.sidebar.error(f"❌ 不合格：必要項 D ({', '.join(mandatory_failed)})")
elif pass_rate >= 90:
    st.sidebar.success("✅ 符合通過標準")
else:
    st.sidebar.warning(f"⚠️ 達成率不足 90% (目前 {passed_count}/{total_items})")

st.sidebar.divider()
st.sidebar.info("💡 114年度標準：\n1. 16項必要條文 100% 達 C 以上。\n2. C級以上項目總數達 90% 以上。 [cite: 17, 134-135]")
