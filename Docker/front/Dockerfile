FROM python:3.7-alpine
WORKDIR /front_app
ENV FLASK_APP front_app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 80
COPY ./front_app /front_app
RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev
RUN pip install -r requirements.txt
RUN pip install pyopenssl
RUN pip install flask-jwt-extended
CMD ["flask", "run", "--cert", "adhoc"]
#CMD ["flask", "run", "--cert", "adhoc", "--no-reload"]
#CMD ["python", "front_app.py"]
