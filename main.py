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


def create_db_connection():
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


def read_query(connection, query):
    """
    Perform a read query using connection.

    Args:
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
                recipe_list[n].ingredients_needed[self.id][2] = False
                recipe_list[n].available = False

    def add_recipe_location(self, recipeID):
        """
        Appends the recipeID to the list of where the ingredient is found
        Args:
            recipeID(int): the recipeID where the ingredient is found
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


def get_ingredient_list(connection):
    """
    Queries the database for the list of ingredients

    Returns:
        a dictionary of objects of class Ingredient
    """
    ingredient_list = {}
    sql_query = "SELECT * FROM minibarmanager.inventory"
    records = read_query(connection, sql_query)
    for n in records:
        ingredient_list[n[0]] = Ingredient(n[0], n[1], n[2])
    return ingredient_list


def get_recipe_list(connection):
    """
    Queries the database for the list of recipes.

    Returns:
        a dictionary of objects of class Recipe
    """
    recipe_list = {}
    sql_query = "SELECT * FROM minibarmanager.recipe"
    records = read_query(connection, sql_query)
    for n in records:
        recipe_list[n[0]] = Recipe(n[0], n[1], n[2], n[3], n[4], n[5])
    return recipe_list


def get_ingredients_needed(recipe_list, ingredient_list, connection):
    """
    Queries the database for the list of ingredients needed per recipe.
    Calls Recipe.add_ingredient() for each result.
    Queries the databse for the list of recipes found per ingredient.
    Updates each Ingredient object with a list of the recipeIDs that uses the Ingredient.

    Args:
        recipe_list(dict): the dictionary holding the id and location of valid objects: Recipe
        ingredient_list(dict): the dictionary holding the id and location of valid objects: Ingredient

    Return:

    """

    sql_query = "SELECT recipeID, inventoryID, amount, unit  FROM minibarmanager.ingredientList ORDER BY recipeID;"
    result = read_query(connection, sql_query)

    # get available ingredients so as to not overwrite existing availbility
    available_list = get_available_ingredients(ingredient_list, True)
    for n in result:
        # ingredient = [ingredientID, amount, unit, available]
        available = False
        for m in available_list:
            if n == m:
                available = True
        ingredient = [n[1], n[2], n[3], available]
        recipe_list[n[0]].add_ingredient(ingredient)

    inventory_query = "SELECT inventoryID, recipeID  FROM minibarmanager.ingredientList ORDER BY inventoryID;"
    result_by_ing = read_query(connection, inventory_query)

    for n in result_by_ing:
        ingredient_list[n[0]].add_recipe_location(n[1])


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


def get_favorite_recipes(recipe_list, like=True):
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


def get_available_ingredients(ingredient_list, available=True):
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


def get_available_recipes(recipe_list):
    """
    searches through all recipes to find all recipes that can be made with ingredients in stock

    Args:
        recipe_list: a dictionary of objects of class Recipe.

    Return:
        a list of values corresponding to the index of recipes where self.avaialabe == True
    """
    result = []
    for n in recipe_list:
        if recipe_list[n].available == True:
            result.append(n)
    return result


def test_prints(ingredient_list, recipe_list, connection):
    # for n in recipe_list:
    #    print(recipe_list[n].name, recipe_list[n].ingredients_needed)

    # for n in ingredient_list:
    #    print(ingredient_list[n].name, ingredient_list[n].recipes_found)

    # search for recipes containing 'bomb'
    # results = search_name(recipe_list, "bomb")
    # for n in results:
    #    print(recipe_list[n].name)

    # search for ingredients containing 'rum'
    # results = search_name(ingredient_list, "rum")
    # for n in results:
    #    print(ingredient_list[n].name)

    # favorites = get_favorite_recipes(recipe_list)
    # print(favorites.name)

    # available = get_available_ingredients(ingredient_list)
    # print(available)

    # Test to see if the recipe search for available recipes based on inventory is working
    # for n in (183, 608, 611, 554, 391, 234, 606):
    #    ingredient_list[n].set_in_stock(recipe_list)
    # available = get_available_recipes(recipe_list)
    # for key in available:
    #    print(recipe_list[key].name)

    return


def main():
    # create the connection
    connection = create_db_connection()

    # query the connected database for data
    ingredient_list = get_ingredient_list(connection)
    recipe_list = get_recipe_list(connection)

    # retrieve the list of ingredients needed for each recipe
    get_ingredients_needed(recipe_list, ingredient_list, connection)

    # do any test prints to verify functions
    test_prints(ingredient_list, recipe_list, connection)

    # close the connection
    if connection.is_connected():
        connection.close()


if __name__ == "__main__":

    main()
