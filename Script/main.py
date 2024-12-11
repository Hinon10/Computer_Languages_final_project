import customtkinter as ctk
import json
from datetime import datetime
from tkcalendar import DateEntry

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Constants
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

FILE_NAME = 'database.json'
DEFAULT_CATEGORY = "shopping"
DEFAULT_OPERATION_TYPE = "spending"

DEFAULT_GEOMETRY = "800x800"
DEFAULT_CATEGORIES = ["shopping", "taxes", "groceries"]
DEFAULT_FILE_PARTS = ["Operations", "Categories", "balance"]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.data = {}
        self._initialize_app()

###########################################################
# Start of an app by initialising main functions and app
###########################################################
    def create_button(self, master, text, command, row, col, sticky, column_span):
        return ctk.CTkButton(master, text=text, command=command, height=35, font=("Arial", 20)).grid(row=row,
                                                                                                     column=col,
                                                                                                     sticky=sticky,
                                                                                                     columnspan=column_span)

    def _initialize_app(self):
        self.load_data()
        self.sort_file()
        self.set_default_values()
        self.configure_window()
        self.initialize_tabs()
        self.initialize_tabs_frames()

    def configure_window(self):
        self.geometry(DEFAULT_GEOMETRY)
        self.minsize(600, 400)

########################################################
# basic functions
########################################################
    def set_default_values(self):
        now = datetime.now()
        self.day = now.day
        self.month = MONTHS[now.month - 1]
        self.year = now.year
        self.category = DEFAULT_CATEGORY
        self.operation_type = DEFAULT_OPERATION_TYPE
        self.balance = self.data['balance']

    def load_data(self):
        try:
            with open(FILE_NAME, 'r') as f:
                self.data = json.load(f)
                self.restore_file()
        except FileNotFoundError:
            self.restore_file()
        else:
            self.save_to_file()

    def sort_file(self):
        sorted_data = {
            year: {month: {day: ops for day, ops in sorted(days.items())}
                   for month, days in sorted(months.items())}
            for year, months in sorted(self.data["Operations"].items())
        }
        self.data["Operations"] = sorted_data
        self.save_to_file()

    def restore_file(self):
        for key in DEFAULT_FILE_PARTS:
            if not key in self.data.keys():
                self.data[key] = {}
                if key == "Categories":
                    self.data[key] = DEFAULT_CATEGORIES
                if key == "balance":
                    self.data[key] = 0

    def save_to_file(self):
        with open(FILE_NAME, 'w') as f:
            json.dump(self.data, f, indent=4)

########################################################
# Layout initialising (tabs)
########################################################
    def initialize_tabs(self):
        self.tabview = ctk.CTkTabview(self, command=self.tab_selected)
        self.tabview.pack(fill="both", expand=True)
        self.family_tabs = ["Operations", "History", "Statistics", "Settings"]
        for tab in self.family_tabs:
            self.tabview.add(tab)
            self.tabview.tab(tab).grid_columnconfigure([0], weight=1)
            self.tabview.tab(tab).rowconfigure(0, weight=1)
            self.tabview.tab(tab).rowconfigure(1, weight=3)

    def tab_selected(self):
        print(f"tab selected: {self.tabview.get()}")

    def initialize_tabs_frames(self):
        self._init_operations_tab_frames()
        self._init_history_frame()
        self._init_settings_tab_frames()
        self._init_statistics_tab_frames()

