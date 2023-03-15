from fastapi import FastAPI
import uvicorn

def run(query):
    return f"Query successfully received {query}"
salesman = FastAPI()
books = {1: "yes", 2: "no"}
@salesman.get('/salesman/{query}')
async def perfect_salesman():
    return {"recommendation": run(query)}
if __name__ == '__main__':
    uvicorn.run(salesman, host='127.0.0.1', port='8000')