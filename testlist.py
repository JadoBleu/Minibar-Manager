from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.icon_definitions import md_icons
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem, OneLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox

import main

KV = """
<ListItemWithCheckbox>:

    IconLeftWidget:
        icon: root.icon

    RightCheckbox:

<MD Checkbox>:

BoxLayout:

    ScrollView:

        MDList:
            id: container
"""


class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """Custom list item."""

    icon = StringProperty("bottle-wine")


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """Custom right container."""

    pass


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        for i in ingredient_list:
            self.root.ids.container.add_widget(
                ListItemWithCheckbox(
                    text=ingredient_list[i].name,
                    on_press=ingredient_list[i].toggle_available(recipe_list),
                ),
            )


connection = ""
recipe_list = {}
ingredient_list = {}

# create the connection
connection = main.create_db_connection()

# query the connected database for data
ingredient_list = main.get_ingredient_list(connection)
recipe_list = main.get_recipe_list(connection)

# retrieve the list of ingredients needed for each recipe
main.get_ingredients_needed(recipe_list, ingredient_list, connection)

# close the connection
if connection.is_connected():
    connection.close()
Test().run()
