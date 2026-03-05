"""
OCR Service for extracting text from images using Amazon Textract
Uses AWS Textract for document text detection with S3 integration
"""

import boto3
import os
import io
from PIL import Image

textract = boto3.client('textract', region_name=os.getenv('AWS_REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
BUCKET = os.getenv('S3_UPLOADS_BUCKET', 'lerno-uploads-demo')

print("Amazon Textract OCR initialized")


def extract_text_from_image(image_bytes: bytes, filename: str = "image.png", user_id: str = "anonymous") -> str:
    """
    Extract text from an image using Amazon Textract

    Args:
        image_bytes: The image file content as bytes
        filename: Original filename for S3 key
        user_id: User ID for S3 key namespacing

    Returns:
        Extracted text from the image
    """
    try:
        # Upload to S3 temporarily
        key = f'ocr-temp/{user_id}/{filename}'
        s3.put_object(Bucket=BUCKET, Key=key, Body=image_bytes)

        # Run Textract
        response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': BUCKET, 'Name': key}}
        )

        # Extract text lines
        text = ' '.join([
            block['Text'] for block in response['Blocks']
            if block['BlockType'] == 'LINE'
        ])

        # Clean up temp file from S3
        s3.delete_object(Bucket=BUCKET, Key=key)

        if text.strip():
            print(f"[Textract] Extracted {len(text)} chars from {filename}")
            return text

        return "No text detected in image."

    except Exception as e:
        print(f"[Textract] Error extracting text: {e}")
        # Try to clean up even on error
        try:
            s3.delete_object(Bucket=BUCKET, Key=key)
        except Exception:
            pass
        raise ValueError(f"Failed to extract text from image: {str(e)}")


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """
    Extract text from image bytes directly using Textract (no S3 upload).
    Uses the synchronous Bytes-based API for small images (<5MB).

    Args:
        image_bytes: The image file content as bytes

    Returns:
        Extracted text from the image
    """
    try:
        response = textract.detect_document_text(
            Document={'Bytes': image_bytes}
        )

        text = ' '.join([
            block['Text'] for block in response['Blocks']
            if block['BlockType'] == 'LINE'
        ])

        if text.strip():
            print(f"[Textract] Extracted {len(text)} chars (direct bytes)")
            return text

        return "No text detected in image."

    except Exception as e:
        print(f"[Textract] Error extracting text: {e}")
        raise ValueError(f"Failed to extract text from image: {str(e)}")


def validate_math_image(image_bytes: bytes) -> bool:
    """
    Validate that the image is suitable for OCR processing
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))

        width, height = image.size
        if width < 50 or height < 50:
            raise ValueError("Image is too small. Please upload a larger image.")

        if width > 4096 or height > 4096:
            raise ValueError("Image is too large. Please upload a smaller image (max 4096x4096).")

        if image.format and image.format.lower() not in ['png', 'jpeg', 'jpg', 'gif', 'bmp', 'webp']:
            raise ValueError(f"Unsupported image format: {image.format}")

        return True

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")
