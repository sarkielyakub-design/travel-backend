from pydantic import BaseModel


class BookingCreate(BaseModel):
    surname: str
    first_name: str
    given_names: str
    nationality: str
    phone: str
    email: str
    
    passport_number: str
    place_of_birth: str
    date_of_birth: str
    passport_issue: str
    passport_expiry: str