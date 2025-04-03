#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = db.session.execute(db.select(Plant)).scalars()
        response = [plant.to_dict(only=('id', 'name', 'image', 'price')) for plant in plants]
        # plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(response), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)

api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = db.session.execute(db.select(Plant).filter_by(id=id)).scalar_one_or_none()
        return make_response(plant.to_dict())
    
    def patch(self, id):
        plant = db.session.execute(db.select(Plant).filter_by(id=id)).scalar_one_or_none()
        params = request.json
        for attr in params:
            setattr(plant, attr, params[attr])
        db.session.commit()
        return make_response(plant.to_dict(), 200)
    
    def delete(self, id):
        plant = db.session.execute(db.select(Plant).filter_by(id=id)).scalar_one_or_none()  
        db.session.delete(plant)
        db.session.commit()
        return make_response({'message': f'Successfully deleted plant with id={id}'}, 204)



api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
