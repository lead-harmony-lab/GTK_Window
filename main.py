import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="OpenGL Window Experiment")
        self.set_border_width(10)
        self.set_default_size(500, 400)
        #self.set_size_request(200, 100)

        #16 How to create a file chooser dialog
        layout_16 = Gtk.Box(spacing=6)
        #self.add(layout_16)

        button = Gtk.Button("Choose File")
        button.connect("clicked", self.on_file_clicked)
        layout_16.add(button)

        #15 How to create pop-up dialogue
        button = Gtk.Button("Open a PopUp")
        button.connect("clicked", self.popup_clicked)
        self.add(button)

        #12 How to create a tree view
        # List of tuples containing data to display in tree view
        people = [("George Taki", 80, "Comms Officer"),
                  ("Ohura Stretch", 23, "Bridge Officer"),
                  ("James T Kirk", 30, "Starghip Captain"),
                  ("Scotty Boy", 42, "Engineering Officer"),
                  ("Lennard MaCoy", 45, "Doctor")]
        layout_12 = Gtk.Box()
        #self.add(layout_12)

        # Each Gtk.TreeView has an associated Gtk.TreeModel. Tree models are usually a Gtk.ListStore
        people_list_store = Gtk.ListStore(str, int, str)  # This constructs the the model

        # list of tuples needs to be converted into ListStore view to be compatable with tree view
        for item in people:
            people_list_store.append(list(item))  # Converts tuple into a list: (n1, n2, n3, ...) => [n1, n2, n3, ...]

        # Treeview is the item that is displayed
        people_tree_view = Gtk.TreeView(people_list_store)
        # We only need to update data in the List Store and the tree view will be automatically updated.

        # This loop creates three columns and adds them to the TreeView
        for i, col_title in enumerate(["Name", "Age", "Profession"]):
            # Manage how to draw the data
            renderer = Gtk.CellRendererText()

            # Create columns (text is the column number)
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)

            # Make columns sortable
            column.set_sort_column_id(i)

            # Add column to TreeView
            people_tree_view.append_column(column)

        # Handle Selection
        selected_row = people_tree_view.get_selection()
        selected_row.connect("changed", self.item_selected)  # item_selected defined below

        # Add the TreeView to the main layout
        layout_12.pack_start(people_tree_view, True, True, 0)


        #for row in people_list_store:
            #print(row[:])
            #print(row[2])

        #11 How to create user input area
        # Layout
        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        #self.add(vertical_box)

        # Username Field
        self.username = Gtk.Entry()  # Input Area
        self.username.set_text("Username")
        vertical_box.pack_start(self.username, True, True, 0)

        # Password Field
        self.password = Gtk.Entry()
        self.password.set_text("Password")
        self.password.set_visibility(False)
        vertical_box.pack_start(self.password, True, True, 0)

        # Sign-in Button
        self.button = Gtk.Button(label="Sign In")
        self.button.connect("clicked", self.sign_in)  # sign_in function defined below
        vertical_box.pack_start(self.button, True, True, 0)

        #10 How to create text styling
        # Create Table Row
        horizontal_box = Gtk.Box(spacing=20)
        horizontal_box.set_homogeneous(False)  # If True, all children get equal space
        # Create Table Data
        vertical_box_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vertical_box_left.set_homogeneous(False)
        # Create Table Data
        vertical_box_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vertical_box_right.set_homogeneous(False)

        # Pack Table Data into continuous row configuration
        horizontal_box.pack_start(vertical_box_left, True, True, 0)
        horizontal_box.pack_start(vertical_box_right, True, True, 0)

        # Normal label
        label = Gtk.Label("This is a plain label")
        vertical_box_left.pack_start(label, True, True, 0)

        # Left Aligned Label
        label = Gtk.Label()
        label.set_text("This is the left aligned text\nMuch lines!\nSuch variety.")
        label.set_justify(Gtk.Justification.LEFT)
        vertical_box_left.pack_start(label, True, True, 0)

        # Right Aligned Label
        label = Gtk.Label("This is the right aligned text\nSuch excitement!")
        label.set_justify(Gtk.Justification.RIGHT)  # Can also set justification to FILL
        vertical_box_left.pack_start(label, True, True, 0)

        # Line Wrapping
        label = Gtk.Label("Hi! My name is... What? My name is... Who? My name is... Slick-a-slick-a Slim Shady!")
        label.set_line_wrap(True)
        vertical_box_right.pack_start(label, True, True, 0)

        # Markup
        label = Gtk.Label()
        label.set_markup("<small>Small text</small>\n"
                         "<big>Big text</big>\n"
                         "<b>This is BOLD text</b>\n"
                         "<i>This is italic text</i>\n"
                         "<a href=\"https://www.google.ca\" title=\"Hover Text\">Search on Google</a>")
        label.set_line_wrap(True)
        vertical_box_right.pack_start(label, True, True, 0)


        #self.add(horizontal_box)


        #9 How to create a notebook
        self.notebook = Gtk.Notebook()
        #self.add(self.notebook)

        # First page (of the notebook)
        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.page1.add(Gtk.Label("Here is the stuff that is in the main area of page 1"))
        self.notebook.append_page(self.page1, Gtk.Label("First Tab"))

        # Second page (of the notebook)
        self.page2 = Gtk.Box()
        self.page2.set_border_width(10)
        self.page2.add(Gtk.Label("Here is the stuff that is in the main area of page 2"))
        icon = Gtk.Image.new_from_icon_name("gnome-dev-cdrom-audio", Gtk.IconSize.MENU)
        self.notebook.append_page(self.page2, icon)


        #8 How to create a header bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = "App of Wonderous Choice"
        #self.set_titlebar(header_bar)

        # Action button on right
        action_button = Gtk.Button()
        cd_icon = Gio.ThemedIcon(name="gnome-dev-cdrom-audio")
        image = Gtk.Image.new_from_gicon(cd_icon, Gtk.IconSize.BUTTON)
        action_button.add(image)
        header_bar.pack_end(action_button)

        # Create a box of linked items
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        # Left arrow
        left_arrow = Gtk.Button()
        left_arrow.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        box.add(left_arrow)

        # Right arrow
        right_arrow = Gtk.Button()
        right_arrow.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        box.add(right_arrow)

        header_bar.pack_start(box)
        #self.add(Gtk.TextView())


        #7 How to create a stack switcher (tabs at top of main area)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        #self.add(box)

        # Create the stack (the main area)
        main_area = Gtk.Stack()
        main_area.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        main_area.set_transition_duration(1000)

        # Add content to the main area (1st tab) (stack)
        # Checkbox
        check_button = Gtk.CheckButton("Checking for main content")
        main_area.add_titled(check_button, "check_button_name", "Check Box")

        # Add content to the main area (2nd tab) (stack)
        label = Gtk.Label()
        label.set_markup("<big>OMG! This text is HUGE!</big>")
        main_area.add_titled(label, "label_name", "Big Label")

        # StackSwitcher
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(main_area)
        box.pack_start(stack_switcher, True, True, 0)
        box.pack_start(main_area, True, True, 0)



        #6 How to use a listbox
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        #self.add(listbox)

        # Add checkbox to listbox
        row_1 = Gtk.ListBoxRow()
        box_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=100)
        row_1.add(box_1)
        label = Gtk.Label("Check if you've checked this box")
        check = Gtk.CheckButton()
        box_1.pack_start(label, True, True, 0)
        box_1.pack_start(check, True, True, 0)
        listbox.add(row_1)

        # Add toggle switch to listbox
        row_2 = Gtk.ListBoxRow()
        box_2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=100)
        row_2.add(box_2)
        label = Gtk.Label("This switch is a real turn-on")
        switch = Gtk.Switch()
        box_2.pack_start(label, True, True, 0)
        box_2.pack_start(switch, True, True, 0)
        listbox.add(row_2)


        #5 How to use a grid layout
        grid = Gtk.Grid()
        #self.add(grid)

        #Create a bunch of buttons
        button1 = Gtk.Button(label="Button 1")
        button2 = Gtk.Button(label="Button 2")
        button3 = Gtk.Button(label="Button 3")
        button4 = Gtk.Button(label="Button 4")
        button5 = Gtk.Button(label="Button 5")
        button6 = Gtk.Button(label="Button 6")

        grid.add(button1)
        grid.attach(button2, 1, 0, 2, 1)
        grid.attach_next_to(button3, button1, Gtk.PositionType.BOTTOM, 1, 2)
        grid.attach_next_to(button4, button3, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach(button5, 1, 2, 1, 1)
        grid.attach_next_to(button6, button5, Gtk.PositionType.RIGHT, 1, 1)


        #4 How to add a box
        self.box = Gtk.Box(spacing=10)
        #self.add(self.box)

        # How to pack buttons in a box
        self.bacon_button = Gtk.Button(label="Bacon")
        self.bacon_button.connect("clicked", self.bacon_clicked)
        self.box.pack_start(self.bacon_button, True, True, 0)

        self.tuna_button = Gtk.Button(label="Tuna")
        self.tuna_button.connect("clicked", self.tuna_clicked)
        self.box.pack_start(self.tuna_button, True, True, 0)

        #3 How to add a basic Button
        self.button = Gtk.Button(label="Click here!")
        self.button.connect("clicked", self.button_clicked)
        #self.add(self.button)

    # User clicks button
    def button_clicked(self, widget):
        print("Render Time")

    def bacon_clicked(self, widget):
        print("You clicked bacon")

    def tuna_clicked(self, widget):
        print("you have clicked", ''.join(widget.get_properties("label")))

    # Function for sign-in button for section #11
    def sign_in(self, widget):
        print(self.username.get_text())
        print(self.password.get_text())

    # Function for user selected row in section #12
    def item_selected(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            print("Name: " + str(model[row][0]))
            print("Age: ", model[row][1])
            print("Job: ", model[row][2])
            print("")

    # Button for popup window in section #15
    def popup_clicked(self, widget):
        dialog = PopUp(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("You clicked the OK button")
        elif response == Gtk.ResponseType.CANCEL:
            print("You clicked the CANCEL button")

        dialog.destroy()

    # Button for file chooser dialog in section #16
    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Select a File", self, Gtk.FileChooserAction.OPEN,
                                       ("CANCEL", Gtk.ResponseType.CANCEL,
                                        "OPEN", Gtk.ResponseType.OK))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("You clicked the OPEN button.\n")
            print("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("You clicked the CANCEL button.")

        dialog.destroy()

class PopUp(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "ALERT - Title", parent, Gtk.DialogFlags.MODAL, (
            "Cancel Text", Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        ))
        self.set_default_size(200, 300)
        self.set_border_width(20)

        area = self.get_content_area()
        area.add(Gtk.Label("Derp! PopUp message of questioning!"))
        self.show_all()


window = MainWindow()


#2 How to add a label
label = Gtk.Label()
label.set_label("OMG. Label Text")
label.set_angle(30)
label.set_halign(Gtk.Align.END)
#window.add(label)

#print(label.get_properties("angle"))

window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()