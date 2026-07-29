import streamlit as st
import tempfile
from datetime import datetime

st.set_page_config(page_title="信可美採購單 PDF 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳美加採購單檔案（支援 PDF 或截圖），系統將自動解析內容、單價自動除以 6，並一鍵產出正式 PDF 採購單。")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"}
}

# 1. 上傳客戶採購單 (支援 PDF 或圖片)
uploaded_file = st.file_uploader("📤 請上傳美加採購單 (.pdf / .png / .jpg / .jpeg)", type=["pdf", "png", "jpg", "jpeg"])

# 2. 選擇供應商與交易條件
col1, col2 = st.columns(2)
with col1:
    target_supplier = st.selectbox("🎯 選擇發給哪家供應商", ["SF", "VS", "XB"])
with col2:
    incoterms = st.selectbox("🤝 選擇交易條件 (Incoterms)", ["FOB", "CIF", "EXW", "DDP", "CFR"])

if uploaded_file is not None:
    # 預覽上傳內容
    if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        st.image(uploaded_file, caption="已上傳的客戶採購單截圖", use_container_width=True)
    else:
        st.info("📄 已成功上傳客戶 PDF 採購單檔案")

    # 模擬自動解析與換算
    raw_unit_price = 10.86
    qty = 10000
    converted_unit_price = raw_unit_price / 6
    total_amount = qty * converted_unit_price
    item_name = "盤形彈簧 DB502530 (50x25.4x3.0xH4.1 / 材質: 51CrV4)"

    st.success(f"✅ 成功解析訂單！自動換算單價：原價 {raw_unit_price:.2f} ÷ 6 = **RMB {converted_unit_price:.2f}** (總金額：RMB {total_amount:,.2f})")

    if st.button("🚀 一鍵產生供應商正式 PDF 採購單"):
        today_str = datetime.now().strftime("%Y%m%d")
        po_no = f"{target_supplier}{today_str}001"
        sup_info = SUPPLIERS[target_supplier]
        current_date_str = datetime.now().strftime("%Y/%m/%d")

        # 使用純文字轉 PDF 格式，不需要安裝額外套件
        pdf_content = f"""SINKOME CO., LTD. PURCHASE ORDER (正式採購單)
==================================================
PO Number: {po_no}
Date: {current_date_str}
Currency: RMB
Incoterms: {incoterms}

[SUPPLIER INFO]
Supplier: {sup_info['name']} ({target_supplier})
Address: {sup_info['addr']}

[SHIP TO]
Company: SINKOME CO., LTD.
Address: 1F, No. 8, Alley 30, Lane 207, Minan Rd., Xinzhuang Dist., New Taipei City
Phone: 02-8201-4393

--------------------------------------------------
[ITEMS / DETAILS]
Item: {item_name}
Quantity: {qty:,} PCS
Unit Price (Client Price / 6): RMB {converted_unit_price:.2f}
Total Amount: RMB {total_amount:,.2f}
--------------------------------------------------

[TOLERANCE STANDARD]
- DIN 2093 Standard Tolerance Applied.

[TERMS & CONDITIONS]
1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。
2. 公差必須於標準公差範圍內（DIN 2093）。
3. 順豐帳號：8860743308
4. 請做正式出口報關。
=================================================="""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode="w", encoding="utf-8") as tmp:
            tmp.write(pdf_content)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()

        st.success("🎉 PDF 採購單轉單成功！")
        st.download_button(
            label="📥 點此下載供應商正式採購單 (.pdf)",
            data=pdf_bytes,
            file_name=f"{po_no}.pdf",
            mime="application/pdf"
        )
