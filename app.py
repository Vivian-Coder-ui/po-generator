import streamlit as st
import tempfile
from datetime import datetime

st.set_page_config(page_title="信可美採購單 PDF 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳美加採購單截圖，輸入原始單價，系統將自動除以 6 計算並產生正式 PDF 採購單。")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"}
}

# 1. 上傳客戶採購單截圖
uploaded_image = st.file_uploader("📤 請上傳客戶採購單截圖 (.png / .jpg / .jpeg)", type=["png", "jpg", "jpeg"])

# 2. 選擇供應商、交易條件與輸入原始單價、數量
col1, col2 = st.columns(2)
with col1:
    target_supplier = st.selectbox("🎯 選擇發給哪家供應商", ["SF", "VS", "XB"])
with col2:
    incoterms = st.selectbox("🤝 選擇交易條件 (Incoterms)", ["FOB", "CIF", "EXW", "DDP", "CFR"])

col3, col4 = st.columns(2)
with col3:
    raw_unit_price = st.number_input("💰 客戶單價 (原價)", value=10.86, format="%.2f")
with col4:
    qty = st.number_input("📦 採購數量 (PCS)", value=10000, step=1)

# 自動將單價除以 6
converted_unit_price = raw_unit_price / 6
total_amount = qty * converted_unit_price

if uploaded_image is not None:
    # 顯示上傳的截圖預覽
    st.image(uploaded_image, caption="已上傳的客戶採購單截圖", use_container_width=True)

    st.write(f"💡 **換算結果**：原價 {raw_unit_price:.2f} ÷ 6 = 供應商單價 **RMB {converted_unit_price:.2f}** (總金額：RMB {total_amount:,.2f})")

    if st.button("🚀 自動轉換並產生 PDF 採購單"):
        today_str = datetime.now().strftime("%Y%m%d")
        po_no = f"{target_supplier}{today_str}001"
        sup_info = SUPPLIERS[target_supplier]

        # 產生格式化的採購單文字內容作為 PDF 內文
        pdf_content = f"""SINKOME CO., LTD. PURCHASE ORDER
==================================================
PO Number: {po_no}
Date: {datetime.now().strftime("%Y/%m/%d")}
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
- Converted based on client PO screenshot.
- Quantity: {qty:,} PCS
- Unit Price (Raw / 6): RMB {converted_unit_price:.2f}
- Total Amount: RMB {total_amount:,.2f}
--------------------------------------------------

[TOLERANCE STANDARD]
- DIN 2093 Standard Tolerance Applied.

[TERMS & CONDITIONS]
1. Please confirm within 3 days if any discrepancy.
2. SF Account: 8860743308
3. Please process official export customs declaration.
=================================================="""

        # 建立純文字 PDF 檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode="w", encoding="utf-8") as tmp:
            tmp.write(pdf_content)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()

        st.success("🎉 PDF 採購單轉單成功！")
        st.download_button(
            label="📥 點此下載供應商採購單 (.pdf)",
            data=pdf_bytes,
            file_name=f"{po_no}.pdf",
            mime="application/pdf"
        )
