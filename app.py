import streamlit as st
import json
import os
import zipfile
import io

# 1. 網頁配置
st.set_page_config(page_title="114年專師認定自檢-智慧旗艦版", layout="wide")

# 建立儲存資料夾
UPLOAD_DIR = "uploaded_evidence"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. 核心資料庫：完整對照 Word 檔 23 項條文 (無缺失、無省略版本) 
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
         "grading": {"C": "提供妥適訓練場所，包含地點與環境空間，兼顧學習、醫療品質、病人安全與隱私。", "B": "符合C項，提供優質場所並兼顧醫療品質與隱私。", "A": "符合B項，具人員工作安全與健康照護策略且成效優良。"},
         "check": ["檢視臨床訓練場所設施與空間"]},
        {"id": "1.2.2", "is_mandatory": True, "chapter": "第1章", "title": "提供訓練必須之設備 (必)", 
         "grading": {"C": "提供訓練所需之相關設備。", "B": "符合C項，具有網路學習平台，提供訓練相關訊息及網路文獻檢索功能。", "A": "符合B項，設置或特約臨床技能訓練中心提供模擬環境。"},
         "check": ["檢視訓練相關設備與環境"]},
        {"id": "1.2.3", "is_mandatory": False, "chapter": "第1章", "title": "適當之圖書期刊管理", 
         "grading": {"C": "提供購置圖書及期刊(含電子)，包括醫倫、法律、品質、醫病溝通、實證醫學、病歷寫作等。", "B": "符合C項，新購資源有清單並定期公告(網路或Email)且有管理機制。", "A": "符合B項，定期評估需求購置教學與研究必要之資源。"},
         "check": ["圖書及期刊管理規則、清單與公告形式"]},

        # --- 第 2 章：教學師資、培育與繼續教育 ---
        {"id": "2.1.1", "is_mandatory": True, "chapter": "第2章", "title": "醫師師資應具適當資格 (必)", 
         "grading": {"C": "應具分科甄審辦法附表所定專科醫師資格，實際從事專科工作至少2年。", "B": "符合C項，具專科教師資格，且符合院內培訓規範。", "A": "符合B項，由負責教育之主治醫師參與規劃督導訓練。"},
         "check": ["臨床指導醫師師資資格證明"]},
        {"id": "2.1.2", "is_mandatory": True, "chapter": "第2章", "title": "專師師資應具適當資格 (必)", 
         "grading": {"C": "應具分科甄審辦法附表所職專師資格，實際從事專師工作至少2年。", "B": "符合C項，從事專師工作滿3年以上佔80%以上。", "A": "符合B項，具碩士2年或學士4年資歷佔80%以上。"},
         "check": ["臨床訓練專師師資資格證明"]},
        {"id": "2.1.3", "is_mandatory": True, "chapter": "第2章", "title": "師資配置比與品質評值 (必)", 
         "grading": {"C": "師生比例 醫師:專師:學員(含補充) = 1:4:4。", "B": "符合C項，並有專責醫護人員負責病人照護及教學。", "A": "符合B項，每年針對師資進行教學評值檢討改善。"},
         "check": ["臨床師資與學員配置比例統計表", "師資評值紀錄"]},
        {"id": "2.2.1", "is_mandatory": True, "chapter": "第2章", "title": "師資培育制度並落實執行 (必)", 
         "grading": {"C": "明訂培訓制度、有計畫地培育師資並訂有師資發展計畫，提供進修訓練。", "B": "符合C項。與學校或其他訓練醫院合作，提供進修課程及獎勵措施。", "A": "符合B項。定期檢討分析執行成效並改善，安排不同階段臨床技能培訓。"},
         "check": ["師資發展計畫及進修訓練紀錄資料"]},
        {"id": "2.2.2", "is_mandatory": False, "chapter": "第2章", "title": "師資教學能力提升之培育", 
         "grading": {"C": "對教師提供教學能力培育課程，醫院教師參與課程至少4小時，參與率達100%。", "B": "符合C項。醫院安排所有專師每年參訓，年資2年以上專師參與率達60%以上。", "A": "符合B項。年資2年以上專師參與率達80%以上，且進行課後成效評估檢討。"},
         "check": ["教師參訓情形與課後成效評估機制"]},
        {"id": "2.2.3", "is_mandatory": True, "chapter": "第2章", "title": "專師繼續教育訓練制度 (必)", 
         "grading": {"C": "訂有繼續教育機制，規劃每年至少辦理20小時繼續教育訓練。", "B": "符合C項，有鼓勵院外學術活動措施且訂定執行能力進階制度。", "A": "符合B項，每年檢討修正繼續教育課程與進階制度內容。"},
         "check": ["專師繼續教育計畫及進階制度紀錄"]},

        # --- 第 3 章：教學訓練計畫與執行成果 ---
        {"id": "3.1.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫內容具體適當 (必)", 
         "grading": {"C": "計畫含目的、目標、課程、品質維護、監測及評值回饋，應用於臨床。", "B": "符合C項，且訓練計畫有教師參與共同訂定。", "A": "符合B項，定期針對計畫進行評估並適時修訂。"},
         "check": ["訓練計畫書內容適當性(含目的課程目標)"]},
        {"id": "3.1.2", "is_mandatory": True, "chapter": "第3章", "title": "適當安排教學課程及活動 (必)", 
         "grading": {"C": "依能力安排合適課程，學員清楚安排，訓練時間合理兼顧學習與工作。", "B": "符合C項。教師依課程安排教學，因故中斷有檢討補救機制。", "A": "符合B項。教師在執行教學過程中有建議管道可反映並修訂。"},
         "check": ["訓練課程法規對應表", "教師反映管道紀錄", "補訓措施紀錄"]},
        {"id": "3.2.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練課程符合法規並落實 (必)", 
         "grading": {"C": "訓練課程內容應符合專科護理師分科及甄審辦法規定。", "B": "符合C項，且定期進行執行成效之檢討。", "A": "符合B項，且執行成效良好足為同儕表率。"},
         "check": ["檢視訓練計畫書符合甄審辦法規範"]},
        {"id": "3.2.2", "is_mandatory": True, "chapter": "第3章", "title": "臨床實務訓練落實與改善 (必)", 
         "grading": {"C": "臨床訓練內容符合甄審辦法並落實執行，具檢討改善機制。", "B": "符合C項，以訓練產出成果呈現確實落實臨床業務。", "A": "符合B項，具證據顯示檢討及持續改善。"},
         "check": ["臨床實務訓練案例產出與評值證據"]},
        {"id": "3.3.1", "is_mandatory": True, "chapter": "第3章", "title": "有回饋機制與反映管道 (必)", 
         "grading": {"C": "教師即時回饋，學員有反映問題及溝通管道，兼顧權益並有紀錄。", "B": "符合C項，針對反映問題有改善措施。", "A": "符合B項，具具體成效。"},
         "check": ["教師輔導回饋及學員反映問題管道紀錄"]},
        {"id": "3.3.2", "is_mandatory": False, "chapter": "第3章", "title": "教師多元化評估機制", 
         "grading": {"C": "訂有評估教師教學成效機制並實際執行，定期利用多元管道評估。", "B": "符合C項，針對評估結果訂有回饋與輔導改善措施。", "A": "符合B項，能落實執行回饋與改善。"},
         "check": ["教師教學成效評估機制與紀錄"]},
        {"id": "3.3.3", "is_mandatory": False, "chapter": "第3章", "title": "訓練成果分析與改善", 
         "grading": {"C": "訂有評估訓練成效機制，利用多元管道評估分析訓練結果。", "B": "符合C項，針對結果訂定回饋與輔導改善措施。", "A": "符合B項，能落實執行回饋與改善輔導。"},
         "check": ["訓練成果檢討與分析報告"]},
        {"id": "3.3.4", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫成效評估 (必)", 
         "grading": {"C": "對訓練計畫成果訂有具體評值計畫(含考照率)，每年定期檢討。", "B": "符合C項，且依評值結果提出檢討改善方法。", "A": "符合B項，改善措施具追蹤機制且成效良好。"},
         "check": ["計畫評值分析報告與檢討改善文件"]}
    ]

