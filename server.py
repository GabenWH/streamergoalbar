import asyncio
import os
import json
from aiohttp import web, ClientSession


def save_goal():
    with open(state_of_goal, "w") as file:
        json.dump({
            "current": goal_current
        },file)
def load_goal():
    try:
        with open(state_of_goal,"r") as file:
            data=json.load(file)
            return int(data.get("current",0))
    except(FileNotFoundError, json.JSONDecodeError):
        return 0

state_of_goal = "goal_state.json"
CB_USERNAME = os.environ["CB_USERNAME"]
CB_EVENTS_TOKEN = os.environ["CB_EVENTS_TOKEN"]

GOAL_TITLE = os.environ["CB_TITLE"]
GOAL_TARGET = int(os.environ["TARGET"])

goal_current = load_goal()

async def index(request):
    return web.FileResponse("overlay.html")


async def state(request):
    return web.json_response({
        "title": GOAL_TITLE,
        "current": goal_current,
        "target": GOAL_TARGET,
    })

async def reset(request):
    global goal_current
    data = await request.json()
    goal_current = int(data.get("current"))

    return web.json_response({
        "ok":True,
        "current":goal_current
    })

async def listen_to_chaturbate(app):
    global goal_current #this is gross weird and gay I hate python :P

    url = (
        f"https://eventsapi.chaturbate.com/events/"
        f"{CB_USERNAME}/{CB_EVENTS_TOKEN}"
    )

    session = ClientSession()

    try:
        #fix this cuz its stupid
        while True:
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    #this will fix it
                for event in data.get("events",[]):
                    print("EVENT:",event)

                    if event.get("method") == "tip":
                        tip = event.get("object",{})
                        amount = int(tip.get("tip",{}).get("tokens",0))
                        if amount>0:
                            goal_current += amount
                            save_goal()
                            print(\
                                f"tip added:{amount}"
                                f"goal: {goal_current}/{GOAL_TARGET}"
                            )
                    #MORE WILL NEED TO BE PUT HERE FOR THE TIP ADDS BUT NOT TODAY LOL
                next_url = data.get("nextUrl")

                #this will also fix it
                if next_url:
                    url = next_url
                else:
                    await asyncio.sleep(2)
            except Exception as error:
                print("so this happened:", error)
                await asyncio.sleep(5)
        
    finally:
        save_goal()
        await session.close()


async def start_listener(app):
    app["listener"] = asyncio.create_task(
        listen_to_chaturbate(app)
    )
async def stop_listener(app):
    app["listener"].cancel()

    try:
        await app["listener"]
    except asyncio.CancelledError:
        pass

app = web.Application()

app.router.add_get("/", index)
app.router.add_get("/api/state", state)
app.router.add_post("/api/reset", reset)

app.on_startup.append(start_listener)
app.on_cleanup.append(stop_listener)


web.run_app(
    app,
    host="127.0.0.1",
    port=8765
)