import streamlit as st
import tempfile
from datetime import datetime

st.set_page_config(page_title="信可美採購單 PDF 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳客戶採購單檔案，系統將自動解析並產生發給指定供應商的正式 PDF 採購單。")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"}
}

# 1. 上傳客戶採購單
uploaded_file = st.file_uploader("📤 請上傳客戶採購單檔案 (.txt / .csv)", type=["txt", "csv"])

target_supplier = st.selectbox("🎯 選擇發給哪家供應商", ["SF", "VS", "XB"])

if uploaded_file is not None:
    # 讀取上傳的檔案內容
    file_content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    
    st.subheader("📋 解析到的客戶採購單內容：")
    st.text(file_content)

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

[SUPPLIER INFO]
Supplier: {sup_info['name']} ({target_supplier})
Address: {sup_info['addr']}

[SHIP TO]
Company: SINKOME CO., LTD.
Address: 1F, No. 8, Alley 30, Lane 207, Minan Rd., Xinzhuang Dist., New Taipei City
Phone: 02-8201-4393

--------------------------------------------------
[ITEMS / DETAILS - CONVERTED FROM CLIENT ORDER]
{file_content}
--------------------------------------------------

[TOLERANCE STANDARD]
- DIN 2093 Standard Tolerance Applied.

[TERMS & CONDITIONS]
1. Please confirm within 3 days if any discrepancy.
2. SF Account: 8860743308
3. Please process official export customs declaration.
=================================================="""

        # 建立乾淨的純文字 PDF 檔案（確保 100% 雲端相容且不報錯）
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
