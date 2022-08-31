from datetime import date, datetime
from flask import Flask, abort, request
from flask_restful import Api, Resource, reqparse, inputs
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import sys

app = Flask(__name__)

# write your code here
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)
api = Api(app)
parser = reqparse.RequestParser()


class EventDB(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)


class EventSchema(Schema):
    id = fields.Integer()
    event = fields.String()
    date = fields.Date()


db.create_all()


parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)


parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)


class EventResource(Resource):
    def get(self):
        schema = EventSchema(many=True)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time and end_time is not None:
            start_time = datetime.strptime(start_time, "%Y-%m-%d")
            end_time = datetime.strptime(end_time, "%Y-%m-%d")
            query = EventDB.query.filter(EventDB.date >= start_time, EventDB.date <= end_time)
            if query is None:
                abort(404, "The events doesn't exist!")
            return schema.dump(query)
        query = EventDB.query.all()
        return schema.dump(query)

    def post(self):
        schema = EventSchema()
        args = parser.parse_args()
        event = EventDB(event=args.event, date=args.date)
        db.session.add(event)
        db.session.commit()
        return {"message": "The event has been added!", "event": args.event, "date": str(args.date.date())}


class EventTodayResource(Resource):
    def get(self):
        schema = EventSchema(many=True)
        today = date.today()
        query = EventDB.query.filter_by(date=today)
        return schema.dump(query)


class EventIDResource(Resource):
    def get(self, entry_id):
        schema = EventSchema()
        query = EventDB.query.filter_by(id=entry_id).first()
        if query is None:
            abort(404, "The event doesn't exist!")
        return schema.dump(query)

    def delete(self, entry_id):
        schema = EventSchema()
        query = EventDB.query.filter_by(id=entry_id)
        element = query.first()
        print(query)
        if element is None:
            abort(404, "The event doesn't exist!")
        query.delete()
        db.session.commit()
        return {"message": "The event has been deleted!"}


api.add_resource(EventResource, '/event')
api.add_resource(EventTodayResource, '/event/today')
api.add_resource(EventIDResource, '/event/<int:entry_id>')


# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
