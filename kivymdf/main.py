import json
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
import os

kv = """
MDScreen:
    BoxLayout:
        orientation: 'vertical'

        # Botões para selecionar os dias da semana
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: "56dp"
            size_hint_x: None
            width: self.minimum_width
            pos_hint: {"center_x": 0.5}
            id: day_buttons_box
            opacity: 1  # Mantém visível no início

            # Botões de cada dia da semana
            MDFlatButton:
                text: 'Segunda'
                on_release: app.update_day('Segunda')  # Atualiza o dia selecionado
                id: segunda

            MDFlatButton:
                text: 'Terça'
                on_release: app.update_day('Terça')
                id: terca

            MDFlatButton:
                text: 'Quarta'
                on_release: app.update_day('Quarta')
                id: quarta

            MDFlatButton:
                text: 'Quinta'
                on_release: app.update_day('Quinta')
                id: quinta

            MDFlatButton:
                text: 'Sexta'
                on_release: app.update_day('Sexta')
                id: sexta

            MDFlatButton:
                text: 'Sábado'
                on_release: app.update_day('Sábado')
                id: sabado

            MDFlatButton:
                text: 'Domingo'
                on_release: app.update_day('Domingo')
                id: domingo

        # Label que exibe o dia selecionado
        MDLabel:
            id: day_label
            text: "Selecione um dia da semana"
            halign: "center"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: "48dp"
            opacity: 1  # Mantém visível no início

        # Label que exibe as tarefas do dia selecionado
        MDLabel:
            id: task_label
            text: "Tarefas: Nenhuma tarefa para hoje"
            halign: "center"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: "48dp"
            opacity: 1  # Mantém visível no início

        # Área rolável que exibe a lista de tarefas
        ScrollView:
            MDList:
                id: task_list

        # Campo de texto para adicionar novas tarefas
        MDTextField:
            id: task_input
            hint_text: "Digite uma nova tarefa"
            size_hint_y: None
            height: "40dp"
            pos_hint: {"center_x": 0.5}

        # Botões para gerenciar tarefas
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: "60dp"
            spacing: "10dp"
            pos_hint: {"right": 1}  # Alinha à direita

            MDRaisedButton:
                text: "Adicionar Tarefa"
                size_hint: None, None
                size: "150dp", "50dp"
                on_release: app.add_task_from_input()  # Adiciona uma nova tarefa

            MDRaisedButton:
                text: "Atualizar Tarefas"
                size_hint: None, None
                size: "150dp", "50dp"
                on_release: app.remove_checked_tasks()  # Remove tarefas concluídas

            MDRaisedButton:
                text: "Nova Semana"
                size_hint: None, None
                size: "150dp", "50dp"
                on_release: app.show_clear_confirmation_dialog()  # Confirmação para limpar todas as tarefas

        # Navegação inferior com abas
        MDBottomNavigation:
            selected_color_background: 'orange'
            text_color_active: "lightgrey"

            # Aba Home
            MDBottomNavigationItem:
                name: 'home_screen'
                text: 'Home'
                icon: 'home'

                BoxLayout:
                    orientation: 'vertical'
                    MDLabel:
                        text: 'Página Inicial'
                        halign: 'center'
                        size_hint_y: None
                        height: "100dp"

            # Aba de tarefas pendentes
            MDBottomNavigationItem:
                name: 'pendentes_screen'
                text: 'Pendentes'
                icon: 'note'

                BoxLayout:
                    orientation: 'vertical'
                    MDLabel:
                        id: total_tasks_label
                        text: 'Tarefas pendentes: 0'  # Exibe o número total de tarefas pendentes
                        halign: 'center'
                        font_style: "H4"
                        size_hint_y: None
                        height: "100dp"
                    ScrollView:
                        MDList:
                            id: settings_task_list  # Lista de tarefas pendentes na aba "Pendentes"
"""

