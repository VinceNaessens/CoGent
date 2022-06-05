# Project CoGent Guide
## Installation
This section will provide more details regarding the installation of the CoGent Guide. 
1. Navigate to the root working directory
2. Run ```pip install -r requirements.txt```

The requirements file contains all needed packages and dependencies which will automatically be downloaded and installed by executing this command. 

## Usage
There are two servers which need to be powered up before using the application. This can be accomplished by executing the following commands from the root working directoryin two different terminals:
1. ```uvicorn main:app --host 0.0.0.0 --port 5000```
2. ```python frontend/app.py```

Both servers can be visited via http://127.0.0.1:5000/ and http://127.0.0.1:8000/ respectively.

Locations of the points of interest are now fetched using a temporary license of [PositionStack][4]. The number of requests to the API is however limited. In order to circumvent the limited number of requests, the possibility to use dummy data has been added in the code. In the ```load_map``` function of callbacks.py and in the ```handle_search``` callback of callbacks.py, parts that rely on the API can be commented out and be replaced by their dummy counterparts.

## Application
The application allows users to query a certain keyword, this keyword will be matched with several possible synonyms. In the input form, the user can also select certain zones in which the user want to search for possible matches with the keyword and the synonyms. After entering the keyword, the user can consult the output in two different visualizations. First, all locations that match with the entered keyword or their synonyms will be pinpointed on the map. Secondly, all objects resulting from the querried keypoint can be consulted via the tab "Objects". All tags which match the certain object can be consulted by clicking the "Read more" button on the card of the specific object.  

### Deliverables
The [Silent Demo][1] presents all features of the application CoGent. Next to this, the [User Story][2] provides more details about the users who will work with the application. The canvasses can be found when clicking on this [link][3].

Final pitch slides: [TODO]

[1]:https://youtu.be/R25ouoxh1rY "Silent Demo"
[2]:https://youtu.be/7bckddyx9jY "User Story"
[3]:https://miro.com/app/board/uXjVO-KzCvs=/ "link"
[4]:https://positionstack.com/ "Positionstack"

### Known problems
- When using the application in other browsers than Google Chrome, the map can experience some issues resulting in a black screen.
- Recursive query can be very slow


NOT FINISHED: Final pitch slides still have to be linked
