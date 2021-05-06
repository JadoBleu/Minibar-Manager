#!/usr/bin/env python3
'''
    Rio Hondo College
    CIT 128: Python Programming II
    Student Directed Project
    Jefferson Wang
    Spring 2021
'''

from dotenv import dotenv_values
from mysql.connector import connect, Error


def create_db_connection():
    '''
    Make the connection using the credentials found in the .env file.

    Return:
        Returns the connection.

    Exception:
        Error: the connection has not been made
    '''
    # config: a dictionary containing the host, user, password, and database}
    config = dotenv_values(".env") 
    connection = None
    try:
        connection = connect(
            # make the connection with the database
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )
    except Error as e:
        print("error reading data from MySQL:", e)
    return connection


def query(query):
    '''
    Perform an execute query using the global connection.
    
    Args:
        query(str): the query to be made to the database in SQL
    '''
    global connection
    with connection.cursor() as cursor:
        try:
            cursor.execute(query)
            connection.commit()
        except Error as e:
            print("error executing query:", e)
    

def read_query(query):
    '''
    Perform a read query using the global connection.
    
    Args:
        query(str): the query to be made to the database in SQL.
    
    Returns:
        A list of dictionaries where each dictionary corresponds to a record returned from the query.
    '''
    global connection
    result = None
    with connection.cursor() as cursor:
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print("error reading data from query:", e)


class Ingredient:
    '''
    Class containing the general info about an ingredient.

    Attributes:
        set_in_stock: set the self.available attribute to True
        set_no_stock: set the self.available attribute to False
    '''
    def __init__(self, inventoryID, ingredientName, available):
        '''
        Args:
            id(int): the corresponding id in the database
            name(str): the name of the recipe
            available(bool): indicates whether the ingredient is in stock, default is False
        '''
        self.id = inventoryID
        self.name = ingredientName
        self.available = bool(available)
        self.recipe_found = []

    def set_in_stock(self):
        # check if changes need to be made
        global recipe_list
        if self.available == True:
            return
        else:
            self.available = True
            # mark ingredients as available
            for n in self.recipe_found:
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
            for n in self.recipe_found:
                recipe_list[n].ingredients_needed[self.id][2] = False
                recipe_list[n].available = False


class Recipe:
    '''
    Class containing the general info about a recipe, not including ingredients.

    Attributes:
        set_like: set the self.like attribute to True
        set_dislike: set the self.like attribute to False
        update_comment(str): replaces the self.comment with the inputted string
    '''
    def __init__(self, id, name, instructions, garnish, like, comments):
        '''
        Args:
            id(int): the corresponding id in the database
            name(str): the name of the recipe
            instructions(str): special instructions regarding the recipe
            garnish(str): recommended garnish items
            like(bool): indicates whether the recipe is liked/disliked/neither
            comments(str): any personal comments the user added to the recipe
        '''
        self.id = id
        self.name = name
        self.instructions = instructions
        self.garnish = garnish
        self.like = bool(like)
        self.comments = comments
        self.available = False
        self.ingredients_needed = []
        
    def set_like(self):
        self.like = True

    def set_dislike(self):
        self.like = False
    
    def update_comment(self, text):
        self.comment = text

    def set_available(self):
        self.available = True

        
def get_ingredient_list():
    '''
    Queries the database for the list of ingredients.

    Updates the global list ingredient_id_list with valid inventoryIDs.

    Args:
        None
    
    Returns:
        a dictionary of objects of class Ingredient
    '''
    global ingredient_id_list
    ingredient_list = {}
    ing_id = []
    sql_query = "SELECT * FROM minibarmanager.inventory"
    records = read_query(sql_query)
    for n in records:
        ingredient_list[n[0]] = Ingredient(n[0], n[1], n[2])
        ing_id.append(n[0]) 
    
    ingredient_id_list = ing_id
    return ingredient_list


def get_recipe_list():
    '''
    Queries the database for the list of recipes.

    Updates the global list recipe_id_list with valid recipeIDs.

    Args:
        None
    
    Returns:
        a dictionary of objects of class Recipe
    '''
    global recipe_id_list
    recipe_list = {}
    rec_id = []
    sql_query = "SELECT * FROM minibarmanager.recipe"
    records = read_query(sql_query)
    for n in records:
        recipe_list[n[0]] = Recipe(n[0], n[1], n[2], n[3], n[4], n[5])
        rec_id.append(n[0]) 
    
    recipe_id_list = rec_id
    return recipe_list


