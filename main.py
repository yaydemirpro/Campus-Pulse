import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, QLabel, QCalendarWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.uic import loadUi
import json
import re
from datetime import datetime
from PyQt5.QtGui import QColor
import mainteacher


os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

class Login(QMainWindow):
    """
    Class representing the login window of the application.

    Attributes:
    - signup_btn: Button for switching to the signup form.
    - contact_adm_btn: Button for switching to the contact admin form.
    - loginbutton: Button for initiating the login process.
    - email_LE: Line edit for entering the email.
    - password_LE: Line edit for entering the password.
    """
        
    def __init__(self):
        """
        Initializes the Login window.

        Connects signals to corresponding slots and loads the UI from 'login.ui'.  
        """
        super(Login, self).__init__()
        loadUi('login.ui', self)

        self.signup_btn.clicked.connect(self.switch_signupform)
        self.contact_adm_btn.clicked.connect(self.switch_adminform)
        self.loginbutton.clicked.connect(self.switch_student)


    def switch_signupform(self):
        """
        Switches to the signup form when the signup button is clicked.
        Clears line edits in the signup form.
        """
        stackedWidget.setCurrentIndex(1)
        signup.clear_line_edits_signupform()

    def switch_adminform(self):
        """
        Switches to the admin form when the contact admin button is clicked.
        Clears line edits in the contact admin form.
        """
        stackedWidget.setCurrentIndex(2)
        cont_admin.clear_line_edits_contactadmin()
    
    def switch_student(self):
        """
        Initiates the login process when the login button is clicked.

        Retrieves email and password, checks against stored accounts, and switches to
        corresponding user interfaces (Student, Teacher, Admin).
        Displays error messages for incorrect credentials or file-related issues.
        """
        email = self.email_LE.text()
        password = self.password_LE.text()
        try:
            with open("accounts.json", "r") as userinfo:
                accounts = json.load(userinfo)
                userprofile.name_line.setText(accounts[email]["name"])
                userprofile.surname_line.setText(accounts[email]["surname"])
                userprofile.telephone_line.setText(accounts[email]["Phone"])
                userprofile.mail_line.setText(accounts[email]["Email"])
                userprofile.type_line.setText(accounts[email]["Account_Type"])
                userprofile.gender_line.setText(accounts[email]["Gender"])
                userprofile.birthdate_line.setText(accounts[email]["DoB"])
                student.label_2.setText("Welcome, "+accounts[email]["name"])
                student.label.setText(accounts[email]["name"]+" "+accounts[email]["surname"])




                if email in accounts:
                    if accounts[email]["password"] == password:
                        if accounts[email]["Account_Type"] == "Student":
                            stackedWidget.setCurrentIndex(3)
                            student.load_attendance()
                            student.load_tasks()
                            student.load_announcements()
                            student.load_calendar_events()
                            student.show_tasks()
                            student.populate_table()
                            student.show_announcements()

                        elif accounts[email]["Account_Type"] == "Teacher":
                            stackedWidget.setCurrentIndex(4)
                            teacher.label_Name.setText(accounts[login.email_LE.text()]["name"]+" "+accounts[login.email_LE.text()]["surname"])
                        elif accounts[email]["Account_Type"] == "Admin":
                            stackedWidget.setCurrentIndex(5)
                            teacher.label_Name.setText(accounts[login.email_LE.text()]["name"]+" "+accounts[login.email_LE.text()]["surname"])
                            admin.fill_table()

                    else:
                        self.show_error_message("The entered password is incorrect. Please verify and re-enter your password to proceed.")  # password is wrong
                else:
                    self.show_error_message("The provided email does not exist in our records. If you need to create an account, please click on the 'Sign Up' button.")  # email doesn't exist

        except FileNotFoundError:
            self.show_error_message("The accounts file is not found. Please check if the file exists.")
        except json.JSONDecodeError:
            self.show_error_message("Error decoding JSON. Please check the file format.")
        except Exception as e:
            self.show_error_message(f"An unexpected error occurred: {str(e)}")

    def show_error_message(self, message): #error messages
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()

    def clear_line_edits_loginform(self):
        """
        Clears line edits in the login form.
        """
        self.email_LE.clear()
        self.password_LE.clear()


