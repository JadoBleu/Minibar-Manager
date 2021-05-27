#!/usr/bin/env python3
"""
    Rio Hondo College
    CIT 128: Python Programming II
    Student Directed Project
    Jefferson Wang
    Spring 2021
"""

from dotenv import dotenv_values
from mysql.connector import connect, Error
import fnmatch
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarIconListItem, IconRightWidget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.properties import StringProperty

data = {}


class Ingredient:
    """
    Class containing the general info about an ingredient.

    Attributes:
        set_in_stock: set the self.available attribute to True
        set_no_stock: set the self.available attribute to False
    """

    def __init__(self, inventoryID, ingredientName, available):
        """
        Args:
            id(int): the corresponding id in the database
            name(str): the name of the recipe
            available(bool): indicates whether the ingredient is in stock, default is False
        """
        self.id = inventoryID
        self.name = ingredientName
        self.available = bool(available)
        self.recipes_found = []

    def set_in_stock(self, recipe_list):
        """
        Sets ingredint in stock.

        Marks corresponding recipes that use said ingredient as available.

        Checks said recipes if all ingredients are available and marks it.

        Args:
            recipe_list: the dictionary of objects of class Recipe.
        """
        # check if changes need to be made
        if self.available == True:
            return
        else:
            self.available = True
            # mark ingredients as available
            for n in self.recipes_found:
                recipe_list[n].ingredients_needed[self.id][2] = True
                # check if all ingredients are available
                for key in recipe_list[n].ingredients_needed:
                    # if any ingredient is not available, break from current recipe
                    if recipe_list[n].ingredients_needed[key][2] == True:
                        continue
                    else:
                        break
                # if all ingredients are available,
                else:
                    recipe_list[n].available = True

    def set_no_stock(self):
        # check if changes need to be made
        if self.available == False:
            return
        else:
            self.available = False
            # mark ingredients as unavailable
            for n in self.recipes_found:
                data["recipe_list"][n].ingredients_needed[self.id][2] = False
                data["recipe_list"][n].available = False

    def toggle_available(self):
        if self.available == True:
            self.set_no_stock()
        else:
            self.set_in_stock(data["recipe_list"])

    def add_recipe_location(self, recipeID):
        """
        Appends the recipeID to the list of where the ingredient is used
        Args:
            recipeID(int): the recipeID where the ingredient is used
        """
        self.recipes_found.append(recipeID)


class Recipe:
    """
    Class containing the general info about a recipe, not including ingredients.

    Attributes:
        set_like: set the self.like attribute to True
        set_dislike: set the self.like attribute to False
        update_comment(str): replaces the self.comment with the inputted string
        add_ingredient(list): appends an ingredient to self.ingredients_needed
    """

    def __init__(self, id, name, instructions, garnish, like, comments):
        """
        Args:
            id(int): the corresponding id in the database
            name(str): the name of the recipe
            instructions(str): special instructions regarding the recipe
            garnish(str): recommended garnish items
            like(bool): indicates whether the recipe is liked/disliked/neither
            comments(str): any personal comments the user added to the recipe
        """
        self.id = id
        self.name = name
        self.instructions = instructions
        self.garnish = garnish
        self.like = bool(like)
        self.comments = comments
        self.available = False
        self.ingredients_needed = {}

    def set_like(self):
        self.like = True

    def set_dislike(self):
        self.like = False

    def update_comment(self, text):
        self.comment = text

    def set_available(self):
        self.available = True

    def add_ingredient(self, ingredient):
        """
        Appends the ingredient to the list of ingredients needed

        Args:
            ingredient(list): [ingredientID, amount, unit, available]}

        """
        if len(self.ingredients_needed) == 0:
            self.ingredients_needed = {
                ingredient[0]: [ingredient[1], ingredient[2], ingredient[3]]
            }
        else:
            self.ingredients_needed[ingredient[0]] = [
                ingredient[1],
                ingredient[2],
                ingredient[3],
            ]


def search_name(where, text=""):
    """
    Searches the list for any objects where the name contains text.

    A custom exception is declared for when the argument is acceptable

    Args:
        where(str): the list of objects to search for;
        text (str): this is the text that is queried for

    Returns:
        A list of the corresponding IDs that match the result.

    Raises:
        ArgumentError: Raised when the parameter for 'what' does not match the required strings.
    """
    search = f"*{text}*"
    result = []
    for i in where:
        if fnmatch.fnmatch(where[i].name, search):
            result.append(where[i].id)
    return result


