#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def restaurant():
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurant_dict={
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address
        }
        restaurants.append(restaurant_dict)
        response = make_response(
            jsonify(restaurants),
            200
        )
        return response

    
@app.route('/restaurants/<int:id>', methods=['GET'])  
def get_restaurant(id):
    session = db.session
    restaurant = session.get(Restaurant, id)
    if restaurant:
        restaurant_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [
                {
                    'id': pizza.id,
                    'pizza_id': pizza.pizza_id,
                    'restaurant_id': pizza.restaurant_id,
                    'price': pizza.price,
                    'pizza_name': Pizza.query.get(pizza.pizza_id).name
                }
                for pizza in RestaurantPizza.query.filter_by(restaurant_id=restaurant.id).all()
            ]
        }
        response = make_response(
            jsonify(restaurant_dict),
            200
        )
        return response
    else:
        response = make_response(
            jsonify({'error': 'Restaurant not found'}),
            404
        )
        return response
    
@app.route('/restaurants/<int:id>' ,methods=['DELETE'])
def delete_restaurant(id):
    session = db.session
    restaurant = session.get(Restaurant, id)
    if restaurant:
        session.delete(restaurant)
        session.commit()
        response = make_response(
            jsonify({'message': 'Restaurant deleted'}),
            204
        )
        return response
    else:
        response = make_response(
            jsonify({'message': 'Restaurant not found'}),
            404
        )
        return response
    
@app.route('/pizzas', methods=['GET']) 
def get_pizzas():
    pizzas = []
    for pizza in Pizza.query.all():
        pizza_dict = {
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        }
        pizzas.append(pizza_dict)
    response = make_response(
        jsonify(pizzas),
        200
    )
    return response

@app.route('/restaurant_pizza', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        response = make_response(jsonify(restaurant_pizza.to_dict()), 201, {'content-type': 'application/json'})
        return response
    except Exception as e:
        print(str(e))  # Log the error
        if data["price"] < 1 or data["price"] > 30:
            return make_response({'error': 'Price must be between 1 and 30'}, 400)
        else:
            return make_response({'error': 'Failed to create restaurant pizza'}, 404)
if __name__ == "__main__":
    app.run(port=5555, debug=True)
