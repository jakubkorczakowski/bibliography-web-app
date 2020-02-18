FROM python:3.7-alpine
WORKDIR /files_app
ENV FLASK_APP rest_files_app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 81
COPY ./files_app /files_app
RUN pip install -r requirements.txt
RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev
RUN pip install pyopenssl
RUN pip install flask-jwt-extended
CMD ["flask", "run", "--cert", "adhoc"]