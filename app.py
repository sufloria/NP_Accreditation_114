import streamlit as st
import json
import os
import zipfile
import io

# 1. 網頁配置與資料夾初始化
st.set_page_config(page_title="114年專師認定自檢-智慧旗艦版", layout="wide")

UPLOAD_DIR = "uploaded_evidence"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. 核心資料庫：完整對照 Word 檔 23 項條文細節 (含 A/B/C 標準) 
def get_full_criteria():
    return [
        # --- 第 1 章：教學資源與組織管理 ---
        {"id": "1.1.1", "is_mandatory": True, "chapter": "第1章", "title": "專責培育及管理單位與勞動權益 (必)", 
         "grading": {"C": "由醫師、專師及護理主管組成，副院長任召集人。每3個月開會1次，每年至少4次，訂有勞動權益維護措施。", "B": "符合C項。專責單位有護理部督導長以上代表，且有專屬窗口負責管理運作。會議內容包含權益維護議題。", "A": "符合B項。專科護理師代表佔委員人數50%（含）以上，具有適當科別代表性，且具具體檢討成效。"},
         "check": ["組織架構及成員名單", "會議運作規範及會議紀錄", "專師執業及勞動權益維護資料"]},
        {"id": "1.1.2", "is_mandatory": True, "chapter": "第1章", "title": "明確之執業內容訂定與公告 (必)", 
         "grading": {"C": "依辦法訂定各分科可執行醫療業務範圍、項目及特定訓練，並公告周知且確實執行。", "B": "符合C項，且依執業內容訂有工作契約書且確實執行。", "A": "符合B項，且每年檢討修訂專科護理師執業內容。"},
         "check": ["分科可執行醫療業務規範與工作契約文件"]},
        {"id": "1.1.3", "is_mandatory": True, "chapter": "第1章", "title": "預立醫療流程 (PMP) SOP (必)", 
         "grading": {"C": "成立委員會由副院長以上任召集人。監督醫師於24小時內完成核對及簽署。", "B": "符合C項。依能力訂定執行項目及範圍，檢視訓練計畫與預立醫療流程之適當性。", "A": "符合B項。PMP有要求特定訓練、評值、定期修正與審查等強化機制。"},
         "check": ["預立醫療流程標準作業程序及其運作情形"]},
        {"id": "1.1.4", "is_mandatory": False, "chapter": "第1章", "title": "病歷書寫之審查機制", 
         "grading": {"C": "主治醫師對專科護理師之病歷記載給予指導。", "B": "符合C項，具體審查項目、抽樣人數、頻率與明確審查機制。", "A": "符合B項，依指導或審查意見製作教案或案例討論教學。"},
         "check": ["專科護理師病歷書寫審查機制與執行情形"]},
        {"id": "1.1.5", "is_mandatory": False, "chapter": "第1章", "title": "臨床執業品質監測機制", 
         "grading": {"C": "依執業範疇與契約訂有品質監測規範、辦法及機制，且提出佐證。", "B": "符合C項，提出指標、方法、具體定義、範圍，且確實執行。", "A": "符合B項，且每年檢討改善。"},
         "check": ["執業品質監測辦法及運作情形"]},
        {"id": "1.1.6", "is_mandatory": False, "chapter": "第1章", "title": "建立專科護理師考核機制", 
         "grading": {"C": "訂有專師考核機制且由醫護部門共同負責。", "B": "符合C項，且有專科護理師參與考核機制。", "A": "符合B項，每年檢討考核機制並有檢討紀錄與改善。"},
         "check": ["專師考核機制規範及運作紀錄"]},
        {"id": "1.2.1", "is_mandatory": True, "chapter": "第1章", "title": "妥適的訓練場所 (必)", 
         "grading": {"C": "提供妥適訓練場所(地點/環境)，兼顧學習、品質、病人安全與隱私。", "B": "符合C項，提供優質場所並兼顧醫療品質與隱私。", "A": "符合B項，具人員工作安全與健康照護策略且成效優良。"},
         "check": ["檢視臨床訓練場所設施與空間"]},
        {"id": "1.2.2", "is_mandatory": True, "chapter": "第1章", "title": "提供訓練必須之設備 (必)", 
         "grading": {"C": "提供訓練所需之相關設備。", "B": "符合C項，具網路學習平台，提供訓練訊息及文獻檢索功能。", "A": "符合B項，設置或特約臨床技能訓練中心提供模擬環境。"},
         "check": ["檢視訓練相關設備與環境"]},
        {"id": "1.2.3", "is_mandatory": False, "chapter": "第1章", "title": "適當之圖書期刊管理", 
         "grading": {"C": "提供購置圖書及期刊(含電子)，含醫倫、法律、品質、實證等。", "B": "符合C項，新購資源有清單並定期公告且有管理機制。", "A": "符合B項，定期評估需求購置必要之圖書及期刊。"},
         "check": ["圖書及期刊管理規則與公告形式"]},

        # --- 第 2 章：教學師資、培育與繼續教育 ---
        {"id": "2.1.1", "is_mandatory": True, "chapter": "第2章", "title": "醫師師資應具適當資格 (必)", 
         "grading": {"C": "具專科醫師資格，實際從事專科工作至少2年。", "B": "符合C項，具有專科教師資格，且符合院內培育制度。", "A": "符合B項，由負責教育之主治醫師參與規劃督導訓練。"},
         "check": ["臨床指導醫師資格證明"]},
        {"id": "2.1.2", "is_mandatory": True, "chapter": "第2章", "title": "專師師資應具適當資格 (必)", 
         "grading": {"C": "具專師資格，且實際從事專科護理師工作至少2年。", "B": "符合C項，從事專師工作滿3年以上佔80%以上。", "A": "符合B項，具碩士2年或學士4年資歷佔80%以上。"},
         "check": ["臨床訓練專師資格證明"]},
        {"id": "2.1.3", "is_mandatory": True, "chapter": "第2章", "title": "配置比與品質評值 (必)", 
         "grading": {"C": "師生比例 醫師:專師:學員(含補充) = 1:4:4。", "B": "符合C項，並有專責醫護人員負責照護及教學。", "A": "符合B項，每年針對師資進行教學評值檢討改善。"},
         "check": ["配置比例統計表", "教學成效評值紀錄"]},
        {"id": "2.2.1", "is_mandatory": True, "chapter": "第2章", "title": "師資培育制度並落實執行 (必)", 
         "grading": {"C": "明訂培訓制度、有計畫地培育師資並訂有發展計畫，提供進修訓練。", "B": "符合C項。與學校或其他醫院合作，提供進修課程及獎勵措施。", "A": "符合B項。定期檢討分析執行成效並改善，安排不同階段臨床技能培訓。"},
         "check": ["師資發展計畫及進修訓練紀錄"]},
        {"id": "2.2.2", "is_mandatory": False, "chapter": "第2章", "title": "專師師資教學能力提升", 
         "grading": {"C": "醫院教師參與教學培育課程至少4小時，參與率達100%。", "B": "符合C項。2年以上年資專師參與課程率達60%以上。", "A": "符合B項。2年以上年資專師參與率達80%以上並課後評估。"},
         "check": ["教師參訓情形與課後成效評估紀錄"]},
        {"id": "2.2.3", "is_mandatory": True, "chapter": "第2章", "title": "專師繼續教育訓練制度 (必)", 
         "grading": {"C": "訂有繼續教育機制，規劃每年至少辦理20小時教育課程。", "B": "符合C項，有鼓勵參與院外學術活動措施且執行進階制度。", "A": "符合B項，每年檢討修正繼續教育課程與進階制度。"},
         "check": ["專師繼續教育計畫及進階制度紀錄"]},

        # --- 第 3 章：教學訓練計畫與執行成果 ---
        {"id": "3.1.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫內容具體適當 (必)", 
         "grading": {"C": "計畫含目的、目標、課程、品質維護與評值回饋，應用於臨床。", "B": "符合C項，且訓練計畫有教師參與共同訂定。", "A": "符合B項，定期針對計畫進行評估並適時修訂計畫。"},
         "check": ["訓練計畫書內容適當性"]},
        {"id": "3.1.2", "is_mandatory": True, "chapter": "第3章", "title": "課程與活動安排 (必)", 
         "grading": {"C": "依能力安排合適課程，學員清楚安排，訓練時間合理兼顧。", "B": "符合C項。因故無法完成時訂有檢討補救機制。", "A": "符合B項。教師在教學過程中有建議管道反映並修訂計畫。"},
         "check": ["訓練課程與法規對應紀錄", "教師反映管道紀錄"]},
        {"id": "3.2.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練課程符合法規並落實 (必)", 
         "grading": {"C": "訓練課程內容應符合專科護理師分科及甄審辦法規定。", "B": "符合C項，且定期檢討執行成效。", "A": "符合B項，且執行成效良好足為同儕表率。"},
         "check": ["檢視訓練計畫書符合甄審辦法"]},
        {"id": "3.2.2", "is_mandatory": True, "chapter": "第3章", "title": "臨床實務訓練落實與改善 (必)", 
         "grading": {"C": "臨床訓練內容符合甄審辦法並落實執行，具檢討改善機制。", "B": "符合C項，以訓練產出成果呈現確實落實臨床業務。", "A": "符合B項，具證據顯示檢討及持續改善之成效。"},
         "check": ["臨床實務訓練案例與評值證據"]},
        {"id": "3.3.1", "is_mandatory": True, "chapter": "第3章", "title": "回饋機制與反映管道 (必)", 
         "grading": {"C": "教師即時回饋紀錄，學員有反映問題溝通管道並保障權益。", "B": "符合C項，針對教師及學員反映問題有具體改善措施。", "A": "符合B項，改善成果具體成效良好。"},
         "check": ["教師輔導回饋及反映管道紀錄"]},
        {"id": "3.3.2", "is_mandatory": False, "chapter": "第3章", "title": "教師多元化評估機制", 
         "grading": {"C": "訂有評估教師教學成效機制，利用多元管道定期評估。", "B": "符合C項，針對評估結果訂有回饋與輔導改善措施。", "A": "符合B項，能落實執行回饋與改善。"},
         "check": ["教師教學成效評估與紀錄"]},
        {"id": "3.3.3", "is_mandatory": False, "chapter": "第3章", "title": "學員訓練成果分析與改善", 
         "grading": {"C": "訂有評估訓練成效機制，多元管道分析結果並實際執行。", "B": "符合C項，針對結果訂定回饋與輔導改善措施。", "A": "符合B項，能落實執行回饋與改善輔導。"},
         "check": ["訓練成果檢討與分析輔導紀錄"]},
        {"id": "3.3.4", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫成效評估 (必)", 
         "grading": {"C": "訂有具體評值計畫(含考照率)，每年定期檢討成果。", "B": "符合C項，且依評值結果提出檢討改善方法。", "A": "符合B項，改善措施具追蹤機制且成效良好。"},
         "check": ["計畫評值分析報告與檢討修正紀錄"]}
    ]