###########################################################
###########################################################
# Operations tab
###########################################################
###########################################################
    def _init_operations_tab_frames(self):
        self.tabview.tab("Operations").grid_columnconfigure([0], weight=1)
        self.tabview.tab("Operations").grid_rowconfigure([0, 1, 2], weight=1)


        self.init_pie_chart()
        self.pie_chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.init_balance_frame()
        self.balance_frame.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

        self.init_actions_frame()
        self.actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    def init_pie_chart(self):
        self.pie_chart_frame = ctk.CTkFrame(master=self.tabview.tab("Operations"))
        self.pie_chart_frame.columnconfigure(0, weight=1)
        self.pie_chart_frame.rowconfigure(0, weight=1)

        total_spending = 0
        total_earning = 0

        now = datetime.now()
        current_year = str(now.year)
        current_month = str(now.month).zfill(2)

        month_data = self.data.get("Operations", {}).get(current_year, {}).get(current_month, {})

        for day_data in month_data.values():
            if isinstance(day_data, dict):
                data_items = day_data.values()
            elif isinstance(day_data, list):
                data_items = day_data
            else:
                continue

            for op_data in data_items:
                if isinstance(op_data, dict) and "value" in op_data:
                    value = op_data["value"]
                    if isinstance(value, (int, float)):
                        if value < 0:
                            total_spending += abs(value)
                        else:
                            total_earning += value

        values = [total_spending, total_earning]
        labels = ['Spending', 'Earning']

        if total_spending == 0 and total_earning == 0:
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.set_xticks([])
            ax.set_yticks([])
            ax.text(0.5, 0.5, 'No data for current month', fontsize=12, va='center', ha='center',
                    transform=ax.transAxes, color='white')
            ax.set_aspect('equal')
            fig.patch.set_facecolor('#2E2E2E')
            ax.set_facecolor('#2E2E2E')
            plt.close(fig)
        else:
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(
                values, labels=labels, autopct='%1.1f%%', startangle=90,
                colors=['#FF6F61', '#6BAED6'],
                textprops={'color': 'white'}
            )
            ax.axis('equal')
            fig.patch.set_facecolor('#2E2E2E')
            ax.set_facecolor('#2E2E2E')
            plt.close(fig)

        self.canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def init_balance_frame(self):
        self.balance_frame = ctk.CTkFrame(master=self.tabview.tab("Operations"))
        self.balance_frame.columnconfigure([0], weight=1)
        self.balance_frame.rowconfigure([0], weight=1)
        self.balance_label = ctk.CTkLabel(self.balance_frame, text="", font=("Arial", 30))
        self.balance_label.grid(row=0, column=0, sticky="nsew")
        self.change_balance()

###########################################################
# Action frame
###########################################################

    def init_actions_frame(self):
        self.actions_frame = ctk.CTkFrame(master=self.tabview.tab("Operations"))
        self.actions_frame.columnconfigure([0, 1, 2, 3, 4], weight=1)

        self.actions_frame.rowconfigure([0, 1, 2, 3], weight=0, pad=20)

        self._create_action_elements()

    def _create_action_elements(self):
        self.label_categories = ctk.CTkLabel(self.actions_frame, text="Categories")
        self.label_categories.grid(row=0, column=2, columnspan=2, sticky="s")

        self._create_calendar_entry()

        self.category_option_menu = ctk.CTkOptionMenu(self.actions_frame, values=self.get_categories(),
                                                      command=self.set_category)
        self.category_option_menu.grid(row=1, column=2, columnspan=2, padx=10, sticky="ew")
        self.category_option_menu.set(DEFAULT_CATEGORY)

        self.value_label = ctk.CTkLabel(self.actions_frame, text="Enter Value:", font=("Arial", 20))
        self.value_label.grid(row=2, column=0, sticky="e")
        self.value_entry = ctk.CTkEntry(self.actions_frame, font=('Arial', 24), insertwidth=2, justify='center')
        self.value_entry.grid(row=2, column=1, columnspan=1, padx=10, sticky="ew")

        self.add_button = self.create_button(self.actions_frame, "Add Operation", self.add_operation, 2, 2, "ew", 2)

        self.error_label = ctk.CTkLabel(self.actions_frame, text="", font=("Arial", 15), text_color="red")
        self.error_label.grid(row=3, column=1, columnspan=1, sticky="n")

    def _create_calendar_entry(self):
        self.date_label = ctk.CTkLabel(self.actions_frame, text="Select Operation Date:", font=("Arial", 20))
        self.date_label.grid(row=1, column=0, sticky='e')
        self.date_entry = DateEntry(self.actions_frame, background='darkblue', foreground='white',
                                    borderwidth=2, date_pattern='dd/MM/yyyy', height=35)
        self.date_entry.grid(row=1, column=1, padx=10, sticky="ew")

