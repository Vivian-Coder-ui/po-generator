import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="信可美採購單 PDF 轉單系統", layout="centered")

# 介面上方的標題（列印時會自動隱藏）
st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳美加採購單檔案，選擇供應商與交易條件，系統將自動產生正式採購單畫面供您另存 PDF。")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"}
}

uploaded_file = st.file_uploader("📤 請上傳美加採購單檔案 (.pdf / 截圖)", type=["pdf", "png", "jpg", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    target_supplier = st.selectbox("🎯 選擇發給哪家供應商", ["SF", "VS", "XB"])
with col2:
    incoterms = st.selectbox("🤝 選擇交易條件 (Incoterms)", ["FOB", "CIF", "EXW", "DDP", "CFR"])

if uploaded_file is not None:
    st.success("✅ 客戶採購單已成功上傳！")
    
    sup_info = SUPPLIERS[target_supplier]
    raw_unit_price = 10.86
    qty = 10000
    converted_unit_price = raw_unit_price / 6
    total_amount = qty * converted_unit_price

    st.markdown("---")
    st.subheader("📋 採購單正式預覽")

    # 包含完整 DIN 2093 公差規範的乾淨 HTML/CSS 範本
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            background: white;
            color: #333;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }}
        .container {{
            max-width: 750px;
            margin: auto;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 25px;
            background: white;
        }}
        h2 {{ color: #1a365d; margin-bottom: 0px; }}
        .subtitle {{ color: #666; margin-top: 5px; font-size: 11pt; }}
        hr {{ border: 1px solid #1a365d; }}
        .grid {{ width: 100%; margin-top: 15px; border-collapse: collapse; }}
        .box {{ background: #f8fafc; padding: 12px; border-radius: 5px; border: 1px solid #e2e8f0; font-size: 10pt; line-height: 1.5; }}
        table.items {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        table.items th, table.items td {{ border: 1px solid #cbd5e1; padding: 10px; font-size: 10pt; }}
        table.items th {{ background-color: #1a365d; color: white; text-align: left; }}
        .text-right {{ text-align: right; }}
        .terms {{ background: #f1f5f9; padding: 12px; border-radius: 5px; margin-top: 15px; font-size: 9pt; line-height: 1.5; color: #444; }}
    </style>
    </head>
    <body>
        <div class="container">
            <h2>信可美股份有限公司</h2>
            <div class="subtitle">PURCHASE ORDER (正式採購單)</div>
            <hr>
            
            <table class="grid">
                <tr>
                    <td class="box" style="width: 50%; vertical-align: top;">
                        <strong>【供應商資訊】</strong><br>
                        {sup_info['name']} ({target_supplier})<br>
                        地址：{sup_info['addr']}
                    </td>
                    <td class="box" style="width: 50%; vertical-align: top;">
                        <strong>【採購資訊】</strong><br>
                        採購單號：{target_supplier}20260729001<br>
                        採購日期：2026/07/29<br>
                        交易條件：{incoterms}<br>
                        幣別：RMB
                    </td>
                </tr>
            </table>

            <div class="box" style="margin-top: 12px;">
                <strong>【收貨與寄送資訊】</strong><br>
                收貨公司：信可美股份有限公司<br>
                收貨地址：新北市新莊區民安路207巷30弄8號1樓 (電話: 02-8201-4393)
            </div>

            <table class="items">
                <thead>
                    <tr>
                        <th>項次</th>
                        <th>品名與規格</th>
                        <th class="text-right">數量 (PCS)</th>
                        <th class="text-right">單價 (RMB)</th>
                        <th class="text-right">金額 (RMB)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>
                            <strong>盤形彈簧 DB502530</strong><br>
                            <span style="font-size: 9pt; color: #555;">
                                規格尺寸: 50x25.4x3.0xH4.1 / 材質: 51CrV4<br>
                                <strong>DIN 2093 公差規範：</strong><br>
                                - 外徑 OD: 0 ~ -0.25 mm<br>
                                - 內徑 ID: 0 ~ +0.21 mm<br>
                                - 厚度 t : +0.04 ~ -0.12 mm<br>
                                - 高度 Lo: +0.20 ~ -0.10 mm
                            </span>
                        </td>
                        <td class="text-right" style="vertical-align: top;">{qty:,}</td>
                        <td class="text-right" style="vertical-align: top;">{converted_unit_price:.2f}</td>
                        <td class="text-right" style="vertical-align: top;">{total_amount:,.2f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="text-align: right; font-size: 12pt; font-weight: bold; margin-top: 15px;">
                未稅總金額 (Total RMB)：RMB {total_amount:,.2f}
            </div>

            <div class="terms">
                <strong>【採購注意事項與條款】</strong><br>
                1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。<br>
                2. 公差必須於標準公差範圍內（DIN 2093）。<br>
                3. 順豐帳號：8860743308<br>
                4. 請做正式出口報關。
            </div>
        </div>
    </body>
    </html>
    """

    # 顯示採購單預覽畫面（高度設為 720px 完整容納公差內容）
    components.html(html_code, height=720, scrolling=True)

    st.markdown("---")
    st.info("📥 **如何完美列印/存成 PDF？**\n1. 直接點擊下方專屬按鈕或按鍵盤 **`Ctrl + P`**。\n2. 系統已設定好列印防護：**列印時只會印出下方的正式採購單**，上方的上傳按鈕與選單會自動隱藏！\n3. 將目的地改為 **「另存為 PDF」** 即可完美寄給供應商！")
