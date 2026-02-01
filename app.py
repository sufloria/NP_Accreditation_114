import streamlit as st
import json
import os
import zipfile
import io

# 1. 網頁配置：設定寬螢幕與標題
st.set_page_config(page_title="114年專師認定自檢-終極旗艦版", layout="wide")

# 建立儲存資料夾
UPLOAD_DIR = "uploaded_evidence"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. 核心資料庫：完整 23 項條文細項 (對照自評表全文，含 A/B/C 標準與評分方法) [cite: 140-268, 291-335]
def get_full_criteria():
    return [
        # --- 第 1 章：教學資源與組織管理 (1.1.1 - 1.2.3) ---
        {"id": "1.1.1", "is_mandatory": True, "chapter": "第1章", "title": "專責培育及管理單位與勞動權益 (必)", 
         "grading": {"C": "由醫師、專師及護理主管組成，副院長任召集人。每3個月開會1次，每年至少4次，訂有勞動權益維護措施。", "B": "符合C項。專責單位有護理部督導長以上代表，且有專屬窗口負責管理運作。會議包含權益議題。", "A": "符合B項。專師代表佔委員人數50%（含）以上，具有適當科別代表性。"},
         "methods": "【書面審查】\n1.檢視組織架構及成員名單\n2.檢視會議運作規範及會議紀錄\n3.檢視執業及勞動權益維護資料",
         "check": ["組織架構及成員名單", "會議運作規範與會議紀錄", "專師執業及勞動權益維護資料"]},
        {"id": "1.1.2", "is_mandatory": True, "chapter": "第1章", "title": "明確之執業內容訂定與公告 (必)", 
         "grading": {"C": "依辦法訂定各分科可執行醫療業務範圍、項目及特定訓練，公告周知並執行。", "B": "符合C項，且依執業內容訂有工作契約書且確實執行。", "A": "符合B項，且每年檢討修訂執業內容。"},
         "methods": "【書面審查】檢視各分科可執行業務規範與工作契約文件\n【訪談】訪談人員確認內容落實情形",
         "check": ["分科可執行業務規範", "工作契約文件"]},
        {"id": "1.1.3", "is_mandatory": True, "chapter": "第1章", "title": "預立醫療流程 (PMP) SOP (必)", 
         "grading": {"C": "成立委員會由副院長以上任召集人。監督醫師於24小時內完成核對及簽署。", "B": "符合C項。依能力訂定執行項目，檢視訓練計畫與預立醫療流程之適當性。", "A": "符合B項。PMP有特定訓練、評值、定期修正與審查等強化機制。"},
         "methods": "【書面審查】檢視 PMP SOP 及其運作情形\n【訪談】訪談相關人員確認 24 小時內核簽之落實",
         "check": ["PMP 標準作業程序", "24小時核簽紀錄"]},
        {"id": "1.1.4", "is_mandatory": False, "chapter": "第1章", "title": "病歷書寫之審查機制", 
         "grading": {"C": "主治醫師對專科護理師之病歷記載給予指導。", "B": "符合C項，具體審查項目、抽樣人數、頻率與明確審查機制。", "A": "符合B項，能依指導或審查意見製作教案或案例討論教學。"},
         "methods": "【書面審查】檢視審查機制與執行情形\n【訪談】訪談確認主治醫師指導之頻率與深度",
         "check": ["病歷審查機制規範", "醫師指導紀錄"]},
        {"id": "1.1.5", "is_mandatory": False, "chapter": "第1章", "title": "臨床執業品質監測機制", 
         "grading": {"C": "依執業範疇與契約訂有品質監測規範、辦法及機制，且提出佐證。", "B": "符合C項，提出指標、方法、具體定義、範圍，且確實執行。", "A": "符合B項，且每年檢討改善。"},
         "methods": "【書面審查】檢視品質監測辦法及運作情形\n【訪談】訪談確認品質指標之監測數據",
         "check": ["品質監測指標數據", "年度改善紀錄"]},
        {"id": "1.1.6", "is_mandatory": False, "chapter": "第1章", "title": "建立專科護理師考核機制", 
         "grading": {"C": "訂有專師考核機制且由醫護部門共同負責。", "B": "符合C項，且有專科護理師參與考核機制。", "A": "符合B項，每年檢討考核機制並有檢討紀錄與改善。"},
         "methods": "【書面審查】檢視考核規範與運作情形\n【訪談】訪談專師代表參與考核之程度",
         "check": ["考核規範與標準", "醫護共同考核紀錄"]},
        {"id": "1.2.1", "is_mandatory": True, "chapter": "第1章", "title": "妥適的訓練場所 (必)", 
         "grading": {"C": "提供妥適場所，兼顧隱私、安全與學習便利性。", "B": "符合C項，提供優質場所並兼顧醫療品質與隱私。", "A": "符合B項，具人員工作安全與健康照護策略。"},
         "methods": "【實地審查】檢視場所空間設施、隱私保護措施\n【訪談】訪談人員對工作安全之感受度",
         "check": ["臨床場所空間配置", "安全健康照護策略"]},
        {"id": "1.2.2", "is_mandatory": True, "chapter": "第1章", "title": "提供訓練必須之設備 (必)", 
         "grading": {"C": "提供訓練所需之相關設備。", "B": "符合C項，具網路學習平台、文獻檢索功能。", "A": "符合B項，設置或特約臨床技能訓練中心。"},
         "methods": "【實地審查】檢核硬體設備、模擬環境與網路學習平台之可用性",
         "check": ["設備清單", "學習平台登入紀錄"]},
        {"id": "1.2.3", "is_mandatory": False, "chapter": "第1章", "title": "圖書期刊資源管理", 
         "grading": {"C": "提供近5年內圖書及期刊，含倫理、法律、品質、實證醫學等。", "B": "符合C項，新購資源有清單並定期公告且有管理機制。", "A": "符合B項，定期評估需求購置教學必要之資源。"},
         "methods": "【實地、書面審查】資源清單、採購規則、公告Email或網頁\n【訪談】確認人員是否了解獲取資源之管道",
         "check": ["資源清單(近5年)", "公告周知紀錄"]},

        # --- 第 2 章：教學師資、培育與繼續教育 (2.1.1 - 2.2.3) ---
        {"id": "2.1.1", "is_mandatory": True, "chapter": "第2章", "title": "醫師師資資格 (必)", 
         "grading": {"C": "具專科醫師資格，實際從事專科工作至少2年。", "B": "符合C項，具有專科教師資格，且符合院內培育制度。", "A": "符合B項，由負責教育之主治醫師參與規劃訓練。"},
         "methods": "【書面審查】醫師證書、服務年資證明、教師資格證明\n【訪談】訪談臨床指導醫師確認教學任務",
         "check": ["醫師證書與年資證明"]},
        {"id": "2.1.2", "is_mandatory": True, "chapter": "第2章", "title": "專師師資資格 (必)", 
         "grading": {"C": "具專師資格，且實際從事專科護理師工作至少2年。", "B": "符合C項，從事專師工作滿3年以上佔80%以上。", "A": "符合B項，具碩士2年或學士4年資歷佔80%以上。"},
         "methods": "【書面審查】專師證書、勞健保或服務證明確認年資\n【訪談】訪談專師指導教師之專業資歷",
         "check": ["專師證書與資歷明細表"]},
        {"id": "2.1.3", "is_mandatory": True, "chapter": "第2章", "title": "配置比與品質評值 (必)", 
         "grading": {"C": "比例 醫師:專師:學員(含補充) = 1:4:4。", "B": "符合C項，並有專職醫護人員負責照護及教學。", "A": "符合B項，每年針對師資評值檢討改善。"},
         "methods": "【書面審查】檢視師生比統計表、師資評值報告\n【訪談】確認臨床分組與實際教學運作",
         "check": ["師生比統計表", "師資教學評值報告"]},
        {"id": "2.2.1", "is_mandatory": True, "chapter": "第2章", "title": "師資培育制度並落實 (必)", 
         "grading": {"C": "明訂培育制度、計畫與提供院內進修活動。", "B": "符合C項，與學校合作，設有獎勵與進修措施。", "A": "符合B項，分析執行成效改善，安排技能培育。"},
         "methods": "【書面審查】師資發展計畫、獎勵辦法、參訓證明\n【訪談】教師對師培資源之滿意度",
         "check": ["師資發展計畫", "進修獎勵證明"]},
        {"id": "2.2.2", "is_mandatory": False, "chapter": "第2章", "title": "師資教學能力提升之培育", 
         "grading": {"C": "教師參訓率100%，課程至少4小時。", "B": "符合C項。2年以上年資專師參與課程率達60%以上。", "A": "符合B項。2年以上年資專師參與率達80%以上且進行評估。"},
         "methods": "【書面審查】參訓簽到簿、時數統計、課後評估機制紀錄",
         "check": ["師資參訓紀錄表", "成效評估報告"]},
        {"id": "2.2.3", "is_mandatory": True, "chapter": "第2章", "title": "專師繼續教育訓練 (必)", 
         "grading": {"C": "規劃每年辦理至少20小時繼續教育。", "B": "符合C項，鼓勵院外活動且執行進階制度。", "A": "符合B項，每年檢討修正計畫內容。"},
         "methods": "【書面審查】年度教育清單、進階制度辦法與執行清冊\n【訪談】訪談專師對進階制度之認知",
         "check": ["繼續教育課程表", "能力進階清冊"]},

        # --- 第 3 章：教學訓練計畫與執行成果 (3.1.1 - 3.3.4) ---
        {"id": "3.1.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫內容具體可行 (必)", 
         "grading": {"C": "計畫含目的、目標、課程、品質維護與評值，應用於臨床。", "B": "符合C項，且訓練計畫有教師參與共同訂定。", "A": "符合B項，定期評估並修訂計畫。"},
         "methods": "【書面審查】檢視訓練計畫書之完整性與邏輯\n【訪談】訪談教師確認其參與計畫訂定之經驗",
         "check": ["2023-2026培訓計畫書", "計畫修訂會議紀錄"]},
        {"id": "3.1.2", "is_mandatory": True, "chapter": "第3章", "title": "課程與活動安排 (必)", 
         "grading": {"C": "依能力安排合適課程，時間兼顧學習與工作。", "B": "符合C項。因故無法完成時訂有檢討補救機制。", "A": "符合B項。教師在教學過程中有管道反映。"},
         "methods": "【書面審查】時程表、補訓規定\n【訪談】1.訪談學員清楚課程安排嗎？2.訪談教師調整機制？",
         "check": ["教學活動時程表", "補訓補救紀錄"]},
        {"id": "3.2.1", "is_mandatory": True, "chapter": "第3章", "title": "訓練課程符合法規 (必)", 
         "grading": {"C": "符合甄審辦法內容規定並落實。", "B": "符合C項，定期檢討執行成效。", "A": "符合B項，執行成效良好足為同儕表率。"},
         "methods": "【書面審查】計畫書法規對照、執行紀錄\n【訪談】確認課程廣度與深度之合規性",
         "check": ["計畫書法規對應表", "課程簽到紀錄"]},
        {"id": "3.2.2", "is_mandatory": True, "chapter": "第3章", "title": "臨床實務訓練落實執行 (必)", 
         "grading": {"C": "內容符合法規並落實執行檢討改善。", "B": "符合C項，以訓練產出成果呈現確實落實臨床。", "A": "符合B項，具有檢討及持續改善之證據。"},
         "methods": "【書面審查】臨床案例、雙向回饋紀錄\n【訪談】訪談確認臨床實務與理論之整合度",
         "check": ["實務訓練案例產出", "持續改善證明文件"]},
        {"id": "3.3.1", "is_mandatory": True, "chapter": "第3章", "title": "回饋機制與反映管道 (必)", 
         "grading": {"C": "教師即時回饋紀錄，學員有反映管道保障權益。", "B": "符合C項，針對反映問題有具體改善措施。", "A": "符合B項，具體成果成效良好。"},
         "methods": "【書面審查】輔導紀錄、問題清冊與改善建議\n【訪談】訪談學員反映問題是否獲得回應",
         "check": ["個別學員輔導紀錄", "問題反映清冊"]},
        {"id": "3.3.2", "is_mandatory": False, "chapter": "第3章", "title": "對於教師多元化評估機制", 
         "grading": {"C": "訂有評量成效機制，利用多元管道評估。", "B": "符合C項，針對結果訂有回饋與輔導改善。", "A": "符合B項，能落實執行回饋與輔導。"},
         "methods": "【書面審查】教師評估辦法、回饋紀錄、輔導改善措施檔案",
         "check": ["教師評量標準表", "教師輔導紀錄"]},
        {"id": "3.3.3", "is_mandatory": False, "chapter": "第3章", "title": "學員訓練成果分析改善", 
         "grading": {"C": "訂有訓練成效評估機制，多元管道分析結果。", "B": "符合C項，針對結果訂定回饋與改善。", "A": "符合B項，能落實執行改善輔導。"},
         "methods": "【書面審查】成績統計、成果檢討報告、補強輔導計畫書",
         "check": ["訓練成果分析報告", "成效不佳者輔導案"]},
        {"id": "3.3.4", "is_mandatory": True, "chapter": "第3章", "title": "訓練計畫成效評估 (必)", 
         "grading": {"C": "對計畫成果訂有評值計畫(含考照率)，每年定期檢討。", "B": "符合C項，依評值結果提出檢討改善方法。", "A": "符合B項，改善措施具追蹤機制且成效良好。"},
         "methods": "【書面審查】計畫評值報告、考照通過率趨勢、追蹤清冊\n【訪談】確認計畫與醫院目標之連結性",
         "check": ["評值檢討報告(含考照率)", "改善措施追蹤表"]}
    ]

