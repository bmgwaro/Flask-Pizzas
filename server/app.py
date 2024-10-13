#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants=Restaurant.query.all()
    restaurants_data=[{"id":restaurant.id, "name":restaurant.name, "address":restaurant.address} for restaurant in restaurants]
    return jsonify(restaurants_data)


# GET /restaurants/:id
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant=Restaurant.query.get(id)
    if restaurant:
        restaurant_data={
            "id":restaurant.id,
            "name":restaurant.name,
            "address":restaurant.address,
            "restaurant_pizzas":[]
        }
        return jsonify(restaurant_data)
    return jsonify({"error":"Restaurant not found"}), 404


# DELETE /restaurant/:id
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    
    if not restaurant:
        return jsonify({"error":"Restaurant not found"}), 404
    
    db.session.delete(restaurant)
    db.session.commit()
    
    return '', 204

# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_data = [{"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients} for pizza in pizzas]
    return jsonify(pizzas_data), 200

#POST restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")
    price = data.get("price")

    
    restaurant = Restaurant.query.get(restaurant_id)
    pizza = Pizza.query.get(pizza_id)

    if not restaurant or not pizza:
        return jsonify({"errors": ["validation errors"]}), 400

   
    if price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400

    
    new_restaurant_pizza = RestaurantPizza(
        pizza_id=pizza_id,
        restaurant_id=restaurant_id,
        price=price
    )

    
    db.session.add(new_restaurant_pizza)
    db.session.commit()

    
    return jsonify({
        "id": new_restaurant_pizza.id,
        "restaurant_id": restaurant_id,
        "pizza_id": pizza_id,
        "price": price,
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        },
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }
    }), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
