import streamlit as st
import json
import os

# 1. 網頁配置與環境初始化
st.set_page_config(page_title="114年專師認定自檢-終極旗艦版", layout="wide")

UPLOAD_DIR = "uploaded_evidence"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. 核心資料庫：對應 114 年度自評表全文 [cite: 140-268]
def get_full_criteria():
    return [
        # --- 第一章：教學資源與組織管理 ---
        {"id": "1.1.1", "is_mandatory": True, "chapter": "第一章", "title": "專責單位與討論議題及勞動權益", 
         "grading": {"C": "副院長召集，每3個月開會1次，每年至少4次。", "B": "符合C項，有護理部督導長以上代表及窗口。", "A": "符合B項，專師代表佔50%以上，具有科別代表性。"},
         "check": ["組織架構與成員名單", "近一年4次會議紀錄", "勞動權益維護資料"], "q": "召集人級別？會議頻率？"},
        {"id": "1.1.2", "is_mandatory": True, "chapter": "第一章", "title": "明確之執業內容訂定與公告", 
         "grading": {"C": "依辦法訂定各分科執行項目並公告周知且確實執行。", "B": "符合C項，依執業內容訂有工作契約書且確實執行。", "A": "符合B項，且每年定期檢討修訂執業內容。"},
         "check": ["分科可執行醫療業務規範", "工作契約書(或授權文件)", "醫院公告證明"], "q": "如何確保業務不超出衛福部附表範圍？"},
        {"id": "1.1.3", "is_mandatory": True, "chapter": "第一章", "title": "預立醫療流程 (PMP) SOP", 
         "grading": {"C": "副院長召集，監督醫師於24小時內完成核對及簽署。", "B": "符合C項，依能力訂定執行項目，檢視PMP適當性。", "A": "符合B項，PMP有特定訓練、評值與定期修正機制。"},
         "check": ["預立醫療流程 SOP", "24小時內核簽紀錄", "委員會名單"], "q": "醫師是否於24小時內補簽名？"},
        {"id": "1.1.4", "is_mandatory": False, "chapter": "第一章", "title": "病歷書寫之審查機制", 
         "grading": {"C": "主治醫師對專科護理師之病歷記載給予指導。", "B": "符合C項，具體審查項目、抽樣人數、頻率機制。", "A": "符合B項，依指導意見製作教案或案例討論教學。"},
         "check": ["病歷審查機制規範", "醫師指導或審查紀錄"], "q": "主治醫師如何給予指導？"},
        {"id": "1.1.5", "is_mandatory": False, "chapter": "第一章", "title": "臨床執業品質監測機制", 
         "grading": {"C": "訂有監測規範、辦法及機制，且提出佐證。", "B": "符合C項，提出指標、方法等具體定義並執行。", "A": "符合B項，且每年檢討改善。"},
         "check": ["品質監測辦法", "監測指標與運作情形"], "q": "醫院如何監測執業品質？"},
        {"id": "1.1.6", "is_mandatory": False, "chapter": "第一章", "title": "專科護理師考核機制", 
         "grading": {"C": "訂有考核機制且由醫護部門共同負責。", "B": "符合C項，且有專科護理師參與考核機制。", "A": "符合B項，每年檢討機制並有相關紀錄。"},
         "check": ["考核規範基準", "醫護共同考核紀錄"], "q": "考核是否由醫護共同負責？"},
        {"id": "1.2.1", "is_mandatory": True, "chapter": "第一章", "title": "妥適的訓練場所", 
         "grading": {"C": "提供妥適場所，兼顧隱私、安全與學習便利性。", "B": "符合C項，依特性提供優質場所及醫療品質。", "A": "符合B項，具工作安全與健康照護策略。"},
         "check": ["臨床訓練場所設施", "人員工作安全健康照護策略"], "q": "實地觀察隱私與病人安全。"},
        {"id": "1.2.2", "is_mandatory": True, "chapter": "第一章", "title": "提供訓練必須之設備", 
         "grading": {"C": "提供訓練所需之相關設備。", "B": "符合C項，具網路學習平台、文獻檢索功能。", "A": "符合B項，設置或特約臨床技能訓練中心。"},
         "check": ["訓練設備與環境", "網路學習平台與文獻庫"], "q": "臨床單位是否能隨時使用學習平台？"},
        {"id": "1.2.3", "is_mandatory": False, "chapter": "第一章", "title": "圖書期刊管理與公告", 
         "grading": {"C": "提供購置圖書及期刊，含實證、法律、倫理等。", "B": "符合C項，新購資源有清單並定期公告管理。", "A": "符合B項，定期評估需求購置教學必要之資源。"},
         "check": ["資源清單(含電子版)", "新購公告紀錄"], "q": "是否了解新購資源之公告管道？"},

        # --- 第二章：教學師資、培育與繼續教育 ---
        {"id": "2.1.1", "is_mandatory": True, "chapter": "第二章", "title": "醫師師資資格", 
         "grading": {"C": "具專科醫師資格，實際從事專科工作至少2年。", "B": "符合C項，具教師資格並符合院內培訓規範。", "A": "符合B項，由負責教育之主治醫師參與規劃督導。"},
         "check": ["醫師證書影本", "服務證明與年資"], "q": "指導醫師資歷是否符合規範？"},
        {"id": "2.1.2", "is_mandatory": True, "chapter": "第二章", "title": "專師師資資格", 
         "grading": {"C": "具專師資格，實際從事專師工作至少2年。", "B": "符合C項，從事專師工作滿3年以上佔80%。", "A": "符合B項，具碩士2年或學士4年資歷佔80%。"},
         "check": ["專師證書影本", "臨床服務年資證明"], "q": "擔任教師之專師資歷？"},
        {"id": "2.1.3", "is_mandatory": True, "chapter": "第二章", "title": "配置比與品質評值", 
         "grading": {"C": "醫師:專師:學員比例須符合 1:4:4。", "B": "符合C項，並有專責醫師專師負責照護教學。", "A": "符合B項，針對師資進行教學評值檢討改善。"},
         "check": ["臨床配置統計表", "師資評值教學紀錄"], "q": "師生比是否符合 1:4:4？"},
        {"id": "2.2.1", "is_mandatory": True, "chapter": "第二章", "title": "師資培育制度並落實", 
         "grading": {"C": "明訂培訓制度、計畫與提供院內進修活動。", "B": "符合C項，與學校合作，設有進修獎勵措施。", "A": "符合B項，定期檢討發展計畫並安排技能課程。"},
         "check": ["師資發展計畫書", "教師參與進修紀錄"], "q": "如何培育教師教學能力？"},
        {"id": "2.2.2", "is_mandatory": False, "chapter": "第二章", "title": "師資教學能力提升之培育", 
         "grading": {"C": "教師課程至少4小時，參與率達100%。", "B": "符合C項，2年以上專師參與課程達60%。", "A": "符合B項，2年以上專師參與率達80%並檢討。"},
         "check": ["參與課程紀錄", "課後成效評估與檢討"], "q": "指導教師參訓率？"},
        {"id": "2.2.3", "is_mandatory": True, "chapter": "第二章", "title": "專師繼續教育制度", 
         "grading": {"C": "規劃每年辦理至少20小時繼續教育課程。", "B": "符合C項，鼓勵院外學術活動及進階制度。", "A": "符合B項，每年檢討修正課程與進階內容。"},
         "check": ["年度繼續教育計畫", "進階制度執行紀錄"], "q": "課程是否足以維持證照效期？"},

        # --- 第三章：教學訓練計畫與執行成果 ---
        {"id": "3.1.1", "is_mandatory": True, "chapter": "第三章", "title": "教學計畫具體可行", 
         "grading": {"C": "含目的、課程、品質維護與評值，應用於臨床。", "B": "符合C項，且訓練計畫有教師參與訂定。", "A": "符合B項，定期針對計畫評估並適時修訂。"},
         "check": ["年度培訓計畫書", "計畫討論修訂紀錄"], "q": "請說明訓練計畫如何確保品質？"},
        {"id": "3.1.2", "is_mandatory": True, "chapter": "第三章", "title": "課程與教學活動安排", 
         "grading": {"C": "依能力安排課程，兼顧學習與工作需要。", "B": "符合C項，依計畫教學，中斷有補救機制。", "A": "符合B項，教師執行教學有回饋管道修訂計畫。"},
         "check": ["教學活動時程表", "開訓說明會紀錄", "補訓補救機制紀錄"], "q": "如何確保訓練不被臨床排擠？"},
        {"id": "3.2.1", "is_mandatory": True, "chapter": "第三章", "title": "訓練課程符合法規規定", 
         "grading": {"C": "內容符合專科護理師分科及甄審辦法。", "B": "符合C項，定期檢討執行成效。", "A": "符合B項，執行成效良好足為同儕表率。"},
         "check": ["計畫書法規對應表", "教材簽到與成果評值"], "q": "如何確保符合法規課程要求？"},
        {"id": "3.2.2", "is_mandatory": True, "chapter": "第三章", "title": "臨床實務訓練落實執行", 
         "grading": {"C": "內容符合甄審辦法並落實執行檢討改善。", "B": "符合C項，產出成果確實落實於臨床業務。", "A": "符合B項，具證據顯示檢討與持續改善。"},
         "check": ["臨床案例產出成果", "改善及檢討證據"], "q": "老師如何在臨床確認成效？"},
        {"id": "3.3.1", "is_mandatory": True, "chapter": "第三章", "title": "有回饋機制與反映管道", 
         "grading": {"C": "教師即時回饋紀錄，設有反映管道保障權益。", "B": "符合C項，針對反映問題有改善措施。", "A": "符合B項，具體成果成效良好。"},
         "check": ["師生輔導回饋紀錄", "反映問題溝通證明"], "q": "學員遇到困難如何反映？"},
        {"id": "3.3.2", "is_mandatory": False, "chapter": "第三章", "title": "對於教師多元化評估機制", 
         "grading": {"C": "訂有評估成效機制，利用多元管道評估。", "B": "符合C項，結果訂有回饋與輔導改善措施。", "A": "符合B項，且能落實執行回饋輔導。"},
         "check": ["教師評估機制文件", "回饋與輔導改善紀錄"], "q": "如何評估導師？結果是否回饋？"},
        {"id": "3.3.3", "is_mandatory": False, "chapter": "第三章", "title": "訓練成果分析與改善", 
         "grading": {"C": "評估分析學員結果，訂有分析機制並執行。", "B": "符合C項，針對結果訂定回饋輔導改善措施。", "A": "符合B項，能落實執行輔導改善措施。"},
         "check": ["成果分析報告", "成果不佳輔導紀錄"], "q": "學習落後如何處理？"},
        {"id": "3.3.4", "is_mandatory": True, "chapter": "第三章", "title": "訓練計畫成效評估", 
         "grading": {"C": "訂有具體評值計畫，且每年檢討。", "B": "符合C項，依結果提出檢討改善方法。", "A": "符合B項，改善措施具追蹤機制成效良好。"},
         "check": ["評值分析報告", "考照通過率統計", "改善追蹤紀錄"], "q": "去年考照率如何調整教學？"}
    ]

