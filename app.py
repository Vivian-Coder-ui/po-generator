import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import zipfile
import xml.etree.ElementTree as ET

st.set_page_config(page_title="信可美採購單 Excel 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 Excel 智慧轉單系統")
st.write("請上傳美加採購單 Excel 檔，系統將自動擷取所有品項、數量與採購單號，設定相關資訊後即可預覽並列印正式採購單！")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"},
    "YX": {"name": "上海允新機械零部件有限公司", "addr": "上海市嘉定區菊園新區環城路2222號"},
    "EX": {"name": "毅骉智造新材料科技（太倉）有限公司", "addr": "江蘇省蘇州市太倉市陳門泾路69號11幢"}
}

SHIPPING_ADDRESSES = {
    "桃園蘆竹倉": {
        "company": "信可美股份有限公司",
        "address": "338桃園市蘆竹區安中街20巷13號4樓",
        "phone": "02-8201-4393"
    },
    "宜蘭蘇澳廠": {
        "company": "信可美股份有限公司 (蘇澳廠)",
        "address": "27048宜蘭縣蘇澳鎮中山路二段417號",
        "phone": "03-959-6641"
    }
}


def extract_po_number(xls):
    """從『單頭資料』分頁抓取採購單號（若欄位名稱是『採購單號』的表頭，取其下一列同欄位的值）。"""
    try:
        if '單頭資料' not in xls.sheet_names:
            return None
        df_header = pd.read_excel(xls, sheet_name='單頭資料', header=None)
        for idx in range(len(df_header)):
            row_vals = [str(v).strip() for v in df_header.iloc[idx].tolist()]
            if '採購單號' in row_vals:
                col_idx = row_vals.index('採購單號')
                if idx + 1 < len(df_header):
                    val = df_header.iloc[idx + 1, col_idx]
                    if pd.notna(val) and str(val).strip():
                        return str(val).strip()
    except Exception:
        pass
    return None


def parse_items_generic(df):
    """
    依欄位『名稱』（而非欄位位置）解析品項，因此不管範本欄位順序如何排列都能正確擷取。
    支援的欄位名稱：
      品號代碼: 品號
      名稱:     品名 (可省略)
      規格:     規格 (可省略)
      數量:     採購數量 或 數量
    """
    header_row_idx = None
    col_map = {}

    for idx in range(len(df)):
        row_vals = [str(v).strip() for v in df.iloc[idx].tolist()]
        if '品號' in row_vals:
            header_row_idx = idx
            for j, v in enumerate(row_vals):
                if v and v != 'nan' and v not in col_map:
                    col_map[v] = j
            break

    if header_row_idx is None:
        return []

    def find_col(candidates):
        for c in candidates:
            if c in col_map:
                return col_map[c]
        return None

    code_col = find_col(['品號'])
    name_col = find_col(['品名'])
    spec_col = find_col(['規格'])
    qty_col = find_col(['採購數量', '數量'])

    items = []
    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]

        code_val = row[code_col] if code_col is not None and code_col < len(row) else None
        code_str = str(code_val).strip() if pd.notna(code_val) else ''
        if not code_str or code_str == 'nan' or '以下空白' in code_str:
            continue

        name_str = ''
        if name_col is not None and name_col < len(row) and pd.notna(row[name_col]):
            name_str = str(row[name_col]).strip()
            if name_str == 'nan':
                name_str = ''

        spec_str = ''
        if spec_col is not None and spec_col < len(row) and pd.notna(row[spec_col]):
            spec_str = str(row[spec_col]).strip()
            if spec_str == 'nan':
                spec_str = ''

        full_name = f"{name_str} {spec_str}".strip()
        if not full_name:
            full_name = code_str  # 沒有品名/規格欄位時，至少不要留空白

        qty = 1.0
        if qty_col is not None and qty_col < len(row) and pd.notna(row[qty_col]):
            try:
                qty = float(row[qty_col])
            except Exception:
                qty = 1.0

        items.append({
            "項次": len(items) + 1,
            "品號": code_str,
            "品名與規格": full_name,
            "數量": int(qty),
            "RMB單價": 0.00
        })

    return items


