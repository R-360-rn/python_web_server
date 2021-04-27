FROM python:3
ADD web.py /
RUN pip install jsonschema
CMD [ "python", "./web.py" ]