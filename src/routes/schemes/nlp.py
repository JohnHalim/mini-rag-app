from pydantic import BaseModel
from typing import Optional


class PushRequest(BaseModel):
    
    '''This is a pydantic scheme for nlp router'''
    
    do_reset: Optional[int] = 0