from classes.connector import Database
import pandas as pd
import streamlit_authenticator as stauth
import streamlit as st
from datetime import datetime
import time
class AuthenticatorConfigurator:
    def __init__(self):
        self.db = Database()

    def fetch_user_data(self):
        query = "SELECT \"username\", \"name\", \"email\", \"password\" FROM public.\"user\""
        fetched_data = self.db.get_request(query)

        user_credentials = {'usernames': {}}
        for user in fetched_data:
            username, name, email, password = user
            cleaned_password = password.replace("{", "").replace("}", "")
            user_credentials['usernames'][username] = {
                'name': name,
                'email': email,
                'password': cleaned_password
            }

        return user_credentials
    
    def register_user(self, username, name, email, password, user_type, submit_button_register):
        if submit_button_register:
            connection = self.db.create_connection()
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM public.\"user\" WHERE \"username\" = %s OR \"email\" = %s;", (username, email))
                existing_user_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM public.\"user\" WHERE \"email\" = %s;", (email,))
                existing_email_count = cursor.fetchone()[0]

                if not username or not name or not email or not password:
                    warning = st.warning('Všechna pole jsou povinná. Prosím, vyplňte všechny údaje.')
                    time.sleep(1.2)
                    warning.empty()
                elif existing_user_count > 0:
                    warning = st.warning('Tento uživatel již existuje.')
                    time.sleep(1.2)
                    warning.empty()                
                elif "@" not in email:
                    warning = st.warning("Email musí obsahovat znak '@'. Prosím, zadejte platný e-mail.")
                    time.sleep(1.2)
                    warning.empty()
                elif "." not in email.split("@")[1]:
                    warning = st.warning("Email by měl obsahovat něco jako doménu (např. 'gmail.com').")
                    time.sleep(1.2)
                    warning.empty()
                elif existing_email_count > 0:
                    warning = st.warning('Tento e-mail již existuje.')
                    time.sleep(1.2)
                    warning.empty()
                elif len(password) < 8:
                    warning = st.warning('Heslo musí obsahovat alespoň 8 znaků.')
                    time.sleep(1.2)
                    warning.empty()
                elif not any(char.islower() for char in password):
                    warning = st.warning('Heslo musí obsahovat alespoň jedno malé písmeno.')
                    time.sleep(1.2)
                    warning.empty()
                elif not any(char.isupper() for char in password):
                    warning = st.warning('Heslo musí obsahovat alespoň jedno velké písmeno.')
                    time.sleep(1.2)
                    warning.empty()
                elif not any(char.isdigit() for char in password):
                    warning = st.warning('Heslo musí obsahovat alespoň jedno číslo.')
                    time.sleep(1.2)
                    warning.empty()
                else:
                    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    hashed_passwords = stauth.Hasher([password]).generate()
                    insert_user_query = """INSERT INTO public."user" ("username", "name", "type_user", "password", "email", "registration_date") 
                    VALUES (%s, %s, %s, %s, %s, %s);"""
                    cursor.execute(insert_user_query, (username, name, user_type, hashed_passwords[0], email, registration_date))                
                    success = st.success("Registrace proběhla úspěšně. Nyní se můžete přihlásit.")
                    time.sleep(1.2)
                    success.empty()
            finally:
                cursor.close()
                connection.close()

    def get_user_type(self, username):
        select_query = "SELECT \"id\", \"username\", \"name\", \"type_user\", \"password\", \"email\", \"registration_date\" FROM public.\"user\""
        user_data = self.db.get_request(select_query)
        
        column_names = ["ID", "Username", "Name", "Type_User", "Password", "Email", "Registration_Date"]
        user_df = pd.DataFrame(user_data, columns=column_names)
        user_df["Username_lower"] = user_df["Username"].str.lower()

        if (user_df["Username_lower"] == username.lower()).any():
            return user_df.loc[user_df["Username_lower"] == username.lower(), "Type_User"].values[0]
        else:
            return None