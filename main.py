from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# @app.post("/v0/pdf/extract-pdf")

# @app.post("/v0/upload-file")

# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}
