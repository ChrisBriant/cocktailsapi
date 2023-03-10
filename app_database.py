import sqlite3, base64
from sqlite3 import Error



class Database:
    def __init__(self,path):
        sql_create_cocktails_table = """CREATE TABLE IF NOT EXISTS cocktail (
                                        id integer PRIMARY KEY,
                                        price real NOT NULL,
                                        name text NOT NULL,
                                        imagename text NOT NULL
                                    );"""

        sql_create_ingredients_table = """CREATE TABLE IF NOT EXISTS ingredient (
                                id integer PRIMARY KEY,
                                ingredient text NOT NULL
                            );"""

        sql_create_cocktails_ingredients_table = """CREATE TABLE IF NOT EXISTS cocktail_ingredient (
                        cocktail_id INTEGER,
                        ingredient_id INTEGER,
                        amount INTEGER,
                        CONSTRAINT fk_cocktail
                            FOREIGN KEY (cocktail_id)
                            REFERENCES cocktail(id),
                        CONSTRAINT fk_ingredient
                            FOREIGN KEY (ingredient_id)
                            REFERENCES ingredient(id)
                    );"""

        # create a database connection
        self.conn = self.create_connection(path)

        # create tables
        if self.conn is not None:
            # create projects table
            self.create_table(sql_create_cocktails_table)
            self.create_table(sql_create_ingredients_table)
            self.create_table(sql_create_cocktails_ingredients_table)
        else:
            print("Error! cannot create the database connection.")


    def create_connection(self,db_file):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            return self.conn
        except Error as e:
            print(e)

        return self.conn


    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_ingredient(self,item):
        sql = f''' UPDATE ingredient SET 
                    name = '{item['ingredient']}'
                WHERE id = {item['id']} '''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid


    def add_ingredient(self,item):
        sql = f''' INSERT INTO ingredient(ingredient)
                VALUES('{item['ingredient']}') '''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid

    def add_cocktail(self,item):
        sql = f''' INSERT INTO cocktail(name,price,imagename)
                VALUES('{item['name']}', {item['price']},'{item['imagename']}') '''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cocktail_id = cur.lastrowid
        for ingredient in item['ingredients']:
            sql = f''' INSERT INTO cocktail_ingredient(cocktail_id,ingredient_id,amount)
                VALUES({cocktail_id}, {ingredient.ingredient_id}, {ingredient.amount}) '''
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
        return cocktail_id

    def all_ingredients(self):
        sql = ''' SELECT * FROM ingredient '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        ingredients = [{
            'id' : r[0],
            'ingredient' : r[1],
        } for r in rows]
        return ingredients

    def all_cocktails(self):
        sql = ''' SELECT * FROM cocktail
                INNER JOIN cocktail_ingredient
                ON cocktail_ingredient.cocktail_id = cocktail.id
                INNER JOIN ingredient
                ON cocktail_ingredient.ingredient_id = ingredient.id
         '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cocktails = {}
        for r in rows:
            cocktails[r[0]] = {
                'name' : r[2],
                'price': r[1],
                'imagename' : r[3],
                'ingredients' : []
            }
        for r in rows:
            cocktails[r[0]]['ingredients'].append({
                'id' : r[7],
                'ingredient' : r[8],
                'amount' : r[6]
            })
        return cocktails

    def cocktails_with_ingredients(self,cocktail_ids):
        id_list_query = '('
        for i in range(0,len(cocktail_ids)):
            id_list_query += f'{cocktail_ids[i]})' if i == len(cocktail_ids)-1 else f'{cocktail_ids[i]},'
        sql = f'''select c.name,c.price,c.imagename, ci.amount, i.ingredient from cocktail as c inner join cocktail_ingredient as ci on ci.cocktail_id = c.id inner join ingredient as i on ci.ingredient_id = i.id  where c.id in {id_list_query} order by c.name;'''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cocktails_obj = {}
        for r in rows:
            with open(f'assets/{r[2]}', "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read())
            cocktails_obj[r[0]] = {
                'name' : r[0],
                'price': r[1],
                'imagename' : r[2],
                'ingredients' : [],
                'image_base64' : image_base64.decode(),
            }
        for r in rows:
            cocktails_obj[r[0]]['ingredients'].append({
                'amount' : r[3],
                'ingredient' : r[4],
            })
        cocktails_as_list = [ cocktails_obj[key] for key in cocktails_obj.keys()]
        return cocktails_as_list
