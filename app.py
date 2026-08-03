import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="信可美採購單 PDF 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳最新的美加採購單檔案（截圖或 PDF），系統將透過 AI 自動判讀品號、品名與數量！")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"},
    "YX": {"name": "上海允新機械零部件有限公司", "addr": "上海市嘉定區菊園新區環城路2222號"},
    "EX": {"name": "毅骉智造新材料科技（太倉）有限公司", "addr": "江蘇省蘇州市太倉市陳門泾路69號11幢"}
}

uploaded_file = st.file_uploader("📤 請上傳美加採購單檔案 (.pdf / 截圖)", type=["pdf", "png", "jpg", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    target_supplier = st.selectbox("🎯 選擇發給哪家供應商", ["SF", "VS", "XB", "YX", "EX"])
with col2:
    incoterms = st.selectbox("🤝 選擇交易條件 (Incoterms)", ["FOB", "CIF", "EXW", "DDP", "CFR"])

items = []

if uploaded_file is not None:
    st.success("✅ 檔案已上傳，AI 正在自動判讀採購單明細...")
    
    try:
        # 使用內建 Gemini 模型進行圖片/文件辨識
        image = Image.open(uploaded_file)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = """
        請仔細辨識這張採購單圖片中的所有明細項目，並嚴格以 JSON 格式回傳一個包含清單的物件，不要包含其他多餘文字。
        格式如下：
        [
          {
            "line1": "品號 (例如 KA2357-01)",
            "line2": "品名與規格第一行 (例如 壓簧 d7.5*0029.8*1.500)",
            "line3": "備註或專案代號 (若無則留空字串)",
            "qty": 數量(數字)
          }
        ]
        """
        response = model.generate_content([image, prompt])
        
        # 解析 AI 回傳的 JSON 結果
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        items = json.loads(clean_text)
        st.success(f"🎉 AI 成功辨識出 {len(items)} 筆品項！")
        
    except Exception as e:
        # 若辨識失敗或上傳的是 PDF，提供預設備用解析避免當機
        st.warning("⚠️ 無法自動解析圖片，已自動載入預設帶入欄位。您也可以直接在下方輸入單價。")
        items = [
            {
                "line1": "KA2357-01",
                "line2": "壓簧 d7.5*0029.8*1.500",
                "line3": "",
                "qty": 5
            }
        ]

    # 手動輸入各品項單價區塊
    st.markdown("---")
    st.subheader("✍️ 手動輸入各品項 RMB 單價")

    manual_prices = []
    for idx, item in enumerate(items):
        p = st.number_input(
            f"項次 {idx+1}",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            key=f"price_{idx}"
        )
        manual_prices.append(p)

    sup_info = SUPPLIERS[target_supplier]
    table_rows_html = ""
    grand_total = 0

    for idx, item in enumerate(items):
        unit_price = manual_prices[idx]
        subtotal = item["qty"] * unit_price
        grand_total += subtotal

        line3_html = f"<br><span>{item['line3']}</span>" if item.get('line3') else ""

        table_rows_html += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #cbd5e1; vertical-align: top;">{idx+1}</td>
            <td style="padding: 10px; border: 1px solid #cbd5e1; vertical-align: top;">
                <strong>{item['line1']}</strong><br>
                <span>{item['line2']}</span>
                {line3_html}
            </td>
            <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; vertical-align: top;">{item['qty']:,}</td>
            <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; vertical-align: top;">{unit_price:,.2f}</td>
            <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; vertical-align: top;">{subtotal:,.2f}</td>
        </tr>
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
                        採購單號：{target_supplier}20260803001<br>
                        採購日期：2026/08/03<br>
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
                    {table_rows_html}
                </tbody>
            </table>

            <div style="text-align: right; font-size: 12pt; font-weight: bold; margin-top: 15px;">
                未稅總金額 (Total RMB)：RMB {grand_total:,.2f}
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

    components.html(html_code, height=950, scrolling=True)