# 3. 資料持久化邏輯
SAVE_FILE = 'progress.json'
def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_progress(progress):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f: json.dump(progress, f, ensure_ascii=False)

# --- 主 UI 介面 ---
st.title("🛡️ 114年度專師認定自檢系統 - 專業自評報告旗艦版")
st.markdown("本系統已完整整合 **23 項認定條文**，支援現況撰寫、備註記錄、標準化命名上傳與分類戰情室。")

all_criteria = get_full_criteria()
saved_progress = load_progress()
user_data = {}

tab_chk, tab_files, tab_time = st.tabs(["📋 專業自評報告書", "🎯 檔案分類戰情室", "🕒 訪視時程規劃"])

with tab_chk:
    for chap_name in ["第一章", "第二章", "第三章"]:
        st.subheader(f"📍 {chap_name}")
        chap_data = [d for d in all_criteria if d['chapter'] == chap_name]
        for item in chap_data:
            badge = " (必)" if item['is_mandatory'] else ""
            with st.expander(f"{item['id']} {item['title']}{badge}"):
                
                # 載入舊數據
                old_data = saved_progress.get(item['id'], {
                    "score": "D", "res": "未指派", "status_desc": "", "obs_note": "", "checks": [], "links": ""
                })

                # 區塊 1：評分指引 (A/B/C) 
                st.write("**⭐ 評分等級指引：**")
                g_col1, g_col2, g_col3 = st.columns(3)
                g_col1.info(f"**【C級基準】**\n{item['grading']['C']}")
                g_col2.success(f"**【B級優化】**\n{item['grading']['B']}")
                g_col3.warning(f"**【A級卓越】**\n{item['grading']['A']}")
                
                # 區塊 2：撰寫區 [cite: 140, 111]
                st.write("**✍️ 自評報告撰寫與備註：**")
                col_text1, col_text2 = st.columns(2)
                with col_text1:
                    status_desc = st.text_area(f"執行現況說明 ({item['id']})", 
                                             value=old_data.get("status_desc", ""), 
                                             placeholder="請描述目前的落實情形與執行細節...", 
                                             height=150, key=f"status_{item['id']}")
                with col_text2:
                    obs_note = st.text_area(f"訪查記錄 / 備註 ({item['id']})", 
                                           value=old_data.get("obs_note", ""), 
                                           placeholder="記錄委員建議、預評待補資料、或實地筆記...", 
                                           height=150, key=f"note_{item['id']}")

                # 區塊 3：佐證核對與上傳
                st.write("**📑 佐證細項核對：**")
                current_checks = []
                for i, check_text in enumerate(item['check']):
                    old_checked = old_data.get("checks", [])[i] if i < len(old_data.get("checks", [])) else False
                    is_checked = st.checkbox(check_text, value=old_checked, key=f"chk_{item['id']}_{i}")
                    current_checks.append(is_checked)

                st.write("**📤 佐證檔案上傳 (系統自動標準化命名)：**")
                files = st.file_uploader(f"選擇檔案 ({item['id']})", accept_multiple_files=True, key=f"up_{item['id']}", label_visibility="collapsed")
                if files:
                    for f in files:
                        ext = os.path.splitext(f.name)[1]
                        std_name = f"{item['id']}_{item['title']}_2026備評用{ext}"
                        if os.path.exists(os.path.join(UPLOAD_DIR, std_name)):
                            st.warning(f"⚠️ 提示：已存在同名檔案，上傳將覆蓋舊版。")
                        with open(os.path.join(UPLOAD_DIR, std_name), "wb") as save_f:
                            save_f.write(f.getbuffer())
                    st.success(f"已上傳 {len(files)} 份標準化檔案。")
                
                # 區塊 4：等級判定
                st.divider()
                c1, c2 = st.columns([1, 1])
                with c1:
                    score = st.radio("自評等級", ["A", "B", "C", "D"], 
                                   index=["A", "B", "C", "D"].index(old_data['score']), 
                                   key=f"r_{item['id']}", horizontal=True)
                with c2:
                    roles = ["未指派", "行政組", "教學組", "臨床組", "學術組長"]
                    def_idx = roles.index(old_data['res']) if old_data['res'] in roles else 0
                    sel_res = st.selectbox("👤 負責組別", roles, index=def_idx, key=f"sel_{item['id']}")
                
                user_data[item['id']] = {
                    "score": score, "res": sel_res, "checks": current_checks, 
                    "status_desc": status_desc, "obs_note": obs_note
                }

    if st.button("💾 儲存自評報告進度"):
        save_progress(user_data)
        st.toast("全院進度已儲存於進度檔！")

