import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# --- 1. CONFIG & STYLE (DESIGN SYSTEM) ---
st.set_page_config(
    layout="wide",
    page_title="Финансы ПВЗ 📦",
    page_icon="📦",
    initial_sidebar_state="collapsed"
)

# Minimalist CSS for mobile-first feel
st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    div[data-testid="stMetricValue"] {font-size: 1.8rem !important; font-weight: 700;}
    h1, h2, h3 {font-family: 'Helvetica Neue', sans-serif; font-weight: 600;}
    
    /* File Uploader Translation Hack */
    section[aria-label="Перетащите файл сюда"] > div > div > span:nth-child(1) {
        font-size: 0 !important;
        line-height: 0 !important;
    }
    section[aria-label="Перетащите файл сюда"] > div > div > span:nth-child(1)::after {
        content: "Перетащите файл сюда";
        font-size: 1rem !important;
        line-height: 1.5 !important;
        display: block;
        text-align: center;
    }
    section[aria-label="Перетащите файл сюда"] > div > div > span:nth-child(2) {
        font-size: 0 !important;
        line-height: 0 !important;
    }
    section[aria-label="Перетащите файл сюда"] > div > div > span:nth-child(2)::after {
        content: "Максимум 200МБ • XLSX / CSV";
        font-size: 0.8rem !important;
        line-height: 1.5 !important;
        display: block;
        text-align: center;
    }
    section[aria-label="Перетащите файл сюда"] button {
        text-indent: -9999px;
        line-height: 0;
    }
    section[aria-label="Перетащите файл сюда"] button::after {
        content: "Обзор";
        text-indent: 0;
        display: block;
        line-height: initial;
    }

