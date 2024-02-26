from classes.connector import Database
from classes.users import AuthenticatorConfigurator
from datetime import datetime
import time
import streamlit as st 

class TaskRequests:
    def __init__(self):
        self.db = Database()
        self.auth_configurator = AuthenticatorConfigurator()
        if st.session_state.get("authentication_status"):
            self.username = st.session_state.get("username")
            self.user_type = self.auth_configurator.get_user_type(self.username)
        else:
            self.username = None
            self.user_type = None

    def task_exists_for_user_type(self, task_name, user_type):
        check_user_type_query = "SELECT COUNT(*) FROM public.tasks WHERE \"Tasks\" = %s AND \"User_type_input_task\" = %s;"
        result = self.db.get_request(check_user_type_query, (task_name, user_type))
        if result:
            count = result[0][0] 
            return count > 0
        return False
            
    def task_exists_for_other_user_type(self, task_name, user_type):
        check_other_user_type_query = "SELECT COUNT(*) FROM public.tasks WHERE \"Tasks\" = %s AND \"User_type_input_task\" != %s;"
        result = self.db.get_request(check_other_user_type_query, (task_name, user_type))
        if result:
            count = result[0][0]  
            return count > 0
        return False

    def add_task(self, task_name, money_md, selected_currency):
        if not self.username or not self.user_type: 
            error = st.error("Uživatel není přihlášen.")
            time.sleep(2)
            error.empty()
        if self.task_exists_for_user_type(task_name, self.user_type):
            error = st.error(f"Task '{task_name}' již existuje pro aktuálního uživatele.")
            time.sleep(2)
            error.empty()
        elif self.task_exists_for_other_user_type(task_name, self.user_type):
            error_mess = st.error(f"Task '{task_name}' již existuje pro jiného uživatele s jiným typem.")
            time.sleep(2)
            error_mess.empty()
        else:
            insert_query = "INSERT INTO public.tasks (\"Tasks\", \"MD\", \"Currency\", \"User\", \"User_type_input_task\") VALUES (%s, %s, %s, %s, %s);"
            self.db.execute_query(insert_query, (task_name, money_md, selected_currency, self.username, self.user_type))
            return f"Úkol '{task_name}' byl úspěšně uložen do databáze."