# 3. 輔助函式
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
total_items = len(all_criteria)  # <--- 重要：修正變數定義位置
saved_progress = load_progress()
user_data = {}

st.title("🛡️ 114年度專師認定自檢 - 終極修正完整版")
st.markdown("針對 **23 項認定基準** [cite: 17, 134-135, 140-268] 設計的備評數位報告系統。")

tab_chk, tab_files, tab_time = st.tabs(["📋 專業報告撰寫", "🎯 檔案分類戰情室", "⏱️ 訪視時程"])

with tab_chk:
    for c_idx in ["第1章", "第2章", "第3章"]:
        st.subheader(f"📍 {c_idx}")
        items = [i for i in all_criteria if i['chapter'] == c_idx]
        for item in items:
            badge = " (必)" if item['is_mandatory'] else ""
            with st.expander(f"{item['id']} {item['title']}{badge}"):
                old = saved_progress.get(item['id'], {"score": "D", "res": "未指派", "status": "", "note": "", "checks": []})
                
                st.write("**⭐ 評分指引：**")
                g1, g2, g3 = st.columns(3)
                g1.info(f"**【C級基準】**\n{item['grading']['C']}")
                g2.success(f"**【B級優化】**\n{item['grading']['B']}")
                g3.warning(f"**【A級卓越】**\n{item['grading']['A']}")
                
                st.write("**✍️ 報告撰寫：**")
                t1, t2 = st.columns(2)
                with t1:
                    status = st.text_area(f"現況分析 ({item['id']})", value=old.get("status", ""), height=120, key=f"st_{item['id']}")
                with t2:
                    note = st.text_area(f"訪查筆記 ({item['id']})", value=old.get("note", ""), height=120, key=f"nt_{item['id']}")

                st.write("**📤 檔案管理：**")
                current_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(f"{item['id']}_")]
                if current_files:
                    for cf in current_files: st.caption(f"- 📄 `{cf}`")
                
                up_files = st.file_uploader(f"選擇上傳", accept_multiple_files=True, key=f"up_{item['id']}", label_visibility="collapsed")
                if up_files:
                    for f in up_files:
                        ext = os.path.splitext(f.name)[1]
                        fname = f"{item['id']}_{item['title'][:15]}_2026備評用{ext}"
                        if os.path.exists(os.path.join(UPLOAD_DIR, fname)):
                            st.warning(f"偵測到重複檔名，將覆蓋舊版。")
                        with open(os.path.join(UPLOAD_DIR, fname), "wb") as sf: sf.write(f.getbuffer())
                    st.success(f"上傳成功！")

                st.write("**📑 檢核與等級：**")
                curr_chks = []
                for idx, txt in enumerate(item['check']):
                    old_c = old.get("checks", [])[idx] if idx < len(old.get("checks", [])) else False
                    curr_chks.append(st.checkbox(txt, value=old_c, key=f"ck_{item['id']}_{idx}"))

                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    score = st.radio("自評等級", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(old['score']), key=f"r_{item['id']}", horizontal=True)
                with c2:
                    roles = ["未指派", "行政組", "教學組", "臨床組", "學術組長"]
                    sel_res = st.selectbox("👤 負責人", roles, index=roles.index(old['res']) if old['res'] in roles else 0, key=f"sl_{item['id']}")
                
                user_data[item['id']] = {"score": score, "res": sel_res, "checks": curr_chks, "status": status, "note": note}

    if st.button("💾 儲存自評進度"):
        save_progress(user_data)
        st.toast("自評報告資料已存檔！")

