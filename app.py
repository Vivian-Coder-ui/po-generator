import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import zipfile
import xml.etree.ElementTree as ET
import openpyxl

st.set_page_config(page_title="信可美採購單 Excel 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 Excel 智慧轉單系統")
st.write("請上傳美加採購單 Excel 檔，系統將自動擷取所有品項與數量，輸入單價與相關資訊後即可預覽並列印正式採購單！")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"},
    "YX": {"name": "上海允新機械零部件有限公司", "addr": "上海市嘉定區菊園新區環城路2222號"},
    "EX": {"name": "毅骉智造新材料科技（太倉）有限公司", "addr": "江蘇省蘇州市太倉市陳門泾路69號11幢"}
}

uploaded_file = st.file_uploader("📤 請上傳美加採購單 Excel 檔 (.xlsx)", type=["xlsx", "xls"])

col1, col2 = st.columns(2)
with col1:
    target_supplier = st.selectbox("🎯 選擇發給哪家供應商", ["SF", "VS", "XB", "YX", "EX"])
with col2:
    incoterms = st.selectbox("🤝 選擇交易條件 (Incoterms)", ["FOB", "CIF", "EXW", "DDP", "CFR"])

# 1. 採購資訊新增「交期」欄位讓使用者填寫
delivery_date = st.text_input("📅 輸入交期 (Delivery Date)", value="2026/09/15")

items_data = []

if uploaded_file is not None:
    try:
        # 自動修復 openpyxl 讀取美加 Excel 常見的 NamedCellStyle 錯誤
        file_bytes = uploaded_file.read()
        fixed_io = io.BytesIO()
        
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zin:
                with zipfile.ZipFile(fixed_io, 'w') as zout:
                    for item in zin.infolist():
                        buffer = zin.read(item.filename)
                        if item.filename == 'xl/styles.xml':
                            root = ET.fromstring(buffer)
                            for elem in root.iter():
                                if elem.tag.endswith('cellStyle') and ('name' not in elem.attrib or not elem.attrib['name']):
                                    elem.attrib['name'] = 'Normal'
                            buffer = ET.tostring(root)
                        zout.writestr(item, buffer)
            fixed_io.seek(0)
            excel_to_read = fixed_io
        except Exception:
            fixed_io.seek(0)
            file_bytes_io = io.BytesIO(file_bytes)
            file_bytes_io.seek(0)
            excel_to_read = file_bytes_io

        # 讀取 Excel 的「單身資料」分頁
        xls = pd.ExcelFile(excel_to_read)
        if '單身資料' in xls.sheet_names:
            df_body = pd.read_excel(excel_to_read, sheet_name='單身資料', header=None)
        else:
            df_body = pd.read_excel(excel_to_read, sheet_name=0, header=None)

        start_row = False
        for idx, row in df_body.iterrows():
            col_0 = str(row.get(0, '')).strip()
            col_1 = str(row.get(1, '')).strip()
            
            if col_0 == '序號' or col_1 == '品號':
                start_row = True
                continue
            
            if start_row:
                if not col_1 or col_1 == 'nan' or '以下空白' in col_1:
                    continue
                
                item_code = col_1
                item_name = str(row.get(2, '')).strip()
                spec = str(row.get(3, '')).strip()  # 欄位 D (索引 3) 為規格
                full_name = f"{item_name} {spec}".strip() if spec and spec != 'nan' else item_name
                
                remark = str(row.get(6, '')).strip()  # 欄位 G (索引 6) 為備註
                if remark == 'nan':
                    remark = ""

                try:
                    qty = float(row.get(4, 1))  # 欄位 E (索引 4) 為數量
                except:
                    qty = 1.0

                items_data.append({
                    "項次": len(items_data) + 1,
                    "品號": item_code,
                    "品名與規格": full_name,
                    "數量": int(qty),
                    "RMB單價": 0.00,
                    "備註": remark
                })

        if not items_data:
            df_named = pd.read_excel(excel_to_read, sheet_name='單身資料', header=2)
            for idx, row in df_named.iterrows():
                item_code = str(row.get('品號', '')).strip()
                if not item_code or item_code == 'nan' or item_code == '品號':
                    continue
                item_name = str(row.get('品名', '')).strip()
                spec = str(row.get('規格', '')).strip()
                full_name = f"{item_name} {spec}".strip() if spec and spec != 'nan' else item_name
                
                remark = str(row.get('備註', '')).strip()
                if remark == 'nan':
                    remark = ""

                try:
                    qty = float(row.get('採購數量', 1))
                except:
                    qty = 1.0
                items_data.append({
                    "項次": len(items_data) + 1,
                    "品號": item_code,
                    "品名與規格": full_name,
                    "數量": int(qty),
                    "RMB單價": 0.00,
                    "備註": remark
                })

        if not items_data:
            items_data = [{"項次": 1, "品號": "KA2357-01", "品名與規格": "壓簧 d7.5*0029.8*1.500", "數量": 5, "RMB單價": 0.00, "備註": ""}]

        st.success(f"✅ 成功從 Excel 自動擷取到 {len(items_data)} 筆品項明細！")

    except Exception as e:
        st.error(f"❌ 讀取 Excel 發生錯誤：{e}")
        items_data = [{"項次": 1, "品號": "KA2357-01", "品名與規格": "壓簧 d7.5*0029.8*1.500", "數量": 5, "RMB單價": 0.00, "備註": ""}]

