import streamlit as st
import tempfile
from datetime import datetime

st.set_page_title("信可美採購單自動生成器", layout="centered")

st.title("📄 信可美採購單自動生成器")
st.write("請輸入美加採購單或品項資訊，系統將自動套用供應商與 DIN 2093 公差規則產生採購單。")

SUPPLIERS = {
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"}
}

with st.form("po_form"):
    col1, col2 = st.columns(2)
    with col1:
        supplier_code = st.selectbox("選擇供應商代號", ["SF", "VS", "XB"])
        po_date = st.text_input("採購日期", value="2026/07/13")
    with col2:
        item_name = st.text_input("品名", value="盤形彈簧 DB502530")
        specs = st.text_input("規格尺寸 (ODxIDtxLo)", value="50x25.4x3.0xH4.1")

    col3, col4 = st.columns(2)
    with col3:
        qty = st.number_input("採購數量 (PCS)", value=10000, step=1)
    with col4:
        unit_price = st.number_input("單價 (RMB)", value=1.81, format="%.2f")

    submit_button = st.form_submit_button(label="🚀 生成採購單檔案")

if submit_button:
    today_str = datetime.now().strftime("%Y%m%d")
    po_no = f"{supplier_code}{today_str}001"
    sup_info = SUPPLIERS[supplier_code]
    total_amount = qty * unit_price

    txt_content = f"""==================================================
        信可美股份有限公司 採購單 (Purchase Order)
==================================================
採購單號：{po_no}
採購日期：{po_date}
幣    別：RMB

【供應商資訊】
供應商：{sup_info['name']} ({supplier_code})
地  址：{sup_info['addr']}

【收貨資訊】
收貨公司：信可美股份有限公司
地  址：新北市新莊區民安路207巷30弄8號1樓
電  話：02-8201-4393

--------------------------------------------------
【採購明細】
項次：1
品名規格：{item_name}
規    格：{specs} / 材質：51CrV4
公差規範 (DIN 2093)：
  - 外徑 OD: 0 ~ -0.25 mm
  - 內徑 ID: 0 ~ +0.21 mm
  - 厚度 t : +0.04 ~ -0.12 mm
  - 高度 Lo: +0.20 ~ -0.10 mm
數    量：{qty:,} PCS
單    價：RMB {unit_price:.2f}
金    額：RMB {total_amount:,.2f}
--------------------------------------------------

未稅總金額 (Total RMB)：RMB {total_amount:,.2f}

【採購注意事項與條款】
1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。
2. 公差必須於標準公差範圍內（DIN 2093）。
3. 順豐帳號：8860743308
4. 請做正式出口報關。
=================================================="""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(txt_content)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        file_bytes = f.read()

    st.success("🎉 採購單資料產生成功！")
    st.download_button(
        label="📥 點此下載採購單檔案 (.txt)",
        data=file_bytes,
        file_name=f"{po_no}.txt",
        mime="text/plain"
    )