# 3. 數據持久化
SAVE_FILE = 'progress.json'
def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_progress(progress):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f: json.dump(progress, f, ensure_ascii=False)

# 4. ZIP 打包下載
def create_zip(upload_dir):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for root, dirs, files in os.walk(upload_dir):
            for file in files: z.write(os.path.join(root, file), file)
    return buf.getvalue()

# --- 主程式流程 ---
# 重要：先載入資料，確定 total_items 被定義
all_criteria = get_full_criteria()
total_items = len(all_criteria) # <--- 修正核心：確保此處先被定義

saved_progress = load_progress()
user_data = {}

# --- 主 UI 介面 ---
st.title("🛡️ 114年度專師認定自檢 - 智慧旗艦完整版 (修復版)")
st.markdown(f"系統已完整對應 **23 項全條文** 。")

tab_chk, tab_files, tab_time = st.tabs(["📋 專業報告與撰寫", "🎯 檔案分類戰情室", "⏱️ 訪視時程"])

with tab_chk:
    for chap_name in ["第1章", "第2章", "第3章"]:
        st.subheader(f"📍 {chap_name}")
        chap_items = [d for d in all_criteria if d['chapter'] == chap_name]
        for item in chap_items:
            badge = " (必)" if item['is_mandatory'] else ""
            with st.expander(f"{item['id']} {item['title']}{badge}"):
                
                old_data = saved_progress.get(item['id'], {
                    "score": "D", "res": "未指派", "status_desc": "", "obs_note": "", "checks": []
                })

                # 區塊 1：詳細評分標準
                st.write("**⭐ 評分標準描述：**")
                g1, g2, g3 = st.columns(3)
                g1.info(f"**【C級基準】**\n{item['grading']['C']}")
                g2.success(f"**【B級優化】**\n{item['grading']['B']}")
                g3.warning(f"**【A級卓越】**\n{item['grading']['A']}")
                
                # 區塊 2：現況分析與備註
                st.write("**✍️ 報告撰寫區：**")
                t1, t2 = st.columns(2)
                with t1:
                    status_desc = st.text_area(f"執行現況說明 ({item['id']})", value=old_data.get("status_desc", ""), height=150, key=f"s_{item['id']}")
                with t2:
                    obs_note = st.text_area(f"訪查記錄 / 備註 ({item['id']})", value=old_data.get("obs_note", ""), height=150, key=f"n_{item['id']}")

                # 區塊 3：檔案管理
                st.write("**📤 佐證檔案上傳 (系統自動標準化命名)：**")
                all_stored = os.listdir(UPLOAD_DIR)
                item_files = [f for f in all_stored if f.startswith(f"{item['id']}_")]
                if item_files:
                    st.caption("目前檔案：")
                    for fn in item_files: st.markdown(f"- 📄 `{fn}`")

                files = st.file_uploader(f"上傳佐證 ({item['id']})", accept_multiple_files=True, key=f"up_{item['id']}", label_visibility="collapsed")
                if files:
                    for f in files:
                        ext = os.path.splitext(f.name)[1]
                        std_name = f"{item['id']}_{item['title'][:15]}_2026備評用{ext}"
                        if os.path.exists(os.path.join(UPLOAD_DIR, std_name)):
                            st.warning(f"⚠️ 提示：偵測到重複命名的舊版『{std_name}』，上傳後將覆蓋。")
                        with open(os.path.join(UPLOAD_DIR, std_name), "wb") as save_f: save_f.write(f.getbuffer())
                    st.success(f"已上傳 {len(files)} 份佐證。")
                
                # 區塊 4：核對清單
                st.write("**📑 佐證細項核對：**")
                curr_checks = []
                for i, text in enumerate(item['check']):
                    old_chked = old_data.get("checks", [])[i] if i < len(old_data.get("checks", [])) else False
                    is_chked = st.checkbox(text, value=old_chked, key=f"chk_{item['id']}_{i}")
                    curr_checks.append(is_chked)

                st.divider()
                c1, c2 = st.columns([1, 1])
                with c1:
                    score = st.radio("自評等級", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(old_data['score']), key=f"r_{item['id']}", horizontal=True)
                with c2:
                    roles = ["未指派", "行政組", "教學組", "臨床組", "學術組長"]
                    sel_res = st.selectbox("👤 負責組別", roles, index=roles.index(old_data['res']) if old_data['res'] in roles else 0, key=f"sel_{item['id']}")
                
                user_data[item['id']] = {
                    "score": score, "res": sel_res, "checks": curr_checks, 
                    "status_desc": status_desc, "obs_note": obs_note
                }

    if st.button("💾 儲存自評報告進度"):
        save_progress(user_data)
        st.toast("所有資料與現況撰寫已成功儲存！")