uploaded_file = st.file_uploader("📤 請上傳美加採購單 Excel 檔 (.xlsx)", type=["xlsx", "xls"])

col1, col2, col3 = st.columns(3)
with col1:
    target_supplier = st.selectbox("🎯 選擇發給哪家供應商", ["SF", "VS", "XB", "YX", "EX"])
with col2:
    incoterms = st.selectbox("🤝 選擇交易條件 (Incoterms)", ["FOB", "CIF", "EXW", "DDP", "CFR"])
with col3:
    shipping_choice = st.selectbox("📍 選擇收貨地址", list(SHIPPING_ADDRESSES.keys()))

delivery_date = st.text_input("📅 輸入交期 (Delivery Date)", value="2026/09/15")

items_data = []
po_number_from_file = None
po_date_default = "2026/08/03"

if uploaded_file is not None:
    try:
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

        xls = pd.ExcelFile(excel_to_read)

        # 抓採購單號
        po_number_from_file = extract_po_number(xls)

        # 抓品項明細（依欄位名稱通用比對，不再依賴欄位位置）
        if '單身資料' in xls.sheet_names:
            df_body = pd.read_excel(xls, sheet_name='單身資料', header=None)
        else:
            df_body = pd.read_excel(xls, sheet_name=0, header=None)

        items_data = parse_items_generic(df_body)

        if not items_data:
            items_data = [{"項次": 1, "品號": "KA2357-01", "品名與規格": "壓簧 d7.5*0029.8*1.500", "數量": 5, "RMB單價": 0.00}]

        if po_number_from_file:
            st.success(f"✅ 成功擷取到 {len(items_data)} 筆品項明細，採購單號：{po_number_from_file}")
        else:
            st.warning(f"⚠️ 成功擷取到 {len(items_data)} 筆品項明細，但未在「單頭資料」找到採購單號，將使用預設值。")

    except Exception as e:
        st.error(f"❌ 讀取 Excel 發生錯誤：{e}")
        items_data = [{"項次": 1, "品號": "KA2357-01", "品名與規格": "壓簧 d7.5*0029.8*1.500", "數量": 5, "RMB單價": 0.00}]

else:
    items_data = [
        {"項次": 1, "品號": "DB502530*", "品名與規格": "盤形彈簧 DB502530* 50x25.4x3.0xH4.2", "數量": 500000, "RMB單價": 14.70}
    ]

st.markdown("---")

# 採購單號 / 採購日期：若從檔案抓到就預帶入，仍可手動覆寫
col_po1, col_po2 = st.columns(2)
with col_po1:
    po_number = st.text_input("🔢 採購單號", value=po_number_from_file or "20260803001")
with col_po2:
    po_date = st.text_input("📅 採購日期", value=po_date_default)

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

st.markdown("---")
additional_remark = st.text_area("📝 輸入其他備註事項 (選填，將顯示於未稅金額下方)", value="")

sup_info = SUPPLIERS[target_supplier]
ship_info = SHIPPING_ADDRESSES[shipping_choice]

table_rows_html = ""
grand_total = 0

for idx, item in enumerate(items_data):
    unit_price = manual_prices[idx]
    qty = item["數量"]
    subtotal = qty * unit_price
    grand_total += subtotal

    table_rows_html += f"""
    <tr>
        <td style="padding: 10px; border: none; border-bottom: 1px solid #e2e8f0; vertical-align: top;">{idx+1}</td>
        <td style="padding: 10px; border: none; border-bottom: 1px solid #e2e8f0; vertical-align: top;">
            <strong>{item['品號']}</strong><br>
            <span>{item['品名與規格']}</span>
        </td>
        <td style="padding: 10px; border: none; border-bottom: 1px solid #e2e8f0; text-align: right; vertical-align: top;">{qty:,}</td>
        <td style="padding: 10px; border: none; border-bottom: 1px solid #e2e8f0; text-align: right; vertical-align: top;">{unit_price:,.2f}</td>
        <td style="padding: 10px; border: none; border-bottom: 1px solid #e2e8f0; text-align: right; vertical-align: top;">{subtotal:,.2f}</td>
    </tr>
    """

