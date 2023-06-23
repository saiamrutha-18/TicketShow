from flask_restful import Api ,Resource,reqparse
from model import *

api=Api()
class Ven_id_Api(Resource):
    def get(self,id):
        venue=Venues.query.filter_by(venue_id=id).first()
        if venue:
            return {"id":venue.venue_id,"vname":venue.venue_name,"place":venue.place,"location":venue.location,"capacity":venue.capacity},200
        else:
            return { "error" : "no such venue" }, 404

    def delete(self,id):
        venue=Venues.query.filter_by(venue_id=id).first()
        venue_shows_to_del = Venue_shows.query.filter_by(venue_id=id).all()
        for venue_show in venue_shows_to_del:
            db.session.delete(venue_show)
        if venue:
            db.session.delete(venue)
            db.session.commit()
            return {"status":"deleted"}, 202
        else:
            return { "error" : "no such venue to delete " }, 404

    def put(self,id):
        p=reqparse.RequestParser()
        p.add_argument('vname',type=str,required=True)
        p.add_argument('place',type=str,required=True)
        p.add_argument('location',type=str,required=True)
        p.add_argument('capacity',type=int,required=True)
        args=p.parse_args()
        venue=Venues.query.filter_by(venue_id=id).first()
        if venue:
            venue.venue_name=args["vname"]
            venue.place=args["place"]
            venue.location=args["location"]
            venue.capacity=args["capacity"]
            db.session.commit()
            return {"id":venue.venue_id,"vname":venue.venue_name,"place":venue.place,"location":venue.location,"capacity":venue.capacity},200
        else:
            return { "error" : "no such venue to update" }, 404

        
class All_Ven_Api(Resource):
    def get(self):
        all_venues={}
        v1= Venues.query.all()
        for ven in v1:
            all_venues[ven.venue_id]=ven.venue_name
        return all_venues
    
    def post(self):
        p=reqparse.RequestParser()
        p.add_argument('vname',type=str,required=True)
        p.add_argument('place',type=str,required=True)
        p.add_argument('location',type=str,required=True)
        p.add_argument('capacity',type=int,required=True)
        args=p.parse_args()
        venue=Venues(venue_name=args["vname"],place=args["place"],location=args["location"],capacity=args["capacity"])
        db.session.add(venue)
        db.session.commit()
        return {"id":venue.venue_id,"vname":venue.venue_name,"place":venue.place,"location":venue.location,"capacity":venue.capacity,},200


api.add_resource(All_Ven_Api,"/api/all_venues")
api.add_resource(Ven_id_Api,"/api/venue/<int:id>")

