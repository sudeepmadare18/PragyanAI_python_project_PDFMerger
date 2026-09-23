# ============================================================
# PRAGYANAI PDF STUDIO
# Utility Functions
# ============================================================

import io
import uuid
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png"
}


# ============================================================
# MAXIMUM FILE SIZE
# ============================================================

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ============================================================
# CHECK FILE EXTENSION
# ============================================================

def get_file_extension(filename: str) -> str:

    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:

    extension = get_file_extension(filename)

    return extension in ALLOWED_EXTENSIONS


# ============================================================
# CHECK FILE SIZE
# ============================================================

def is_file_size_valid(
    file_data: bytes,
    max_size: int = MAX_FILE_SIZE
) -> bool:

    return len(file_data) <= max_size


# ============================================================
# FORMAT FILE SIZE
# ============================================================

def format_file_size(size_in_bytes: int) -> str:

    if size_in_bytes < 1024:

        return f"{size_in_bytes} Bytes"

    elif size_in_bytes < 1024 * 1024:

        return f"{size_in_bytes / 1024:.2f} KB"

    elif size_in_bytes < 1024 * 1024 * 1024:

        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

    else:

        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"


# ============================================================
# CONVERT IMAGE TO PDF
# ============================================================

def image_to_pdf(image_data: bytes) -> io.BytesIO:

    image = Image.open(
        io.BytesIO(image_data)
    )

    # --------------------------------------------------------
    # Handle transparency
    # --------------------------------------------------------

    if image.mode in ("RGBA", "LA", "P"):

        if image.mode == "P":

            image = image.convert("RGBA")


        background = Image.new(
            "RGB",
            image.size,
            "white"
        )


        if image.mode == "RGBA":

            background.paste(
                image,
                mask=image.getchannel("A")
            )

        else:

            background.paste(
                image
            )


        image = background

    else:

        image = image.convert("RGB")


    # --------------------------------------------------------
    # Save image as PDF in memory
    # --------------------------------------------------------

    pdf_buffer = io.BytesIO()

    image.save(
        pdf_buffer,
        format="PDF",
        resolution=100.0
    )

    pdf_buffer.seek(0)

    return pdf_buffer


# ============================================================
# ADD PDF TO WRITER
# ============================================================

def add_pdf_to_writer(
    writer: PdfWriter,
    pdf_data: bytes
):

    pdf_stream = io.BytesIO(
        pdf_data
    )

    reader = PdfReader(
        pdf_stream
    )


    # --------------------------------------------------------
    # Check encrypted PDF
    # --------------------------------------------------------

    if reader.is_encrypted:

        try:

            result = reader.decrypt("")

            if result == 0:

                raise ValueError(
                    "Password-protected PDF is not supported."
                )

        except Exception:

            raise ValueError(
                "Password-protected PDF is not supported."
            )


    # --------------------------------------------------------
    # Add pages
    # --------------------------------------------------------

    for page in reader.pages:

        writer.add_page(page)


# ============================================================
# MERGE PDF AND IMAGE DATA
# ============================================================

def merge_files(
    files_data: list
) -> io.BytesIO:

    writer = PdfWriter()


    for filename, file_data in files_data:

        extension = get_file_extension(
            filename
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


        else:

            raise ValueError(
                f"Unsupported file type: {filename}"
            )


    # --------------------------------------------------------
    # Check pages
    # --------------------------------------------------------

    if len(writer.pages) == 0:

        raise ValueError(
            "No pages found to merge."
        )


    # --------------------------------------------------------
    # Create output PDF
    # --------------------------------------------------------

    output = io.BytesIO()

    writer.write(
        output
    )

    output.seek(0)

    return output


# ============================================================
# GENERATE UNIQUE FILE NAME
# ============================================================

def generate_filename(
    prefix: str = "PragyanAI-Merged",
    extension: str = ".pdf"
) -> str:

    unique_id = uuid.uuid4().hex[:8]

    return f"{prefix}-{unique_id}{extension}"


# ============================================================
# SAVE FILE
# ============================================================

def save_file(
    file_data: bytes,
    output_directory: Path,
    filename: str
) -> Path:

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )


    file_path = (
        output_directory /
        filename
    )


    with open(
        file_path,
        "wb"
    ) as file:

        file.write(
            file_data
        )


    return file_path


# ============================================================
# DELETE FILE
# ============================================================

def delete_file(
    file_path: Path
) -> bool:

    if not file_path.exists():

        return False


    if not file_path.is_file():

        return False


    file_path.unlink()

    return True


# ============================================================
# CLEAR DIRECTORY
# ============================================================

def clear_directory(
    directory: Path
) -> int:

    deleted_count = 0


    if not directory.exists():

        return deleted_count


    for item in directory.iterdir():

        if item.is_file():

            try:

                item.unlink()

                deleted_count += 1

            except Exception:

                pass


    return deleted_count


# ============================================================
# GET FILE INFORMATION
# ============================================================

def get_file_info(
    file_path: Path
) -> dict:

    return {

        "filename": file_path.name,

        "size": file_path.stat().st_size,

        "size_formatted":
            format_file_size(
                file_path.stat().st_size
            ),

        "extension":
            file_path.suffix.lower(),

        "type":
            "application/pdf"

    }


# ============================================================
# GET ALL GENERATED FILES
# ============================================================

def get_generated_files(
    directory: Path
) -> list:

    files = []


    if not directory.exists():

        return files


    for file_path in directory.iterdir():

        if file_path.is_file():

            files.append(
                get_file_info(
                    file_path
                )
            )


    return files
