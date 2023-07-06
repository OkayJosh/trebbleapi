### trebbleapi

_This repository contains the submission for the Trebble Hackathon._

### Documentation

[Please refer to the API documentation for detailed information about the endpoints and how to use them.](https://documenter.getpostman.com/view/22833562/2s93zFVyTM)

_In the above link, authenticate with your linkedin using oauth2 to authenticate with your linkedin account_

### Set up

Clone Repository
`git clone https://github.com/OkayJosh/trebbleapi.git`
Install Requirements
`pip install -r requirements.txt`
* Run the App
`python manage.py runserver`

* Verification
_obtain a **OPENAI** api-key_
* to use ssl obtain an self sign certificate with the following instructions
  `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout localhost.key -out localhost.crt` use `127.0.0.1` as the name
* Run the following command to start the server with HTTPS
  `python manage.py runserver_plus --cert-file localhost.crt`



Use the API key in your requests to access protected endpoints.
Remember to include the API key in the headers of your requests for authentication.

Feel free to reach out if you have any questions or need further assistance!