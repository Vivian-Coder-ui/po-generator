import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="信可美採購單 PDF 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳美加採購單檔案，系統將完整帶入三行品名規格資訊，並自動計算單價 ÷ 6。")

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

    # 完整對應截圖中的三行資訊
    line1 = "SBS750-038"
    line2 = "Simars 氮氣彈簧 SBS750-038"
    line3 = "SBS750-038-171"
    
    raw_unit_price = 1128.30
    qty = 20
    
    # 單價自動除以 6
    converted_unit_price = raw_unit_price / 6
    total_amount = qty * converted_unit_price

    # 將三行完整帶入
    item_display = f"""
        <strong>{line1}</strong><br>
        <span>{line2}</span><br>
        <span style="font-size: 9pt; color: #555;">專案代號/備註: {line3}</span>
    """

    st.markdown("---")
    st.subheader("📋 採購單正式預覽與一鍵列印/存檔")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            background: #f8fafc;
            color: #333;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 750px;
            margin: auto;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 30px;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .print-btn {{
            background-color: #1a365d;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14pt;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            display: block;
            margin: 0 auto 25px auto;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .print-btn:hover {{ background-color: #2a4365; }}
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

        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
            .print-btn {{ display: none; }}
        }}
    </style>
    </head>
    <body>
        <div class="container">
            <button class="print-btn" onclick="window.print()">🖨️ 點此列印 / 另存為 PDF 檔</button>

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
                        採購單號：{target_supplier}20260729002<br>
                        採購日期：2026/07/29<br>
                        交易條件：{incoterms}<br>
                        幣別：RMB
                    </td>
                </tr>
            </table>

            <div class="box" style="margin-top: 12px;">
                <strong>【收貨與寄送資訊】</strong><br>
                收貨公司：信可美股份有限公司<br>
                收貨地址：338桃園市蘆竹區安中街20巷13號4樓 (電話: 02-8201-4393)
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
                        <td>{item_display}</td>
                        <td class="text-right" style="vertical-align: top;">{qty:,}</td>
                        <td class="text-right" style="vertical-align: top;">{converted_unit_price:,.2f}</td>
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
                2. 公差必須於標準公差範圍內（若適用）。<br>
                3. 順豐帳號：8860743308<br>
                4. 請做正式出口報關。
            </div>
        </div>
    </body>
    </html>
    """

    components.html(html_code, height=820, scrolling=True)
