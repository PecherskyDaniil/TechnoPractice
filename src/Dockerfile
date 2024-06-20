FROM python:3.7

# Create app directory
WORKDIR /app

# Install app dependencies
COPY ./requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/gnss-lab/gnss-tec@dev
# Bundle app source
COPY ./publisher.py /app
VOLUME ./rnxfiles
EXPOSE 8080
