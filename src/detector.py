# This file is to detect the type of pdf

from typing import Literal

DocType = Literal["echallan","na"]

def detect_doc_type(page_count:int)-> DocType:
    """Detect document type by simple page-count rule.

    - Fewer than 5 pages => NA document
    - 5 pages or more   => eChallan document
    """

    if page_count < 5:
        return "na"
    
    return "echallan"