class Agenda(MDApp):
    def build(self):
        self.title = "Agenda"  
        self.theme_cls.theme_style = "Dark"  
        screen = Builder.load_string(kv) 
        self.root = screen
        self.selected_day = None  # Dia atualmente selecionado
        self.tasks = self.load_tasks()  # Carrega as tarefas salvas no arquivo JSON
        self.checkboxes = {}  # Dicionário para armazenar os checkboxes associados às tarefas
        self.update_total_tasks()  
        return screen

    # Atualiza o dia selecionado e exibe as tarefas correspondentes
    def update_day(self, day):
        self.selected_day = day  # Define o dia selecionado
        self.root.ids.day_label.text = f"Dia selecionado: {self.selected_day}"  
        self.update_button_backgrounds()  
        self.update_task_label()  # Atualiza a lista de tarefas do dia selecionado

    # Atualiza a aparência dos botões de dias da semana
    def update_button_backgrounds(self):
        for day_button in ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']:
            button = self.root.ids.get(day_button)  # Obtém o botão correspondente
            button.background_color = (1, 1, 1, 1) if button.text == self.selected_day else (0.2, 0.2, 0.2, 1)

    # Exibe a lista de tarefas do dia selecionado
    def update_task_label(self):
        task_label = self.root.ids.task_label  
        task_list = self.root.ids.task_list  
        task_list.clear_widgets()  # Limpa a lista de tarefas exibidas atualmente
        self.checkboxes.clear()  # Limpa os checkboxes armazenados

        # Verifica se há tarefas para o dia selecionado
        if self.selected_day and self.selected_day in self.tasks:
            tasks_for_day = self.tasks[self.selected_day]  # Obtém as tarefas do dia selecionado
            task_label.text = f"Tarefas para {self.selected_day}:"

            # Adiciona cada tarefa como um item na lista
            for task in tasks_for_day:
                task_item = BoxLayout(size_hint_y=None, height="40dp", orientation="horizontal")
                task_label = MDLabel(text=task, halign="left", size_hint_x=0.8)  # Texto da tarefa
                checkbox = MDCheckbox(size_hint_x=0.2)  # Checkbox para marcar a tarefa como concluída
                checkbox.bind(active=lambda checkbox, value, item=task_item: self.set_task_background(item, value))
                self.checkboxes[task] = checkbox  # Armazena o checkbox associado à tarefa
                task_item.add_widget(task_label)
                task_item.add_widget(checkbox)
                task_list.add_widget(task_item)  # Adiciona o item à lista exibida
        else:
            task_label.text = f"Tarefas: Nenhuma tarefa para {self.selected_day}"  

    def set_task_background(self, task_item, is_checked):
        with task_item.canvas.before:  
            task_item.canvas.before.clear()  
            if is_checked:  # Se o checkbox estiver marcado
                Color(0, 1, 0, 0.3)  # Define uma cor verde translúcida
                Rectangle(size=task_item.size, pos=task_item.pos)  

    # Adiciona uma nova tarefa a partir do texto digitado no campo de entrada
    def add_task_from_input(self):
        task_description = self.root.ids.task_input.text  # Obtém o texto do campo de entrada
        if task_description.strip() and self.selected_day:  # Verifica se o texto não está vazio e um dia foi selecionado
            if self.selected_day not in self.tasks: 
                self.tasks[self.selected_day] = [] 
            self.tasks[self.selected_day].append(task_description) 
            self.update_task_label()  # Atualiza a exibição das tarefas
            self.save_tasks()  # Salva as tarefas no arquivo JSON
            self.update_total_tasks()  # Atualiza a contagem total de tarefas pendentes
            self.root.ids.task_input.text = ""  # Limpa o campo de entrada

    # Remove as tarefas que foram marcadas como concluídas
    def remove_checked_tasks(self):
        if self.selected_day in self.tasks:  # Verifica se há tarefas no dia selecionado
            tasks_to_remove = [task for task, checkbox in self.checkboxes.items() if checkbox.active]
            
            for task in tasks_to_remove:
                self.tasks[self.selected_day].remove(task)
            
            self.update_task_label()
            self.save_tasks()  # Salva as mudanças no arquivo JSON
            self.update_total_tasks()  # Atualiza a contagem total de tarefas pendentes

    # Atualiza o total de tarefas pendentes em todas as abas
    def update_total_tasks(self):
        total_tasks = sum(len(tasks) for tasks in self.tasks.values())
        self.root.ids.total_tasks_label.text = f"Tarefas pendentes: {total_tasks}" 

        # Atualiza a lista de tarefas pendentes exibida na aba "Pendentes"
        settings_task_list = self.root.ids.settings_task_list
        settings_task_list.clear_widgets()  # Limpa a lista antes de recarregar

        for day, tasks in self.tasks.items():  # Itera sobre todos os dias e suas tarefas
            for task in tasks:  # Adiciona cada tarefa à lista de pendentes
                task_item = BoxLayout(size_hint_y=None, height="40dp", orientation="horizontal")
                task_label = MDLabel(text=task, halign="left", size_hint_x=0.8)  # Exibe o nome da tarefa
                task_item.add_widget(task_label)
                settings_task_list.add_widget(task_item)  # Adiciona à lista exibida

    # Salva as tarefas no arquivo JSON 
    def save_tasks(self):
        try:
            with open("tasks.json", "w") as f:  # Abre o arquivo JSON no modo de escrita
                json.dump(self.tasks, f)  # Salva o dicionário de tarefas no arquivo
        except Exception as e: 
            print(f"Erro ao salvar tarefas: {e}")  

    # Carrega as tarefas do arquivo JSON para inicialização
    def load_tasks(self):
        if os.path.exists("tasks.json"):  # Verifica se o arquivo existe
            try:
                with open("tasks.json", "r") as f:  # Abre o arquivo JSON no modo de leitura
                    return json.load(f)  # Retorna o dicionário de tarefas carregado
            except Exception as e:  
                print(f"Erro ao carregar tarefas: {e}")
                return {}  
        return {} 

    # Exibe um diálogo de confirmação para limpar todas as tarefas
    def show_clear_confirmation_dialog(self):
        self.dialog = MDDialog(
            title="Nova Semana", 
            text="Você tem certeza que deseja iniciar uma nova semana? (Isso excluirá todas as tarefas pendentes)",
            size_hint=(0.8, 1),  
            buttons=[
                MDRaisedButton(text="Cancelar", on_release=self.dismiss_dialog),  
                MDRaisedButton(text="Confirmar", on_release=self.confirm_clear_tasks),  
            ],
        )
        self.dialog.open()  

    # Fecha o diálogo sem realizar nenhuma ação
    def dismiss_dialog(self, instance):
        self.dialog.dismiss()  

    # Confirma a exclusão de todas as tarefas
    def confirm_clear_tasks(self, instance):
        self.tasks.clear()  
        self.update_task_label()  
        self.save_tasks()  
        self.update_total_tasks()  
        self.dialog.dismiss()  

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        # Oculta os elementos da aba "Home" quando a aba "Pendentes" é selecionada
        if tab_text == "Settings":
            self.root.ids.day_buttons_box.opacity = 0
            self.root.ids.day_label.opacity = 0
            self.root.ids.task_label.opacity = 0
        else:
            self.root.ids.day_buttons_box.opacity = 1
            self.root.ids.day_label.opacity = 1
            self.root.ids.task_label.opacity = 1

if __name__ == "__main__":
    Agenda().run()
