from typing import Union, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app_database import Database
import pdfkit, jinja2

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Database
DATABASE_PATH = r"./cocktails.db"

#Models

class Ingredient(BaseModel):
    ingredient: str

class IngredientResponse(BaseModel):
    id: int
    ingredient: str

class IngredientAmount(BaseModel):
    ingredient_id: int
    amount: int

class IngredientAmountResponse(BaseModel):
    id: int
    ingredient: str
    amount: int

class Cocktail(BaseModel):
    name: str
    price: float
    imagename: str
    ingredients: List[IngredientAmount] 

class CocktailResponse(BaseModel):
    id: int
    name: str
    price: float
    imagename: str
    ingredients: List[IngredientAmount]

class AllCocktailsResponse(BaseModel):
    id: int
    name: str
    price: float
    imagename: str
    ingredients: List[IngredientAmountResponse]

class PDFDownloadResponse(BaseModel):
    download_url : str

@app.get("/ingredients/{item_id}",response_model=IngredientResponse)
def read_ingredient(ingredient_id: int):
    db_conn = Database(DATABASE_PATH)
    ingredient = db_conn.get_ingredient(ingredient_id)
    return ingredient

@app.get("/allingredients/",response_model=List[IngredientResponse])
def get_all_ingredients():
    db_conn = Database(DATABASE_PATH)
    ingredients = db_conn.all_ingredients()
    return ingredients

@app.get("/allcocktails/",response_model=List[AllCocktailsResponse])
def get_all_cocktails():
    db_conn = Database(DATABASE_PATH)
    cocktails = db_conn.all_cocktails()
    cocktail_list = []

    for k in cocktails.keys():
        ingredient_list = [ IngredientAmountResponse(
            id=i['id'],
            ingredient=i['ingredient'],
            amount=i['amount']
        ) for i in cocktails[k]['ingredients']]
        cocktail_list.append(
            AllCocktailsResponse(
                id=k,
                name=cocktails[k]['name'],
                price=cocktails[k]['price'],
                imagename =cocktails[k]['imagename'],
                ingredients=ingredient_list,
            )
        )
    return cocktail_list

#UPDATE METHODS

@app.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(ingredient_id: int, ingredient: Ingredient):
    db_conn = Database(DATABASE_PATH)
    success = db_conn.create_ingredient({
        'id': ingredient_id,
        'name':ingredient.ingredient,
    })
    return {"ingredient": ingredient.ingredient, "id": ingredient_id}

#CREATE METHODS

@app.post("/ingredients/addcocktail", response_model=CocktailResponse)
def add_cocktail(cocktail: Cocktail):
    db_conn = Database(DATABASE_PATH)
    success = db_conn.add_cocktail({
        'name':cocktail.name,
        'price':cocktail.price,
        'imagename' : cocktail.imagename,
        'ingredients':cocktail.ingredients
    })
    return {"id": success, "name": cocktail.name, 'price':cocktail.price,'ingredients':cocktail.ingredients}


@app.post("/cocktails/addingredient", response_model=IngredientResponse)
def add_ingredient(ingredient: Ingredient):
    db_conn = Database(DATABASE_PATH)
    #success= 1
    success = db_conn.add_ingredient({
        'ingredient':ingredient.ingredient,
    })
    return {"id": success, "ingredient": ingredient.ingredient}

@app.post('/cocktails/createpdf',response_model=PDFDownloadResponse)
def create_pdf(cocktail_ids: List[int]):
    print('Will create a PDF')
    #Get the cocktails from the database
    db_conn = Database(DATABASE_PATH)
    #success= 1
    context = {
        'cocktail_list' : db_conn.cocktails_with_ingredients(cocktail_ids)
    }
    print('COntext data', context)
    #Code below will generate the PDF
    # context = {
    #     'test_text' : 'This is a test'
    # }
    template_loader =  jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)
    
    template = template_env.get_template('pdf_template.html')
    output_text = template.render(context)
    #print('OUTPUTTED HTML', output_text)
    f = open("htmltest.html", "w")
    f.write(output_text)
    f.close()

    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    pdfkit.from_string(output_text,'pdf_gen.pdf',configuration=config,css='style.css',options={"enable-local-file-access": ""})
    return { 'download_url' : 'This will be a link to down load it' }