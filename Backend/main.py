```python
# ============================================================
# PRAGYANAI PDF STUDIO
# FastAPI Backend
# ============================================================

import io
import os
import uuid
import shutil
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import (
    StreamingResponse,
    FileResponse
)

from pypdf import (
    PdfReader,
    PdfWriter
)

from PIL import Image


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "PragyanAI PDF Studio"

VERSION = "1.0.0"

MAX_FILES = 20

MAX_FILE_SIZE = 50 * 1024 * 1024   # 50 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png"
}


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    description="PDF and Image Merger API",
    version=VERSION
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "generated_files"

OUTPUT_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# ROOT API
# ============================================================

@app.get("/")
async def root():

    return {
        "application": APP_NAME,
        "version": VERSION,
        "status": "running",
        "message": "PragyanAI PDF Studio API is running"
    }


# ============================================================
# HEALTH API
# ============================================================

@app.get("/api/health")
async def health_check():

    return {
        "status": "online",
        "application": APP_NAME,
        "version": VERSION
    }


# ============================================================
# CHECK FILE EXTENSION
# ============================================================

def check_extension(filename: str):

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                "Allowed types are PDF, JPG, JPEG and PNG."
            )
        )

    return extension


# ============================================================
# CHECK FILE SIZE
# ============================================================

async def check_file_size(file: UploadFile):

    contents = await file.read()

    size = len(contents)

    if size > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                f"{file.filename} is too large. "
                "Maximum file size is 50 MB."
            )
        )

    return contents


# ============================================================
# CONVERT IMAGE TO PDF
# ============================================================

def image_to_pdf(image_data: bytes):

    try:

        image = Image.open(
            io.BytesIO(image_data)
        )

        # Convert image to RGB
        # Required because PDF does not support
        # some image modes such as RGBA directly.

        if image.mode in ("RGBA", "LA", "P"):

            background = Image.new(
                "RGB",
                image.size,
                "white"
            )

            if image.mode == "P":

                image = image.convert("RGBA")

            background.paste(
                image,
                mask=image.getchannel("A")
                if image.mode == "RGBA"
                else None
            )

            image = background

        else:

            image = image.convert("RGB")


        # Save image as PDF in memory

        pdf_buffer = io.BytesIO()

        image.save(
            pdf_buffer,
            format="PDF",
            resolution=100.0
        )

        pdf_buffer.seek(0)

        return pdf_buffer


    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to process image: {str(error)}"
        )


# ============================================================
# MERGE PDF FILES
# ============================================================

def add_pdf_to_writer(
    writer: PdfWriter,
    pdf_data: bytes
):

    try:

        pdf_stream = io.BytesIO(
            pdf_data
        )

        reader = PdfReader(
            pdf_stream
        )

        if reader.is_encrypted:

            try:

                reader.decrypt("")

            except Exception:

                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDF files are not supported."
                )


        for page in reader.pages:

            writer.add_page(page)


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid PDF file: {str(error)}"
        )


# ============================================================
# MERGE API
# ============================================================

@app.post("/api/merge")
async def merge_files(
    files: list[UploadFile] = File(...)
):

    # --------------------------------------------------------
    # CHECK NUMBER OF FILES
    # --------------------------------------------------------

    if len(files) < 2:

        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 files."
        )


    if len(files) > MAX_FILES:

        raise HTTPException(
            status_code=400,
            detail=f"You can upload a maximum of {MAX_FILES} files."
        )


    # --------------------------------------------------------
    # CREATE PDF WRITER
    # --------------------------------------------------------

    writer = PdfWriter()


    # --------------------------------------------------------
    # PROCESS FILES IN UPLOAD ORDER
    # --------------------------------------------------------

    for file in files:

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="A file has no filename."
            )


        extension = check_extension(
            file.filename
        )


        # Read file

        file_data = await check_file_size(
            file
        )


        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if extension == ".pdf":

            add_pdf_to_writer(
                writer,
                file_data
            )


        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        elif extension in (
            ".jpg",
            ".jpeg",
            ".png"
        ):

            image_pdf = image_to_pdf(
                file_data
            )


            reader = PdfReader(
                image_pdf
            )


            for page in reader.pages:

                writer.add_page(page)


    # --------------------------------------------------------
    # CHECK RESULT
    # --------------------------------------------------------

    if len(writer.pages) == 0:

        raise HTTPException(
            status_code=400,
            detail="No valid pages were found in the uploaded files."
        )


    # --------------------------------------------------------
    # WRITE MERGED PDF TO MEMORY
    # --------------------------------------------------------

    merged_pdf = io.BytesIO()

    writer.write(
        merged_pdf
    )

    merged_pdf.seek(0)


    # --------------------------------------------------------
    # CREATE OUTPUT FILE
    # -----------------------
```
