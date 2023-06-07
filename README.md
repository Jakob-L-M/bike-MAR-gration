# Bike-MAR-Gration

As part of the lecture "Data Integration" at the University of Marburg Bela Schinke and Jakob L. Müller launched the (Next)Bike Mar(burg) (inte)gration project.

This document will given an overview over the steps taken, technologies used and the goal we want to archive.

## Structure

This data integration project has four components: preparation, data integration, data cleaning, and showcase.

- `data`: This folder explains how we obtained the underlying data. We describe the data pools as well as why and how we use the data.

- `preperation`: Code to extract and load the datasets into a MySQL Database. Here we also do some selections, transformation and perform basic cleaning

- `integration`: We perform On-Line integration. The folder includes some of the used queries and information how the different sources are integrated on varying request.

- `prediction-training`: Experiments to use the integrated dataset to predict bike distribution changes.

- `web-showcase`: Code to run the interactive web app and use the integration pipeline.

## Documentation

All code documentation and instructions should be placed in this `README.md`;
feel free to erase this intro text.
