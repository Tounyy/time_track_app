from classes.connector import Database
from classes.users import AuthenticatorConfigurator
from datetime import datetime, timedelta
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

    def fetch_tasks(self):
        select_query = "SELECT * FROM public.tasks"
        return self.db.get_request(select_query)

    def generate_tasks_df(self):
        tasks_data = self.fetch_tasks()
        tasks_df = pd.DataFrame(tasks_data, columns=["ID", "Task", "User_input_task", "MD", "Currency", "Customer_confirm_task", "Agency_confirm_task", "User_type_input_task", "Approval_Status", "Assigned_Worker", "Time_start_of_tracking", "Time_stop_of_tracking", "Time_track"
    ])
        return tasks_df

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

    def process_tasks_for_confirmation(self, user_type):
        tasks_df = self.generate_tasks_df() 
        filtered_tasks_df_sorted = tasks_df.sort_values(by='ID')

        if user_type == 'Agency':
            available_tasks = filtered_tasks_df_sorted.loc[filtered_tasks_df_sorted["Agency_confirm_task"] != 'confirm', "Task"]
        elif user_type == 'Customer':
            available_tasks = filtered_tasks_df_sorted.loc[filtered_tasks_df_sorted["Customer_confirm_task"] != 'confirm', "Task"]

        return available_tasks
    
    def process_tasks_for_remove_confirmation(self, user_type):
        tasks_df = self.generate_tasks_df()         
        filtered_tasks_df_sorted_2 = tasks_df.sort_values(by='ID')

        if user_type == 'Agency':
            available_tasks_2 = filtered_tasks_df_sorted_2.loc[filtered_tasks_df_sorted_2["Agency_confirm_task"] == 'confirm', "Task"]
        elif user_type == 'Customer':
            available_tasks_2 = filtered_tasks_df_sorted_2.loc[filtered_tasks_df_sorted_2["Customer_confirm_task"] == 'confirm', "Task"]

        return available_tasks_2

    def confirm_task(self, task_name, user_type, confirmation_btn, selected_task):
        if confirmation_btn and selected_task:  
            if user_type == 'Agency':
                update_query = "UPDATE public.tasks SET \"agency_confirm_task\" = 'confirm' WHERE \"tasks\" = %s;"
            elif user_type == 'Customer':
                update_query = "UPDATE public.tasks SET \"customer_confirm_task\" = 'confirm' WHERE \"tasks\" = %s;"
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
                update_query = "UPDATE public.tasks SET \"agency_confirm_task\" = NULL WHERE \"tasks\" = %s;"
            elif user_type == 'Customer':
                update_query = "UPDATE public.tasks SET \"customer_confirm_task\" = NULL WHERE \"tasks\" = %s;"
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
        tasks_df = self.generate_tasks_df() 
        admin_tasks_df = tasks_df[tasks_df['User_input_task'] == username]
        
        return admin_tasks_df
    
    def get_user_tasks_summary(self, username):
        tasks_df = self.generate_tasks_df() 
        tasks_df.drop(columns=['Customer_confirm_task', 'Agency_confirm_task'], inplace=True)
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

    def select_and_track_task(self):
        tasks_df = self.generate_tasks_df() 
        fill_tasks_df_sorted = tasks_df.sort_values(by='ID')
        select_df = fill_tasks_df_sorted.loc[
            (fill_tasks_df_sorted["Customer_confirm_task"] == 'confirm') & 
            (fill_tasks_df_sorted["Agency_confirm_task"] == 'confirm') & 
            (fill_tasks_df_sorted["Approval_Status"].isnull()), ['ID', 'Task']
        ]

        return select_df
    
    def update_tasks_to_pending(self, selected_task_display, approval_btn, username):
        if approval_btn and selected_task_display:
            update_query = """
            UPDATE public.tasks
            SET \"approval_status\" = 'Pending', \"assigned_worker\" = %s
            WHERE \"approval_status\" IS NULL
            AND \"assigned_worker\" IS NULL
            AND \"customer_confirm_task\" = 'confirm'
            AND \"agency_confirm_task\" = 'confirm';
            """
            self.db.execute_query(update_query, (username,))
            success = st.success(f"Úkol '{selected_task_display}' byl aktualizován na čekající schválení a přiřazen pracovníkovi {username}.")
            time.sleep(2)
            success.empty()
            st.experimental_rerun()
        elif not selected_task_display and approval_btn: 
            warning = st.warning("Není žádný úkol k přijetí.")
            time.sleep(2)
            warning.empty()

    def select_approval_status(self):
        tasks_df = self.generate_tasks_df() 
        fill_tasks_df_sorted = tasks_df.sort_values(by='ID')
        select_df = fill_tasks_df_sorted.loc[
            (fill_tasks_df_sorted["Approval_Status"] == 'Approved')
        ]

        return select_df
    
    def select_pending_status(self):
        tasks_df = self.generate_tasks_df() 
        fill_tasks_df_sorted = tasks_df.sort_values(by='ID')
        select_df = fill_tasks_df_sorted.loc[
            (fill_tasks_df_sorted["Approval_Status"] == 'Pending')
        ]

        return select_df
    
    def update_tasks_to_approved(self, selected_task_display_approved, approval_btn_approved):
        if approval_btn_approved and selected_task_display_approved:
            update_query = """
            UPDATE public.tasks
            SET approval_status = 'Approved'
            WHERE approval_status = 'Pending'
            AND customer_confirm_task = 'confirm'
            AND agency_confirm_task = 'confirm';
            """
            self.db.execute_query(update_query)
            success = st.success(f"Úkol '{selected_task_display_approved}' byl aktualizován na schválený.")
            time.sleep(2)
            success.empty()
            st.experimental_rerun()
        elif not selected_task_display_approved and approval_btn_approved: 
            warning = st.warning("Není žádný úkol k schválení.")
            time.sleep(2)
            warning.empty()

    def revoke_task_approval(self, selected_task_display_revoked, revoke_approval_btn):
        if revoke_approval_btn and selected_task_display_revoked:
            update_query = """
            UPDATE public.tasks
            SET approval_status = NULL, assigned_worker = NULL
            WHERE approval_status = 'Approved'
            AND customer_confirm_task = 'confirm'
            AND agency_confirm_task = 'confirm';
            """
            self.db.execute_query(update_query)
            success = st.success(f"Schválení úkolu '{selected_task_display_revoked}' bylo úspěšně odebráno.")
            time.sleep(2)
            success.empty()
            st.experimental_rerun()
        elif not selected_task_display_revoked and revoke_approval_btn: 
            warning = st.warning("Není k dispozici žádný schválený úkol k odebrání.")
            time.sleep(2)
            warning.empty()