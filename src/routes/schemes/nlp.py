from pydantic import BaseModel
from typing import Optional


class PushRequest(BaseModel):
    
    '''This is a pydantic scheme for nlp router.   
       only has do_reset --> optional int = 0'''
    
    do_reset: Optional[int] = 0