# 3. 數據管理函式
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
total_items = len(all_criteria) # <--- 置頂定義：確保全域可用，徹底修復 NameError
saved_progress = load_progress()
user_data = {}

st.title("🛡️ 114年度專師認定自檢 - 終極整合旗艦版")
st.markdown(f"系統已對照自評表補齊 **23 項全條文** [cite: 17, 134-135, 140-268]。合格門檻：C級以上達 90% 且必要項 100% 達標。")

tab_chk, tab_files, tab_time = st.tabs(["📝 專業報告撰寫", "🎯 檔案/網址戰情室", "🕒 訪視時程參考"])

with tab_chk:
    for chap_idx in ["第1章", "第2章", "第3章"]:
        st.subheader(f"📍 {chap_idx}")
        chap_items = [d for d in all_criteria if d['chapter'] == chap_idx]
        for item in chap_items:
            badge = " (必)" if item['is_mandatory'] else ""
            with st.expander(f"{item['id']} {item['title']}{badge}"):
                
                # 數據安全載入
                old = saved_progress.get(item['id'], {})
                
                # 區塊 1：等級指引卡片
                st.write("**⭐ 評分標準詳述：**")
                g1, g2, g3 = st.columns(3)
                g1.info(f"**【C級基準】**\n{item['grading']['C']}")
                g2.success(f"**【B級優化】**\n{item['grading']['B']}")
                g3.warning(f"**【A級卓越】**\n{item['grading']['A']}")
                
                # 評分方法區 (新增)
                with st.container():
                    st.markdown("---")
                    st.write("**📋 評分方法 (委員查核重點)：**")
                    st.code(item.get("methods", "尚無詳細方法說明"), language="text")

                # 區塊 2：現況分析撰寫
                st.write("**✍️ 自評報告撰寫區：**")
                t1, t2 = st.columns(2)
                with t1:
                    status = st.text_area(f"執行現況說明 ({item['id']})", value=old.get("status", ""), height=150, key=f"st_{item['id']}")
                with t2:
                    note = st.text_area(f"訪查記錄 / 備註 ({item['id']})", value=old.get("note", ""), height=150, key=f"nt_{item['id']}")

                # 區塊 3：檔案管理與網址連結 (完美並存)
                st.divider()
                st.write("**📤 佐證資料管理 (支援上傳檔案與網址連結)：**")
                c_up, c_url = st.columns(2)
                with c_up:
                    files = st.file_uploader(f"上傳檔案", accept_multiple_files=True, key=f"up_{item['id']}", label_visibility="collapsed")
                    if files:
                        for f in files:
                            ext = os.path.splitext(f.name)[1]
                            std_name = f"{item['id']}_{item['title'][:15]}_2026備評用{ext}"
                            with open(os.path.join(UPLOAD_DIR, std_name), "wb") as sf: sf.write(f.getbuffer())
                        st.success("上傳成功。")
                with c_url:
                    url_in = st.text_input("🔗 雲端連結網址 (多網址用逗號 , 分隔)", value=old.get("urls", ""), key=f"url_{item['id']}", placeholder="貼上網址")
                    if url_in:
                        url_list = [u.strip() for u in url_in.split(",") if u.strip()]
                        btn_cols = st.columns(len(url_list))
                        for idx, link in enumerate(url_list):
                            with btn_cols[idx]: st.link_button(f"🌐 連結佐證 {idx+1}", link, use_container_width=True)

                # 區塊 4：檢核細項
                st.write("**📑 檢核項目核對：**")
                curr_chks = []
                old_chks_list = old.get("checks", [])
                for idx, text in enumerate(item['check']):
                    # 徹底修復第 177 行語法報錯：採用保險的陣列長度檢查
                    val_checked = False
                    if idx < len(old_chks_list):
                        val_checked = old_chks_list[idx]
                    curr_chks.append(st.checkbox(text, value=val_checked, key=f"chk_{item['id']}_{idx}"))

                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    score = st.radio("自評等級", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(old.get("score", "D")), key=f"r_{item['id']}", horizontal=True)
                with c2:
                    roles = ["未指派", "行政組", "教學組", "臨床組", "學術組長"]
                    sel_res = st.selectbox("👤 負責組別", roles, index=roles.index(old.get("res", "未指派")), key=f"sl_{item['id']}")
                
                user_data[item['id']] = {"score": score, "res": sel_res, "checks": curr_chks, "status": status, "note": note, "urls": url_in}

    if st.button("💾 儲存自評報告進度"):
        save_progress(user_data)
        st.toast("所有自評內容與網址連結已存檔！")

