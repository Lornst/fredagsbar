import os

import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")


def callApi(method, path, body=None):
    try:
        response = httpx.request(method, API_URL + path, json=body, timeout=2)
        response.raise_for_status()
        return response
    except httpx.ConnectError:
        st.error("Kan ikke forbinde til API'en")
    except httpx.TimeoutException:
        st.error("API'en svarer for langsomt")
    except httpx.HTTPStatusError as error:
        st.error(error.response.json().get("error"))

    return None


st.title("Fredagsbar")

response = callApi("GET", "/events")
eventList = response.json() if response is not None else []

st.header("Oversigt")
st.dataframe([
    {
        "Titel": event["title"],
        "Dato": event["date"],
        "Tilmeldte": len(event["participants"]),
        "Ledige pladser": event["capacity"] - len(event["participants"]),
    }
    for event in eventList
])

st.header("Tilmeld og afmeld")

if eventList:
    eventTitle = st.selectbox("Event", [event["title"] for event in eventList])

    for event in eventList:
        if event["title"] == eventTitle:
            break

    eventId = event["id"]
    isFull = len(event["participants"]) >= event["capacity"]

    st.write("Deltagere:", ", ".join(event["participants"]))

    name = st.text_input("Dit navn", key="name")

    if st.button("Tilmeld", disabled=isFull or not name):
        if callApi("POST", f"/events/{eventId}/signups", {"name": name}) is not None:
            st.rerun()

    if st.button("Afmeld", disabled=not name):
        if callApi("DELETE", f"/events/{eventId}/signups/{name}") is not None:
            st.rerun()

st.header("Opret event")

with st.form("newEvent"):
    title = st.text_input("Titel")
    date = st.date_input("Dato")
    capacity = st.number_input("Antal pladser", min_value=1, step=1)

    if st.form_submit_button("Opret"):
        body = {"title": title, "date": date.isoformat(), "capacity": int(capacity)}
        if callApi("POST", "/events", body) is not None:
            st.success("Event oprettet")
