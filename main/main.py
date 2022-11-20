###  IMPORTS ########
import sys
import psycopg2
from PyQt5 import QtGui
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDialog, QStackedWidget

import threading
import time



hostname = 'containers-us-west-99.railway.app'
database = 'railway'
username = 'postgres'
pwd = '4h9h2AFJqspFGsTq2XVQ'
port_id = 5623


# ------------------welcomeScreen screen---------------------------#
class WelcomeScreen(QDialog):

    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi('welcome.ui', self)  # loading elements from gui##

        self.login_but.clicked.connect(self.gotologin)  # login button pressed -> goin to login screen

        self.reg_but.clicked.connect(self.gotocreate)  # register button pressed -> goin to register screen

    def gotologin(self):
        login_obj = LoginScreen()  # creating login screen obj
        widget.addWidget(login_obj)
        widget.setCurrentIndex(widget.currentIndex() + 1)  # setting the login screen on top of current welcomeScreen screen

    def gotocreate(self):
        register_obj = RegisterScreen()  # creating registration screen obj
        widget.addWidget(register_obj)
        widget.setCurrentIndex(widget.currentIndex() + 1)  # setting the login screen on top of current welcomeScreen screen


# -------------------register screen---------------#
class RegisterScreen(QDialog):

    def __init__(self):
        super(RegisterScreen, self).__init__()
        loadUi("register.ui", self)

        self.signup.clicked.connect(self.signupfunction)  # signup button pressed -> goin to signupfunction

    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()

        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0:
            self.error.setText("Please fill in all inputs.")

        elif password != confirmpassword:
            self.error.setText("Passwords do not match.")
        else:
            conn = psycopg2.connect(
                host=hostname,
                dbname=database,
                user=username,
                password=pwd,
                port=port_id)
            cur = conn.cursor()

            user_info = (user, password)
            cur.execute('INSERT INTO login_info (username, password) VALUES (%s,%s)', user_info)

            conn.commit()
            conn.close()
            welcome.gotologin()


# --------------------login screen------------------#
class LoginScreen(QDialog):

    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)  # loading elements from login screen

        self.login.clicked.connect(self.loginfunction)  # login button pressed -> goin to login FUNCTION

    def loginfunction(self):
        global result_pass
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")

        else:
            conn = psycopg2.connect(
                host=hostname,
                dbname=database,
                user=username,
                password=pwd,
                port=port_id)
            cur = conn.cursor()
            query = 'SELECT password FROM login_info WHERE username =\'' + user + "\'"
            cur.execute(query)

            try:
                result_pass = cur.fetchone()[0]
            except TypeError:
                self.error.setText("User dose not exist")
                self.emailfield.setText('')
                self.passwordfield.setText('')
                return
            except Exception as E:
                self.error.setText(f"Report to admin - Error:{E}")
                self.emailfield.setText('')
                self.passwordfield.setText('')
                return

            if result_pass == password:
                print("Successfully logged.")
                self.error.setText("")
                pomodoro_obj = PomodoroScreen()  # creating pomodoro screen obj
                widget.addWidget(pomodoro_obj)
                widget.setCurrentIndex(widget.currentIndex() + 1)  # setting the pomodoro screen on top of current welcomeScreen screen

            else:
                self.error.setText("Invalid username or password")


# ---------------------pomodoro screen---------------#
class PomodoroScreen(QDialog):

    def __init__(self):
        self.minutes_count = None
        self.pause = 0
        self.ticks = 0
        self.seconds_count = None

        super(PomodoroScreen, self).__init__()
        loadUi("pomodoro.ui", self)
        self.stop.hide()

        self.pomodoro.clicked.connect(self.P_pomodoro)

        self.start.clicked.connect(self.P_start)

        self.break5.clicked.connect(self.P_break5)

        self.reset.clicked.connect(self.P_reset)

        self.stop.clicked.connect(self.P_stop)

    def P_start(self):
        self.pause = 0
        self.start.hide()
        self.stop.show()

        if self.ticks <= 0 :
            self.ticks = 25 * 60
            self.minute.setText('25')
            self.second.setText('00')
            self.msg.setText('')
            x = threading.Thread(target=self.countdown)
            x.start()

        elif 300 < self.ticks <= 1500:
            x = threading.Thread(target=self.countdown)
            x.start()

        elif 0 < self.ticks <= 300:
            x = threading.Thread(target=self.countdown)
            x.start()

    def P_stop(self):

        self.pause = 1
        self.stop.hide()
        self.start.show()

    def countdown(self):

        while self.ticks and self.pause != 1:
            QApplication.processEvents()
            self.minutes_count, self.seconds_count = divmod(self.ticks, 60)
            self.minutes_count, self.seconds_count = str(self.minutes_count), str(self.seconds_count)
            time.sleep(1)
            self.display()
            print(threading.active_count())
            self.ticks -= 1
        if self.ticks == 0:
            self.minutes_count, self.seconds_count = '00', '00'
            self.display()
        self.start.show()

    def P_pomodoro(self):
        self.P_stop()
        self.ticks = 25 * 60
        self.minutes_count = '25'
        self.seconds_count = '00'
        self.minute.setText('25')
        self.second.setText('00')
        self.msg.setText('')

    def P_reset(self):
        self.P_stop()
        self.ticks = 0
        self.minutes_count = '00'
        self.seconds_count = '00'
        self.minute.setText('00')
        self.second.setText('00')
        self.msg.setText('!!Select a mode!!')

    def P_break5(self):
        self.ticks = 5 * 60
        self.P_stop()
        self.minutes_count = '05'
        self.seconds_count = '00'
        self.minute.setText('05')
        self.second.setText('00')
        self.msg.setText('')

    def display(self):
        self.second.setText(self.seconds_count.zfill(2))
        self.minute.setText(self.minutes_count.zfill(2))


# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(600)
widget.setFixedWidth(900)
widget.setWindowTitle('pomodoro timer')

widget.show()
widget.setWindowIcon(QtGui.QIcon('clock.png'))
try:
    sys.exit(app.exec())
except:
    print('Exiting')
