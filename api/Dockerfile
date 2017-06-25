FROM api
ADD requirements.txt /tmp/requirements.txt
RUN python -m pip install -r /tmp/requirements.txt
ADD . /code
WORKDIR /code
EXPOSE 8000
#CMD ["python", "main.py"]