###########################################################
###########################################################
# History tab
###########################################################
###########################################################
# history frame (under development)
##############################################################
    def filter_checkbox_event(self):
        if self.filter_checkbox_var.get() == "disabled":
            self.saved_states = {
                'day': self.day_filter_checkbox_var.get(),
                'month': self.month_filter_checkbox_var.get(),
                'year': self.year_filter_checkbox_var.get()
            }
            self.day_filter_checkbox.configure(state="disabled")
            self.month_filter_checkbox.configure(state="disabled")
            self.year_filter_checkbox.configure(state="disabled")

            self.day_option_menu.configure(state="disabled")
            self.month_option_menu.configure(state="disabled")
            self.year_option_menu.configure(state="disabled")
        else:

            self.day_filter_checkbox.configure(state="normal")
            self.month_filter_checkbox.configure(state="normal")
            self.year_filter_checkbox.configure(state="normal")

            self.day_filter_checkbox_var.set(self.saved_states['day'])
            self.month_filter_checkbox_var.set(self.saved_states['month'])
            self.year_filter_checkbox_var.set(self.saved_states['year'])

            if self.saved_states['day'] == "disabled":
                self.day_option_menu.configure(state="disabled")
            else:
                self.day_option_menu.configure(state="normal")
            if self.saved_states['month'] == "disabled":
                self.month_option_menu.configure(state="disabled")
            else:
                self.month_option_menu.configure(state="normal")
            if self.saved_states['year'] == "disabled":
                self.year_option_menu.configure(state="disabled")
            else:
                self.year_option_menu.configure(state="normal")

        self.fill_operation_info_frame()

    def day_filter_checkbox_event(self):
        checkbox_state = self.day_filter_checkbox_var.get()
        if checkbox_state == "disabled":
            self.day_option_menu.configure(state="disabled")
        else:
            self.day_option_menu.configure(state="normal")
        self.fill_operation_info_frame()

    def month_filter_checkbox_event(self):
        checkbox_state = self.month_filter_checkbox_var.get()
        if checkbox_state == "disabled":
            self.month_option_menu.configure(state="disabled")
        else:
            self.month_option_menu.configure(state="normal")
        self.fill_operation_info_frame()

    def year_filter_checkbox_event(self):
        checkbox_state = self.year_filter_checkbox_var.get()
        if checkbox_state == "disabled":
            self.year_option_menu.configure(state="disabled")
        else:
            self.year_option_menu.configure(state="normal")
        self.fill_operation_info_frame()

    def _init_history_frame(self):

        self.history_frame = ctk.CTkFrame(master=self.tabview.tab("History"))
        self.history_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.history_frame.columnconfigure([0, 2, 4], weight=6)
        self.history_frame.columnconfigure([1, 3, 5], weight=1)
        self.history_frame.rowconfigure([0, 1, 2, 3, 4, 5], weight=0)

        self.day_filter_label = ctk.CTkLabel(self.history_frame, text="Day")
        self.day_filter_label.grid(row=1, column=0, sticky="ew")

        self.month_filter_label = ctk.CTkLabel(self.history_frame, text="Month")
        self.month_filter_label.grid(row=1, column=2, sticky="ew")

        self.year_filter_label = ctk.CTkLabel(self.history_frame, text="Year")
        self.year_filter_label.grid(row=1, column=4, sticky="ew")

        self.operations_info_frame = ctk.CTkScrollableFrame(self.history_frame)
        self.operations_info_frame.grid(row=5, column=0, pady=10, columnspan=6, sticky="nsew")
        self.operations_info_frame.columnconfigure([0, 1, 2, 3, 4, 5], weight=1)
        self.operations_info_frame.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], weight=1)

        self.init_option_menus()
        self.init_switches()
        self.fill_operation_info_frame()

