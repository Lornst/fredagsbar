from flask import Flask, request

app = Flask(__name__)


eventList = [
    {"id": 1, "title": "Quizaften", "date": "2026-11-13", "capacity": 3, "participants": ["Anna", "Bo"]},
    {"id": 2, "title": "Braetspilsaften", "date": "2026-11-20", "capacity": 8, "participants": ["Carl", "Dorte", "Emil"]},
    {"id": 3, "title": "Julefrokost", "date": "2026-12-04", "capacity": 20, "participants": []},
]

@app.get("/events")
def events():
    return eventList, 200

@app.get("/events/<int:id>")
def specificEvent(id):
    for event in eventList:
        if event.get("id") == id:
            return event, 200

    return {"error": "Event not found"}, 404

@app.post("/events")
def newEvent():
    data = request.get_json()

    if data.keys() != {"title", "date", "capacity"}:
        return {"error": "Event keys do not match or are missing"}, 400
    elif data.get("capacity") <= 0:
        return {"error": "Event capacity must be greater than 0"}, 400

    newEvent = {
        "id": max((event["id"] for event in eventList), default=0) + 1,
        "title" : data["title"],
        "date" : data["date"],
        "capacity" : data["capacity"],
        "participants" : [],
    }

    eventList.append(newEvent)
    return newEvent, 201


@app.post("/events/<int:id>/signups")
def signup(id):
    data = request.get_json()

    if data.keys() != {"name"}:
        return {"error": "Signup name is missing"}, 400

    for event in eventList:
        if event.get("id") == id:
            if len(event.get("participants")) >= event.get("capacity"):
                return {"error": "Event capacity full"}, 409
            elif data["name"] in event.get("participants"):
                return {"error": "Name already signed up to this event"}, 409

            event.get("participants").append(data["name"])
            return event, 201

    return {"error": "Event not found"}, 404

@app.delete("/events/<int:id>/signups/<name>")
def removeSignup(id, name):
    for event in eventList:
        if event.get("id") == id:
            if name not in event.get("participants"):
                return {"error": "Signup not found"}, 404

            event.get("participants").remove(name)
            return "", 204

    return {"error": "Event not found"}, 404

@app.delete("/events/<int:id>")
def deleteEvent(id):
    for event in eventList:
        if event.get("id") == id:
            eventList.remove(event)
            return "", 204

    return {"error": "Event not found"}, 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)