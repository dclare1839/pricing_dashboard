import pandas as pd
import streamlit as st

pricing_df = pd.read_excel("pricing_db.xlsx", sheet_name="Sheet1")
software_price = pd.read_excel("software_price.xlsx", sheet_name="Sheet1")

st.session_state.final_price = 0

# options와 versions 딕셔너리는 그대로 사용
options = {"Civil NX": ["None", "Rail Track Analysis"], 
           "Gen": ["None", "Heat of Hydration", "Material Nonlinear Analysis", 
                   "Inelastic Time History Analysis"],
           "GTS NX": ["None", "Slope Stability", "Seepage Analysis", 
                              "Consolidation", "Dynamic Analysis", "Fully Coupled", 
                              "Fully Coupled Thermal-Seepage"],
            "CIM":["None"],
            "nGen":["None"],
            "FEA NX":["None"]}

versions = {"Civil NX":["Plus","Advanced","Full"], "Gen":["Plus","Advanced","Full"], "CIM":["Full"],
            "nGen":["Full"], "GTS NX":["2D","2D Full", "3D", "3D Full", "2D&3D", "2D&3D Full"]}


st.title("MIDAS Pricing Dashboard")

# ----------------- SESSION STATE 초기화 -----------------
# **if 문으로 모든 session_state를 올바르게 초기화합니다.**
if 'df_license' not in st.session_state:
    st.session_state.df_license = pd.DataFrame(columns=["Software","Version","Quantity", "Options", "Price"])

if 'second_year' not in st.session_state:
    st.session_state.second_year = pd.DataFrame(columns=["Software","Version","Quantity", "Maintenance Rate", "Price"])

if 'software_type_value' not in st.session_state:
    st.session_state.software_type_value = 'Civil NX'
if 'version_value' not in st.session_state:
    st.session_state.version_value = 'Plus'
if 'quantity_value' not in st.session_state:
    st.session_state.quantity_value = 1
if 'additional_option_value' not in st.session_state:
    st.session_state.additional_option_value = ['None']
if 'show_success_message' not in st.session_state:
    st.session_state.show_success_message = False

# --------------------------------------------------------


# ----------------- 함수 -----------------
def add_license():
    # 1. 새 라이선스 데이터 딕셔너리 생성 (session_state 값을 리스트로 감싸기)

    option_price = 0
    for option in st.session_state.additional_option_value:
        if option != 'None':
            option_price_row = pricing_df[
                (pricing_df['Software'] == st.session_state.software_type_value) &
                (pricing_df['Option'] == option) # .isin() 대신 == 사용 (단일 항목이므로)
            ]
            
            # 필터링 결과가 비어있지 않을 때만 가격을 가져와 더합니다.
            if not option_price_row.empty:
                option_price += option_price_row['Price'].iloc[0]

    original_price = software_price[(software_price['Software']==st.session_state.software_type_value)&
                                             (software_price['Version']==st.session_state.version_value)]['Price'].iloc[0]
    maintenance_rate = software_price[(software_price['Software']==st.session_state.software_type_value)&
                                             (software_price['Version']==st.session_state.version_value)]['mods_rate'].iloc[0]
    st.session_state.price = st.session_state.quantity_value * (original_price+option_price) * (1+maintenance_rate) * (1-st.session_state.discount)
    
    new_data = {
        "Software": [st.session_state.software_type_value],
        "Version": [st.session_state.version_value],
        "Quantity": [st.session_state.quantity_value],
        "Options": [", ".join(st.session_state.additional_option_value)],
        "Discount": [st.session_state.discount],
        "Price": [st.session_state.price] # price를 계산해서 넣어야 합니다. 현재는 임시값
    }
    new_df = pd.DataFrame(new_data)
    
    second_data = {
        "Software": [st.session_state.software_type_value],
        "Version": [st.session_state.version_value],
        "Quantity": [st.session_state.quantity_value],
        "Maintenance Rate": [maintenance_rate],
        "Price": [st.session_state.quantity_value * (original_price+option_price)*maintenance_rate]
    }

    second_df = pd.DataFrame(second_data)
    st.session_state.second_year = pd.concat([st.session_state.second_year, second_df], ignore_index=True)


    # 2. DataFrame에 새 행 추가
    st.session_state.df_license = pd.concat([st.session_state.df_license, new_df], ignore_index=True)
    
    # 3. 위젯 값 초기화
    st.session_state.software_type_value = 'Civil NX'
    st.session_state.version_value = 'Plus' # 'Plus Full'이 아닌 'Plus'로 수정
    st.session_state.quantity_value = 1
    st.session_state.additional_option_value = ['None']
    
    # 4. 성공 메시지 플래그를 True로 설정
    st.session_state.show_success_message = True

# def calculate_all():
#     st.session_state.final_price = st.session_state.df_license['Price'].sum()
#     st.write("Final Price is:", st.session_state.final_price)


# ----------------- 위젯 배치 -----------------
# 성공 메시지를 띄우는 부분
if st.session_state.show_success_message:
    st.info("License is added.")
    # 메시지를 한 번만 보여주고 플래그를 False로 변경하여 다음 리런 때는 표시하지 않도록 함
    st.session_state.show_success_message = False


col1, col2, col3 = st.columns(3)

with col1:
    st.selectbox(
        "Software Type", 
        ("Civil NX", "CIM", "Gen", "nGen", "GTS NX", "FEA NX"),
        key='software_type_value'
    )

with col2:
    st.selectbox(
        "Version",
        versions[st.session_state.software_type_value],
        key='version_value'
    )

with col3:
    st.number_input(
        "Quantity",
        min_value=1,
        max_value=1000,
        key='quantity_value'
    )

coll1, coll2 = st.columns(2)

with coll1:
    st.multiselect(
        "Additional Option", 
        options[st.session_state.software_type_value],
        key='additional_option_value'
    ) 

with coll2:
    st.session_state.discount = st.number_input(
        "Discount",
        min_value=0.0,
        max_value=1.0,
    )

# 버튼 클릭 시 add_license 함수 호출
st.button("Add", on_click=add_license)


st.markdown("# List ")
st.markdown("## License List")
st.dataframe(st.session_state.df_license, use_container_width=True)

# st.button("Calculate", on_click=calculate_all)
st.session_state.final_price = st.session_state.df_license['Price'].sum()
st.markdown(f"## Final Price is: {int(st.session_state.final_price)}")

st.markdown("### From Second Year")
st.dataframe(st.session_state.second_year, use_container_width=True)