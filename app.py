import streamlit as st
import json
import os

# 1. 網頁配置與環境初始化
st.set_page_config(page_title="114年專師認定自檢-終極完整版", layout="wide")

UPLOAD_DIR = "uploaded_evidence"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. 核心資料庫：對照 Word 檔 23 項條文 (含 16 項必評) 
def get_full_criteria():
    return [
        # --- 第一章：教學資源與組織管理 (1.1.1 - 1.2.3) ---
        {"id": "1.1.1", "is_mandatory": True, "chapter": "第一章", "title": "設有專責單位並討論執業議題及勞動權益", "c_level": "副院長級召集人，每3個月開會1次，每年至少4次。", "check": ["組織架構及成員名單", "會議紀錄(近一年4次)", "執業及勞動權益維護資料"]},
        {"id": "1.1.2", "is_mandatory": True, "chapter": "第一章", "title": "訂定明確之執業內容且適時檢討修訂", "c_level": "依辦法訂定各分科執行項目及特定訓練並公告周知。", "check": ["各分科執業範圍規範", "工作契約書(或授權文件)", "醫院公告證明"]},
        {"id": "1.1.3", "is_mandatory": True, "chapter": "第一章", "title": "訂有預立醫療流程 (PMP) SOP", "c_level": "醫師須於24小時內完成核對及簽署。", "check": ["預立醫療流程 SOP", "24小時內核簽紀錄", "委員會名單"]},
        {"id": "1.1.4", "is_mandatory": False, "chapter": "第一章", "title": "建立病歷書寫之審查機制", "c_level": "主治醫師對專師病歷記載給予指導。", "check": ["病歷審查機制規範", "醫師指導痕跡或紀錄"]},
        {"id": "1.1.5", "is_mandatory": False, "chapter": "第一章", "title": "訂定臨床執業品質監測機制", "c_level": "訂有監測規範、辦法及機制，且提出佐證。", "check": ["品質監測辦法", "監測指標與運作情形"]},
        {"id": "1.1.6", "is_mandatory": False, "chapter": "第一章", "title": "建立專科護理師考核機制", "c_level": "訂有考核機制且由醫護部門共同負責。", "check": ["考核規範基準", "醫護共同考核紀錄"]},
        {"id": "1.2.1", "is_mandatory": True, "chapter": "第一章", "title": "妥適的訓練場所", "c_level": "提供兼顧隱私、安全與學習便利性之場所。", "check": ["臨床訓練場所設施", "人員工作安全與健康照護策略"]},
        {"id": "1.2.2", "is_mandatory": True, "chapter": "第一章", "title": "提供訓練必須之設備", "c_level": "提供所需硬體與網路學習平台、文獻檢索功能。", "check": ["訓練相關設備環境", "網路學習平台"]},
        {"id": "1.2.3", "is_mandatory": False, "chapter": "第一章", "title": "提供適當之圖書、期刊並適當管理", "c_level": "提供近5年內圖書及期刊(含實證、法律、醫倫)。", "check": ["資源清單(含電子版)", "新購公告紀錄"]},

        # --- 第二章：教學師資、培育與繼續教育 (2.1.1 - 2.2.3) ---
        {"id": "2.1.1", "is_mandatory": True, "chapter": "第二章", "title": "臨床訓練師資-醫師應具適當資格", "c_level": "具專科醫師資格，實際從事專科工作至少2年。", "check": ["醫師證書影本", "年資服務證明"]},
        {"id": "2.1.2", "is_mandatory": True, "chapter": "第二章", "title": "臨床訓練師資-專師應具適當資格", "c_level": "具專師資格，實際從事專師工作至少2年。", "check": ["專師證書影本", "服務年資證明"]},
        {"id": "2.1.3", "is_mandatory": True, "chapter": "第二章", "title": "師資配置比與品質評值", "c_level": "醫師:專師:學員比例須符合 1:4:4。", "check": ["配置比例統計表", "師資評值教學成效紀錄"]},
        {"id": "2.2.1", "is_mandatory": True, "chapter": "第二章", "title": "明訂具體師資培育制度並落實", "c_level": "明訂培育制度、發展計畫與進修訓練紀錄。", "check": ["師資發展計畫書", "教師參與進修紀錄"]},
        {"id": "2.2.2", "is_mandatory": False, "chapter": "第二章", "title": "師資教學能力提升之培育", "c_level": "教師參與能力課程4小時以上，參與率100%。", "check": ["參與課程紀錄", "課後成效評估檢討"]},
        {"id": "2.2.3", "is_mandatory": True, "chapter": "第二章", "title": "專師繼續教育訓練制度", "c_level": "規劃每年至少辦理20小時繼續教育課程。", "check": ["年度計畫清單", "能力進階制度執行紀錄"]},

        # --- 第三章：教學訓練計畫與執行成果 (3.1.1 - 3.3.4) ---
        {"id": "3.1.1", "is_mandatory": True, "chapter": "第三章", "title": "教學訓練計畫具體可行", "c_level": "含目的、目標、課程、品質維護及評值。", "check": ["培訓計畫書", "計畫討論修訂紀錄"]},
        {"id": "3.1.2", "is_mandatory": True, "chapter": "第三章", "title": "適當安排教學課程內容與活動", "c_level": "合理兼顧學習與工作需要，具補訓機制。", "check": ["教學活動時程表", "開訓說明會紀錄", "補訓措施證明"]},
        {"id": "3.2.1", "is_mandatory": True, "chapter": "第三章", "title": "訓練課程符合法規規定並落實", "c_level": "內容須符合專科護理師分科及甄審辦法。", "check": ["計畫書法規對應", "教材、簽到與成果評值"]},
        {"id": "3.2.2", "is_mandatory": True, "chapter": "第三章", "title": "臨床實務訓練落實執行與改善", "c_level": "反映學習目標，具檢討改善機制。", "check": ["實務訓練產生成果", "檢討改善之證據"]},
        {"id": "3.3.1", "is_mandatory": True, "chapter": "第三章", "title": "有回饋機制與反映管道", "c_level": "教師即時回饋並紀錄，保障學員權益。", "check": ["師生輔導紀錄", "問題反映與溝通證明"]},
        {"id": "3.3.2", "is_mandatory": False, "chapter": "第三章", "title": "對於教師多元化評估機制", "c_level": "訂有教師教學成效評估機制並執行。", "check": ["教師評估機制文件", "回饋與輔導改善紀錄"]},
        {"id": "3.3.3", "is_mandatory": False, "chapter": "第三章", "title": "學員訓練成果分析與改善", "c_level": "多元評估結果並分析輔導。", "check": ["成果分析報告", "成果不佳輔導紀錄"]},
        {"id": "3.3.4", "is_mandatory": True, "chapter": "第三章", "title": "訓練計畫成效評估並每年檢討", "c_level": "訂有具體評值計畫且每年檢討(含考照率)。", "check": ["評值分析報告", "考照通過率統計", "改善追蹤紀錄"]}
    ]

