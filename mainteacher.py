from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime
import json
from Ui_teacher_page import Ui_MainWindow

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
            with open('announcements.json', 'r') as f:
                self.announcements_data = json.load(f)
        except FileNotFoundError:
            self.announcements_data = []

    def save_data(self):
        # accounts.json, tasks.json ve announcements.json dosyalarına verileri yaz
        with open('accounts.json', 'w') as f:
            json.dump(self.accounts_data, f, indent=2)

        with open('tasks.json', 'w') as f:
            json.dump(self.tasks_data, f, indent=2)

        with open('announcements.json', 'w') as f:
            json.dump(self.announcements_data, f, indent=2)

    def get_all_tasks(self):
        # Tüm görevleri al ve ID'ye göre sırala
        all_tasks = [task for tasks in self.tasks_data.values() for task in tasks.get("tasks", [])]
        sorted_tasks = sorted(all_tasks, key=lambda x: int(x["id"]), reverse=True)
        return sorted_tasks

    def get_students(self):
        # accounts.json dosyasındaki öğrenci bilgilerini getir
        students = [data for data in self.accounts_data.values() if data.get("Account_Type") == "Student"]
        return students

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

# PyQt5 UI sınıfını ornekleme
class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.task_manager = TaskManager()
        self.populate_students_list()
        self.populate_todo_list()
        
        self.tableWidget_ToDoList.setColumnWidth(0, 95)  # 0. sütunun genişliği
        self.tableWidget_ToDoList.setColumnWidth(1, 450)  # 1. sütunun genişliği
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

            
    def update_announcements(self):
        # Anonsları güncelle
        if self.announcement_index < len(self.announcements):
            announcement = self.announcements[self.announcement_index]
            last_date = announcement.get("last_date")
            current_date = datetime.now().strftime("%Y-%m-%d")
            if last_date >= current_date:
                self.textEdit_AnnouncementView.clear()
                self.textEdit_AnnouncementView.append(
                    f" {announcement['content']} ")

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
        #numberofassignees=tasks.

        for task in tasks:
            row_position = self.tableWidget_ToDoList.rowCount()
            self.tableWidget_ToDoList.insertRow(row_position)

            self.tableWidget_ToDoList.setItem(row_position, 0, QTableWidgetItem(str(task["id"])))
            self.tableWidget_ToDoList.setItem(row_position, 1, QTableWidgetItem(task["task"]))
            self.tableWidget_ToDoList.setItem(row_position, 2, QTableWidgetItem(task["deadline"]))
            
if __name__ == "__main__":
    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec_()
