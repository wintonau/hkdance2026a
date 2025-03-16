FROM python:3.12
WORKDIR /app

COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

COPY ./app /app
COPY ./app/shared.py /usr/local/lib/python3.12/site-packages/pptx/oxml/shapes/
COPY ./app/base.py /usr/local/lib/python3.12/site-packages/pptx/shapes/
#COPY ./app/collections /usr/local/lib/python3.10/collections
#COPY ./app/markupsafe /usr/local/lib/python3.10/site-packages/markupsafe

ENV FLASK_APP=hkdance.py
ENV PYTHONUNBUFFERED=1
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8000" ]

