
from PyQt5.QtWidgets import QTableWidget, QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime
import json
from Ui_teacher_page import Ui_MainWindow
from PyQt5.uic import loadUi
import main

class TaskManager:
    def __init__(self):
        self.load_data()

    def load_data(self):
        # accounts.json, tasks.json ve announcements.json dosyalarını oku
        
        with open('accounts.json', 'r') as f:
            self.accounts_data = json.load(f)

        with open('tasks.json', 'r') as f:
            self.tasks_data = json.load(f)

        try:    
            with open('attendance.json', 'r') as f:
                self.attendance_data = json.load(f)    
        except (FileNotFoundError, json.JSONDecodeError):
            self.attendance_data = {}

        try:
            with open('announcements.json', 'r') as f:
                self.announcements_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.announcements_data = []


    def populate_students_list(self):
        # accounts.json dosyasındaki 'Student' olan öğrencileri listWidget_StudentList'e ekle
        students = [data for data in self.accounts_data.values() if data.get("Account_Type") == "Student"]
        for student in students:
            email = student.get("Email", "")
            name = student.get("name", "")
            surname = student.get("surname", "")
            self.listWidget_studentlist.addItem(f"{name} {surname} ({email})")


    def save_data(self):
        # accounts.json, tasks.json ve announcements.json dosyalarına verileri yaz
        with open('accounts.json', 'w') as f:
            json.dump(self.accounts_data, f, indent=2)

        with open('tasks.json', 'w') as f:
            json.dump(self.tasks_data, f, indent=2)

        with open('announcements.json', 'w') as f:
            json.dump(self.announcements_data, f, indent=2)

        # attendance.json dosyasına verileri yaz
        with open('attendance.json', 'w') as f:
            json.dump(self.attendance_data, f, indent=2)
            
    def get_all_tasks(self):
        # Tüm görevleri al ve ID'ye göre sırala
        all_tasks = [task for tasks in self.tasks_data.values() for task in tasks.get("tasks", [])]
        unique_tasks = {task["id"]: task for task in all_tasks}
        sorted_tasks = sorted(unique_tasks.values(), key=lambda x: int(x["id"]), reverse=True)
        return sorted_tasks

    def get_students(self):
        # accounts.json dosyasındaki öğrenci bilgilerini getir
        students = [data for data in self.accounts_data.values() if data.get("Account_Type") == "Student"]
        return students

    def get_student_tasks(self, email):
        # Öğrenciye ait görevleri getir
        if email in self.tasks_data:
            return self.tasks_data[email].get("tasks", [])
        return []

    def create_task(self, assigned_emails, task_text, deadline):
        # En yüksek task ID'sini bul
        max_task_id = max(
            (int(task["id"]) for email_tasks in self.tasks_data.values() for task in email_tasks.get("tasks", [])),
            default=0)

        # Yeni task ID'sini oluştur
        new_task_id = str(max_task_id + 1)

        # Yeni bir görev oluştur
        new_task = {
            "id": new_task_id,
            "task": task_text,
            "status": False,
            "deadline": deadline
        }

        # Görevi belirtilen e-posta adreslerine ata
        for email in assigned_emails:
            if email in self.tasks_data:
                # Ensure the "tasks" key exists for the email
                if "tasks" not in self.tasks_data[email]:
                    self.tasks_data[email]["tasks"] = []
                self.tasks_data[email]["tasks"].append(new_task)

        # tasks.json dosyasını güncelle
        self.save_data()
        
        

    def create_announcement(self, announcement_text, last_date):
        # Yeni bir anons oluştur
        new_announcement = {
            "content": announcement_text,
            "last_date": last_date
        }

        # Announcements listesine ekle
        self.announcements_data.append(new_announcement)

        # announcements.json dosyasını güncelle
        self.save_data()

    def get_all_announcements(self):
        # Tüm anonsları al, last_date'e göre sırala
        sorted_announcements = sorted(self.announcements_data, key=lambda x: x["last_date"])
        return sorted_announcements

    def update_attendance_data(self, email, meeting_type, date, status):
        if email not in self.attendance_data:
            self.attendance_data[email] = {}

        if meeting_type not in self.attendance_data[email]:
            self.attendance_data[email][meeting_type] = {}

            # Sadece durumu "N/A" değilse güncelle
        if status != "N/A":
            # Update attendance data for the specified meeting type
            self.attendance_data[email][meeting_type][date] = status

        # Update attendence.json file
        with open('attendance.json', 'w') as f:
            json.dump(self.attendance_data, f, indent=2)

    def switch_chatboard(self):
        main.stackedWidget.setCurrentIndex(6)
        main.chatboard.fill_user_list2()

    def switch_login(self):
        main.stackedWidget.setCurrentIndex(0)
        main.login.clear_line_edits_loginform()


