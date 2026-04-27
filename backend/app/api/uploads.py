from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session
import boto3
from botocore.exceptions import ClientError
import uuid
from pathlib import Path
import shutil
from ..database import get_db
from ..models import User
from ..clerk_auth import get_current_active_user
from ..config import settings

router = APIRouter()


def _public_base_url(request: Request) -> str:
    """Prefer the public ngrok URL for images so Telegram can fetch them."""
    if settings.TELEGRAM_WEBHOOK_URL:
        return settings.TELEGRAM_WEBHOOK_URL.split("/api/telegram/webhook")[0].rstrip("/")
    return str(request.base_url).rstrip("/")


@router.post("/presigned-url")
def get_presigned_url(
    filename: str,
    content_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a presigned URL for uploading images directly to S3.
    
    Args:
        filename: Original filename
        content_type: MIME type (e.g., image/jpeg)
    
    Returns:
        Presigned URL and final S3 key
    """
    try:
        # Generate unique filename
        file_extension = filename.split('.')[-1]
        unique_filename = f"{current_user.id}/{uuid.uuid4()}.{file_extension}"
        
        # Create S3 client
        s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET_IMAGES,
                'Key': unique_filename,
                'ContentType': content_type
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        # Construct public URL
        public_url = f"https://{settings.S3_BUCKET_IMAGES}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
        
        return {
            "presigned_url": presigned_url,
            "public_url": public_url,
            "s3_key": unique_filename
        }
    
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating presigned URL: {str(e)}"
        )


@router.post("/local")
def upload_local_image(
    request: Request,
    file: UploadFile = File(...),
):
    """
    Local/demo upload endpoint.

    Stores product images on the local backend instead of S3. This keeps demos
    working without AWS credentials and returns a public ngrok URL when
    TELEGRAM_WEBHOOK_URL is configured.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are allowed"
        )

    try:
        # Keep local demo uploads independent of auth/session issues. Products
        # are still protected when saved, but images can be staged first.
        extension = Path(file.filename or "upload.jpg").suffix or ".jpg"
        upload_dir = Path("static") / "uploads" / "demo"
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4()}{extension}"
        destination = upload_dir / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        relative_url = f"/static/uploads/demo/{filename}"
        return {
            "public_url": f"{_public_base_url(request)}{relative_url}",
            "local_path": str(destination)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image locally: {str(e)}"
        )
