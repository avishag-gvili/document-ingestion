Document Processing System - README
This system includes all the necessary steps to run the services, send API requests, and test the system.

Prerequisites
Docker and Docker Compose installed on your machine.
How to Run the System
1. Clone the Repository

git clone https://github.com/avishag-gvili/document-ingestion.git

2. Run Docker Compose
To start all the containers (Node.js, Python, PostgreSQL, RabbitMQ), use the following command:

docker-compose up --build
This command will build and start the required containers.

3. Send Data with POSTMAN or Command Line
Uploading a File Request:
URL: http://localhost:3000/upload
Method: POST

In POSTMAN, use the FORM-DATA type to upload a file.

If you prefer to send the request via command line:

curl -X POST -F "file=@/path/to/your/file.xlsx" http://localhost:3000/upload
The system will return the document ID (document_id), which will be stored in the database.

Checking Document Status
URL: http://localhost:3000/status/:id
Method: GET

Check the status of the document after uploading:

curl http://localhost:3000/status/1
The response will be something like this:

{
    "status": "processing"
}

4. If You Need to Restart the Containers
If you need to stop and restart the containers, use the following commands:


docker-compose down

docker-compose up --build