class Signup(QMainWindow):
    """
    Class representing the signup window of the application.

    Attributes:
    - sign_up_but: Button for initiating the signup process.
    - Back_Log_but: Button for switching back to the login form.
    - signup_email_LE: Line edit for entering the signup email.
    - signup_password_LE: Line edit for entering the signup password.
    - confirmpass_LE: Line edit for confirming the signup password.
    - name_LE: Line edit for entering the user's name.
    - surname_LE: Line edit for entering the user's surname.
    """
    def __init__(self):
        """
        Initializes the Signup window.

        Connects signals to corresponding slots and loads the UI from 'signup.ui'.
        """
        super(Signup, self).__init__()
        loadUi('signup.ui', self)
        self.sign_up_but.clicked.connect(self.signup_swt_login)
        self.Back_Log_but.clicked.connect(self.switch_loginform)

    def signup_swt_login(self):
        """
        Initiates the signup process when the signup button is clicked.

        Retrieves user input, checks for existing email, password matching,
        and password strength. If all conditions are met, adds the new account
        to the 'accounts.json' file and switches to the login form.
        """
        email = self.signup_email_LE.text()
        password = self.signup_password_LE.text()
        password_conf= self.confirmpass_LE.text()
        good_to_go=False
        try:
            with open("accounts.json", "r") as userinfo:
                accounts = json.load(userinfo)

                if email in accounts:
                    self.show_error_message("The email address provided already exists in our records. If you have an existing account, please proceed to the login page.")  # email exists. if you have an account go to login page.
                elif password != password_conf:
                    self.show_error_message("The passwords entered do not match. Please ensure that the passwords are identical and try again.")
                elif not self.password_strength(password):
                    self.show_error_message("Please use at least 2 uppercase, 2 lowercase, and 2 special characters. Minimum length is 8 characters.")
                else:
                    accounts[email] = {
                        "password": password,
                        "Account_Type": "Student",
                        "name": self.name_LE.text(),
                        "surname": self.surname_LE.text(),
                        "Email": email,
                        "Gender": "",
                        "DoB": "",
                        "Phone": ""
                    }
                    good_to_go = True

        except FileNotFoundError:
            self.show_error_message("The accounts file is not found. Please check if the file exists.")
        except json.JSONDecodeError:
            self.show_error_message("Error decoding JSON. Please check the file format.")
        except Exception as e:
            self.show_error_message(f"An unexpected error occurred: {str(e)}")

                                            
        if good_to_go:
            try:
                with open("accounts.json", "w") as userinfo:
                    json.dump(accounts, userinfo, indent=2)
                stackedWidget.setCurrentIndex(0)
                login.clear_line_edits_loginform()
            except Exception as e:
                self.show_error_message(f"An unexpected error occurred while saving the account information: {str(e)}")


    def switch_loginform(self):
        """
        Switches back to the login form when the 'Back to Login' button is clicked.
        Clears line edits in the login form.
        """
        stackedWidget.setCurrentIndex(0)
        login.clear_line_edits_loginform()

    
    def show_error_message(self, message): #error messages
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()
    
    def password_strength(self, psword):
        """
        Checks the strength of the password.

        Args:
        - psword: The password to be checked.

        Returns:
        - True if the password meets strength requirements, False otherwise.
        """
        if len(psword) < 8:
            return False

        num_of_uppercase = 0
        num_of_lowercase = 0
        num_of_specialchars = 0

        for i in psword:
            if i.isupper():
                num_of_uppercase += 1
            elif i.islower():
                num_of_lowercase += 1
            elif not i.isalnum():
                num_of_specialchars += 1

        if num_of_lowercase < 2 or num_of_uppercase < 2 or num_of_specialchars < 2:
            return False

        return True
    
    def clear_line_edits_signupform(self):
        """
        Clears line edits in the signup form.
        """
        self.signup_email_LE.clear()
        self.signup_password_LE.clear()
        self.confirmpass_LE.clear()
        self.name_LE.clear()
        self.surname_LE.clear()
    
