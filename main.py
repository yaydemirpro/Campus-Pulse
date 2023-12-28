import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QWidget
from PyQt5.uic import loadUi
import json
import re

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        loadUi('login.ui', self)

        self.signup_btn.clicked.connect(self.switch_signupform)
        self.contact_adm_btn.clicked.connect(self.switch_adminform)
        self.loginbutton.clicked.connect(self.switch_student)


    def switch_signupform(self):
        stackedWidget.setCurrentIndex(1)
        signup.clear_line_edits_signupform()

    def switch_adminform(self):
        stackedWidget.setCurrentIndex(2)
        cont_admin.clear_line_edits_contactadmin()
    
    def switch_student(self):
        email = self.email_LE.text()
        password = self.password_LE.text()
        with open("accounts.json", "r") as userinfo:
            accounts = json.load(userinfo)

            if email in accounts:
                if accounts[email]["password"] == password:
                    if accounts[email]["Account_Type"] == "Student":
                        stackedWidget.setCurrentIndex(3)
                        student.resize(825, 600)
                    elif accounts[email]["Account_Type"] == "Teacher":
                        stackedWidget.setCurrentIndex(4)
                        teacher.resize(825, 600)
                    elif accounts[email]["Account_Type"] == "Admin":
                        stackedWidget.setCurrentIndex(5)
                        admin.resize(825, 600)
                        admin.setFixedSize(825, 600)

                else:
                    self.show_error_message("The entered password is incorrect. Please verify and re-enter your password to proceed.") #password is wrong
            else:
                self.show_error_message("The provided email does not exist in our records. If you need to create an account, please click on the 'Sign Up' button.")  #email doesn't exist

    def show_error_message(self, message): #error messages
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()

    def clear_line_edits_loginform(self):
        self.email_LE.clear()
        self.password_LE.clear()


class Signup(QMainWindow):
    def __init__(self):
        super(Signup, self).__init__()
        loadUi('signup.ui', self)
        self.sign_up_but.clicked.connect(self.signup_swt_login)
        self.Back_Log_but.clicked.connect(self.switch_loginform)

    def signup_swt_login(self):
        email = self.signup_email_LE.text()
        password = self.signup_password_LE.text()
        password_conf= self.confirmpass_LE.text()
        good_to_go=False
        with open("accounts.json", "r") as userinfo:
            accounts = json.load(userinfo)
            if email in accounts:
                self.show_error_message("The email address provided already exists in our records. If you have an existing account, please proceed to the login page.")  #email exists. if you have an account go to login page.
            elif password!=password_conf:
                self.show_error_message("The passwords entered do not match. Please ensure that the passwords are identical and try again.")
            elif self.password_strength(password)==False:
                 self.show_error_message("Please use at least 2 uppercase, 2 lowercase, and 2 special characters. Minimum length is 8 characters.")
            else: 
                accounts[email] = {
                    "password": password,
                    "Account_Type": "Student", 
                    "name": self.name_LE.text(),
                    "surname": self.surname_LE.text()
                }
                good_to_go=True
                                            
        if good_to_go:
            with open("accounts.json", "w") as userinfo:
                json.dump(accounts, userinfo, indent=2)        
            stackedWidget.setCurrentIndex(0)
        login.clear_line_edits_loginform()


    def switch_loginform(self):
        stackedWidget.setCurrentIndex(0)
        login.clear_line_edits_loginform()

    
    def show_error_message(self, message): #error messages
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()
    
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
    
    def clear_line_edits_signupform(self):
        self.signup_email_LE.clear()
        self.signup_password_LE.clear()
        self.confirmpass_LE.clear()
        self.name_LE.clear()
        self.surname_LE.clear()
    
class ContactAdmin(QMainWindow):
    def __init__(self):
        super(ContactAdmin, self).__init__()
        loadUi('contactadmin.ui', self)
        self.Back_to_login_but.clicked.connect(self.switch_loginform)
        self.Create_TA_but.clicked.connect(self.send_TA_Account)

    def switch_loginform(self):
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
        email = self.TA_email_LE.text()
        password = self.TA_password_LE.text()
        password_conf= self.TA_confirmpass_LE.text()
        good_to_go=False
        pendinginfo= open("TA_tobecreated.json","r")
        pending_accounts=json.load(pendinginfo)
        if email in pending_accounts:
            self.show_error_message("You have already applied for creating an account. Admin will create your account in 24 hours")  #Pending account.
            pendinginfo.close()
        else:
            with open("accounts.json", "r") as userinfo:
                accounts = json.load(userinfo)
                if email in accounts:
                    self.show_error_message("The email address provided already exists in our records. If you have an existing account, please proceed to the login page.")  #email exists. if you have an account go to login page.
                elif password!=password_conf:
                    self.show_error_message("The passwords entered do not match. Please ensure that the passwords are identical and try again.")
                elif self.password_strength(password)==False:
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

    def clear_line_edits_contactadmin(self):
        self.TA_email_LE.clear()
        self.TA_password_LE.clear()
        self.TA_confirmpass_LE.clear()
        self.TA_name_LE.clear()
        self.TA_surname_LE.clear()



class Student(QMainWindow):
    def __init__(self):
        super(Student, self).__init__()
        loadUi('student.ui', self)
        self.Back_Log_but.clicked.connect(self.switch_loginform)

    def switch_loginform(self):
        stackedWidget.setCurrentIndex(0)

class Teacher(QMainWindow):
    def __init__(self):
        super(Teacher, self).__init__()
        loadUi('teacher.ui', self)
        self.Back_Log_but.clicked.connect(self.switch_loginform)
        
    def switch_loginform(self):
        stackedWidget.setCurrentIndex(0)
        login.resize(450, 600)

class Admin(QMainWindow):
    def __init__(self):
        super(Admin, self).__init__()
        loadUi('admin.ui', self)

        self.Back_Log_but.clicked.connect(self.switch_loginform)
        self.tableWidget.setColumnWidth(0,250)
        self.tableWidget.setColumnWidth(1,150)
        self.tableWidget.setColumnWidth(2,150)
        
    def switch_loginform(self):
        stackedWidget.setCurrentIndex(0)
        login.resize(450, 600)
        login.setFixedSize(450, 600)
    
    def loaddata(self):
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)

    stackedWidget = QStackedWidget()

    login = Login()
    signup = Signup()
    cont_admin = ContactAdmin()
    student=Student()
    teacher=Teacher()
    admin=Admin()



    login.setFixedSize(450, 600)  
    signup.setFixedSize(450, 600)
    cont_admin.setFixedSize(450, 600)
    student.setFixedSize(450, 600)
    teacher.setFixedSize(450, 600)





    stackedWidget.addWidget(login)
    stackedWidget.addWidget(signup)
    stackedWidget.addWidget(cont_admin)
    stackedWidget.addWidget(student)
    stackedWidget.addWidget(teacher)
    stackedWidget.addWidget(admin)


    stackedWidget.show()
    sys.exit(app.exec_())
