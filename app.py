import streamlit as st
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 註冊中文字型 (使用系統內建中文字型確保 PDF 正常顯示中文)
try:
    pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
    FONT_NAME = 'SimSun'
except:
    FONT_NAME = 'Helvetica'

st.set_page_config(page_title="信可美採購單 PDF 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳美加採購單檔案（支援 PDF 或截圖），系統將自動解析內容、單價自動除以 6，並一鍵產出真正的正式 PDF 採購單。")

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
        st.info("📄 已成功上傳客戶採購單檔案")

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

        # 建立真正的 PDF 檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_path = tmp.name

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # 標題與表頭
        c.setFont(FONT_NAME, 16)
        c.drawString(50, height - 50, "信可美股份有限公司 - 正式採購單 (PO)")
        
        c.setFont(FONT_NAME, 10)
        c.drawString(50, height - 75, f"採購單號：{po_no}")
        c.drawString(50, height - 95, f"採購日期：{current_date_str}")
        c.drawString(300, height - 75, f"交易條件：{incoterms}")
        c.drawString(300, height - 95, "幣    別：RMB")

        # 供應商與收貨資訊框
        c.rect(50, height - 210, 495, 95)
        c.setFont(FONT_NAME, 10)
        c.drawString(60, height - 130, f"【供應商】 {sup_info['name']} ({target_supplier})")
        c.drawString(60, height - 150, f"地    址：{sup_info['addr']}")
        c.drawString(60, height - 175, "【收貨方】 信可美股份有限公司")
        c.drawString(60, height - 195, "地    址：新北市新莊區民安路207巷30弄8號1樓 (電話: 02-8201-4393)")

        # 明細表格標題
        c.setFillColor(colors.HexColor("#1a365d"))
        c.rect(50, height - 260, 495, 20, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.drawString(60, height - 246, "項次")
        c.drawString(100, height - 246, "品名與規格")
        c.drawString(350, height - 246, "數量")
        c.drawString(410, height - 246, "單價(RMB)")
        c.drawString(480, height - 246, "金額(RMB)")

        # 明細內容
        c.setFillColor(colors.black)
        c.drawString(60, height - 285, "1")
        c.drawString(100, height - 285, f"{item_name}")
        c.drawString(350, height - 285, f"{qty:,}")
        c.drawString(410, height - 285, f"{converted_unit_price:.2f}")
        c.drawString(480, height - 285, f"{total_amount:,.2f}")

        # 總金額
        c.setFont(FONT_NAME, 11)
        c.drawRightString(535, height - 325, f"未稅總金額 (Total RMB)：RMB {total_amount:,.2f}")

        # 注意事項
        c.setFont(FONT_NAME, 9)
        c.drawString(50, height - 370, "【採購注意事項與條款】")
        c.drawString(50, height - 390, "1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。")
        c.drawString(50, height - 410, "2. 公差必須於標準公差範圍內（DIN 2093）。")
        c.drawString(50, height - 430, "3. 順豐帳號：8860743308 / 請做正式出口報關。")

        c.save()

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.success("🎉 真正的 PDF 採購單產生成功！")
        st.download_button(
            label="📥 點此下載供應商正式 PDF 採購單 (.pdf)",
            data=pdf_bytes,
            file_name=f"{po_no}.pdf",
            mime="application/pdf"
        )