else:
    # 預設示範資料
    items_data = [
        {"項次": 1, "品號": "DB502530*", "品名與規格": "盤形彈簧 DB502530* 50x25.4x3.0xH4.2", "數量": 500000, "RMB單價": 14.70, "備註": "此批公差:OD/-0.25 ID20.27~20.46 T+0.09/-0.12 H+0.3"}
    ]

st.markdown("---")
st.subheader("✍️ 輸入各品項 RMB 單價")

manual_prices = []
for idx, item in enumerate(items_data):
    st.markdown(f"**【項次 {idx+1}】** 品號: `{item['品號']}` | 品名: `{item['品名與規格']}` | 數量: **{item['數量']:,} PCS**")
    price = st.number_input(
        f"請輸入項次 {idx+1} 的 RMB 單價",
        min_value=0.0,
        value=float(item.get('RMB單價', 0.0)),
        step=0.01,
        format="%.2f",
        key=f"price_{idx}"
    )
    manual_prices.append(price)
    st.markdown("")

# 2. 未稅總金額下方新增「其他備註」欄位讓使用者填寫
st.markdown("---")
additional_remark = st.text_area("📝 輸入其他備註事項 (選填，將顯示於未稅金額下方)", value="")

sup_info = SUPPLIERS[target_supplier]
table_rows_html = ""
grand_total = 0

for idx, item in enumerate(items_data):
    unit_price = manual_prices[idx]
    qty = item["數量"]
    subtotal = qty * unit_price
    grand_total += subtotal
    remark = item.get("備註", "")

    table_rows_html += f"""
    <tr>
        <td style="padding: 10px; border: 1px solid #cbd5e1; vertical-align: top;">{idx+1}</td>
        <td style="padding: 10px; border: 1px solid #cbd5e1; vertical-align: top;">
            <strong>{item['品號']}</strong><br>
            <span>{item['品名與規格']}</span>
        </td>
        <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; vertical-align: top;">{qty:,}</td>
        <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; vertical-align: top;">{unit_price:,.2f}</td>
        <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right; vertical-align: top;">{subtotal:,.2f}</td>
        <td style="padding: 10px; border: 1px solid #cbd5e1; vertical-align: top; font-size: 9pt;">{remark}</td>
    </tr>
    """

# 組合其他備註的 HTML 區塊
additional_remark_html = f"""
<div style="margin-top: 10px; padding: 10px; background: #fffbeb; border: 1px solid #fef3c7; border-radius: 5px; font-size: 10pt; color: #92400e;">
    <strong>備註說明：</strong> {additional_remark.replace(chr(10), '<br>')}
</div>
""" if additional_remark.strip() != "" else ""

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
        max-width: 850px;
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
    .signature-table {{ width: 100%; margin-top: 30px; border-collapse: collapse; }}
    .signature-box {{ width: 48%; border: 1px solid #cbd5e1; border-radius: 6px; padding: 15px; vertical-align: top; background: #fff; height: 90px; }}

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
                    交期：{delivery_date}<br>
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
                    <th>備註</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>

        <div style="text-align: right; font-size: 12pt; font-weight: bold; margin-top: 15px;">
            未稅總金額 (Total RMB)：RMB {grand_total:,.2f}
        </div>

        {additional_remark_html}

        <div class="terms">
            <strong>【採購注意事項與條款】</strong><br>
            1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。<br>
            2. 公差必須於標準公差範圍內（若適用）。<br>
            3. 順豐帳號：8860743308<br>
            4. 請做正式出口報關。
        </div>

        <!-- 3. 最底下新增簽名欄位 (左：供應商 / 右：信可美) -->
        <table class="signature-table">
            <tr>
                <td class="signature-box" style="float: left;">
                    <strong>【供應商簽名確認】</strong><br><br><br>
                    簽章：___________________________
                </td>
                <td style="width: 4%;"></td>
                <td class="signature-box" style="float: right;">
                    <strong>【信可美股份有限公司】</strong><br><br><br>
                    採購核准：_______________________
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
"""

components.html(html_code, height=1050, scrolling=True)