# PyQt5 UI sınıfını ornekleme
class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        #self.setupUi(self)
        loadUi("teacher_page.ui", self)
        self.task_manager = TaskManager()
        self.populate_students_list()
        self.populate_todo_list()
        self.populate_students_table()
        self.populate_attendance_table()
        self.populate_mentor_attendance_table()
        self.connect_table_signals() 
        
        self.pushButton_SchSave.clicked.connect(self.save_attendance)
        self.tableWidget_Students.setColumnWidth(0,100)
        self.tableWidget_Students.setColumnWidth(1,150)
        self.tableWidget_Students.setColumnWidth(2,250)
        self.tableWidget_Students.setColumnWidth(3,335)

        self.tableWidget_ToDoList.setColumnWidth(0, 50)  # 0. sütunun genişliği
        self.tableWidget_ToDoList.setColumnWidth(1, 635)  # 1. sütunun genişliği
        self.tableWidget_ToDoList.setColumnWidth(2, 150)
        # Create Task butonuna tıklandığında
        self.pushButton_CreateTask.clicked.connect(self.create_task)

        # Send Announcement butonuna tıklandığında
        self.pushButton_SendAnnouncement.clicked.connect(self.send_announcement)

        self.announcements = self.task_manager.get_all_announcements()
        self.announcement_index = 0  # Sıradaki anonsun indeksi

        # QTimer oluştur
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_announcements)
        self.timer.start(5000)  # 5 saniyede bir kontrol et
        self.update_announcements()  # Başlangıçta da çalıştır

    def populate_attendance_table(self):
        # Get students and dates from your data
        students = self.task_manager.get_students()
        dates = self.get_distinct_dates_from_attendance()
        # print("Tarihler:", dates)

        # Set the row and column counts
        self.tableWidget_cattendencetable.setRowCount(len(students) + 1)  # +1 for the header row
        self.tableWidget_cattendencetable.setColumnCount(len(dates) + 3)  # +1 for the student names column

        # Set the headers
        headers = ["Name","Surname","Email"] + dates
        # print("Başlıklar:", headers)

        self.tableWidget_cattendencetable.setHorizontalHeaderLabels(headers)

        # Populate the table with data
        for row, student in enumerate(students):
            # Set the student name
            name = student.get("name", "")
            surname = student.get("surname", "")
            email = student.get("Email", "")
            self.tableWidget_cattendencetable.setItem(row, 0, QTableWidgetItem(name))
            self.tableWidget_cattendencetable.setItem(row, 1, QTableWidgetItem(surname))
            self.tableWidget_cattendencetable.setItem(row, 2, QTableWidgetItem(email))

            # Set attendance for each date
            for col, date in enumerate(dates):
                email = student['Email']
                status = self.get_attendance_status(email, date, "Data Science")
                self.tableWidget_cattendencetable.setItem(row, col + 3, QTableWidgetItem(status))
            

    def populate_mentor_attendance_table(self):
            # Get students with account type 'Student' from accounts.json
            students = [data for data in self.task_manager.accounts_data.values() if data.get("Account_Type") == "Student"]

            # Get distinct dates from Mentor Meeting attendance in attendance.json
            dates = self.get_distinct_dates_from_mentor_attendance()
            # print("Tarihler:", dates)
            # Set the row and column counts
            self.tableWidget_mattendencetable.setRowCount(len(students))
            self.tableWidget_mattendencetable.setColumnCount(len(dates) + 3)  # +3 for Name, Surname, Email columns

            # Set the headers
            headers = ["Name", "Surname", "Email"] + dates
            # print("Başlıklar:", headers)

            self.tableWidget_mattendencetable.setHorizontalHeaderLabels(headers)

            # Populate the table with data
            for row, student in enumerate(students):
                name = student.get("name", "")
                surname = student.get("surname", "")
                email = student.get("Email", "")

                # Set the Name, Surname, and Email columns
                self.tableWidget_mattendencetable.setItem(row, 0, QTableWidgetItem(name))
                self.tableWidget_mattendencetable.setItem(row, 1, QTableWidgetItem(surname))
                self.tableWidget_mattendencetable.setItem(row, 2, QTableWidgetItem(email))

                # Set attendance for each date
                for col, date in enumerate(dates):
                    status = self.get_attendance_status(email, date, "Mentor Meeting")
                    self.tableWidget_mattendencetable.setItem(row, col + 3, QTableWidgetItem(status))


    def get_distinct_dates_from_attendance(self):
        # Get distinct dates from attendance_data
        all_dates = []
        for student_attendance in self.task_manager.attendance_data.values():
            for course_dates in student_attendance.values():
                all_dates.extend(course_dates.keys())
        # print(all_dates)
        return list(set(all_dates))

    def get_attendance_status(self, email, date, meeting_type):
            # Get attendance status for the given email, date, and meeting type
            if email in self.task_manager.attendance_data:
                if meeting_type in self.task_manager.attendance_data[email]:
                    if date in self.task_manager.attendance_data[email][meeting_type]:
                        return self.task_manager.attendance_data[email][meeting_type][date]

            return "N/A"



    def get_distinct_dates_from_mentor_attendance(self):
        # Get distinct dates from Mentor Meeting attendance in attendence.json
        all_dates = []
        for student_attendance in self.task_manager.attendance_data.values():
            if "Mentor Meeting" in student_attendance:
                all_dates.extend(student_attendance["Mentor Meeting"].keys())

        return list(set(all_dates))
                 
    def update_announcements(self):
        # Anonsları güncelle
        if self.announcement_index < len(self.announcements):
            announcement = self.announcements[self.announcement_index]
            last_date = announcement.get("last_date")
            current_date = datetime.now().strftime("%Y-%m-%d")
            if last_date >= current_date:
                self.textEdit_AnnouncementView.clear()
                self.textEdit_AnnouncementView.append(
                    f"📢 {announcement['content']} ")

            # Bir sonraki anonsa geç
            self.announcement_index += 1
        else:
            # Anons listesinin sonuna gelindiğinde başa dön
            self.announcement_index = 0
            
    def populate_students_list(self):
        # Öğrenci listesini doldur
        students = self.task_manager.get_students()
        for student in students:
            email = student.get("Email", "")
            name = student.get("name", "")
            surname = student.get("surname", "")
            self.listWidget_AssignList.addItem(f"{name} {surname} ({email})")
            self.listWidget_studentlist.addItem(f"{name} {surname} ({email})")
            
    def create_task(self):
        # Yeni görev oluştur
        task_text = self.plainTextEdit_NewTask.toPlainText()

        deadline = self.dateTimeEdit_Deadline.date().toString("yyyy-MM-dd")

        # Seçilen öğrenci e-postalarını al
        selected_items = self.listWidget_AssignList.selectedItems()
        assigned_emails = [item.text().split("(")[-1].split(")")[0] for item in selected_items]

        # Görev yöneticisine görev oluşturma işlemini yapması için bildir
        self.task_manager.create_task(assigned_emails, task_text, deadline)
        QMessageBox.information(self, "Success", "Task created successfully!")

        # Görev oluşturulduktan sonra formu temizle
        self.plainTextEdit_NewTask.clear()
        self.dateTimeEdit_Deadline.clear()
        self.populate_todo_list()
        self.update_table()

    def send_announcement(self):
        # Yeni anons oluştur ve görev yöneticisine bildir
        announcement_text = self.textEdit_announcementtext.toPlainText()
        last_date = self.dateEdit_lastdateofannouncement.date().toString("yyyy-MM-dd")
        self.task_manager.create_announcement(announcement_text, last_date)
        QMessageBox.information(self, "Success", "Announcement created successfully!")

        # Anons oluşturulduktan sonra formu temizle
        self.textEdit_announcementtext.clear()
        self.dateEdit_lastdateofannouncement.clear()

    def populate_todo_list(self):
        self.tableWidget_ToDoList.setRowCount(0)  # Önceki verileri temizle

        tasks = self.task_manager.get_all_tasks()

        for task in tasks:
            row_position = self.tableWidget_ToDoList.rowCount()
            self.tableWidget_ToDoList.insertRow(row_position)

            self.tableWidget_ToDoList.setItem(row_position, 0, QTableWidgetItem(str(task["id"])))
            self.tableWidget_ToDoList.setItem(row_position, 1, QTableWidgetItem(task["task"]))
            self.tableWidget_ToDoList.setItem(row_position, 2, QTableWidgetItem(task["deadline"]))

    def populate_students_table(self):
        # Students tablosunu güncelle
        students = self.task_manager.get_students()
        self.tableWidget_Students.setRowCount(len(students))

        for row, student in enumerate(students):
            email = student.get("Email", "")
            name = student.get("name", "")
            surname = student.get("surname", "")
            tasks = self.task_manager.get_student_tasks(email)

            # Satırı eklemek için rowCount kullanmamıza gerek yok
            self.tableWidget_Students.insertRow(row)

            self.tableWidget_Students.setItem(row, 2, QTableWidgetItem(email))
            self.tableWidget_Students.setItem(row, 0, QTableWidgetItem(name))
            self.tableWidget_Students.setItem(row, 1, QTableWidgetItem(surname))

            # Görevleri birleştirip metin oluştur
            tasks_text = ", ".join(f"{task.get('id')}={'✅' if task.get('status') else '❌'}" for task in tasks)

            # Doğru sütuna QTableWidgetItem ekleyin
            self.tableWidget_Students.setItem(row, 3, QTableWidgetItem(tasks_text))

    def save_attendance(self):
        # PushButton_SchSave butonuna tıklandığında çalışacak işlemler
        selected_items = self.listWidget_studentlist.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select at least one student.")
            return

        selected_date = self.dateTimeEdit_sch.date().toString("yyyy-MM-dd")
        selected_course = self.listWidget_coursemeet.currentItem().text()

        for item in selected_items:
            student_info = item.text().split("(")
            student_email = student_info[-1].split(")")[0]

            if student_email in self.task_manager.attendance_data:
                if selected_course not in self.task_manager.attendance_data[student_email]:
                    self.task_manager.attendance_data[student_email][selected_course] = {}

                self.task_manager.attendance_data[student_email][selected_course][selected_date] = "Not Attended"
            else:
                self.task_manager.attendance_data[student_email] = {
                    selected_course: {selected_date: "Not Attended"}
                }

        # attendence.json dosyasını güncelle
        with open('attendance.json', 'w') as f:
            json.dump(self.task_manager.attendance_data, f, indent=2)

        QMessageBox.information(self, "Success", "Attendance records saved successfully!")


    def connect_table_signals(self):
            # Connect cellChanged signal for both tables to the update_attendance function
            self.tableWidget_mattendencetable.cellChanged.connect(self.update_attendance)
            self.tableWidget_cattendencetable.cellChanged.connect(self.update_attendance)

    def update_attendance(self, row, col):

        # Get the email from the respective table
        email_col = 2  # Assuming Email column is at index 2
        email_m = self.tableWidget_mattendencetable.item(row, email_col).text()
        email_c = self.tableWidget_cattendencetable.item(row, email_col).text()

        # Check if the column corresponds to a date (skip Name, Surname, and Email columns)
        if col > 2:
            # Get the date from the respective table
            date_m = self.get_date_from_table(self.tableWidget_mattendencetable, col) if email_m else None
            date_c = self.get_date_from_table(self.tableWidget_cattendencetable, col) if email_c else None

            # Get the new attendance status from the table cell
            status_m_item = self.tableWidget_mattendencetable.item(row, col)
            status_m = status_m_item.text() if status_m_item is not None else None

            status_c_item = self.tableWidget_cattendencetable.item(row, col)
            status_c = status_c_item.text() if status_c_item is not None else None

            # Update attendance data only if all necessary information is available
            if email_m and date_m and status_m:
                self.task_manager.update_attendance_data(email_m, "Mentor Meeting", date_m, status_m)

            if email_c and date_c and status_c:
                self.task_manager.update_attendance_data(email_c, "Data Science", date_c, status_c)





    def get_date_from_table(self, table_widget, col):
        # Get the date from the respective table
        header_item = table_widget.horizontalHeaderItem(col)
        if header_item is not None:
            return header_item.text()
        return None

    def update_table(self):
        # Students tablosunu güncelle
        students = self.task_manager.get_students()
        self.tableWidget_Students.setRowCount(len(students))




        for row, student in enumerate(students):
            email = student.get("Email", "")
            name = student.get("name", "")
            surname = student.get("surname", "")
            tasks = self.task_manager.get_student_tasks(email)

            # Satırı eklemek için rowCount kullanmamıza gerek yok
            self.tableWidget_Students.insertRow(row)

            self.tableWidget_Students.setItem(row, 2, QTableWidgetItem(email))
            self.tableWidget_Students.setItem(row, 0, QTableWidgetItem(name))
            self.tableWidget_Students.setItem(row, 1, QTableWidgetItem(surname))

            # Görevleri birleştirip metin oluştur
            tasks_text = ", ".join(f"{task.get('id')}={'✅' if task.get('status') else '❌'}" for task in tasks)

            # Doğru sütuna QTableWidgetItem ekleyin
            self.tableWidget_Students.setItem(row, 3, QTableWidgetItem(tasks_text))


                 
if __name__ == "__main__":
    app = QApplication([])
    window = MyMainWindow()
   # window.set( 900, 600 )
    window.show()
    app.exec_()


# TaskId leri bir kere listele.
#900-600