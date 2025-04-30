import grpc
from concurrent import futures
import xml.etree.ElementTree as ET
import time
import requests
import ttc_pb2
import ttc_pb2_grpc

class RouteListServiceServicer(ttc_pb2_grpc.RouteListServiceServicer):
    def GetRouteList(self, request, context):
        agency_tag = request.agency_tag
        url = f"https://retro.umoiq.com/service/publicXMLFeed?command=routeList&a={agency_tag}"
        response = requests.get(url)
        root = ET.fromstring(response.text)

        routes = []
        for route in root.findall('route'):
            route_tag = route.get('tag')
            route_name = route.get('title')
            routes.append(ttc_pb2.Route(route_tag=route_tag, route_name=route_name)) 

        return ttc_pb2.RouteListResponse(routes=routes)

class RouteConfigServiceServicer(ttc_pb2_grpc.RouteConfigServiceServicer):
    def GetRouteConfig(self, request, context):
        print("In service")
        agency_tag = request.agency_tag
        route_tag = request.route_tag
        url = f"https://retro.umoiq.com/service/publicXMLFeed?command=routeConfig&a={agency_tag}&r={route_tag}"
        response = requests.get(url)

        root = ET.fromstring(response.text)

        route = root.find('route')

        stop_dict = {}
        print("before first")
        for stop in route.findall('stop'):
            stop_tag = stop.get('tag')
            stop_id = stop.get('stopId')
            stop_name = stop.get('title')
            if stop_id and stop_name and stop_tag:
                stop_dict[stop_tag] = ttc_pb2.RouteStop(
                    stop_id=stop_id,
                    stop_name=stop_name,
                    stop_tag=stop_tag
                )

        routes_dirs = []
        
        for direction in route.findall('direction'):
            direction_tag = direction.get('tag')
            direction_title = direction.get('title')
            direction_name = direction.get('name')

            # Collect stops for this specific direction
            stop_dir_objects = [
                stop_dict[stop_dir.get('tag')]
                for stop_dir in direction.findall('stop')
                if stop_dir.get('tag') in stop_dict
            ]

            if direction_tag and direction_title and direction_name:
                routes_dirs.append(ttc_pb2.RouteDirection(
                    direction_tag=direction_tag,
                    direction_title=direction_title,
                    direction_name=direction_name,
                    stops=stop_dir_objects
                ))

        #print(routes_dirs)

        return ttc_pb2.RouteConfigResponse(
            directions=routes_dirs
        )


class PredictionsServiceServicer(ttc_pb2_grpc.PredictionsServiceServicer):
    def GetPrediction(self, request, context):
        agency_tag = request.agency_tag
        stop_id = request.stop_id
        route_tag = request.route_tag
        url = f"https://retro.umoiq.com/service/publicXMLFeed?command=predictions&a={agency_tag}&stopId={stop_id}&routeTag={route_tag}"
        
        response = requests.get(url)
        print(response.text)

        root = ET.fromstring(response.text)
        prediction_final = []

        predictions = root.find('predictions')

        for direction in predictions.findall('direction'):
            prediction = direction.find('prediction')
            
            if prediction is not None:
                prediction_minute = prediction.get('minutes')
                direction_title = direction.get('title')
                
                prediction_final.append(ttc_pb2.PredictionFinal(direction_title=direction_title, prediction=prediction_minute))

        return ttc_pb2.PredictionResponse(next_bus_arrival=prediction_final)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ttc_pb2_grpc.add_RouteListServiceServicer_to_server(RouteListServiceServicer(), server)
    ttc_pb2_grpc.add_RouteConfigServiceServicer_to_server(RouteConfigServiceServicer(), server)
    ttc_pb2_grpc.add_PredictionsServiceServicer_to_server(PredictionsServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Server started...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # Keep server running
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
