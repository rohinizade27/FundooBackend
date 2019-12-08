FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

COPY requirements.txt ./
RUN pip install -r requirements.txt

# COPY entrypoint.sh ./
# RUN echo $PATH
# RUN chmod 777 entrypoint.sh
COPY . ./