additional_remark_html = f"""
<div style="margin-top: 12px; padding: 12px; background: #fffbeb; border: none; border-radius: 5px; font-size: 10pt; color: #92400e; white-space: pre-wrap; word-break: break-word; text-align: justify; text-justify: inter-ideograph;">
    <strong>備註說明：</strong><br>{additional_remark}
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
    @page {{
        size: A4;
        margin: 10mm 12mm;
    }}
    body {{
        background: #f8fafc;
        color: #333;
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        font-size: 10pt;
    }}
    .container {{
        max-width: 850px;
        width: 100%;
        min-height: 255mm;
        margin: auto;
        border: none;
        padding: 20px;
        background: white;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
    h2 {{ color: #1a365d; margin: 0 0 5px 0; font-size: 18pt; }}
    .subtitle {{ color: #666; margin-bottom: 10px; font-size: 11pt; }}
    hr {{ border: none; border-top: 1px solid #1a365d; margin: 10px 0; }}
    .grid {{ width: 100%; margin-top: 12px; border-collapse: collapse; border: none; }}
    .box {{ background: #f8fafc; padding: 12px; border-radius: 5px; border: none; font-size: 10pt; line-height: 1.6; }}

    table.items {{ width: 100%; border-collapse: collapse; margin-top: 15px; border: none; }}
    table.items th, table.items td {{ border: none; padding: 10px; font-size: 10pt; }}
    table.items th {{ background-color: #1a365d; color: white; text-align: left; border: none; padding: 10px; }}
    table.items tr {{ border-bottom: 1px solid #e2e8f0; }}

    .text-right {{ text-align: right; }}

    .terms {{
        background: #f1f5f9;
        padding: 12px;
        border-radius: 5px;
        margin-top: 15px;
        font-size: 9pt;
        line-height: 1.5;
        color: #444;
        border: none;
        text-align: justify;
        text-justify: inter-ideograph;
    }}

    .signature-container {{
        display: flex;
        justify-content: space-between;
        margin-top: 20px;
        width: 100%;
    }}
    .signature-cell {{
        width: 46%;
        border: none;
        padding: 10px;
        background: #fff;
        height: 70px;
        font-size: 10pt;
    }}

    @media print {{
        body {{ background: white; padding: 0; }}
        .container {{ border: none; box-shadow: none; padding: 0; width: 100%; max-width: 100%; min-height: 275mm; }}
        .print-btn {{ display: none; }}
    }}
</style>
</head>
<body>
    <div class="container">
        <div>
            <button class="print-btn" onclick="window.print()">🖨️ 點此列印 / 另存為單頁 A4 PDF</button>

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
                        採購單號：{target_supplier}{po_number}<br>
                        採購日期：{po_date}<br>
                        交期：{delivery_date}<br>
                        交易條件：{incoterms}<br>
                        幣別：RMB
                    </td>
                </tr>
            </table>

            <div class="box" style="margin-top: 10px; line-height: 1.6;">
                <strong>【收貨與寄送資訊】</strong><br>
                收貨公司：{ship_info['company']}<br>
                收貨地址：{ship_info['address']} (電話: {ship_info['phone']})
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

            {additional_remark_html}

            <div class="terms">
                <strong>【採購注意事項與條款】</strong><br>
                1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。<br>
                2. 公差必須於標準公差範圍內（若適用）。<br>
                3. 順豐帳號：8860743308 ｜ 4. 請做正式出口報關。
            </div>
        </div>

        <div class="signature-container">
            <div class="signature-cell">
                <strong>供應商簽名</strong><br><br>
                簽章：___________________________
            </div>
            <div class="signature-cell">
                <strong>信可美簽名</strong><br><br>
                簽章：___________________________
            </div>
        </div>
    </div>
</body>
</html>
"""

components.html(html_code, height=950, scrolling=True)
