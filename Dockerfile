FROM python:3.15.0a8-bookworm

WORKDIR /
COPY App App
COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install waitress

EXPOSE 8080
CMD ["waitress-serve", "--call", "App:create_app"]