from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import boto3
from botocore.exceptions import ClientError
import uuid
from ..database import get_db
from ..models import User
from ..clerk_auth import get_current_active_user
from ..config import settings

router = APIRouter()


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