####### CheckBoxes ######
    def init_switches(self):
        switch = ["disabled", "normal"]
        self.filter_checkbox_var = ctk.StringVar(value=switch[0])
        self.filter_checkbox = ctk.CTkCheckBox(self.history_frame, text="Filters", command=self.filter_checkbox_event,
                                               variable=self.filter_checkbox_var, onvalue=switch[1], offvalue=switch[0])
        self.filter_checkbox.grid(row=0, column=0)

        self.day_filter_checkbox_var = ctk.StringVar(value=switch[0])
        self.day_filter_checkbox = ctk.CTkCheckBox(self.history_frame, text="",
                                                   command=self.day_filter_checkbox_event,
                                                   variable=self.day_filter_checkbox_var, onvalue=switch[1],
                                                   offvalue=switch[0])
        self.day_filter_checkbox.grid(row=2, column=1, padx=5, sticky="w")

        self.month_filter_checkbox_var = ctk.StringVar(value=switch[0])
        self.month_filter_checkbox = ctk.CTkCheckBox(self.history_frame, text="",
                                                     command=self.month_filter_checkbox_event,
                                                     variable=self.month_filter_checkbox_var, onvalue=switch[1],
                                                     offvalue=switch[0])
        self.month_filter_checkbox.grid(row=2, column=3, padx=5, sticky="w")

        self.year_filter_checkbox_var = ctk.StringVar(value=switch[0])
        self.year_filter_checkbox = ctk.CTkCheckBox(self.history_frame, text="",
                                                    command=self.year_filter_checkbox_event,
                                                    variable=self.year_filter_checkbox_var, onvalue=switch[1],
                                                    offvalue=switch[0])
        self.year_filter_checkbox.grid(row=2, column=5, padx=5, sticky="w")
        self.default_checkbox_values()

    def default_checkbox_values(self):
        self.filter_checkbox.select()
        self.day_filter_checkbox.select()
        self.month_filter_checkbox.select()
        self.year_filter_checkbox.select()

