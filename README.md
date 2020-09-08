# Readme  

## Get started  

A get started page is avaliable within the app to help you use it correctly. Including some dummy data to test the app with a test user already set up.
A demo app is avaliable under the following address : https://uri-generator.herokuapp.com/ this is meant to play with a test user and do all the mistakes you can before messing a local database.  
This server is just a demo version, not to be used in a production context.

## URI generator  

This is a python application using Flask and Dash framework.
In order to run this application locally you should clone this repository.  
Open it using VScode (or an other software) set a python terminal and run the following commands :  

``` bash
start.sh
```

You will need to install the appropriate libraries. To do so *conda* environment or *venv* are suitable.  
you can read the requirements.txt file and install all the dependancies.  

 ``` bash
 pip install -r requirements.txt
 ```

## Docker run

The app is also compatible with Docker, you can build an image reading the dockerfile.

``` bash
docker build -t generator .
docker run -d --name=generatorURI -p 3838:3838 generator
```

## Adapt it  

The generator is using *jinja2* templates, it improves a base template named generator.html using :  

```python
{% extends "generator.html" %}
{% block title %}
```

To make use of this generator for your own instance, you can replace generator.html with your own page (using your own design). just make sure that the links to the different actions are accessibles.

For more details about the Flask framework you can see the official documentation [here](https://flask.palletsprojects.com/en/1.1.x/)  
For details about the VSCode implémentation see [here](https://code.visualstudio.com/docs/python/tutorial-flask)  
For additionnal questions about this app you can contact me at : jean-eudes.hollebecq@inare.fr  
