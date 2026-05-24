FROM python:3.12
WORKDIR /app

# Copy requirements.txt and install dependencies

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
	&& pip install setuptools wheel \
	&& pip install -r requirements.txt

# Copy application code (including your own pptx package)
COPY ./app /app
#COPY ./app/shared.py /usr/local/lib/python3.12/site-packages/pptx/oxml/shapes/
#COPY ./app/base.py /usr/local/lib/python3.12/site-packages/pptx/shapes/
#COPY ./app/collections /usr/local/lib/python3.10/collections
#COPY ./app/markupsafe /usr/local/lib/python3.10/site-packages/markupsafe

ENV FLASK_APP=hkdance.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000" ]