# 分類戰情室
with tab_files:
    st.subheader("🎯 備評佐證分類管理戰情室")
    all_stored = sorted(os.listdir(UPLOAD_DIR))
    for chap_name in ["第一章", "第二章", "第三章"]:
        with st.expander(f"📁 {chap_name} 佐證彙整"):
            chap_items = [d for d in all_criteria if d['chapter'] == chap_name]
            for item in chap_items:
                item_files = [f for f in all_stored if f.startswith(f"{item['id']}_")]
                if item_files:
                    st.write(f"📌 **{item['id']} {item['title']}**")
                    for fn in item_files:
                        col_fn, col_dl = st.columns([8, 2])
                        col_fn.write(f"📄 {fn}")
                        if col_dl.button("🗑️ 刪除", key=f"del_{fn}"):
                            os.remove(os.path.join(UPLOAD_DIR, fn))
                            st.rerun()
                else:
                    st.caption(f"⚪ {item['id']} 尚未上傳佐證檔案")

# 時程規劃 [cite: 50-51]
with tab_time:
    st.info("🕒 訪視當天總計 3.5 小時：")
    st.table([
        {"階段": "會前會", "時間": "20 min", "重點": "委員溝通與確認程序"},
        {"階段": "簡報", "時間": "20 min", "重點": "15min 簡報 + 5min 致詞"},
        {"階段": "實地/書審/訪談", "時間": "130 min", "重點": "文件核對與人員訪談"},
        {"階段": "回饋", "時間": "40 min", "重點": "委員建議與初步回饋"}
    ])

# 側邊欄邏輯 
passed_count = sum(1 for d in user_data.values() if d['score'] in ['A', 'B', 'C'])
pass_rate = (passed_count / total_items) * 100
mandatory_failed = [id for id, d in user_data.items() if any(i['id'] == id and i['is_mandatory'] for i in all_criteria) and d['score'] == 'D']

st.sidebar.metric("總達成率", f"{pass_rate:.1f}%")
if mandatory_failed:
    st.sidebar.error(f"❌ 不合格：必要項 D ({', '.join(mandatory_failed)})")
elif pass_rate >= 90:
    st.sidebar.success("✅ 符合通過門檻")
else:
    st.sidebar.warning(f"⚠️ 達成率不足 90% (需達 90%)")

st.sidebar.divider()
st.sidebar.info("💡 通過門檻：C等級以上達 90% 且 16 項必要條文全數通過 。")
