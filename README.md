# Bike-MAR-Gration

As part of the lecture "Data Integration" at the University of Marburg Bela Schinke and Jakob L. Müller launched the (Next)Bike Mar(burg) (inte)gration project.

This document will given an overview over the steps taken, technologies used and the goal we want to archive.

## Structure

This data integration project has four components: preparation, data integration, data cleaning, and showcase.

- `data`: This folder explains how we obtained the underlying data. We describe the data pools as well as why and how we use the data.

- `preparation`: Code to extract and load the datasets into a MySQL Database. Here we also do some selections, transformation and perform basic cleaning

- `integration`: We perform On-Line integration. The folder includes some of the used queries and information how the different sources are integrated on varying request.

- `prediction-training`: Experiments to use the integrated dataset to predict bike distribution changes.

- `web-showcase`: Code to run the interactive web app and use the integration pipeline.

- `presentations`: Milestone presentations in the context of the course

## Documentation

### Running the dev version locally
First init node.js
```
cd web-showcase
npm install
```
Then start the tailwind watcher and node server
```
npx tailwindcss -i ./input.css -o ./assets/css/tw.css --watch
```
```
npm run dev
```
This will start a server listening on localhost:3000 which auto updates/restarts on changes

### Using the trained model in production
We use the tensorflowjs python library to converted the trained model for web usage. See the [official tutorial](https://www.tensorflow.org/js/tutorials/conversion/import_saved_model). For us, a clean python 3.11.4 was used

Command for conversion, execute in a shell an root level
```
tensorflowjs_converter ./prediction-training/models/MODEL-NAME ./web-showcase/assets/model --input_format=tf_saved_model --output_node_names=web-model
```