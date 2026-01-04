from pydantic import BaseModel

class PaymentBase(BaseModel):
    amount: float
