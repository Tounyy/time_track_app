from classes.connector import Database
from classes.users import AuthenticatorConfigurator
from datetime import datetime
import time
import streamlit as st 
import pandas as pd

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

    def fetch_tasks(self):
        select_query = "SELECT * FROM public.tasks"
        return self.db.get_request(select_query)

    def confirm_task(self, task_name, user_type):
        if user_type == 'Agency':
            update_query = "UPDATE public.tasks SET \"Agency_input_task\" = 'confirm' WHERE \"Tasks\" = %s;"
        elif user_type == 'Customer':
            update_query = "UPDATE public.tasks SET \"Customer_input_task\" = 'confirm' WHERE \"Tasks\" = %s;"
        self.db.execute_query(update_query, (task_name,))

    def process_tasks_for_confirmation(self, user_type):
        tasks_data = self.fetch_tasks()
        tasks_df = pd.DataFrame(tasks_data, columns=["ID", "Task", "Tracking_time_tasks", "Start_time_of_tracking", "Stop_time_of_tracking", "User", "MD", "Currency", "Customer_input_task", "Agency_input_task", "User_type_input_task"])
        
        if user_type == 'Agency':
            available_tasks = tasks_df.loc[tasks_df["Agency_input_task"] != 'confirm', "Task"]
        elif user_type == 'Customer':
            available_tasks = tasks_df.loc[tasks_df["Customer_input_task"] != 'confirm', "Task"]

        return available_tasks

    def remove_confirmation(self, task_name, user_type):
        if user_type == 'Agency':
            update_query = "UPDATE public.tasks SET \"Agency_input_task\" = NULL WHERE \"Tasks\" = %s;"
        elif user_type == 'Customer':
            update_query = "UPDATE public.tasks SET \"Customer_input_task\" = NULL WHERE \"Tasks\" = %s;"
        self.db.execute_query(update_query, (task_name,))
    
    def process_tasks_for_remove_confirmation(self, user_type):
        tasks_data = self.fetch_tasks()
        tasks_df = pd.DataFrame(tasks_data, columns=["ID", "Task", "Tracking_time_tasks", "Start_time_of_tracking", "Stop_time_of_tracking", "User", "MD", "Currency", "Customer_input_task", "Agency_input_task", "User_type_input_task"])
        
        if user_type == 'Agency':
            available_tasks_2 = tasks_df.loc[tasks_df["Agency_input_task"] == 'confirm', "Task"]
        elif user_type == 'Customer':
            available_tasks_2 = tasks_df.loc[tasks_df["Customer_input_task"] == 'confirm', "Task"]

        return available_tasks_2