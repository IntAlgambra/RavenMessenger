import npyscreen
import client_backend
import rsa

#Кастомизируем класс Title text

class CustomTitleText(npyscreen.TitleText):
    _entry_type = npyscreen.Textfield
    def __init__(self, *args, **kwargs):
        super(CustomTitleText, self).__init__(*args, **kwargs)
        self.allow_override_begin_entry_at = True

#Блок отображения истории сообщений
class ChatBox(npyscreen.BoxTitle):

    def __init__(self, *args, **kwargs):
        super(ChatBox, self).__init__(*args, **kwargs)

    _contained_widget = npyscreen.Pager

#Блок для ввода сообщений пользователя
class MessageBox(npyscreen.BoxTitle):
    def __init__(self, *args, **kwargs):
        super(MessageBox, self).__init__(*args, **kwargs)

    _contained_widget = npyscreen.MultiLineEdit

class LoginBox(npyscreen.BoxTitle):
    def __init__(self, *args, **kwargs):
        super(LoginBox, self).__init__(*args, **kwargs)


#Кнопка отправки сообщения
class SendButton(npyscreen.ButtonPress):
    def __init__(self, *args, **kwargs):
        self.message_widget = kwargs.get('message_widget')
        self.chat_widget = kwargs.get('chat_widget')
        self.contacts_widget = kwargs.get('contacts_widget')
        super(SendButton, self).__init__(*args, **kwargs)

    def whenPressed(self):
        user_to = self.contacts_widget.get_selected_objects()[0]
        text = self.message_widget.value
        sending_status = client.send_message(user_to, text)
        if not sending_status:
            self.chat_widget.values.append('ERROR! NO CONNECTION')
        else:
            self.message_widget.value = ''

#Кнопка регистрации в месседжере
class RegistrationButton(npyscreen.ButtonPress):
    def __init__(self, *args, **kwargs):
        self.parent_form = kwargs.get('parent_form')
        super(RegistrationButton, self).__init__(*args, **kwargs)
    
    def whenPressed(self):
        self.parent_form.parentApp.switchForm('REGISTRATION')

#Класс для основной формы
class MainForm(npyscreen.Form):

    def __init__(self, *args, **kwargs):
        super(MainForm, self).__init__(*args, **kwargs)

    def create(self):
        self.keypress_timeout = 10
        self.columns = 80
        self.lines = 50
        #добавляем блок списка доступных контактов
        values = client.get_contacts()
        self.contacts = self.add(
            npyscreen.SelectOne,
            values = values,
            max_height=len(values)+1,
            scroll_exit=True
        )
        #добавляем блок вывода чата в форму
        self.chatbox = self.add(ChatBox, name='Chat history: ', max_height=20, scroll_exit=True)
        #получаем доступ к самому виджету чата и записываем в него историю сообщений
        self.chat = self.chatbox.entry_widget
        self.chat.values = client.get_history()
        #теперь то же самое для блока с вводом сообщений
        self.messagebox = self.add(MessageBox, name='Input your message: ', max_height=5)
        self.message = self.messagebox.entry_widget
        #добавляем кнопку отправки сообщения
        self.send_button = self.add(
            SendButton,
            message_widget = self.message,
            chat_widget = self.chat,
            contacts_widget = self.contacts,
            name = 'send message'
        )

    def while_waiting(self):
        contacts = client.get_contacts()
        self.contacts.max_height = len(contacts) + 1
        self.contacts.values = contacts
        try:
            selected_contact = self.contacts.get_selected_objects()[0]
        except IndexError:
            selected_contact = client.login
        self.chat.values = client.get_history(selected_contact)
        self.display()

    def afterEditing(self):
        client.stop()
        self.parentApp.setNextForm(None)

#Класс для формы аутентификации
class AuthForm(npyscreen.ActionFormV2):

    def __init__(self, *args, **kwargs):
        super(AuthForm, self).__init__(*args, **kwargs)

    def create(self):
        y, x = self.useable_space()
        # self.login = self.add(npyscreen.TitleText, name='login', relx=x//2-1)
        self.login = self.add(
            CustomTitleText,
            begin_entry_at = 10,
            use_two_lines = False,
            name = 'login',
            # max_width = x//2,
            # relx = x//2 - 1,
            # rely = y//2 + 1,
        )
        # self.password = self.add(npyscreen.TitlePassword, name='password')
        self.password = self.add(
            npyscreen.TitlePassword,
            name = 'password',
            begin_entry_at = 10,
            use_two_lines = False,
            # max_width = x//2,
            # relx = x//2 - 1,
            # rely = y//2,
        )
        self.registration_button = self.add(
            RegistrationButton,
            name='sign in',
            # parent_form=self,
            # relx = x//2 - 3,
            # rely = y//2 + 2,
        )
        # self.registration_button = self.add(RegistrationButton, name='sign in', parent_form=self)

    def on_cancel(self):
        self.parentApp.setNextForm(None)

    def on_ok(self):
        login, password = self.login.value, self.password.value
        auth_status = client.auth(login, password)
        if auth_status:
            self.parentApp.setNextForm('RAVEN')
            client.start_receive_thread()
        else:
            self.parentApp.setNextForm('MAIN')

#Класс для формы регистрации
class RegistrationForm(npyscreen.ActionFormV2):
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def create(self):
        self.login = self.add(npyscreen.TitleText, name='login')
        self.temp_password = self.add(npyscreen.TitlePassword, name = 'temporary password')
        self.password = self.add(npyscreen.TitlePassword, name='password')
        self.confirm_password = self.add(npyscreen.TitlePassword, name='confirm password')

    def on_cancel(self):
        self.parentApp.setNextForm('MAIN')

    def on_ok(self):
        login = self.login.value
        temp_password = self.temp_password.value
        password = self.password.value
        confirm_password = self.confirm_password.value
        if password != confirm_password:
            self.confirm_password.value = ''
            self.password.value = ''
            self.display()
        else:
            reg_status = client.registrate(login, temp_password, password)
            if reg_status:
                self.parentApp.setNextForm('MAIN')
            else:
                self.parentApp.setNextForm('REGISTRATION')


class ClientApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', AuthForm, name='Raven login')
        self.addForm('RAVEN', MainForm, name='Raven messeger')
        self.addForm('REGISTRATION', RegistrationForm, name='Raven registration')

if __name__ == '__main__':
    pubkey, privkey = rsa.newkeys(512, poolsize=8)
    #создаем клиента
    client = client_backend.Client(client_backend.HOST, client_backend.PORT, pubkey, privkey)
    #запускаем поток для подключения к серверу
    client.start_connection_thread()
    client_app = ClientApp().run()