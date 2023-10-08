#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

from models import db, Hero, Power, Hero_powers

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        response_message = {
            "message": "WELCOME TO THE SUPER HEROES API."
        }
        return make_response(response_message, 200)

api.add_resource(Home, '/')

class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        hero_list = []
        for hero in heroes:
            hero_dict = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                
            }
            hero_list.append(hero_dict)
        return make_response(jsonify(hero_list), 200)

api.add_resource(Heroes, '/heroes')

class HeroByID(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            hero_dict = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                "powers": [
                    {
                        "id": hero_power.power.id,
                        "name": hero_power.power.name,
                        "description": hero_power.power.description,
                    }
                    for hero_power in hero.powers
                ]
            }
            return make_response(jsonify(hero_dict), 200)
        else:
            return make_response(jsonify({"error": "Hero not found"}), 404)

api.add_resource(HeroByID, '/heroes/<int:id>')

class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        power_list = []
        for power in powers:
            power_dict = {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            power_list.append(power_dict)
        return make_response(jsonify(power_list), 200)

api.add_resource(Powers, '/powers')

class Heropowers(Resource):
    def post(self):
        data = request.get_json()

        # Validate that the required fields are present in the request
        if not all(key in data for key in ("strength", "hero_id", "power_id")):
            return make_response(jsonify({"errors": ["Validation error: Include all required keys"]}), 400)

        strength = data["strength"]
        power_id = data["power_id"]
        hero_id = data["hero_id"]

        # Check if the Power and Hero exist
        power = Power.query.get(power_id)
        hero = Hero.query.get(hero_id)

        if not power or not hero:
            return make_response(jsonify({"errors": ["Validation error: Power or Hero doesn't exist"]}), 400)

        hero_power = Hero_powers(
            strength=strength,
            power_id=power_id,
            hero_id=hero_id
        )

        db.session.add(hero_power)
        db.session.commit()

        power_data = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }

        return make_response(jsonify(power_data), 201)

api.add_resource(Heropowers, '/hero_powers')

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: The requested resource does not exist.",
        404
    )
    return response

if __name__ == '__main__':
    app.run(port=5555,debug=True)