class ContactAdmin(QMainWindow):
    """
    Class representing the contact admin window of the application.

    Attributes:
    - Back_to_login_but: Button for switching back to the login form.
    - Create_TA_but: Button for creating a TA (Teacher Assistant) account.
    - TA_email_LE: Line edit for entering the TA's email.
    - TA_password_LE: Line edit for entering the TA's password.
    - TA_confirmpass_LE: Line edit for confirming the TA's password.
    - TA_name_LE: Line edit for entering the TA's name.
    - TA_surname_LE: Line edit for entering the TA's surname.
    """
    def __init__(self):
        """
        Initializes the ContactAdmin window.

        Connects signals to corresponding slots and loads the UI from 'contactadmin.ui'.
        """
        super(ContactAdmin, self).__init__()
        loadUi('contactadmin.ui', self)
        self.Back_to_login_but.clicked.connect(self.switch_loginform)
        self.Create_TA_but.clicked.connect(self.send_TA_Account)

    def switch_loginform(self):
        """
        Switches back to the login form when the 'Back to Login' button is clicked.
        Clears line edits in the login form.
        """
        stackedWidget.setCurrentIndex(0)
        login.clear_line_edits_loginform()

    
    def password_strength(self, psword):
        if len(psword) < 8:
            return False

        num_of_uppercase = 0
        num_of_lowercase = 0
        num_of_specialchars = 0

        for i in psword:
            if i.isupper():
                num_of_uppercase += 1
            elif i.islower():
                num_of_lowercase += 1
            elif not i.isalnum():
                num_of_specialchars += 1

        if num_of_lowercase < 2 or num_of_uppercase < 2 or num_of_specialchars < 2:
            return False

        return True

    def show_error_message(self, message): #error messages
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()

    def send_TA_Account(self):
        """
        Sends a request to create a Teacher Assistant (TA) account.

        Retrieves user input, checks for existing requests, existing accounts,
        password matching, and password strength. If all conditions are met,
        adds the new TA account request to the 'TA_tobecreated.json' file.
        """
        email = self.TA_email_LE.text()
        password = self.TA_password_LE.text()
        password_conf= self.TA_confirmpass_LE.text()
        good_to_go=False
        try:
            with open("TA_tobecreated.json", "r") as pendinginfo:
                pending_accounts = json.load(pendinginfo)

            if email in pending_accounts:
                self.show_error_message("You have already applied for creating an account. Admin will create your account in 24 hours")  # Pending account.
            else:
                try:
                    with open("accounts.json", "r") as userinfo:
                        accounts = json.load(userinfo)

                    if email in accounts:
                        self.show_error_message("The email address provided already exists in our records. If you have an existing account, please proceed to the login page.")  # email exists. if you have an account go to login page.
                    elif password != password_conf:
                        self.show_error_message("The passwords entered do not match. Please ensure that the passwords are identical and try again.")
                    elif not self.password_strength(password):
                        self.show_error_message("Please use at least 2 uppercase, 2 lowercase, and 2 special characters. Minimum length is 8 characters.")
                    else:
                        pending_accounts[email] = {
                            "password": password,
                            "Account_Type": "Teacher",
                            "name": self.TA_name_LE.text(),
                            "surname": self.TA_surname_LE.text()
                        }

                        with open("TA_tobecreated.json", "w") as pendinginfo:
                            json.dump(pending_accounts, pendinginfo, indent=2)

                        stackedWidget.setCurrentIndex(0)

                except FileNotFoundError:
                    self.show_error_message("The accounts file is not found. Please check if the file exists.")
                except json.JSONDecodeError:
                    self.show_error_message("Error decoding JSON. Please check the file format.")
                except Exception as e:
                    self.show_error_message(f"An unexpected error occurred while processing the accounts file: {str(e)}")

        except FileNotFoundError:
            self.show_error_message("The pending accounts file is not found. Please check if the file exists.")
        except json.JSONDecodeError:
            self.show_error_message("Error decoding JSON. Please check the file format.")
        except Exception as e:
            self.show_error_message(f"An unexpected error occurred while processing the pending accounts file: {str(e)}")

    def clear_line_edits_contactadmin(self):
        """
        Clears line edits in the contact admin form.
        """
        self.TA_email_LE.clear()
        self.TA_password_LE.clear()
        self.TA_confirmpass_LE.clear()
        self.TA_name_LE.clear()
        self.TA_surname_LE.clear()



# class Student(QMainWindow):
#     def __init__(self):
#         super(Student, self).__init__()
#         loadUi('student.ui', self)
#         # self.Back_Log_but.clicked.connect(self.switch_loginform)


#     def switch_loginform(self):
#         stackedWidget.setCurrentIndex(0)

class Teacher(QMainWindow):
    def __init__(self):
        super(Teacher, self).__init__()
        loadUi('teacher_page.ui', self)
        self.Back_Log_but.clicked.connect(self.switch_loginform)
        self.Chatboard_but.clicked.connect(self.switch_chatboard)
        
    def switch_loginform(self):
        stackedWidget.setCurrentIndex(0)
    
    def switch_chatboard(self):
        stackedWidget.setCurrentIndex(6)
        chatboard.fill_user_list2()

class User_Profile(QMainWindow):
    def __init__(self):
        super(User_Profile, self).__init__()
        loadUi('user_profile_information.ui', self)
        self.save_pushButton.clicked.connect(self.save_profile)
        self.Back_Button.clicked.connect(self.switch_previous_form)
        
    def save_profile(self):
        user_mail=login.email_LE.text()
        with open("accounts.json", "r") as userinfo:
            accounts = json.load(userinfo)
        accounts[user_mail]["name"]=userprofile.name_line.text()
        accounts[user_mail]["surname"]=userprofile.surname_line.text()
        accounts[user_mail]["Phone"]=userprofile.telephone_line.text()
        accounts[user_mail]["Gender"]=userprofile.gender_line.text()
        accounts[user_mail]["DoB"]=userprofile.birthdate_line.text()

        with open("accounts.json", "w") as userinfo:
            json.dump(accounts, userinfo, indent=2)

    def switch_previous_form(self):
        with open("accounts.json", "r") as userinfo:
            accounts = json.load(userinfo)
        if accounts[login.email_LE.text()]["Account_Type"]=="Student":
            stackedWidget.setCurrentIndex(3)
        elif accounts[login.email_LE.text()]["Account_Type"]=="Teacher":
            stackedWidget.setCurrentIndex(4)
        elif accounts[login.email_LE.text()]["Account_Type"]=="Admin":
            stackedWidget.setCurrentIndex(5)