# 3. 檔案與進度管理
SAVE_FILE = 'progress.json'
def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_progress(progress):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f: json.dump(progress, f, ensure_ascii=False)

# --- 主 UI ---
st.title("🛡️ 114年度專師認定自檢-智慧旗艦版")
st.markdown("本系統已整合 **23 項全條文** ，並啟用自動標準化命名、重複提示與分類戰情室。")

all_criteria = get_full_criteria()
saved_progress = load_progress()
user_data = {}

tab_chk, tab_files, tab_time = st.tabs(["📋 條文自檢與上傳", "🎯 檔案分類戰情室", "⏱️ 訪視時程"])

with tab_chk:
    for chap in ["第一章", "第二章", "第三章"]:
        st.subheader(f"📍 {chap}")
        for item in [d for d in all_criteria if d['chapter'] == chap]:
            badge = " (必)" if item['is_mandatory'] else ""
            with st.expander(f"{item['id']} {item['title']}{badge}"):
                st.write(f"**【C等級標準】**：{item['c_level']}")
                st.warning(f"🎤 訪談模擬題：{item.get('q', '請說明此項目的落實情形。')}")
                
                old_data = saved_progress.get(item['id'], {"score": "D", "res": "未指派", "checks": [], "links": ""})
                
                # 功能：重複偵測與標準化命名
                st.write("**📤 佐證檔案上傳：**")
                files = st.file_uploader(f"選擇檔案 ({item['id']})", accept_multiple_files=True, key=f"up_{item['id']}", label_visibility="collapsed")
                
                if files:
                    for f in files:
                        ext = os.path.splitext(f.name)[1]
                        std_name = f"{item['id']}_{item['title']}_2026備評用{ext}"
                        if os.path.exists(os.path.join(UPLOAD_DIR, std_name)):
                            st.warning(f"⚠️ 注意：偵測到重複命名檔案，將覆蓋舊版『{std_name}』。")
                        with open(os.path.join(UPLOAD_DIR, std_name), "wb") as save_f:
                            save_f.write(f.getbuffer())
                    st.success(f"已上傳 {len(files)} 份佐證。")
                
                # 功能：細項檢核
                st.write("**📑 佐證資料細項核對：**")
                current_checks = []
                for i, check_text in enumerate(item['check']):
                    old_checked = old_data.get("checks", [])[i] if i < len(old_data.get("checks", [])) else False
                    is_checked = st.checkbox(check_text, value=old_checked, key=f"chk_{item['id']}_{i}")
                    current_checks.append(is_checked)

                # 評分與分工
                c1, c2 = st.columns([1, 1])
                with c1:
                    roles = ["未指派", "行政組", "教學組", "臨床組", "學術組長"]
                    def_idx = roles.index(old_data['res']) if old_data['res'] in roles else 0
                    sel_res = st.selectbox("👤 負責組別", roles, index=def_idx, key=f"sel_{item['id']}")
                with c2:
                    score = st.radio("自評等級", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(old_data['score']), key=f"r_{item['id']}", horizontal=True)
                
                # 額外連結紀錄
                extra_links = st.text_input("🔗 多重 URL 連結 (用逗號隔開)", value=old_data.get("links", ""), key=f"lnk_{item['id']}")
                user_data[item['id']] = {"score": score, "res": sel_res, "checks": current_checks, "links": extra_links}

    if st.button("💾 儲存自檢進度"):
        save_progress(user_data)
        st.toast("全院進度已同步儲存！")

# 智慧分類檔案管理
with tab_files:
    st.subheader("🎯 備評佐證分類管理")
    all_stored = os.listdir(UPLOAD_DIR)
    for chap_name in ["第一章", "第二章", "第三章"]:
        with st.expander(f"📁 {chap_name} 佐證彙整"):
            for item in [d for d in all_criteria if d['chapter'] == chap_name]:
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
                    st.caption(f"⚪ {item['id']} 尚未上傳檔案")

with tab_time:
    st.info("🕒 訪視當天總計 3.5 小時：")
    st.table([
        {"階段": "會前會", "時間": "20 min", "重點": "委員共識與流程確認"},
        {"階段": "簡報", "時間": "20 min", "重點": "15min 簡報 + 5min 致詞"},
        {"階段": "實地/書審/訪談", "時間": "130 min", "重點": "文件核對與人員訪談"},
        {"階段": "回饋", "時間": "10 min", "重點": "委員建議與初步回饋"}
    ])

# 判定邏輯判定 
total_items = len(all_criteria)
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
st.sidebar.info("💡 提醒：必要條文須 100% 達 C 以上，且總達成率需達 90% 以上 [cite: 17] 。")