def get_ingredients_needed(recipe_list, ingredient_list):
    '''
    Queries the database for the list of ingredients needed per recipe. 
    
    Updates each Recipe object with a dictionary of keys(ingredientIDs):values(the amount, unit, and availablility).

    Queries the databse for the list of recipes found per ingredient.

    Updates each Ingredient object with a list of the recipeIDs that object found in.

    Args:
        recipe_list(dict): the dictionary holding the id and location of valid objects: Recipe
        ingredient_lust(dict): the dictionary holding the id and location of valid objects: Ingredient
    '''
    
    sql_query = "SELECT recipeID, inventoryID, amount, unit  FROM minibarmanager.ingredientList ORDER BY recipeID;"
    result = read_query(sql_query)
    n = 0
   
    while n < len(result):
        if result[n][0] != result[n-1][0]:
            # if the recipeID is different from the previous result, create a new dictionary key
            recipe_list[result[n][0]].ingredients_needed = {result[n][1]: [result[n][2], result[n][3], False]}
        else:
            # if the recipeID is the same as the previouos result, append the dictionary value(list) with another tuple.
            recipe_list[result[n][0]].ingredients_needed[result[n][1]]= [result[n][2], result[n][3], False]
        n += 1
    
    inventory_query = "SELECT inventoryID, recipeID  FROM minibarmanager.ingredientList ORDER BY inventoryID;"
    result_by_inv = read_query(inventory_query)
    n = 0
    while n < len(result):
        if result_by_inv[n][0] != result_by_inv[n-1][0]:
            ingredient_list[result_by_inv[n][0]].recipe_found = [result_by_inv[n][1]]
        else:
            ingredient_list[result_by_inv[n][0]].recipe_found.append(result_by_inv[n][1])
        n += 1
    

def search_name(text="", what= ""):
    '''
    Queries the database for a list of results.

    A custom exception is declared for when the argument is acceptable

    Args:
        text (str): this is the text that is queried for
        what(str): must be 'ingredient' or 'recipe;

    Returns:
        A list of the corresponding IDs that match the result.

    Raises:
        ArgumentError: when the parameter for 'what' does not match the required strings.
    '''
    class ArgumentError(Exception):
        pass

    result_index = []
    if what == "ingredient":
        where = "inventory"
    elif what == "recipe":
        where = "recipe"
    else:
        raise ArgumentError("arg:what must be 'ingredient' or 'recipe'")

    sql_query = f"SELECT {where}ID FROM minibarmanager.{where} WHERE {what}Name LIKE \"%{text}%\";"
    results = read_query(sql_query)
    for n in results:
        result_index.append(n[0])
    return result_index


def get_favorite_recipes(recipe_list, like = True):
    '''
    returns an index of recipes where like is True or False

    Args:
        recipe_list: a list of objects containing all recipes
        like(bool): select whether to return liked or not liked recipes
    
    Returns: 
        A list of ID values for resulting recipes
    '''
    global recipe_id_list
    rec_id = recipe_id_list
    result = []
    for n in rec_id:
        if recipe_list[n].like == like:
            result.append(recipe_list[n].id)
    return result


def get_available_ingredients(ingredient_list, available = True):
    '''
    returns an index of ingredients where available = True/False

    Args:
        ingredient_list: a list of objects containing all ingredients
        available(bool): Select whether to return in stock or out of stock ingredients
    Returns: 
        A list of ID values for resulting ingredients
    '''
    global ingredient_id_list
    ing_id = ingredient_id_list
    result = []
    for n in ing_id:
        if ingredient_list[n].available == available:
            result.append(ingredient_list[n].id)

    return result


#def get_available_recipes(ingredient_list, recipe_list, ingredients_needed):
    '''
    searches through all recipes to find all recipes that can be made with ingredients in stock

    '''
    #for n in recipe_list:


def test_prints():
    # for n in recipe_list:    
    #    print(recipe_list[n].name, recipe_list[n].ingredients_needed)
    
    # for n in ingredient_list:    
    #    print(ingredient_list[n].name, ingredient_list[n].recipe_found)

    # search for recipes containing 'bomb'
    # results = search_name("bomb", "recipe")
    # for n in results:
    #     print(recipe_list[n].name)
    
    # search for ingredients containing 'rum'
    # results = search_name("rum", "ingredient")
    
    # for n in results:
    #     print(ingredient_list[n].name)
    
    # favorites = get_favorite_recipes(recipe_list)
    # print(favorites)
    
    # available = get_available_ingredients(ingredient_list)
    # print(available)
    
    # Test to see if the recipe search for available recipes based on inventory is working  
    for n in (183,608,611,554,391,234,606):
        ingredient_list[n].set_in_stock()

    for n in recipe_id_list:
        
        if recipe_list[n].available == True:
            print(recipe_list[n].name)

    

    return


if __name__=="__main__":
    # create the connection 
    connection = create_db_connection()
    
    # retrieve the inventory list and populate a dictionary called ingredient_list 
    ingredient_id_list = [] # initialize the index of ingredients to be updated in get_ingredient_list()
    ingredient_list = get_ingredient_list() 
    
    # retrieve the recipe list and populate a dictionary called recipe_list 
    recipe_id_list = [] # initialize the index of recipes to be updated in get_recipe_list()
    recipe_list = get_recipe_list()
    
    # retrieve the list of ingredients needed for each recipe
    get_ingredients_needed(recipe_list, ingredient_list)


    test_prints()


    # close the connection
    if connection.is_connected():
        connection.close()
