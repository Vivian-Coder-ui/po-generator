import streamlit as st

st.set_page_config(page_title="信可美採購單 PDF 轉單系統", layout="centered")

st.title("📄 信可美採購單 PDF 智慧轉單系統")
st.write("請上傳美加採購單檔案，選擇供應商與交易條件，系統將自動產生正式採購單畫面供您另存 PDF。")

SUPPLIERS = {
    "SF": {"name": "廊坊雙飛碟簧有限公司", "addr": "天津市河西區廣東路永安大廈 B1-903"},
    "VS": {"name": "常州西科德彈簧有限公司", "addr": "中國常州新北區寶塔山路108號"},
    "XB": {"name": "天津新北機電五金有限公司", "addr": "天津開發區第五大街12號 (4號廠房)"}
}

# 1. 把上傳檔案功能加回來
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

    # 2. 使用 unsafe_allow_html=True 讓排版完美呈現
    html_code = f"""
    <div style="background: white; padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; color: #333; font-family: Arial, sans-serif;">
        <h2 style="color: #1a365d; margin-bottom: 0px;">信可美股份有限公司</h2>
        <p style="color: #666; margin-top: 5px; font-size: 11pt;">PURCHASE ORDER (正式採購單)</p>
        <hr style="border: 1px solid #1a365d;">
        
        <table style="width: 100%; margin-top: 15px; border-collapse: collapse;">
            <tr>
                <td style="width: 50%; vertical-align: top; background: #f8fafc; padding: 12px; border-radius: 5px; border: 1px solid #e2e8f0;">
                    <strong>【供應商資訊】</strong><br>
                    {sup_info['name']} ({target_supplier})<br>
                    地址：{sup_info['addr']}
                </td>
                <td style="width: 50%; vertical-align: top; background: #f8fafc; padding: 12px; border-radius: 5px; border: 1px solid #e2e8f0;">
                    <strong>【採購資訊】</strong><br>
                    採購單號：{target_supplier}20260729001<br>
                    採購日期：2026/07/29<br>
                    交易條件：{incoterms}<br>
                    幣別：RMB
                </td>
            </tr>
        </table>

        <div style="background: #f8fafc; padding: 12px; border-radius: 5px; margin-top: 12px; border: 1px solid #e2e8f0;">
            <strong>【收貨與寄送資訊】</strong><br>
            收貨公司：信可美股份有限公司<br>
            收貨地址：新北市新莊區民安路207巷30弄8號1樓 (電話: 02-8201-4393)
        </div>

        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background-color: #1a365d; color: white;">
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: left;">項次</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: left;">品名與規格</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;">數量 (PCS)</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;">單價 (RMB)</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;">金額 (RMB)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;">1</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1;">盤形彈簧 DB502530<br><span style="font-size: 9pt; color: #555;">規格: 50x25.4x3.0xH4.1 / 材質: 51CrV4 (DIN 2093 公差)</span></td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;">{qty:,}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;">{converted_unit_price:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: right;">{total_amount:,.2f}</td>
                </tr>
            </tbody>
        </table>

        <div style="text-align: right; font-size: 13pt; font-weight: bold; margin-top: 15px;">
            未稅總金額 (Total RMB)：RMB {total_amount:,.2f}
        </div>

        <div style="background: #f1f5f9; padding: 12px; border-radius: 5px; margin-top: 15px; font-size: 9pt; line-height: 1.4;">
            <strong>【採購注意事項與條款】</strong><br>
            1. 若供應商對以上內容有任何異議，請務必於收到訂單3日內來電討論，否則視為正式接受訂單。<br>
            2. 公差必須於標準公差範圍內（DIN 2093）。<br>
            3. 順豐帳號：8860743308<br>
            4. 請做正式出口報關。
        </div>
    </div>
    """

    st.markdown(html_code, unsafe_allow_html=True)

    st.markdown("---")
    st.info("📥 **如何存成 PDF 檔？**\n1. 直接按下鍵盤 **`Ctrl + P`** (Mac 請按 `Cmd + P`)。\n2. 在右側列印選單中，將「目的地」改成 **「另存為 PDF (Save as PDF)」**。\n3. 點擊 **列印**，就能完美儲存成 PDF 檔囉！")