class Admin(QMainWindow):
    """
    Class representing the admin window of the application.

    Attributes:
    - Back_Log_but: Button for switching back to the login form.
    - Approve_but: Button for approving selected accounts.
    - Discard_but: Button for discarding selected accounts.
    - tableWidget: Table widget for displaying pending TA accounts.
    """
    def __init__(self):
        """
        Initializes the Admin window.

        Connects signals to corresponding slots, sets up the table, and fills it with data.
        """
        super(Admin, self).__init__()
        loadUi('admin.ui', self)

        self.Back_Log_but.clicked.connect(self.switch_teacherform)
        self.Chatboard_but.clicked.connect(self.switch_chatboard)
        self.Approve_but.clicked.connect(self.approve_account)
        self.Discard_but.clicked.connect(self.discard_account)
        self.tableWidget.setColumnWidth(0,50)
        self.tableWidget.setColumnWidth(1,150)
        self.tableWidget.setColumnWidth(2,150)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels([ "Select", "Email", "Name", "Surname"])
        self.fill_table()


    def fill_table(self):
       """
        Fills the table with pending TA account data.
        """
       try:
          with open("TA_tobecreated.json", "r") as pendinginfo:
                pending_accounts = json.load(pendinginfo)
                row = 0
                self.tableWidget.setRowCount(len(pending_accounts))
                for emails in pending_accounts:
                    checkbox = QCheckBox()
                    self.tableWidget.setCellWidget(row, 0, checkbox)
                    self.tableWidget.setItem(row, 1, QTableWidgetItem(emails))
                    self.tableWidget.setItem(row, 2, QTableWidgetItem(pending_accounts[emails]["name"]))
                    self.tableWidget.setItem(row, 3, QTableWidgetItem(pending_accounts[emails]["surname"]))

                    row += 1
       except Exception as e:
           print(f"Error loading data: {e}")


    def approve_account(self):
        """
        Approves selected accounts and updates the tables accordingly.
        """
        pendinginfo = open("TA_tobecreated.json", "r")
        pending_accounts = json.load(pendinginfo)
        userinfo = open("accounts.json", "r")
        accounts = json.load(userinfo)
        pending_accounts_rest=dict()
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.cellWidget(row, 0)
            email_item = self.tableWidget.item(row, 1)
            email_key = email_item.text() if email_item else None
            if checkbox.isChecked():
                if email_key in pending_accounts:
                    accounts[email_key] = {
                        "password": pending_accounts[email_key]["password"],
                        "Account_Type": "Teacher",
                        "name": pending_accounts[email_key]["name"],
                        "surname": pending_accounts[email_key]["surname"]
                    }
            else:
                pending_accounts_rest[email_key] = {
                    "password": pending_accounts[email_key]["password"],
                    "Account_Type": "Teacher",
                    "name": pending_accounts[email_key]["name"],
                    "surname": pending_accounts[email_key]["surname"]
                 }

                
        pendinginfo.close()
        userinfo.close()
        with open("accounts.json", "w") as userinfo:
                json.dump(accounts, userinfo, indent=2)
        with open("TA_tobecreated.json", "w") as pendinginfo:
                json.dump(pending_accounts_rest, pendinginfo, indent=2)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(pending_accounts_rest))
        row = 0
        for emails in pending_accounts_rest:
            checkbox = QCheckBox()
            self.tableWidget.setCellWidget(row, 0, checkbox)
            self.tableWidget.setItem(row, 1, QTableWidgetItem(emails))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(pending_accounts_rest[emails]["name"]))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(pending_accounts_rest[emails]["surname"]))
            row += 1            

    def discard_account(self):
        """
        Discards selected accounts and updates the tables accordingly.
        """
        pendinginfo = open("TA_tobecreated.json", "r")
        pending_accounts = json.load(pendinginfo)
        pending_accounts_rest=dict()
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.cellWidget(row, 0)
            email_item = self.tableWidget.item(row, 1)
            email_key = email_item.text() if email_item else None
            if not checkbox.isChecked():
                if email_key in pending_accounts:
                    pending_accounts_rest[email_key] = {
                        "password": pending_accounts[email_key]["password"],
                        "Account_Type": "Teacher",
                        "name": pending_accounts[email_key]["name"],
                        "surname": pending_accounts[email_key]["surname"]
                    }
             
        pendinginfo.close()
        with open("TA_tobecreated.json", "w") as pendinginfo:
                json.dump(pending_accounts_rest, pendinginfo, indent=2)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(pending_accounts_rest))
        row = 0
        for emails in pending_accounts_rest:
            checkbox = QCheckBox()
            self.tableWidget.setCellWidget(row, 0, checkbox)
            self.tableWidget.setItem(row, 1, QTableWidgetItem(emails))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(pending_accounts_rest[emails]["name"]))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(pending_accounts_rest[emails]["surname"]))
            row += 1   

    def switch_teacherform(self):
        stackedWidget.setCurrentIndex(4)

    def switch_chatboard(self):
        stackedWidget.setCurrentIndex(6)
        chatboard.fill_user_list2()
    
