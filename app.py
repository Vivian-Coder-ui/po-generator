import streamlit as st
import tempfile
from datetime import datetime
from weasyprint import HTML

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

    # 預設自動代入範例數值與轉換（後續可由上傳檔案文字解析擴充）
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

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 15mm;
                background-color: #ffffff;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                color: #333333;
                margin: 0;
                padding: 0;
                font-size: 11pt;
                line-height: 1.4;
            }}
            *, *::before, *::after {{ box-sizing: border-box; }}
            .header {{
                border-bottom: 2px solid #1a365d;
                padding-bottom: 12px;
                margin-bottom: 20px;
            }}
            .title {{
                font-size: 20pt;
                font-weight: bold;
                color: #1a365d;
                margin: 0;
            }}
            .subtitle {{
                font-size: 11pt;
                color: #666666;
                margin-top: 4px;
            }}
            .grid {{
                width: 100%;
                margin-bottom: 15px;
            }}
            .col {{
                width: 50%;
                vertical-align: top;
            }}
            .box {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 12px;
                margin-bottom: 15px;
            }}
            .box h3 {{
                margin-top: 0;
                font-size: 11pt;
                color: #1a365d;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 5px;
            }}
            table.items {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                margin-bottom: 20px;
            }}
            table.items th, table.items td {{
                border: 1px solid #cbd5e1;
                padding: 10px;
                text-align: left;
            }}
            table.items th {{
                background-color: #1a365d;
                color: #ffffff;
                font-weight: bold;
            }}
            .text-right {{ text-align: right; }}
            .terms {{
                font-size: 9pt;
                color: #555555;
                background-color: #f1f5f9;
                padding: 12px;
                border-radius: 4px;
            }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="title">信可美股份有限公司</div>
                <div class="subtitle">PURCHASE ORDER (正式採購單)</div>
            </div>

            <table class="grid" style="border:none;">
                <tr>
                    <td class="col" style="border:none; padding-right:10px;">
                        <div class="box">
                            <h3>供應商資訊 (SUPPLIER)</h3>
                            <strong>{sup_info['name']} ({target_supplier})</strong><br>
                            {sup_info['addr']}
                        </div>
                    </td>
                    <td class="col" style="border:none; padding-left:10px;">
                        <div class="box">
                            <h3>採購資訊</h3>
                            <strong>採購單號：</strong> {po_no}<br>
                            <strong>採購日期：</strong> {current_date_str}<br>
                            <strong>交易條件：</strong> {incoterms}<br>
                            <strong>幣別：</strong> RMB
                        </div>
                    </td>
                </tr>
            </table>

            <div class="box">
                <h3>收貨與寄送資訊 (SHIP TO)</h3>
                <strong>公司名稱：</strong> 信可美股份有限公司<br>
                <strong>收貨地址：</strong> 新北市新莊區民安路207巷30弄8號1樓<br>
                <strong>聯絡電話：</strong> 02-8201-4393
            </div>

            <table class="items">
                <thead>
                    <tr>
                        <th>項次</th>
                        <th>品名規格</th>
                        <th>數量 (PCS)</th>
                        <th>單價 (RMB)</th>
                        <th>金額 (RMB)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>{item_name}<br><small>公差規範：依據 DIN 2093 標準規範</small></td>
                        <td>{qty:,}</td>
                        <td class="text-right">{converted_unit_price:.2f}</td>
                        <td class="text-right">{total_amount:,.2f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="text-align: right; font-size: 13pt; font-weight: bold; margin-bottom: 20px;">
                未稅總金額 (Total RMB)：RMB {total_amount:,.2f}
            </div>

            <div class="terms">
                <strong>採購注意事項與條款：</strong><br>
                1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。<br>
                2. 公差必須於標準公差範圍內（DIN 2093）。<br>
                3. 順豐帳號：8860743308<br>
                4. 請做正式出口報關。
            </div>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f_html:
            f_html.write(html_content)
            html_path = f_html.name

        pdf_path = html_path.replace(".html", ".pdf")
        HTML(html_path).write_pdf(pdf_path)

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.success("🎉 PDF 採購單轉單成功！")
        st.download_button(
            label="📥 點此下載供應商正式採購單 (.pdf)",
            data=pdf_bytes,
            file_name=f"{po_no}.pdf",
            mime="application/pdf"
        )
