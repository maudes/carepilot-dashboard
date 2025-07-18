from fastapi import FastAPI

app = FastAPI(title="CarePilot Demo API")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "FastAPI is running 🎉"}


@app.get("/hello")
def say_hello(name: str = "world"):
    return {"greeting": f"Hello, {name}!"}