class Chatboard(QMainWindow):
    """
    Class representing the chatboard window of the application.

    Attributes:
    - Back_TF_but: Button for switching back to the teacher form.
    - Send_but: Button for sending a message.
    - usertableWidget: Table widget for displaying user information.
    - history_LE: Line edit for displaying chat history.
    - send_TE: Text edit for typing and sending messages.
    """
    def __init__(self):
        """
        Initializes the Chatboard window.

        Connects signals to corresponding slots, sets up the user table, and initializes UI elements.
        """
        super(Chatboard, self).__init__()
        loadUi('chatbot.ui', self)
        # self.usertableWidget.setColumnWidth(0,10)
        self.usertableWidget.setColumnWidth(0,400)
        # self.usertableWidget.setColumnCount(2)
        # self.usertableWidget.setHorizontalHeaderLabels([ "","Name"])
        self.usertableWidget.setColumnCount(2)
        self.usertableWidget.setHorizontalHeaderLabels(["Name","Email"])
        # self.fill_user_list2()
        self.Back_TF_but.clicked.connect(self.switch_previous_form)
        self.Send_but.clicked.connect(self.send_message)
        self.usertableWidget.itemSelectionChanged.connect(self.selection)
        self.history_LE.setReadOnly(True)


    def fill_user_list2(self):
        """
        Fills the user table with user information and unread message counts.
        """
        try:
            with open("chats.json", "r") as chatinfo:
                chat_entries = json.load(chatinfo)
        except Exception as e:
            print(f"Error loading data: {e}")
            return
        
        try:
            with open("accounts.json", "r") as userinfo:
                user_accounts = json.load(userinfo)
        except Exception as e:
            print(f"Error loading data: {e}")
            return

        unread_list=dict()

        user_email = login.email_LE.text()


        try:
            for i in user_accounts:
                unread_count = 0
                msg_count = 1
                if i not in chat_entries[user_email]:
                    unread_list[i] = 0
                else:
                    for j in chat_entries[user_email][i]:
                        messageid = "message" + str(msg_count)
                        if (
                            messageid in chat_entries[user_email][i]
                            and chat_entries[user_email][i][messageid]["read"] == 0
                            and chat_entries[user_email][i][messageid]["Status"] == "Received"
                        ):
                            unread_count += 1
                        msg_count += 1
                    unread_list[i] = unread_count
        except Exception as e:
            print(f"Error loading data: {e}")
        
        row = 0
        self.usertableWidget.setRowCount(len(user_accounts))
        self.usertableWidget.setColumnWidth(0, 185)
        self.usertableWidget.setColumnWidth(1, 0)