with tab_files:
    st.subheader("🎯 戰情室檔案分類")
    stored = sorted(os.listdir(UPLOAD_DIR))
    for cn in ["第1章", "第2章", "第3章"]:
        with st.expander(f"📁 {cn}"):
            c_items = [i for i in all_criteria if i['chapter'] == cn]
            for it in c_items:
                fl = [f for f in stored if f.startswith(f"{it['id']}_")]
                if fl:
                    st.write(f"📌 **{it['id']} {it['title']}**")
                    for f in fl:
                        col1, col2 = st.columns([8, 2])
                        col1.write(f"📄 {f}")
                        if col2.button("🗑️ 刪除", key=f"del_{f}"):
                            os.remove(os.path.join(UPLOAD_DIR, f)); st.rerun()
                else: st.caption(f"⚪ {it['id']} 無檔案")
    st.divider()
    st.download_button("📦 打包下載 (.zip)", data=create_zip(UPLOAD_DIR), file_name="認定佐證包.zip")

with tab_time:
    st.info("🕒 訪視作業流程規劃：")
    st.table([
        {"階段": "會前會", "時間": "20 min", "重點": "委員溝通流程"},
        {"階段": "致詞簡報", "時間": "20 min", "重點": "限定於訓練訪視項目"},
        {"階段": "實地書審", "時間": "130 min", "重點": "文件核對與人員訪談"},
        {"階段": "意見交流", "時間": "40 min", "重點": "討論共識與回饋建議"}
    ])

# 側邊欄計算
passed_count = sum(1 for d in user_data.values() if d['score'] in ['A', 'B', 'C'])
pass_rate = (passed_count / total_items) * 100 if total_items > 0 else 0
mandatory_failed = [id for id, d in user_data.items() if any(i['id'] == id and i['is_mandatory'] for i in all_criteria) and d['score'] == 'D']

st.sidebar.metric("總達成率", f"{pass_rate:.1f}%")
if mandatory_failed:
    st.sidebar.error(f"❌ 必要項 D ({', '.join(mandatory_failed)})")
elif pass_rate >= 90:
    st.sidebar.success("✅ 符合通過標準")
else:
    st.sidebar.warning(f"⚠️ 未達 90% ({passed_count}/{total_items})")

st.sidebar.divider()
st.sidebar.info("💡 114年度標準：\n1. 必要項 100% 達 C 以上。\n2. 總數達 90% 以上達 C 以上。 [cite: 17, 134-135]")
