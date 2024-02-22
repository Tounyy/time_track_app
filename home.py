from classes.users import AuthenticatorConfigurator
import streamlit_authenticator as stauth
import streamlit as st
import time

auth_configurator = AuthenticatorConfigurator()
user_credentials = auth_configurator.fetch_user_data()

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

authenticator.login('Login')

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')

elif st.session_state["authentication_status"] is False:
    warning_message = st.warning('Uživatelské jméno/heslo je nesprávné nebo je prázdné')
    time.sleep(1.2)
    warning_message.empty()

elif st.session_state["authentication_status"] is None:
    warning_message = st.warning('Zadejte prosím své uživatelské jméno a heslo.')
    time.sleep(1.2)
    warning_message.empty()

with st.form("Registrační formulář"):
    st.header("Register")
    username = st.text_input("Uživatelské jméno")
    name = st.text_input("Jméno")
    email = st.text_input("Email")
    password = st.text_input("Heslo", type="password")
    user_type = st.selectbox("Vyberte typ uživatele", ["Customer", "Agency", "Worker"])
    submit_button = st.form_submit_button("Registrovat")

    if submit_button:
        auth_configurator.register_user(username, name, email, password, user_type, submit_button)