#Emailin chats.jsonda yer almaması durumunda hata veriyor. Düzeltilmesi gerekiyor.
        

        for email, data in user_accounts.items():
            unread_count = unread_list.get(email, 0)
            if unread_count > 0:
                self.usertableWidget.setItem(
                    row,
                    0,
                    QTableWidgetItem(data["surname"] + ", " + data["name"] + " (" + str(unread_list[email]) + ")"),
                )
                self.usertableWidget.item(row, 0).setBackground(QColor(255, 0, 0))
            else:
                self.usertableWidget.setItem(row, 0, QTableWidgetItem(data["surname"] + ", " + data["name"]))
            self.usertableWidget.setItem(row, 1, QTableWidgetItem(email))
            row += 1




    def selection(self):
        """
        Handles user selection from the user table and displays the chat history.
        """
        selected_items = self.usertableWidget.selectedItems()

        if not selected_items:
            return
        selected_row=selected_items[0].row()
        recipient=self.usertableWidget.item(selected_row,1).text()

        user_email = login.email_LE.text()


        with open("accounts.json", "r") as userinfo:
            accounts=json.load(userinfo)
            name_of_sender=accounts[user_email]["name"]
            name_of_recepient=accounts[recipient]["name"]

        with open("chats.json", "r") as chatinfo:
            chat_entries=json.load(chatinfo)

            # Check if user_email and recipient exist in chat_entries
        if user_email not in chat_entries or recipient not in chat_entries[user_email]:
            if hasattr(self, 'history_LE'):
                self.history_LE.setText("")
            return


        for key in chat_entries[user_email][recipient]:
            inner_dict = chat_entries[user_email][recipient][key]
            inner_dict["read"]=1

        with open("chats.json", "w") as chatinfo:
            json.dump(chat_entries, chatinfo, indent=2)
        

        count=0

        chat_recipient = chat_entries[user_email].get(recipient, {})

        if not chat_recipient:
            if hasattr(self, 'history_LE'):
                self.history_LE.setText("")
            return

        for i in chat_entries[user_email][recipient]:
            if count==0:
                time1=chat_entries[user_email][recipient][i]["Time"]
                sender=chat_entries[user_email][recipient][i]["Status"]
                message=chat_entries[user_email][recipient][i]["Message"]
                formatted_date1 = datetime.fromtimestamp(time1).strftime("%A, %B %d")
                formatted_time=datetime.fromtimestamp(time1).strftime("%H:%M")
                padding = "-" * ((50 - len(formatted_date1)) // 2)
                if hasattr(self, 'history_LE'):
                    self.history_LE.setText(padding + formatted_date1 + padding + "\n")
                    if sender == "Sent":
                        self.history_LE.append("you : " + formatted_time + "\n" + message + "\n")
                    else:
                        self.history_LE.insertPlainText(name_of_recepient+ " : " + formatted_time + "\n" + message + "\n")

                count+=1
            else:
                time2=chat_entries[user_email][recipient][i]["Time"]
                sender=chat_entries[user_email][recipient][i]["Status"]
                message=chat_entries[user_email][recipient][i]["Message"]
                formatted_date2 = datetime.fromtimestamp(time2).strftime("%A, %B %d")
                formatted_time=datetime.fromtimestamp(time2).strftime("%H:%M")
                if formatted_date1==formatted_date2:
                    if sender=="Sent":
                        self.history_LE.append("you : " + formatted_time + "\n" + message+"\n")

                    else:
                        self.history_LE.append(name_of_recepient + " : " + formatted_time + "\n" + message+"\n")

                else:
                    padding = "-" * ((50 - len(formatted_date2)) // 2)

                    self.history_LE.append(padding + formatted_date2 + padding+"\n")
                    if sender=="Sent":
                        self.history_LE.append("you : " + formatted_time + "\n" + message+"\n")

                    else:
                        self.history_LE.append(name_of_recepient + " : " + formatted_time + "\n" + message+"\n")

                count+=1
                formatted_date1=formatted_date2        

        count=0
        self.fill_user_list2()


    
    def send_message(self):
        """
        Sends a message to the selected recipient and updates the chat entries.
        """
        message=self.send_TE.toPlainText()
        # user_email=login.email_LE.text()
        selected_items = self.usertableWidget.selectedItems()
        user_email = login.email_LE.text()

        if not selected_items:
            return
        
        selected_row=selected_items[0].row()
        recipient=self.usertableWidget.item(selected_row,1).text()
        
        with open("chats.json", "r") as chat_file:
            chat_entries = json.load(chat_file)
        
        if user_email not in chat_entries:
            chat_entries[user_email] = {}
        
        chat_entries.setdefault(user_email, {})
        chat_entries.setdefault(recipient, {})
        
        time=datetime.now().timestamp()
        new_message_key_user = f"message{len(chat_entries[user_email].get(recipient, {})) + 1}"
        new_message_key_recipient = f"message{len(chat_entries[recipient].get(user_email, {})) + 1}"
        # new_message_key = f"message{len(chat_entries[user_email][recipient]) + 1}"

        chat_entries[user_email].setdefault(recipient, {})[new_message_key_user] = {
        "Time": time,
        "Status": "Sent",
        "read": 1,
        "Message": message
        }

        chat_entries[recipient].setdefault(user_email, {})[new_message_key_recipient] = {
        "Time": time,
        "Status": "Received",
        "read": 0,
        "Message": message
        }

        with open("chats.json", "w") as chat_file:
            json.dump(chat_entries, chat_file, indent=2) 
        
        self.send_TE.setText("")
        self.selection()

        
    def switch_previous_form(self):
        with open("accounts.json", "r") as userinfo:
            accounts = json.load(userinfo)
        if accounts[login.email_LE.text()]["Account_Type"]=="Student":
            stackedWidget.setCurrentIndex(3)
        elif accounts[login.email_LE.text()]["Account_Type"]=="Teacher":
            stackedWidget.setCurrentIndex(4)
        elif accounts[login.email_LE.text()]["Account_Type"]=="Admin":
            stackedWidget.setCurrentIndex(5)
    
    def switch_chatboard(self):
        stackedWidget.setCurrentIndex(6)
        chatboard.fill_user_list2()


class Main_Window(QMainWindow):
    def __init__(self):
        super(Main_Window, self).__init__()


        loadUi('student.ui', self)  # UI dosyasını yükle
        # loadUi(r'C:\Users\Gebruiker\Desktop\Python\PYQT5\calendar\student - Kopya (2).ui', self)  # UI dosyasını yükle
        self.pushButton.clicked.connect(self.switch_chatboard)
        self.pushButton_2.clicked.connect(self.switch_userprofile)

        self.setFixedSize(900,600)
        self.setWindowTitle('Campus Pulse')
        

        self.note_edit = self.findChild(QLabel, 'note_edit')  # UI dosyasındaki note_edit adlı öğeyi bul
        self.calendar = self.findChild(QCalendarWidget, 'calendarWidget')  # UI dosyasındaki calendarWidget adlı öğeyi bul
        self.mission_complete = self.findChild(QPushButton, 'self.mission_complete') 

        # self.load_attendance()
        # self.load_tasks()
        # self.load_announcements()
        # self.load_calendar_events()
        # self.show_tasks()
        # self.populate_table()
        # self.show_announcements()
        self.calendar.clicked.connect(self.load_calendar_events)
        self.comboBox_2.currentIndexChanged.connect(self.populate_table)
        self.comboBox_3.currentIndexChanged.connect(self.populate_table)
        # self.check()

        

#load file

    def load_attendance(self):
        try:
            with open('attendance.json', 'r') as file_2:
                self.attendance = json.load(file_2)
        except FileNotFoundError:
            self.attendance = {}

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file_3:
                self.tasks = json.load(file_3)
        except FileNotFoundError:
            self.tasks = {}

    def load_announcements(self):
        try:
            with open('announcements.json', 'r') as file_4:
                self.announcements = json.load(file_4)
        except FileNotFoundError:
            self.announcements = {}

#meeting calendar
    def load_calendar_events(self):
        self.mail = login.email_LE.text()

        if self.mail in self.attendance:
            meeting = self.attendance[self.mail]
            mentor = meeting["Mentor Meeting"]
            data_science = meeting["Data Science"]
        
            for date_str in mentor.keys():
                date = QDate.fromString(str(date_str), Qt.ISODate)
                if date.isValid():  #and result1==['Mentor']:
                    self.calendar.setDateTextFormat(date, self.get_calendar_event_format1())

            for date_str in data_science.keys():
                date = QDate.fromString(str(date_str), Qt.ISODate)
                if date.isValid():  #and result2==['Data Science']:
                    self.calendar.setDateTextFormat(date, self.get_calendar_event_format2())

            selected_date = self.calendar.selectedDate().toString(Qt.ISODate)
            if selected_date in data_science:
                self.note_edit.setText('Data Science Course')
            elif selected_date in mentor:
                self.note_edit.setText('Mentor Meeting')
            else:
                self.note_edit.clear()
        else:
            pass


    def get_calendar_event_format1(self):
        format = self.calendar.dateTextFormat(self.calendar.selectedDate())
        font = format.font()
        font.setBold(True)  # Metni bold yap
        format.setFont(font)
        format.setForeground(Qt.red)
        format.setBackground(Qt.green)
        return format
    
    def get_calendar_event_format2(self):
        format = self.calendar.dateTextFormat(self.calendar.selectedDate())
        font = format.font()
        font.setBold(True)  # Metni bold yap
        format.setFont(font)
        format.setForeground(Qt.green)
        format.setBackground(Qt.red)
        return format   

#status of attendance
    def populate_table(self):
        self.mail = login.email_LE.text()

        if self.mail in self.attendance:
      
            for i in range(self.tableWidget.rowCount() - 1, -1, -1):
                is_row_empty = all(self.tableWidget.item(i, j) is None or self.tableWidget.item(i, j).text() == '' for j in range(self.tableWidget.columnCount()))
                if not is_row_empty:
                    self.tableWidget.removeRow(i)

            filter_statu1 = self.comboBox_2.currentText()
            filter_statu2 = self.comboBox_3.currentText()

            dates = self.attendance[self.mail]
            result = dates[filter_statu1]
            for date, value in result.items():

                if value==filter_statu2 and QDate.fromString(date, "yyyy-MM-dd") <= QDate.currentDate():
                    row_position = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(row_position)
                    item_date = QTableWidgetItem(date)
                    item_value = QTableWidgetItem(str(value))
                    self.tableWidget.setItem(row_position, 0, item_value)
                    self.tableWidget.setVerticalHeaderItem(row_position, item_date)
                if filter_statu2=='Make your choice' and (filter_statu1=='Mentor Meeting' or filter_statu1=='Data Science') and QDate.fromString(date, "yyyy-MM-dd") <= QDate.currentDate():
                    row_position = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(row_position)
                    item_date = QTableWidgetItem(date)
                    item_value = QTableWidgetItem(str(value))
                    self.tableWidget.setItem(row_position, 0, item_value)
                    self.tableWidget.setVerticalHeaderItem(row_position, item_date)
        else:
            pass

                # value_str = str(value)
                # symbol = '\u2717'
                # value_with_symbol = f"{value_str} {symbol}"

                # # QTableWidgetItem oluştur ve tabloya ekle
                # item_value = QTableWidgetItem(value_with_symbol)
                # self.tableWidget.setItem(row_position, 0, item_value)
                # self.tableWidget.setVerticalHeaderItem(row_position, item_date)

# to do list
    def show_tasks(self):
        self.mail = login.email_LE.text()

        if self.mail in self.tasks:

            assignment=self.tasks[self.mail]
            self.mission=assignment['tasks']
            self.check_boxes = []

        
            for i in self.mission:
                row_position = self.table_todolist.rowCount()
            
                self.table_todolist.insertRow(row_position)
                self.table_todolist.setItem(row_position, 1, QTableWidgetItem(str(i['task'])))
                self.table_todolist.setItem(row_position, 2, QTableWidgetItem(i['deadline']))
                self.table_todolist.setVerticalHeaderItem(row_position, QTableWidgetItem(str(i['id'])))
            
                self.check_box = QCheckBox()
                if self.mission[row_position]['status'] == True:
                    self.check_box.setChecked(True)
                else:
                    self.check_box.setChecked(False)
                self.table_todolist.setCellWidget(row_position,0, self.check_box)

                self.check_boxes.append(self.check_box)

        

            self.table_todolist.setColumnWidth(0,30)
            self.table_todolist.setColumnWidth(1,415)
            self.table_todolist.setColumnWidth(2,100)
     

            self.connect_check_boxes()
        else:
            pass

# to do list check
    def connect_check_boxes(self):
        for row, check_box in enumerate(self.check_boxes):
            check_box.stateChanged.connect(lambda state, r=row: self.onCheckBoxStateChanged(state, r))

    def onCheckBoxStateChanged(self, state, row):
        self.mail = login.email_LE.text()
        if self.mail in self.tasks:
            self.assignment=self.tasks[self.mail]

            if state == 2:  # Qt.Checked
                self.mission[row]['status'] = True   
            else:
                self.mission[row]['status'] = False 

            with open('tasks.json', 'w') as json_file:
                    json.dump(self.tasks, json_file, indent=2)
        else:
            pass
        # print(self.mission[row]['status'])
            


# # announcements  
    def show_announcements(self):
        # content=self.announcements["content"]
        # print(t)
        # for k in self.announcements:
            # row = self.announcement_widget.rowCount()
            
            # self.announcement_widget.insertRow(row)
            # self.announcement_widget.setItem(row, 0, QTableWidgetItem(k["content"]))
            # self.announcement_widget.setVerticalHeaderItem(row_position, QTableWidgetItem(str(i['id'])))
            
        self.announcement_index = 0  # Sıradaki anonsun indeksi

        # QTimer oluştur
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_announcements)
        self.timer.start(1500)  # 5 saniyede bir kontrol et
        self.update_announcements()  # Başlangıçta da çalıştır

    def update_announcements(self):
        # Anonsları güncelle
        if self.announcement_index < len(self.announcements):
            announcement = self.announcements[self.announcement_index]
            last_date = announcement.get("last_date")
            current_date = datetime.now().strftime("%Y-%m-%d")
            if last_date >= current_date:
                self.announcement_textedit.setText('')
                self.announcement_textedit.setText('  \u2605  ' + announcement['content']) #ekranda sola bitisik yazmasin

            # Bir sonraki anonsa geç
            self.announcement_index += 1
        else:
            # Anons listesinin sonuna gelindiğinde başa dön
            self.announcement_index = 0
    
    def switch_chatboard(self):
        stackedWidget.setCurrentIndex(6)
        chatboard.fill_user_list2()

    def switch_login(self):
        stackedWidget.setCurrentIndex(0)
        login.clear_line_edits_loginform()
    
    def switch_userprofile(self):
        stackedWidget.setCurrentIndex(7)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    stackedWidget = QStackedWidget()

    login = Login()
    signup = Signup()
    cont_admin = ContactAdmin()
    student=Main_Window()
    teacher=mainteacher.MyMainWindow()
    admin=Admin()
    chatboard=Chatboard()
    userprofile=User_Profile()



    login.setFixedSize(900, 600)  
    signup.setFixedSize(900, 600)
    cont_admin.setFixedSize(900, 600)
    student.setFixedSize(900, 600)
    teacher.setFixedSize(900, 600)
    admin.setFixedSize(900, 600)
    chatboard.setFixedSize(900, 600)
    userprofile.setFixedSize(900, 600)





    stackedWidget.addWidget(login)
    stackedWidget.addWidget(signup)
    stackedWidget.addWidget(cont_admin)
    stackedWidget.addWidget(student)
    stackedWidget.addWidget(teacher)
    stackedWidget.addWidget(admin)
    stackedWidget.addWidget(chatboard)
    stackedWidget.addWidget(userprofile)



    stackedWidget.show()
    sys.exit(app.exec_())
