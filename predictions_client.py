import grpc
import ttc_pb2
import ttc_pb2_grpc
import uvicorn
from fastapi import FastAPI
from google.protobuf.json_format import MessageToDict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

def get_grpc_stub():
    channel = grpc.insecure_channel("localhost:50051")
    return {
        "route_list": ttc_pb2_grpc.RouteListServiceStub(channel),
        "route_config": ttc_pb2_grpc.RouteConfigServiceStub(channel),
        "predictions": ttc_pb2_grpc.PredictionsServiceStub(channel),
    }

@app.get("/routes") #API call used to retrieve routes
def get_route_list():
    #Returns list of routes
    stubs = get_grpc_stub()
    route_list_request = ttc_pb2.RouteListRequest(agency_tag="ttc")
    route_list_response = stubs["route_list"].GetRouteList(route_list_request)
    
    return {"routes": [{"route_name": r.route_name, "route_tag": r.route_tag} for r in route_list_response.routes]}

@app.get("/route_config/{route_tag}")
def get_route_config(route_tag: str):
    #Get all info related to a route, stops, directions, etc.
    stubs = get_grpc_stub()
    route_config_request = ttc_pb2.RouteConfigRequest(agency_tag="ttc", route_tag=route_tag)
    route_config_response = stubs["route_config"].GetRouteConfig(route_config_request)

    directions = []
    for direction in route_config_response.directions:
        directions.append({
            "direction_tag": direction.direction_tag,
            "direction_title": direction.direction_title,
            "direction_name": direction.direction_name,
            "stops": [stop for stop in direction.stops]
        })

    return MessageToDict(route_config_response)

@app.get("/predictions/{stop_id}/{route_tag}")
def get_predictions(stop_id: str, route_tag: str):
    #Next bus arrival time
    stubs = get_grpc_stub()
    prediction_request = ttc_pb2.PredictionRequest(agency_tag="ttc", stop_id=stop_id, route_tag=route_tag)
    prediction_response = stubs["predictions"].GetPrediction(prediction_request)

    return {
        "predictions": [
            {"direction": p.direction_title, "minutes": p.prediction}
            for p in prediction_response.next_bus_arrival
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