class StartScreen(Screen):
    def setup(self):
        # declare globals
        global data
        # create the connection
        connection = self.create_db_connection()
        data = {}
        # query the connected database for data
        data["ingredient_list"] = self.get_ingredient_list(connection)
        data["recipe_list"] = self.get_recipe_list(connection)

        # retrieve the list of ingredients needed for each recipe
        self.get_ingredients_needed(data, connection)

        # close the connection
        if connection.is_connected():
            connection.close()
        # do any test prints to verify functions
        # test_prints(data["ingredient_list"], data["recipe_list"])

    def create_db_connection(self):
        """
        Make the connection using the credentials found in the .env file.

        Return:
            Returns the connection.

        Exception:
            Error: the connection has not been made
        """
        # config: a dictionary containing the host, user, password, and database}
        config = dotenv_values(".env")
        connection = None
        try:
            connection = connect(
                # make the connection with the database
                host=config["host"],
                user=config["user"],
                password=config["password"],
                database=config["database"],
            )
        except Error as e:
            print("error reading data from MySQL:", e)
        return connection

    def read_query(self, connection, query):
        """
        Perform a read query using connection.

        Args:
            connection: the connection data made in create_db_connection()
            query(str): the query to be made to the database in SQL.

        Returns:
            A list of dictionaries where each dictionary corresponds to a record returned from the query.
        """
        result = None
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
            except Error as e:
                print("error reading data from query:", e)

    def get_recipe_list(self, connection):
        """
        Queries the database for the list of recipes.

        Returns:
            a dictionary of objects of class Recipe
        """
        recipe_list = {}
        sql_query = "SELECT * FROM minibarmanager.recipe"
        records = self.read_query(connection, sql_query)
        for n in records:
            recipe_list[n[0]] = Recipe(n[0], n[1], n[2], n[3], n[4], n[5])
        return recipe_list

    def get_ingredient_list(self, connection):
        """
        Queries the database for the list of ingredients

        Returns:
            a dictionary of objects of class Ingredient
        """
        ingredient_list = {}
        sql_query = "SELECT * FROM minibarmanager.inventory"
        records = self.read_query(connection, sql_query)
        for n in records:
            ingredient_list[n[0]] = Ingredient(n[0], n[1], n[2])
        return ingredient_list

    def get_ingredients_needed(self, data, connection):
        """
        Queries the database for the list of ingredients needed per recipe.
        Calls Recipe.add_ingredient() for each result.
        Queries the databse for the list of recipes found per ingredient.
        Updates each Ingredient object with a list of the recipeIDs that uses the Ingredient.

        Args:
            data: the dictionary holding the following lists:
                recipe_list(dict): the dictionary holding the id and location of objects Recipe
                ingredients_list(dict): the dictionary holding the id and location of objects Ingredient

        Return:

        """

        sql_query = "SELECT recipeID, inventoryID, amount, unit  FROM minibarmanager.ingredientList ORDER BY recipeID;"
        result = self.read_query(connection, sql_query)

        for n in result:
            # ingredient = [ingredientID, amount, unit, available]
            available = False

            ingredient = [n[1], n[2], n[3], available]
            data["recipe_list"][n[0]].add_ingredient(ingredient)

        inventory_query = "SELECT inventoryID, recipeID  FROM minibarmanager.ingredientList ORDER BY inventoryID;"
        result_by_ing = self.read_query(connection, inventory_query)

        for n in result_by_ing:
            data["ingredient_list"][n[0]].add_recipe_location(n[1])


class MainMenu(Screen):
    pass