# 分類檔案戰情室
with tab_files:
    st.subheader("📁 分類檔案與連結備份")
    st.write("**📥 資料備份：** 系統更新前，建議先下載 JSON 備份進度檔案。")
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.download_button("☁️ 下載進度備份 (progress.json)", data=json.dumps(user_data, ensure_ascii=False, indent=2), file_name="progress_backup.json")
    with c_b2:
        st.download_button("📦 打包下載所有檔案 (.zip)", data=create_zip(UPLOAD_DIR), file_name="114專師佐證彙編.zip")
    
    st.divider()
    stored = sorted(os.listdir(UPLOAD_DIR))
    for cn in ["第1章", "第2章", "第3章"]:
        with st.expander(f"📂 {cn} 佐證檔案集"):
            c_items = [i for i in all_criteria if i['chapter'] == cn]
            for it in c_items:
                fl = [f for f in stored if f.startswith(f"{it['id']}_")]
                if fl:
                    st.write(f"📌 **{it['id']} {it['title']}**")
                    for fn in fl:
                        col1, col2 = st.columns([8, 2])
                        col1.write(f"📄 {fn}")
                        if col2.button("🗑️ 刪除", key=f"del_{fn}"):
                            os.remove(os.path.join(UPLOAD_DIR, fn)); st.rerun()
                else: st.caption(f"⚪ {it['id']} 尚無檔案")

# 時程規劃
with tab_time:
    st.info("🕒 訪視作業流程規劃 [cite: 50-51]：")
    st.table([
        {"階段": "會前會", "時間": "20 min", "重點": "委員先行溝通確認"},
        {"階段": "醫院簡報", "時間": "20 min", "重點": "簡報 15min + 致詞 5min"},
        {"階段": "實地/書審", "時間": "130 min", "重點": "佐證核對與訪談"},
        {"階段": "整理回饋", "時間": "40 min", "重點": "初步建議說明"}
    ])

# 側邊欄邏輯判定與顯示
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
st.sidebar.info("💡 通過標準：\n1. 必要項 100% 達 C 以上。\n2. C級以上項目總數達 90% 以上 。 [cite: 17, 134-135]")