####### Option Menus ######
    def init_option_menus(self):
        now = datetime.now()
        self.day_option_menu = ctk.CTkOptionMenu(self.history_frame, values=[str(day) for day in range(1, 32)],
                                                 command=self.set_filter_day)
        self.day_option_menu.grid(row=2, column=0, columnspan=1, sticky="ew")
        self.day_option_menu.set(str(now.day))
        self.filtered_day = (str(now.day))

        self.month_option_menu = ctk.CTkOptionMenu(self.history_frame, values=MONTHS, command=self.set_filter_month)
        self.month_option_menu.grid(row=2, column=2, columnspan=1, sticky="ew")
        self.month_option_menu.set(str(MONTHS[now.month - 1]))
        self.filtered_month = (str(MONTHS[now.month - 1]))

        self.year_option_menu = ctk.CTkOptionMenu(self.history_frame, values=self.get_years(),
                                                  command=self.set_filter_year)
        self.year_option_menu.grid(row=2, column=4, columnspan=1, sticky="ew")
        self.year_option_menu.set(now.year)
        self.filtered_year = now.year

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def fill_operation_info_frame(self):
        self.clear_frame(self.operations_info_frame)
        self.filter_information()

        self.data_label = ctk.CTkLabel(self.operations_info_frame,
                                       text=f"Year: {(self.filters[2] if self.filters[2] is not None else 'All')}    "
                                            f"Month: {(self.filters[1] if self.filters[1] is not None else 'All')}    "
                                            f"Day: {(self.filters[0] if self.filters[0] is not None else 'All')}")
        self.data_label.grid(row=0, column=0, columnspan=6, sticky="ew")

        self.needed_data = [[[year, month, day], ops] for year, months in self.filtered_data.items() for month, days in
                            months.items() for day, ops in days.items()]

        row = 0
        for date_operation in self.needed_data:
            for index, operation in enumerate(date_operation[1]):
                timeline = '/'.join(date_operation[0])
                label = ctk.CTkLabel(self.operations_info_frame, text=f"{timeline}")
                label.grid(row=row + 1, column=0, sticky="ew")

                spent_label = ctk.CTkLabel(self.operations_info_frame, text=f"Transaction:")
                spent_label.grid(row=row + 1, column=1, sticky="ew", padx=10)

                spent = ctk.CTkEntry(self.operations_info_frame,
                                     font=('Arial', 24), insertwidth=2, justify='center')
                spent.insert(0, str(operation['value']))
                spent.configure(state="disabled")
                spent.grid(row=row + 1, column=2, pady=10, sticky="ew")

                category_label = ctk.CTkLabel(self.operations_info_frame, text=f"Category:")
                category_label.grid(row=row + 1, column=3, sticky="ew", padx=10)

                category = ctk.CTkOptionMenu(self.operations_info_frame, values=self.get_categories(), state="disabled")
                category.grid(row=row + 1, column=4, columnspan=1, padx=10, sticky="ew")
                category.set(operation['category'])
                category.configure(state="disabled")

                save_button = ctk.CTkButton(self.operations_info_frame, text="Save",
                                            command=lambda t=date_operation[0], i=index,
                                                           s=spent, c=category: self.save_edit(t, i, s, c), width=50,
                                            state="disabled")

                button = ctk.CTkButton(self.operations_info_frame, text="Delete",
                                       command=lambda t=date_operation[0], i=index: self.delete_operation(t, i),
                                       width=60, state="disabled")

                save_button.grid(row=row + 1, column=5, pady=10, sticky="ew", padx=5)
                button.grid(row=row + 1, column=6, pady=10, sticky="ew", padx=5)

                edit_var = ctk.StringVar(value="disabled")
                edit = ctk.CTkCheckBox(self.operations_info_frame, text="Edit", command=lambda
                    edit_array=[edit_var, spent, category, save_button, button]: self.edit_operation(edit_array),
                                       variable=edit_var, onvalue="normal", offvalue="disabled", width=50)
                edit.grid(row=row + 1, column=7, pady=10, sticky="ew", padx=5)

                row += 1

    def save_edit(self, time, index, spent_entry, category_menu):
        try:
            year, month, day = time
            new_value = float(spent_entry.get())
            new_category = category_menu.get()

            operation = self.data["Operations"][year][month][day][index]

            self.balance -= operation["value"]
            self.balance += new_value

            operation["value"] = new_value
            operation["category"] = new_category

            self.change_balance()
            self.save_to_file()
            self.fill_operation_info_frame()
            print("Changes saved successfully")
        except ValueError:
            print("Invalid input for value. Please enter a numeric value.")
        except Exception as e:
            print(f"Failed to save changes: {e}")

    def filter_information(self):
        self.filters = [None, None, None]
        if self.filter_checkbox_var.get() == "normal":
            if self.day_filter_checkbox_var.get() == "normal":
                self.filters[0] = self.filtered_day
            if self.month_filter_checkbox_var.get() == "normal":
                self.filters[1] = self.filtered_month
            if self.year_filter_checkbox_var.get() == "normal":
                self.filters[2] = self.filtered_year

        filtered_data = self.data["Operations"]

        if self.filters[2] is not None:
            filtered_data = {year: month for year, month in filtered_data.items() if year == str(self.filters[2]).zfill(2)}

        if self.filters[1] is not None:
            filtered_data = {year: {month: day for month, day in months.items() if month == str(self.filters[1]).zfill(2)}
                for year, months in filtered_data.items()}

        if self.filters[0] is not None:
            filtered_data = {year: {month: {day: ops for day, ops in days.items() if day == str(self.filters[0]).zfill(2)}
                                    for month, days in months.items()} for year, months in filtered_data.items()}
        self.filtered_data = filtered_data

    def delete_operation(self, time, index):
        try:
            year = time[0]
            month = time[1]
            day = time[2]

            operation = self.data["Operations"][year][month][day][index]

            self.balance -= operation["value"]

            self.data["Operations"][year][month][day].pop(index)

            if not self.data["Operations"][year][month][day]:
                del self.data["Operations"][year][month][day]
                if not self.data["Operations"][year][month]:
                    del self.data["Operations"][year]

            self.change_balance()
            self.save_to_file()
            self.fill_operation_info_frame()
            self.update_option_menus()
            print("successful delete")
        except Exception as e:
            print(f"Deletion faced an error: {e}")

    def edit_operation(self, edit_array):
        if edit_array[0].get()=="disabled":
            for button in edit_array[1:]:
                button.configure(state="disabled")
        else:
            for button in edit_array[1:]:
                button.configure(state="normal")



