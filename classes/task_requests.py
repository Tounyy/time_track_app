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
        check_user_type_query = "SELECT COUNT(*) FROM public.tasks WHERE \"tasks\" = %s AND \"user_type_input_task\" = %s;"
        result = self.db.get_request(check_user_type_query, (task_name, user_type))
        if result:
            count = result[0][0] 
            return count > 0
        return False
            
    def task_exists_for_other_user_type(self, task_name, user_type):
        check_other_user_type_query = "SELECT COUNT(*) FROM public.tasks WHERE \"tasks\" = %s AND \"user_type_input_task\" != %s;"
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
            insert_query = "INSERT INTO public.tasks (\"tasks\", \"md\", \"currency\", \"user_input_task\", \"user_type_input_task\") VALUES (%s, %s, %s, %s, %s);"
            self.db.execute_query(insert_query, (task_name, money_md, selected_currency, self.username, self.user_type))
            return f"Úkol '{task_name}' byl úspěšně uložen do databáze."

    def fetch_tasks(self):
        select_query = "SELECT * FROM public.tasks"
        return self.db.get_request(select_query)

    def process_tasks_for_confirmation(self, user_type):
        tasks_data = self.fetch_tasks()
        tasks_df = pd.DataFrame(tasks_data, columns=["ID", "Task", "User_input_task", "MD", "Currency", "Customer_input_task", "Agency_input_task", "User_type_input_task"])
        filtered_tasks_df_sorted = tasks_df.sort_values(by='ID')

        if user_type == 'Agency':
            available_tasks = filtered_tasks_df_sorted.loc[filtered_tasks_df_sorted["Agency_input_task"] != 'confirm', "Task"]
        elif user_type == 'Customer':
            available_tasks = filtered_tasks_df_sorted.loc[filtered_tasks_df_sorted["Customer_input_task"] != 'confirm', "Task"]

        return available_tasks
    
    def process_tasks_for_remove_confirmation(self, user_type):
        tasks_data = self.fetch_tasks()
        tasks_df = pd.DataFrame(tasks_data, columns=["ID", "Task", "User_input_task", "MD", "Currency", "Customer_input_task", "Agency_input_task", "User_type_input_task"])
        filtered_tasks_df_sorted_2 = tasks_df.sort_values(by='ID')

        if user_type == 'Agency':
            available_tasks_2 = filtered_tasks_df_sorted_2.loc[filtered_tasks_df_sorted_2["Agency_input_task"] == 'confirm', "Task"]
        elif user_type == 'Customer':
            available_tasks_2 = filtered_tasks_df_sorted_2.loc[filtered_tasks_df_sorted_2["Customer_input_task"] == 'confirm', "Task"]

        return available_tasks_2

    def confirm_task(self, task_name, user_type, confirmation_btn, selected_task):
        if confirmation_btn and selected_task:  
            if user_type == 'Agency':
                update_query = "UPDATE public.tasks SET \"agency_input_task\" = 'confirm' WHERE \"tasks\" = %s;"
            elif user_type == 'Customer':
                update_query = "UPDATE public.tasks SET \"customer_input_task\" = 'confirm' WHERE \"tasks\" = %s;"
            self.db.execute_query(update_query, (task_name,))
            success = st.success(f"Potvrzení bylo odesláno pro úkol '{selected_task}'.")
            time.sleep(1.2)
            success.empty()
            st.experimental_rerun()
        elif not selected_task and confirmation_btn: 
            warning = st.warning("Není co k potvrzení.")
            time.sleep(2)
            warning.empty()

    def remove_confirmation(self, task_name, user_type, remove_confirmation_btn, selected_task2):
        if remove_confirmation_btn and selected_task2:  
            if user_type == 'Agency':
                update_query = "UPDATE public.tasks SET \"agency_input_task\" = NULL WHERE \"tasks\" = %s;"
            elif user_type == 'Customer':
                update_query = "UPDATE public.tasks SET \"customer_input_task\" = NULL WHERE \"tasks\" = %s;"
            self.db.execute_query(update_query, (task_name,))
            success = st.success(f"Potvrzení bylo odstraněno pro úkol '{selected_task2}'.")
            time.sleep(1.2)
            success.empty()
            st.experimental_rerun()
        elif not selected_task2 and remove_confirmation_btn: 
            warning = st.warning("Není co odstranění potvrzení.")
            time.sleep(2)
            warning.empty()
    
    def get_user_tasks(self, username):
        tasks_data = self.fetch_tasks()
        tasks_df = pd.DataFrame(tasks_data, columns=["ID", "Task", "User_input_task", "MD", "Currency", "Customer_input_task", "Agency_input_task", "User_type_input_task"])
        admin_tasks_df = tasks_df[tasks_df['User_input_task'] == username]
        
        return admin_tasks_df
    
    def get_user_tasks_summary(self, username):
        tasks_data = self.fetch_tasks()
        tasks_df = pd.DataFrame(tasks_data, columns=["ID", "Task", "User_input_task", "MD", "Currency", "Customer_input_task", "Agency_input_task", "User_type_input_task"])
        tasks_df.drop(columns=['Customer_input_task', 'Agency_input_task'], inplace=True)
        admin_tasks_df_1 = tasks_df[tasks_df['User_input_task'] == username]
        admin_tasks_df_1.drop(columns=['User_input_task'], inplace=True)
        return admin_tasks_df_1
    
    def delete_task(self, selected_task, delete_button):
        if delete_button and selected_task:  
            delete_query = "DELETE FROM tasks WHERE \"tasks\" = %s;"
            self.db.execute_query(delete_query, (selected_task,))
            success = st.success(f"Úkol '{selected_task}' je smazán z databáze.")
            time.sleep(2)    
            success.empty()        
            st.experimental_rerun()
        elif not selected_task and delete_button: 
            warning = st.warning("Není žádný task k smazání.")
            time.sleep(2)
            warning.empty()