An API to help you gauge how much clothing you need for a given outdoors situation.

I built this thing because I wanted to be able to reliably predict how i'd feel warmth/coldness wise given the state of my body and weather conditions outside, so i started collecting data and build the python classifier. but i didn't like the programmatic interface for accessing the classifier provided by the library itself, so i wrote an API in java on top of the python script so it would be 1) easier for me to get my predictions and 2) i can potentially write a UI client to make the predictions even easier.

Use instructions:
1. Train the classifier: Upload the data you've collected as a CSV file