###########################################################
###########################################################
# Settings tab
###########################################################
###########################################################
# settings frame
##############################################################

    def _init_settings_tab_frames(self):
        self.settings_frame = ctk.CTkScrollableFrame(master=self.tabview.tab("Settings"))
        self.settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.settings_frame.grid_columnconfigure([0, 2], weigh=1)
        self.settings_frame.grid_columnconfigure([1], weigh=2)
        self.settings_frame.grid_rowconfigure([0], weigh=1)
        self.settings_frame.grid_rowconfigure([1], weigh=3)

        self.settings_label = ctk.CTkLabel(self.settings_frame, text="Settings", font=("Arial", 30))
        self.settings_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10)

        self.category_label = ctk.CTkLabel(self.settings_frame, text="Enter new category:")
        self.category_label.grid(row=2, column=0, sticky="e")

        self.category_entry = ctk.CTkEntry(self.settings_frame, font=('Arial', 24), insertwidth=2, justify='center')
        self.category_entry.grid(row=2, column=1, columnspan=1, padx=5, sticky="")

        self.category_button = self.create_button(self.settings_frame, "Add Category", self.add_category,
                                                  2, 2, "ew", 1)

###########################################################
###########################################################
# Statistics tab
###########################################################

    def _init_statistics_tab_frames(self):
        self.statistics_frame = ctk.CTkFrame(
            master=self.tabview.tab("Statistics"))
        self.statistics_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure columns
        self.statistics_frame.grid_columnconfigure(0, weight=1)
        self.statistics_frame.grid_columnconfigure(1, weight=1)
        self.statistics_frame.grid_columnconfigure(2, weight=1)

        self.statistics_frame.grid_rowconfigure(0, weight=1)
        self.statistics_frame.grid_rowconfigure(1, weight=0)
        self.statistics_frame.grid_rowconfigure(2, weight=6)

        year_options = self.get_years()
        month_options = [MONTHS[i] for i in range(12)]

        self.year_combobox = ctk.CTkComboBox(self.statistics_frame, values=year_options)
        self.year_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.year_combobox.set(str(datetime.now().year))

        self.month_combobox = ctk.CTkComboBox(self.statistics_frame, values=month_options)
        self.month_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.month_combobox.set(MONTHS[datetime.now().month - 1])

        self.generate_graph_button = ctk.CTkButton(self.statistics_frame, text="Generate Graph",
                                                   command=self.generate_statistics_graph)
        self.generate_graph_button.grid(row=0, column=2, padx=10, pady=10)

    def generate_statistics_graph(self):
        selected_year = self.year_combobox.get()
        selected_month = str(MONTHS.index(self.month_combobox.get()) + 1).zfill(2)

        monthly_operations = self.data["Operations"].get(selected_year, {}).get(selected_month, {})
        expenses_per_day = {day: sum(op["value"] for op in ops) for day, ops in monthly_operations.items()}

        days = list(expenses_per_day.keys())
        expenses = list(expenses_per_day.values())

        plt.style.use('dark_background')

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(days, expenses, marker='o', color='cyan')
        ax.set_title(f"Balance in {self.month_combobox.get()} {selected_year}", color='white')
        ax.set_xlabel("Day", color='white')
        ax.set_ylabel("Balance", color='white')

        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        canvas = FigureCanvasTkAgg(fig, master=self.statistics_frame)
        canvas_widget = canvas.get_tk_widget()

        canvas_widget.grid(row=2, column=0, columnspan=3, sticky="nsew")

        plt.close(fig)

        self.statistics_frame.grid_rowconfigure(2, weight=6)
        self.statistics_frame.grid_columnconfigure(0, weight=1)

        self.statistics_frame.grid_rowconfigure(0, weight=1)
        self.statistics_frame.grid_rowconfigure(1, weight=0)

        canvas.draw()


