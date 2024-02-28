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
    name, authentication_status, username = authenticator.login('Login', 'main')

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


    tab1, tab2, tab3, tab4 = st.tabs(["Přidat task", "Smazat task", "Potvrdit task", "Zobrazit tabulku s časem"])

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

    with tab2:
        with st.form("Delete_task_form", clear_on_submit=True):
            st.subheader("Smazat task")

            admin_tasks_df_1 = task_requests.get_user_tasks_summary(username)
            st.dataframe(admin_tasks_df_1, hide_index=True, use_container_width=True)        

            admin_tasks_df = task_requests.get_user_tasks(username)
            selected_task = st.selectbox("Vyberte task ke smazání", admin_tasks_df["Task"])
            delete_button = st.form_submit_button("Smazat")
            
            if delete_button:
                delete_success = task_requests.delete_task(selected_task, delete_button)

    with tab3:
        with st.form("Confirm_form", clear_on_submit=True):
            st.subheader("Potvrzení a odstranění potvrzení")

            available_tasks = task_requests.process_tasks_for_confirmation(user_type)
            selected_task = st.selectbox("Vyberte task k potvrzení", available_tasks)

            if st.form_submit_button("Potvrdit"):
                task_requests.confirm_task(selected_task, user_type)
                success = st.success(f"Potvrzení bylo odesláno pro úkol '{selected_task}'.")
                time.sleep(1.2)
                success.empty()
                st.experimental_rerun()
            
            available_tasks_2 = task_requests.process_tasks_for_remove_confirmation(user_type)
            selected_task2 = st.selectbox("Vyberte task k odstranění potvrzení", available_tasks_2)

            if st.form_submit_button("Odstranit potvrzení"):
                task_requests.remove_confirmation(selected_task2, user_type)
                success = st.success(f"Potvrzení bylo odstraněno pro úkol '{selected_task2}'.")
                time.sleep(1.2)
                success.empty()
                st.experimental_rerun()

    authenticator.logout("Logout")
    st.write(f"username: {username}")
    st.write(f"user type: {user_type}")