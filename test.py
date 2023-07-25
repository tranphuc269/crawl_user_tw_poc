from fastapi import UploadFile
import io

def bytesio_to_uploadfile(bytes_io: io.BytesIO, filename: str, content_type: str) -> UploadFile:
    return UploadFile(filename=filename, content_type=content_type, file=bytes_io)
