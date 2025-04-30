Install following pip packages using CLI commands below:

python -m pip install uvicorn
python -m pip install fastapi uvicorn
python -m pip install grpcio grpcio-tools
python -m pip install grpcio grpcio-tools requests

Using either VScode terminal or CLI terminal, run the predictions_client.py:
python predictions_client.py

Then compile the server:
python grpc_server.py


Lastly, change the directory to frontend on VScode terminal and run the react page:
cd frontend

npm start

