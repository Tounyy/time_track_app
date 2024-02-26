from classes.users import AuthenticatorConfigurator
from classes.task_requests import TaskRequests
import streamlit_authenticator as stauth
import streamlit as st
import time

auth_configurator = AuthenticatorConfigurator()
user_credentials = auth_configurator.fetch_user_data()

task_requests = TaskRequests()

cookie_config = {
    'expiry_days': 30,
    'key': 'some_random_signature_key',
    'name': 'some_random_cookie_name'
}

authenticator = stauth.Authenticate(
    user_credentials,
    cookie_config['name'],
    cookie_config['key'],
    cookie_config['expiry_days']
)

if not st.session_state.get("authentication_status"):
    navigation_choice = st.sidebar.selectbox("Navigace", ["Login", "Register"])
else:
    navigation_choice = "Authenticated"

if navigation_choice == "Login":
    name, authentication_status, username = authenticator.login("Login", "main")

    if st.session_state.get("authentication_status") is False:
        warning_message = st.warning('Uživatelské jméno/heslo je nesprávné nebo je prázdné')
        time.sleep(1.2)
        warning_message.empty()
    
    elif st.session_state.get("authentication_status") is None:
        info = st.info('Zadejte prosím své uživatelské jméno a heslo.')
        time.sleep(1.2)
        info.empty()

    if authentication_status:
        st.session_state["authentication_status"] = authentication_status
        st.session_state["username"] = username

elif navigation_choice == "Register":
    with st.form("Registrační formulář", clear_on_submit=True):
        st.header("Registrace")
        username = st.text_input("Uživatelské jméno")
        name = st.text_input("Jméno")
        email = st.text_input("Email")
        password = st.text_input("Heslo", type="password")
        user_type = st.selectbox("Vyberte typ uživatele", ["Customer", "Agency", "Worker"])
        submit_button_register = st.form_submit_button("Registrovat")
        
        if submit_button_register:
            registration_success = auth_configurator.register_user(username, name, email, password, user_type, submit_button_register)

elif navigation_choice == "Authenticated":
    if st.session_state.get("authentication_status"):
        username = st.session_state.get("username")
    if not st.session_state.get("authentication_status"):
        error = st.error("Prosím, přihlaste se pro přidání úkolu.")
        time.sleep(2)
        error.empty()
    else:
        user_type = task_requests.user_type

    if user_type == 'Agency' or user_type == 'Customer':
        tab1, tab2, tab3, tab4 = st.tabs(["Přidat task", "Confirmation task", "Smazat task", "Zobrazit tabulku s časem"])

    with tab1:
        with st.form("Add_task_form", clear_on_submit=True):
            st.subheader("Přidat task")
            task_name = st.text_input("Název tasku")
            money_MD = st.number_input("Zadej částku peněz", min_value=1)
            currency_options = ["CZK", "USD", "EUR"]
            selected_currency = st.selectbox("Vyber měnu", currency_options)
            submit_button_add = st.form_submit_button("Uložit do databáze")

            if submit_button_add:
                if task_name.strip() == "":
                    warning = st.warning("Název tasku je povinný. Prosím, doplňte ho.")
                    time.sleep(2)
                    warning.empty()
                else:
                    message = task_requests.add_task(task_name, money_MD, selected_currency)
                    if message:
                        success = st.success(message)
                        time.sleep(1.2)
                        success.empty()

    authenticator.logout("Logout")
    st.write(username)
    st.write(user_type)