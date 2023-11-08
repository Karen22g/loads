import streamlit as st
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import os
import pandas as pd
import mysql.connector
import re
import bcrypt
import time

def main():

    st.set_page_config(page_title="Planner ef", page_icon="./logo_ef.png", layout="wide")

    with open('./styles/style_main.css', 'r') as f:
        styles = f.read()

    st.markdown(f'<style>{styles}</style>', unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()
    
@st.cache_data()
def get_vars():
    
    load_dotenv()
    
    pass
 
def validate_words(text, box, alpha = False):
    
    if not(text.strip() != ""):
        st.warning(f"The {box} field can not be blank.")
        st.stop()
    
    if alpha:
        if re.match(r'^[a-zA-Z\s]+$', text):
            return text
        else:
            st.warning(f"Please enter only letters in {box}.")
            st.stop()
            return ""
        
    else:
        return text
    
def validate_email(email):
    
    if not(email.strip() != ""):
        st.warning(f"The email field can not be blank.")
        st.stop()
    
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return email
    else:
        st.warning("Please enter a valid email address.")
        st.stop()
        return ""

def fill_users_sql(name_db, name_table, user_type, name, username, credential, password, email, team):
    
    connection = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("USER_DB"),
        password = os.getenv("PASSWORD_DB"),
        database = name_db
    )
    
    cursor = connection.cursor()
    
    try:
        # Fill users
        cursor.execute(f'''
                            INSERT INTO {name_table} (user_type, name, username, credential, password, email, team)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (user_type, name, username, credential, password, email, team))
        
        # Confirm changes
        connection.commit()
        
        # Close connection
        connection.close()
        
        st.success("Successful sign up")
    
    except mysql.connector.IntegrityError as e:

        st.error("This user already exists.")
        
        connection.close()

        st.stop()

def verify_user(name_db, name_table, username, password):
    
    connection = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("USER_DB"),
        password = os.getenv("PASSWORD_DB"),
        database = name_db
    )
    
    cursor = connection.cursor()
    
    cursor.execute(f"SELECT password FROM {name_table} WHERE username = %s", (username,))
    result = cursor.fetchone()
    
    # Close connection
    connection.close()
    
    if result:
        stored_hash = result[0].encode('utf-8')
        
        # Compares the stored hash with the hash of the provided password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            st.success("Successful login.")
            return True
            
        else:
            st.error("Username or password incorrect.")
            return False
            
    else:
        st.error("Username not found in the database.")
        return False

def sign_up():
    
    try:
    
        with st.form("SignUp Form", clear_on_submit=True):
                
            team = st.selectbox('Team', ["R+D", "IT"])
            name = st.text_input("Full Name", key="name")
            email = st.text_input("Email", key="email")
            username = st.text_input("Username", key="username")
            password = st.text_input("Password", type="password", key="password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
                
            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")

            if submitted:
                name = validate_words(name, "full name", True)
                email = validate_email(email)
                username = validate_words(username, "username")
                password = validate_words(password, "password")
                confirm_password = validate_words(confirm_password, "confirm password")

                if password != confirm_password:
                    
                    st.error("Passwords do not match")
                    st.stop()
                    
                else:
                    
                    password = password.encode('utf-8')
                    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                    credential = f"{username.lower()}_{team}"
                    
                    fill_users_sql("users_db", "users", "User", name.lower(), username.lower(), credential, hashed_password, email.lower(), team)
    except:
        print("")            
    pass

@st.cache_data()
def get_credentials(name_db, name_table):
    
    connection = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("USER_DB"),
        password = os.getenv("PASSWORD_DB"),
        database = name_db
    )
    
    cursor = connection.cursor()
    
    # Query to get all usernames
    cursor.execute(f"SELECT username, password, email FROM {name_table}")
    results = cursor.fetchall()
    
    # Close connection
    connection.close()
    
    usernames, passwords, emails = zip(*results)
    usernames, passwords, emails = list(usernames), list(passwords), list(emails)
    
    credentials = {'usernames': {}}
    for index in range(len(emails)):
        credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}
    
    return usernames, credentials

# @st.cache_data()
def get_user_data(name_db, name_table, username):
    
    connection = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("USER_DB"),
        password = os.getenv("PASSWORD_DB"),
        database = name_db
    )
    cursor = connection.cursor()
    
    # Query to get all usernames
    cursor.execute(f"SELECT user_type, name, email, team FROM {name_table} WHERE username = %s", (username,))
    results = cursor.fetchall()

    # Close connection
    connection.close()
    
    user_type, name, email, team = zip(*results)
    
    return user_type[0], name[0], email[0], team[0]

def update_user_type(name_db, name_table, col_upd, value_upd, username):
    
    connection = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("USER_DB"),
        password = os.getenv("PASSWORD_DB"),
        database = name_db
    )
    cursor = connection.cursor()
    
    # Query to get all usernames
    cursor.execute(f"UPDATE {name_table} SET {col_upd} = %s WHERE username = %s", (value_upd, username))

    # Confirm changes
    connection.commit()

    # Close connection
    connection.close()
    
    return True

get_vars()

usernames, credentials = get_credentials("users_db", "users")

Authenticator = stauth.Authenticate(credentials, cookie_name='ef_planner', key='abcdef', cookie_expiry_days=365)
email, authentication_status, username = Authenticator.login(':green[Login]', 'main')

if authentication_status == False:
    if not(username in usernames):
        st.error("Username not found, please sign up.") 
    else:
        st.error("Username or password incorrect.")

if not authentication_status: 
    with st.expander("Sign Up"):
        sign_up()
        
if authentication_status:
    
    time.sleep(1)
    user = username
    user_type, name, email, team = get_user_data("users_db", "users", user)

    if user_type == "Admin":
        
        with st.sidebar:  
            
            Authenticator.logout('Log Out')     
            app = option_menu(
                menu_title='Main menu',
                options=['Admin Options'],
                icons=['person-check-fill'],
                menu_icon='house-fill',
                default_index=0)
        
        if app == "Admin Options":
            
            st.header('Give permissions')
            st.markdown("---")
            
            user_upd = st.selectbox('Select user', usernames)
            value_user_upd = st.selectbox('Select user type', ['Admin', 'User'])
            
            if st.button("Update", type="primary"):
                
                time.sleep(1)
                upd_utype = update_user_type("users_db", "users", "user_type", value_user_upd, user_upd)
                
                if upd_utype:
                    
                    st.success("Updated user")
                    
            
            
       