class RecipeList(Screen):
    global data

    def get_available_recipes(self):
        """
        searches through all recipes to find all recipes that can be made with ingredients in stock

        Return:
            a list of values corresponding to the index of recipes where self.available == True
        """
        result = []
        for n in data["recipe_list"]:
            if data["recipe_list"][n].available == True:
                result.append(n)
        return result

    def get_favorite_recipes(self, recipe_list, like=True):
        """
        returns a list of indices of recipes where like is True or False

        Args:
            recipe_list: a list of objects containing all recipes
            like(bool): select whether to return liked or not liked recipes

        Returns:
            A list of ID values for resulting recipes
        """
        result = []
        for n in recipe_list:
            if recipe_list[n].like == like:
                result.append(recipe_list[n].id)
        print(result)
        return result

    def get_r_list(self):
        self.ids.r_scroll.clear_widgets()
        for i in data["recipe_list"]:
            icon_name = "emoticon-sad-outline"
            if data["recipe_list"][i].available == True:
                icon_name = "emoticon-happy"
            icons = IconRightWidget(icon=icon_name)
            items = TwoLineAvatarIconListItem(
                text=data["recipe_list"][i].name,
                secondary_text=str(i),
                secondary_theme_text_color="Custom",
                secondary_text_color=(0.188, 0.188, 0.188),
                on_press=lambda x, item=i: self.show_recipe(item),
            )
            items.add_widget(icons)
            self.ids.r_scroll.add_widget(items)

    def show_recipe(self, id):
        self.manager.transition.direction = "left"
        self.manager.get_screen("r_disp").recipe_id = id
        self.manager.current = "r_disp"


class IngredientList(Screen):
    class ListItemWithCheckbox(TwoLineAvatarIconListItem):
        """Custom list item."""

    class RightCheckbox(IRightBodyTouch, MDCheckbox):
        """Custom right container."""

        def toggle_check(self, id):
            id = int(id)
            data["ingredient_list"][id].toggle_available()

    def get_i_list(self):
        global data
        for i in data["ingredient_list"]:
            self.ids.i_scroll.add_widget(
                self.ListItemWithCheckbox(
                    text=data["ingredient_list"][i].name,
                    secondary_text=str(i),
                    secondary_theme_text_color="Custom",
                    secondary_text_color=(0.188, 0.188, 0.188),
                )
            )

    def get_available_ingredients(self, ingredient_list, available=True):
        """
        returns a list of indices of ingredients where available = True/False

        Args:
            ingredient_list: a list of objects containing all ingredients
            available(bool): Select whether to return in stock or out of stock ingredients
        Returns:
            A list of ID values for resulting ingredients
        """
        result = []
        for n in ingredient_list:
            if ingredient_list[n].available == available:
                result.append(ingredient_list[n].id)

        return result


class RecipeDisplay(Screen):
    recipe_id = 0
    recipe_name = StringProperty("Recipe")
    garnish = StringProperty(" ")
    instructions = StringProperty(" ")

    def get_data(self):
        self.recipe_name = data["recipe_list"][self.recipe_id].name
        self.garnish = data["recipe_list"][self.recipe_id].garnish
        self.instructions = data["recipe_list"][self.recipe_id].instructions
        self.build_list(self.recipe_id)

    def build_list(self, id):
        global data
        self.ids.ingredient_scroll.clear_widgets()
        print(data["recipe_list"][id].name, data["recipe_list"][id].ingredients_needed)
        for i in data["recipe_list"][id].ingredients_needed:
            self.add_list_item(i, id)

    def add_list_item(self, i_id, r_id):
        global data
        name = data["ingredient_list"][i_id].name
        amount = "     "
        if data["recipe_list"][r_id].ingredients_needed[i_id][0] != None:
            amount = (
                "     "
                + str(data["recipe_list"][r_id].ingredients_needed[i_id][0])
                + " "
                + str(data["recipe_list"][r_id].ingredients_needed[i_id][1])
            )
        self.ids.ingredient_scroll.add_widget(
            TwoLineAvatarIconListItem(text=name, secondary_text=amount)
        )
        print("Name:", name, "\nAmount: ", amount)


# main ui app
class MinibarManagerApp(MDApp):
    sm = ScreenManager()

    def build(self):
        self.sm.add_widget(StartScreen(name="start"))
        self.sm.add_widget(MainMenu(name="m_menu"))
        self.sm.add_widget(RecipeList(name="r_list"))
        self.sm.add_widget(IngredientList(name="i_list"))
        self.sm.add_widget(RecipeDisplay(name="r_disp"))

        self.theme_cls.theme_style = "Dark"

        return self.sm


if __name__ == "__main__":
    MinibarManagerApp().run()
