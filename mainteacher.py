import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem,QWidget, QGridLayout
from datetime import datetime
from Ui_teacher_page import Ui_MainWindow



class TaskManager:
    def __init__(self):
        self.load_data()

    def load_data(self):
        # accounts.json ve tasks.json dosyalarını oku
        with open('accounts.json', 'r') as f:
            self.accounts_data = json.load(f)
           

        with open('tasks.json', 'r') as f:
            self.tasks_data = json.load(f)

    def save_data(self):
        # accounts.json ve tasks.json dosyalarına verileri yaz
        with open('accounts.json', 'w') as f:
            json.dump(self.accounts_data, f, indent=2)

        with open('tasks.json', 'w') as f:
            json.dump(self.tasks_data, f, indent=2)

    def get_students(self):
        # accounts.json dosyasındaki öğrenci bilgilerini getir
        students = []
        for data in self.accounts_data.values():
            
            if data.get("Account_Type") == "Student":
                
                students.append(data)
                print(students)
        return students

    def create_task(self, assigned_emails, task_text, deadline, taskId):
        # Yeni bir görev oluştur
        print(assigned_emails)
        new_task = {
            "id": taskId,
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

# PyQt5 UI sınıfını ornekleme

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.task_manager = TaskManager()
        self.populate_students_list()
        self.populate_todo_list()
        
        # Create Task butonuna tıklandığında
        self.pushButton_pushButton_CreateTask.clicked.connect(self.create_task)
        

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
        taskId = self.lineEdit_TaskId.text()

        # Seçilen öğrenci e-postalarını al
        selected_items = self.listWidget_AssignList.selectedItems()
        assigned_emails = []
        for item in selected_items:
            print(item.text())
            assigned_email=item.text().split("(")[-1].split(")")[0]
            print("assigned email: "+assigned_email)
            assigned_emails.append(assigned_email)

        # Görev yöneticisine görev oluşturma işlemini yapması için bildir
        self.task_manager.create_task(assigned_emails, task_text, deadline, taskId)
        QMessageBox.information(self, "Success", "Task created successfully!")

        # Görev oluşturulduktan sonra formu temizle
        self.plainTextEdit_NewTask.clear()
        self.dateTimeEdit_Deadline.clear()
        self.lineEdit_TaskId.clear()
        self.populate_todo_list()

    def populate_todo_list(self):
        self.tableWidget_ToDoList.setRowCount(0)  # Önceki verileri temizle

        tasks_by_id = {}  # taskId'ye göre görevleri depolamak için bir sözlük
        for email, tasks in self.task_manager.tasks_data.items():
            for task in tasks.get("tasks", []):
                task_id = str(task["id"])
                if task_id not in tasks_by_id:
                    tasks_by_id[task_id] = task

        for task_id, task_data in tasks_by_id.items():
            row_position = self.tableWidget_ToDoList.rowCount()
            self.tableWidget_ToDoList.insertRow(row_position)

            self.tableWidget_ToDoList.setItem(row_position, 0, QTableWidgetItem(task_id))
            self.tableWidget_ToDoList.setItem(row_position, 1, QTableWidgetItem(task_data["task"]))
            self.tableWidget_ToDoList.setItem(row_position, 2, QTableWidgetItem(task_data["deadline"]))
            self.tableWidget_ToDoList.setItem(row_position, 3, QTableWidgetItem("Completed" if task_data["status"] else "Incomplete"))

if __name__ == "__main__":
    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec_()
