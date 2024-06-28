FROM python:3.7

# Create app directory
WORKDIR /app

# Install app dependencies
COPY ./dockerrequirements.txt ./

RUN pip install -r dockerrequirements.txt
RUN pip install git+https://github.com/gnss-lab/gnss-tec@dev
# Bundle app source
COPY ./publisher.py /app

EXPOSE 8080
