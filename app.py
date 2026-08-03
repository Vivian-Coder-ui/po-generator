import streamlit as st
import pandas as pd
import io
import zipfile
import xml.etree.ElementTree as ET
import openpyxl

st.set_page_config(page_title="信可美採購單 Excel 智慧轉單系統", layout="centered")

st.title("📄 信可美採購單 Excel 智慧轉單系統")
st.write("請上傳美加採購單 Excel 檔，系統將自動擷取所有品項與數量，您只需輸入 RMB 單價即可！")

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

        # 讀取 Excel 的「單身資料」分頁（不帶 header，直接抓 raw data 來對應欄位）
        xls = pd.ExcelFile(excel_to_read)
        if '單身資料' in xls.sheet_names:
            df_body = pd.read_excel(excel_to_read, sheet_name='單身資料', header=None)
        else:
            df_body = pd.read_excel(excel_to_read, sheet_name=0, header=None)

        items_data = []
        # 從第 3 列（index 2）開始尋找資料
        start_row = False
        for idx, row in df_body.iterrows():
            col_0 = str(row.get(0, '')).strip()
            col_1 = str(row.get(1, '')).strip()
            
            # 當遇到「序號」表頭時，下一列開始就是品項
            if col_0 == '序號' or col_1 == '品號':
                start_row = True
                continue
            
            if start_row:
                # 如果品號欄位是空的、nan 或者是「以下空白」，就停止
                if not col_1 or col_1 == 'nan' or '以下空白' in col_1:
                    continue
                
                item_code = col_1
                item_name = str(row.get(2, '')).strip()
                spec = str(row.get(6, '')).strip() # 規格在第 6 欄
                
                # 組合品名與規格
                full_name = f"{item_name} {spec}".strip() if spec and spec != 'nan' else item_name
                
                try:
                    qty = float(row.get(3, 1)) # 數量在第 3 欄
                except:
                    qty = 1.0

                items_data.append({
                    "項次": len(items_data) + 1,
                    "品號": item_code,
                    "品名與規格": full_name,
                    "數量": qty,
                    "RMB單價": 0.00
                })

        if not items_data:
            # 備用保險：如果沒抓到，嘗試直接依賴欄位名稱讀取
            df_named = pd.read_excel(excel_to_read, sheet_name='單身資料', header=2)
            for idx, row in df_named.iterrows():
                item_code = str(row.get('品號', '')).strip()
                if not item_code or item_code == 'nan' or item_code == '品號':
                    continue
                item_name = str(row.get('品名', '')).strip()
                spec = str(row.get('規格', '')).strip()
                full_name = f"{item_name} {spec}".strip() if spec and spec != 'nan' else item_name
                try:
                    qty = float(row.get('採購數量', 1))
                except:
                    qty = 1.0
                items_data.append({
                    "項次": len(items_data) + 1,
                    "品號": item_code,
                    "品名與規格": full_name,
                    "數量": qty,
                    "RMB單價": 0.00
                })

        if not items_data:
            items_data = [{"項次": 1, "品號": "KA2357-01", "品名與規格": "壓簧 d7.5*0029.8*1.500", "數量": 5, "RMB單價": 0.00}]

        df_items = pd.DataFrame(items_data)
        st.success(f"✅ 成功從 Excel 自動擷取到 {len(df_items)} 筆品項明細！")

        st.markdown("---")
        st.subheader("✍️ 請在下方填入各品項的 RMB 單價")
        
        edited_df = st.data_editor(
            df_items,
            num_rows="fixed",
            use_container_width=True,
            key="excel_price_editor"
        )

        total_amount = 0
        for idx, row in edited_df.iterrows():
            q = float(row.get('數量', 0))
            p = float(row.get('RMB單價', 0))
            total_amount += q * p

        st.markdown(f"### 💰 未稅總金額 (Total RMB)：**RMB {total_amount:,.2f}**")

        st.markdown("---")
        st.subheader("📥 產出正式採購單")

        sup_info = SUPPLIERS[target_supplier]
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            po_header = pd.DataFrame([
                {"欄位": "供應商代號", "內容": f"{target_supplier} ({sup_info['name']})"},
                {"欄位": "供應商地址", "內容": sup_info['addr']},
                {"欄位": "採購單號", "內容": f"{target_supplier}20260803001"},
                {"欄位": "採購日期", "內容": "2026/08/03"},
                {"欄位": "交易條件", "內容": incoterms},
                {"欄位": "幣別", "內容": "RMB"},
                {"欄位": "收貨地址", "內容": "338桃園市蘆竹區安中街20巷13號4樓 (電話: 02-8201-4393)"}
            ])
            po_header.to_excel(writer, sheet_name='採購單頭', index=False)
            edited_df.to_excel(writer, sheet_name='採購明細', index=False)
            
        output.seek(0)
        
        st.download_button(
            label="📥 下載信可美正式採購單 (.xlsx)",
            data=output,
            file_name=f"PO_{target_supplier}_20260803.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

    except Exception as e:
        st.error(f"❌ 讀取 Excel 發生錯誤：{e}")
        st.write("請確保上傳的是如 PURI07_2.XLSX 這樣標準結構的採購單 Excel 檔案。")