</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION (SECURITY) ---
def check_password():
    """Простая защита доступа"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔒 Вход в систему")
            pwd = st.text_input("Введите пароль доступа", type="password")
            if st.button("Войти", type="primary", use_container_width=True):
                if pwd == "admin":  # ЗАДАЙ ПАРОЛЬ ЗДЕСЬ
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Неверный пароль")
        return False
    return True

if not check_password():
    st.stop()

# --- 3. DATA ENGINE (LOGIC) ---
@st.cache_data
def get_mock_data():
    """Генерация демо-данных (кэшируем для скорости)"""
    dates = pd.date_range(end=pd.Timestamp.today(), periods=7).tolist()
    random_dates = np.random.choice(dates, 500)
    
    data = {
        'date': random_dates,
        'operation_type': np.random.choice(['Выдача', 'Возврат', 'Приемка'], 500, p=[0.7, 0.1, 0.2]),
        'wb_reward': np.random.uniform(15.0, 120.0, 500).round(2),
        'penalty_amount': np.random.choice([0, 50, 100, 500], 500, p=[0.7, 0.15, 0.1, 0.05]),
        'penalty_reason': np.random.choice(
            ['Отсутствует', 'Подмена', 'Брак', 'Рейтинг', 'Утеря'], 
            500, 
            p=[0.7, 0.05, 0.1, 0.1, 0.05]
        )
    }
    df = pd.DataFrame(data)
    df.loc[df['penalty_amount'] == 0, 'penalty_reason'] = 'Отсутствует'
    return df

# --- 4. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("⚙️ Настройки расходов")
    
    st.subheader("Загрузка данных")
    st.info("Чтобы построить отчет, загрузите Excel-файл с детализацией из Wildberries.")
    uploaded_file = st.file_uploader("Перетащите файл сюда", type=['xlsx', 'csv'])
    
    st.divider()
    
    st.subheader("Финансы (мес)")
    rent = st.number_input("Аренда", value=30000, step=1000)
    internet_security = st.number_input("Охрана/ПО", value=3000, step=500)
    consumables = st.number_input("Расходники", value=5000, step=500)
    amortization = st.number_input("Амортизация", value=2000, step=500)
    
    st.divider()
    
    st.subheader("Налоги")
    tax_rate = st.number_input("Налог УСН (%)", value=6.0, step=0.5)
    reserve_rate = st.number_input("% в Резерв", value=15.0, step=1.0)

# --- 5. MAIN INTERFACE ---
st.title("Финансы ПВЗ 📦")

# --- A. STAFF MANAGEMENT (Hidden by default to focus on metrics) ---
with st.expander("👥 Управление сменами (ФОТ)", expanded=False):
    # Дефолтные данные
    default_staff = pd.DataFrame([
        {"Сотрудник": "Иванов А.", "Кол-во смен": 3, "Ставка": 1500, "Бонус": 0},
        {"Сотрудник": "Петрова С.", "Кол-во смен": 4, "Ставка": 1500, "Бонус": 1000}
    ])
    
    edited_staff = st.data_editor(
        default_staff, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Ставка": st.column_config.NumberColumn(format="%d ₽"),
            "Бонус": st.column_config.NumberColumn(format="%d ₽")
        }
    )
    # Расчет ФОТ
    edited_staff['Total'] = (edited_staff['Кол-во смен'] * edited_staff['Ставка']) + edited_staff['Бонус']
    total_fot = edited_staff['Total'].sum()
    st.caption(f"Итого ФОТ за период: {total_fot:,.0f} ₽")

# --- B. DATA PROCESSING ---
if uploaded_file:
    try:
        df = None
        # 1. Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            try:
                # Attempt 1: Try reading as standard CSV (comma, utf-8)
                df = pd.read_csv(uploaded_file)
                # If it looks like it failed to parse columns (e.g. all in one column), try separator ';'
                if df.shape[1] < 2:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=';')
            except:
                # Attempt 2: Try reading as Russian Excel CSV (semicolon, cp1251)
                uploaded_file.seek(0)
                try:
                    df = pd.read_csv(uploaded_file, sep=';', encoding='cp1251')
                except:
                    # Final attempt: just utf-8 with semicolon
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
        else:
            # Smart Sheet Search
            xls = pd.read_excel(uploaded_file, sheet_name=None) # Read all sheets
            
            # Potential column names we are looking for (Russian or English)
            target_columns = ['wb_reward', 'Вайлдберриз реализовал', 'Прибыль', 'Штрафы']
            
            found_sheet = False
            for sheet_name, sheet_df in xls.items():
                # Check if any target column exists in this sheet
                if any(col in sheet_df.columns for col in target_columns):
                    df = sheet_df
                    found_sheet = True
                    st.toast(f"✅ Данные найдены на листе: {sheet_name}", icon="📄")
                    break
            
            if not found_sheet:
                # Fallback to first sheet if nothing specific found
                df = list(xls.values())[0]

        # 2. Normalize and Rename columns
        # Strip whitespace from column names
        df.columns = df.columns.astype(str).str.strip()
        
        # --- FORMAT 1: Standard WB Detailization ---
        # Map known WB columns to our internal variable names
        column_mapping_standard = {
            'Вайлдберриз реализовал': 'wb_reward',
            'Штрафы': 'penalty_amount',
            'Тип операции': 'operation_type',
            'Обоснование штрафа': 'penalty_reason',
            'Вид начисления': 'operation_type',
            'Начислено': 'wb_reward',
            'Кол-во': 'quantity',
            'Баркод': 'barcode',
            'Дата': 'date',
            'date': 'date',
            'Время': 'date'
        }
        df = df.rename(columns=column_mapping_standard)
        
        # --- FORMAT 2: Sales Report (Analytics/Unit Economics) ---
        # If standard columns are missing, try to construct them from Sales Report columns
        if 'wb_reward' not in df.columns and 'Прибыль' in df.columns:
            st.toast("Обнаружен формат 'Отчет по продажам'. Адаптируем...", icon="🔄")
            df['wb_reward'] = df['Прибыль'] # Map Profit to Reward
            
            if 'Удержания' in df.columns:
                df['penalty_amount'] = df['Удержания']
            else:
                df['penalty_amount'] = 0
                
            df['operation_type'] = 'Выдача' # Assume all rows are sales
            df['penalty_reason'] = 'Прочее'

        # Validation of columns
        required_cols = ['wb_reward', 'penalty_amount', 'operation_type', 'penalty_reason']
        # Check if columns exist (case-insensitive check could be added here if needed, but rename handles it if mapping is correct)
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Ошибка структуры файла. Не найдены столбцы: {', '.join(missing_cols)}")
            st.warning(f"Найденные столбцы: {list(df.columns)}")
            st.info("Попробуйте сохранить файл как обычный Excel (.xlsx) или проверьте названия заголовков.")
            st.stop()
            
        # Fill NaNs for safety
        df['penalty_amount'] = df['penalty_amount'].fillna(0)
        df['wb_reward'] = df['wb_reward'].fillna(0)
            
    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
        st.stop()
else:
    df = get_mock_data()

# --- DATE DETECTION ---
report_period = ""
if 'date' in df.columns:
    try:
        # Try to convert to datetime, errors='coerce' turns bad data into NaT
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        min_date = df['date'].min()
        max_date = df['date'].max()
        if pd.notnull(min_date) and pd.notnull(max_date):
            report_period = f"{min_date.strftime('%d.%m')} — {max_date.strftime('%d.%m')}"
            # st.header removed here, moved to verdict block
    except:
        pass # Fail silently if date parsing fails

# --- C. CALCULATIONS (THE CORE) ---
gross_income = df['wb_reward'].sum()
total_penalties = df['penalty_amount'].sum()
tax_sum = gross_income * (tax_rate / 100)
weekly_fixed_costs = (rent + internet_security + consumables + amortization) / 4.3
net_profit = gross_income - total_penalties - tax_sum - weekly_fixed_costs - total_fot
dividends = net_profit * (1 - reserve_rate / 100)

# Unit Economics
issue_ops = df[df['operation_type'] == 'Выдача'].shape[0]
total_expenses = total_penalties + tax_sum + weekly_fixed_costs + total_fot
unit_cost = total_expenses / issue_ops if issue_ops > 0 else 0
avg_revenue = (gross_income / issue_ops) if issue_ops > 0 else 0

# --- D. DASHBOARD LAYOUT ---

# 1. Key Metrics (Mobile Friendly Grid)
st.subheader("Финансовый результат")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Начислено", f"{gross_income:,.0f} ₽".replace(',', ' '))
c2.metric("Штрафы", f"{total_penalties:,.0f} ₽".replace(',', ' '))
c3.metric("Прибыль (Net)", f"{net_profit:,.0f} ₽".replace(',', ' '))
c4.metric("На вывод", f"{dividends:,.0f} ₽".replace(',', ' '), help=f"За вычетом {reserve_rate}% резерва")

st.markdown("---")

# --- SIMPLE CONCLUSIONS (HUMAN READABLE) ---
st.subheader("🤖 Анализ ситуации")

if net_profit > 0:
    st.success(f"✅ **Отличная работа!**\n\nТочка в плюсе на **{net_profit:,.0f} ₽**. Можно выводить дивиденды.\n\n📅 *Отчет по операциям за период: {report_period}*")
else:
    st.error(f"🚨 **Внимание! Убыток {abs(net_profit):,.0f} ₽.**\n\nРасходы превышают доходы. Проверьте штрафы и ФОТ.\n\n📅 *Отчет по операциям за период: {report_period}*")

st.markdown("---")

# 2. Charts (Responsive)
col_main, col_side = st.columns([2, 1])

with col_main:
    # Waterfall
    fig_waterfall = go.Figure(go.Waterfall(
        name="Cashflow", orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=["Выручка", "Штрафы", "Налоги", "Расходы (fix)", "ФОТ", "Прибыль"],
        textposition="outside",
        text=[f"{x/1000:.1f}k" for x in [gross_income, -total_penalties, -tax_sum, -weekly_fixed_costs, -total_fot, net_profit]],
        y=[gross_income, -total_penalties, -tax_sum, -weekly_fixed_costs, -total_fot, net_profit],
        connector={"line": {"color": "rgb(200, 200, 200)"}},
        decreasing={"marker": {"color": "#FF4B4B"}},
        increasing={"marker": {"color": "#2BD17E"}},
        totals={"marker": {"color": "#333333"}}
    ))
    fig_waterfall.update_traces(hovertemplate='%{label}: %{value:,.0f} ₽<extra></extra>')
    fig_waterfall.update_layout(
        title="Движение средств (Waterfall)", 
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        showlegend=False
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

with col_side:
    # Penalties Breakdown
    penalties_df = df[df['penalty_amount'] > 0]
    if not penalties_df.empty:
        reason_group = penalties_df.groupby('penalty_reason')['penalty_amount'].sum().reset_index()
        fig_pie = px.pie(
            reason_group, 
            values='penalty_amount', 
            names='penalty_reason', 
            title='Структура штрафов',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_pie.update_traces(hovertemplate='%{label}: %{value:,.0f} ₽<extra></extra>')
        fig_pie.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=350, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.container(height=350, border=True).write("✅ Штрафов нет")

# 3. Unit Economics Insights
st.markdown("### 🧠 Unit-экономика")
e1, e2 = st.columns(2)
with e1:
    st.info(f"Себестоимость выдачи: **{unit_cost:.1f} ₽** / шт")
with e2:
    margin = avg_revenue - unit_cost
    if margin > 0:
        st.success(f"Заработок с 1 выдачи: **{margin:.1f} ₽**")
    else:
        st.error(f"Убыток с 1 выдачи: **{margin:.1f} ₽**")