###########################################################
# Working with data get and changing
###########################################################
    def set_filter_day(self, day):
        self.filtered_day = day.zfill(2)
        self.fill_operation_info_frame()

    def set_filter_month(self, month):
        self.filtered_month = str(MONTHS.index(month) + 1).zfill(2)
        self.fill_operation_info_frame()

    def set_filter_year(self, year):
        self.filtered_year = year
        self.fill_operation_info_frame()

    def set_category(self, category):
        self.category = category

    def get_years(self):
        try:
            if sorted(self.data["Operations"])==[]:
                raise AttributeError
            else:
                return sorted(self.data["Operations"])
        except AttributeError:
            return [str(datetime.now().year)]

    def get_categories(self):
        try:
            return sorted(self.data["Categories"])
        except AttributeError:
            return [DEFAULT_CATEGORY]

    def submit_calendar(self):
        date = self.date_entry.get_date()
        self.day = date.day
        self.month = MONTHS[date.month - 1]
        self.year = date.year

    def get_timestamp(self):
        self.submit_calendar()
        return f"{self.year}{str(MONTHS.index(self.month) + 1).zfill(2)}{str(self.day).zfill(2)}"

    def change_balance(self):
        self.data['balance'] = self.balance
        self.balance_label.configure(text=f"Balance: {self.balance}")

###########################################################
# Functions and methods of using variables
###########################################################
    def add_operation(self):
        self.submit_calendar()
        self.timestamp = self.get_timestamp()
        try:
            value = int(self.value_entry.get())
            self.balance += value
            operation = {
                "value": value,
                "category": self.category
            }
            try:
                self.data.setdefault("Operations", {}).setdefault(self.timestamp[0:4], {}).setdefault(
                    self.timestamp[4:6], {}).setdefault(self.timestamp[6:8], []).append(operation)
            except KeyError:
                self.data["Operations"] = {
                    self.timestamp[0:4]: {self.timestamp[4:6]: {self.timestamp[6:8]: [operation]}}}

            self.change_balance()
            self.sort_file()
            self.fill_operation_info_frame()
            self.update_option_menus()
            self.error_label.configure(text="Added", text_color="green")


        except ValueError as e:
            if self.value_entry.get() == "":
                self.error_label.configure(text="No input", text_color="red")
            else:
                self.error_label.configure(text="Your input is not numeric", text_color="red")

    def add_category(self):
        category = self.category_entry.get()
        if category in self.data["Categories"]:
            print("Category already exist")
        elif category != "":
            try:
                self.data["Categories"].append(category)
                self.category_option_menu.configure(values=self.get_categories())

            except:
                self.data["Categories"] = [category]
            self.save_to_file()
        else:
            print("Your input is invalid")

    def update_option_menus(self):
        self.year_option_menu.configure(values=self.get_years())


if __name__ == "__main__":
    app = App()
    app.mainloop()
