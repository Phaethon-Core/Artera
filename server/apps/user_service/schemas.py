from pydantic import BaseModel


class RegisterUser(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserDataResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    bio: str
    created_at: str


class ProfilePayload(BaseModel):
    bio: str
    instagram_link: str = None
    x_link: str = None
    art_station_link: str = None