# 戰情室檔案分類
with tab_files:
    st.subheader("🎯 備評佐證分類管理戰情室")
    all_stored_final = sorted(os.listdir(UPLOAD_DIR))
    for c_name in ["第1章", "第2章", "第3章"]:
        with st.expander(f"📁 {c_name} 佐證彙整"):
            items_in_c = [d for d in all_criteria if d['chapter'] == c_name]
            for it in items_in_c:
                f_list = [f for f in all_stored_final if f.startswith(f"{it['id']}_")]
                if f_list:
                    st.write(f"📌 **{it['id']} {it['title']}**")
                    for fn in f_list:
                        cf, cd = st.columns([8, 2])
                        cf.write(f"📄 {fn}")
                        if cd.button("🗑️ 刪除", key=f"del_{fn}"):
                            os.remove(os.path.join(UPLOAD_DIR, fn)); st.rerun()
                else: st.caption(f"⚪ {it['id']} 尚未上傳檔案")
    st.divider()
    zip_data = create_zip(UPLOAD_DIR)
    st.download_button("📦 打包下載所有備評檔案 (.zip)", data=zip_data, file_name="114專師認定佐證包.zip")

# 訪視時程 [cite: 50-51]
with tab_time:
    st.info("🕒 訪視作業流程規劃：")
    st.table([
        {"階段": "會前會", "時間": "20 min", "重點": "委員溝通確認與程序共識"},
        {"階段": "致詞簡報", "時間": "20 min", "重點": "15min 醫院簡報 + 5min 致詞"},
        {"階段": "實地/書審", "時間": "130 min", "重點": "文件核對、場所訪視、人員訪談"},
        {"階段": "意見交流", "時間": "40 min", "重點": "委員共識討論與初步回饋建議"}
    ])

# 側邊欄邏輯判定
passed_count = sum(1 for d in user_data.values() if d['score'] in ['A', 'B', 'C'])
pass_rate = (passed_count / total_items) * 100 if total_items > 0 else 0
mandatory_failed = [id for id, d in user_data.items() if any(i['id'] == id and i['is_mandatory'] for i in all_criteria) and d['score'] == 'D']

st.sidebar.metric("總達成率", f"{pass_rate:.1f}%")
if mandatory_failed:
    st.sidebar.error(f"❌ 不及格：必要項 D ({', '.join(mandatory_failed)})")
elif pass_rate >= 90:
    st.sidebar.success("✅ 符合通過門檻")
else:
    st.sidebar.warning(f"⚠️ 達成率未達 90% (目前 {passed_count}/{total_items})")

st.sidebar.divider()
st.sidebar.info("💡 114年度標準：\n1. 必要項 100% 達 C 以上。\n2. C等級以上評量項目達 90% 以上。 [cite: 17, 134-135, 287]")
